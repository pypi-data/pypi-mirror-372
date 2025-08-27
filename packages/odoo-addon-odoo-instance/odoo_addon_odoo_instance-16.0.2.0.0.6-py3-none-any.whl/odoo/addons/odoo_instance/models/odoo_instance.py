import logging
import re
from datetime import datetime, time, timedelta
from urllib.parse import urlparse
import pytz
import requests
import yaml

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OdooInstance(models.Model):
    _name = 'odoo.instance'
    _description = 'Odoo Instance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # General Information

    name = fields.Char(string='Instance Name', required=True)
    description = fields.Text(string='Instance Description')
    start_date = fields.Date(string='Start Date')

    project_id = fields.Many2one(
        'project.project', string='Project', ondelete='set null')
    helpdesk_team_id = fields.Many2one(
        'helpdesk.ticket.team', string='Helpdesk Team', ondelete='set null')
    instance_url = fields.Char(string='Instance URL')

    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    client_contact_id = fields.Many2one(
        'res.partner', string='Client Contact', domain=[('type', '=', 'contact')])

    technician_ids = fields.Many2many(
        'res.users', string='Technicians', relation='odoo_instance_technician_rel')
    functional_ids = fields.Many2many(
        'res.users', string='Functional Experts', relation='odoo_instance_functional_rel')

    odoo_version_id = fields.Many2one(
        'odoo.version', string="Odoo Version", required=True)

    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('cancelled', 'Terminated')
    ], string='State', default='in_progress')

    # Technical Information

    inventory_url = fields.Char(string='Inventory URL')
    branch = fields.Char(string='Branch', required=True)
    odoo_release_id = fields.Many2one('odoo.release', string='Odoo Release')
    instance_type = fields.Selection([
        ('test', 'Test'),
        ('production', 'Production'),
    ], string="Instance Type", required=True)

    deploy_schedule = fields.One2many(
        'odoo.instance.schedule', 'instance_id', string="Deploy Schedule")

    unavailable_windows = fields.One2many(
        'odoo.instance.unavailable_schedule', 'instance_id', string='Unavailable Windows')

    deploy_event_ids = fields.One2many(
        'calendar.event', 'instance_id', string='Deploy Events')

    server_information = fields.Text(string='Server Information')
    requirements_url = fields.Char(string='Requirements URL')
    module_ids = fields.Many2many('odoo.instance.module', string='Modules')

    server_type = fields.Selection([
        ('cx11', 'cx11'),
        ('cpx11', 'cpx11'),
        ('cx21', 'cx21'),
        ('cpx21', 'cpx21'),
        ('cx31', 'cx31'),
        ('cpx31', 'cpx31'),
        ('cx41', 'cx41'),
        ('cpx41', 'cpx41'),
        ('cx51', 'cx51'),
        ('cpx51', 'cpx51'),
    ], string="Server Type")

    troubleshooting_ids = fields.One2many(
        'odoo.instance.troubleshooting', 'instance_id', string='Troubleshooting')
    deploy_duration = fields.Float(
        string='Deploy Duration', default=1.0, help="Duration in hours")

    database_ids = fields.One2many(
        'odoo.instance.database', 'instance_id', string='Databases')

    # Functional Information
    process_ids = fields.Many2many(
        'odoo.instance.process',
        'odoo_instance_process_rel',
        'instance_id',
        'process_id',
        string='Processes'
    )
    available_windows = fields.One2many(
        'odoo.instance.window', 'instance_id', string='Available Windows')

    functional_requirement_ids = fields.One2many(
        'odoo.instance.functional_requirement', 'odoo_instance_id', string='Functional Requirements')

    functional_configuration_ids = fields.Many2many(
        'odoo.instance.functional_configuration',
        string='Functional Configurations',
        relation='odoo_instance_functional_configuration_rel',
        column1='odoo_instance_id',
        column2='functional_configuration_id',
        track_visibility='onchange',
        help='List of functional configurations related to the current instance.'
    )

    # Commercial Information
    contact_role_id = fields.Many2one('res.partner', string='Rol de Contacto')
    maintenance_contract_ids = fields.Char(string='Contratos de Mantenimiento')
    support_contract_ids = fields.Char(string='Contratos de Soporte')
    implementation_contract_id = fields.Char(
        string='Contrato de Implementación')

    # maintenance_contract_ids = fields.Many2many('contract.contract', string='Contratos de Mantenimiento', relation='odoo_instance_maintenance_contract_rel')
    # support_contract_ids = fields.Many2many('contract.contract', string='Contratos de Soporte', relation='odoo_instance_support_contract_rel')
    # implementation_contract_id = fields.Many2one('contract.contract', string='Contrato de Implementación', relation='odoo_instance_implementation_contract_rel')

    def _strip_protocol_and_port(self):
        parsed_url = urlparse(self.instance_url)
        return parsed_url.hostname

    def _get_instance_config_yaml(self, url):
        def ignore_vault(loader, node):
            return "<<VAULT_BLOCK>>"
        yaml.SafeLoader.add_constructor('!vault', ignore_vault)
        # Get the YAML content
        response = requests.get(url)
        if response.status_code != 200:
            return {}
        response.raise_for_status()
        return yaml.safe_load(response.text)

    def _update_instance_dbs(self):
        base_url = self.inventory_url
        branch = self.branch
        instance_url = self._strip_protocol_and_port()
        urls = {
            'host_vars': f"{base_url}/-/raw/{branch}/inventory/host_vars/{instance_url}/config.yml",
            'group_vars': f"{base_url}/-/raw/{branch}/inventory/group_vars/all.yml",
        }

        for url in urls.values():
            yaml_content = self._get_instance_config_yaml(url)
            odoo_dbs = yaml_content.get("odoo_role_odoo_dbs", [])
            test_dbs = yaml_content.get("odoo_role_test_dbs", [])

            instance_dbs_info = []
            self.database_ids.unlink()

        for db in odoo_dbs:
            self.database_ids.create({
                'name': db,
                'is_test': False,
                'instance_id': self.id,
            })

        for test_db in test_dbs:
            self.database_ids.create({
                'name': test_db,
                'is_test': True,
                'instance_id': self.id,
            })

    def update_odoo_release(self):
        inventory_url = self.inventory_url
        branch = self.branch
        raw_inventory_url = f"{inventory_url}/-/raw/{branch}/inventory/group_vars/all.yml"
        response = requests.get(raw_inventory_url)

        if response.status_code == 200:
            inventory_data = yaml.safe_load(response.text)
            odoo_release_str = inventory_data.get('odoo_role_odoo_release')

            if odoo_release_str:
                odoo_version, release_date_str = odoo_release_str.split('_')
                release_date = fields.Date.from_string(release_date_str)

                odoo_version_id = self.env['odoo.version'].search(
                    [('name', '=', odoo_version)], limit=1)
                if odoo_version_id:
                    odoo_release = self.env['odoo.release'].search([
                        ('name', '=', odoo_release_str),
                        ('odoo_version_id', '=', odoo_version_id.id)
                    ], limit=1)

                    if not odoo_release:
                        odoo_release = self.env['odoo.release'].create({
                            'name': odoo_release_str,
                            'release_date': release_date,
                            'odoo_version_id': odoo_version_id.id,
                        })

                    self.odoo_release_id = odoo_release

    def update_instance_info(self):
        for instance in self:
            # Update Odoo Release
            instance.update_odoo_release()

            # Update Instance DBs
            instance._update_instance_dbs()

    @api.model
    def enqueue_update_instance_info(self):
        instances = self.search([])
        for instance in instances:
            if instance.inventory_url:
                instance.with_delay().update_instance_info()
            if instance.requirements_url:
                instance.with_delay().download_and_process_requirements_txt()

    def toggle_state(self):
        state_order = ['in_progress', 'running', 'paused', 'cancelled']
        next_state_index = (state_order.index(
            self.state) + 1) % len(state_order)
        self.state = state_order[next_state_index]

    def download_and_process_requirements_txt(self):
        if not self.requirements_url:
            return
        response = requests.get(self.requirements_url)
        if response.status_code == 200:
            requirements_txt = response.text
            self.import_requirements_txt(requirements_txt)
        else:
            raise UserError(
                ('Error downloading requirements.txt file. Status code: %s') % response.status_code)

    def open_calendar_event_wizard(self):
        self.ensure_one()
        wizard = self.env['odoo.instance.calendar.event.wizard'].create({
            'instance_id': self.id,
            'date_start': self.next_window,
            'duration': self.deploy_duration,
        })

        return {
            'name': ('Create Calendar Event'),
            'type': 'ir.actions.act_window',
            'res_model': 'odoo.instance.calendar.event.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def import_requirements_txt(self, file_content):
        """Parse a requirements.txt file and update the modules field."""
        Module = self.env['odoo.instance.module']
        ModuleVersion = self.env['odoo.instance.module.version']
        modules_to_link = []

        current_versions = ModuleVersion.search([
            ('instance_ids', 'in', [self.id]),
        ], limit=1)
        for version in current_versions:
            # delete the instance in the version
            version.instance_ids = [(3, self.id)]
            # if the version is not used by any instance, delete it
            if not version.instance_ids:
                version.unlink()

        for line in file_content.splitlines():
            line = line.strip()
            if not line or '==' not in line:
                continue

            module_name, version = line.split('==')
            module = Module.search(
                [('technical_name', '=', module_name)], limit=1)

            if not module:
                module_data = self.get_module_name_from_pypi(module_name)

                module = Module.create({
                    'technical_name': module_data['technical_name'],
                    'name': module_data['name'],
                    'module_type': module_data['module_type'],
                    'odoo_version_id': module_data['odoo_version_id'],
                    'pypi_url': f'https://pypi.org/project/{module_name}/',
                    'is_odoo_module': module_data['is_odoo_module'],
                })

            version_record = ModuleVersion.search([
                ('name', '=', version),
                ('module_id', '=', module.id),
            ], limit=1)

            if version_record:
                # Update the existing version record by adding the instance
                _logger.critical("Version found %s",
                                 version_record.instance_ids)
                version_record.instance_ids |= self
            else:
                # Create a new version record
                _logger.critical("Version not found, creating it")
                version_record = ModuleVersion.create({
                    'name': version,
                    'module_id': module.id,
                    'instance_ids': [(4, self.id)],
                })

            modules_to_link.append(module.id)

        self.module_ids = [(6, 0, modules_to_link)]
        ModuleVersion.archive_or_delete_unassociated_module_versions()

    def get_module_name_from_pypi(self, technical_name):
        url = f'https://pypi.org/pypi/{technical_name}/json'
        response = requests.get(url)
        module_data = {
            'technical_name': technical_name,
            'name': technical_name,
            'module_type': 'dep',
            'odoo_version_id': self.odoo_version_id.id,
            'is_odoo_module': False
        }

        if response.status_code == 200:
            data = response.json()
            module_data['technical_name'] = data['info']['name']
            module_data['name'] = data['info']['summary']
            module_data['home_page'] = data['info']['home_page']
            module_data['is_odoo_module'] = False
            _logger.debug('Importing technical_name: %s', technical_name)

            if 'odoo' in module_data['technical_name'].lower():
                module_data['is_odoo_module'] = True

            if module_data['is_odoo_module']:
                # Check if the module is Odoo core or OCA
                if 'oca' in module_data['home_page'].lower():
                    module_data['module_type'] = 'OCA'

                # extract odoo version from version key. Example: version	"14.0.1.0.3"
                odoo_version_pattern = r"(\d{1,2}\.\d{1,2})"
                match = re.search(odoo_version_pattern,
                                  data['info']['version'])
                if match:
                    module_data['odoo_version'] = match.group(1)
                    module_data['odoo_version_id'] = self.env['odoo.version'].search([('name', '=', match.group(1))],
                                                                                     limit=1).id

        else:
            _logger.warning(
                f'Error fetching module name from pypi.org for {technical_name}')

        return module_data

    def compute_available_windows(self):
        for instance in self:
            # Clear existing available windows
            instance.available_windows.unlink()

            # Calculate the available windows in the next 7 days
            now_utc = datetime.utcnow()
            user_tz = pytz.timezone(self.env.user.tz or 'UTC')
            now_local = now_utc.astimezone(user_tz)

            for i in range(7):
                current_date = now_local.date() + timedelta(days=i)
                current_weekday = str(current_date.weekday())

                unavailable_periods = []
                for schedule in instance.unavailable_windows:
                    if schedule.day_of_week == current_weekday:
                        unavailable_periods.append(
                            schedule.get_unavailable_periods(current_date, user_tz))

                unavailable_periods.sort()
                available_start_time = user_tz.localize(
                    datetime.combine(current_date, time(0, 0)))

                for period_start, period_end in unavailable_periods:
                    if period_start > available_start_time:
                        deploy_end_time = period_start - \
                            timedelta(hours=instance.deploy_duration)
                        if deploy_end_time > available_start_time:
                            instance.available_windows.create({
                                'instance_id': instance.id,
                                'start_time': available_start_time.astimezone(pytz.utc).replace(tzinfo=None),
                                'end_time': deploy_end_time.astimezone(pytz.utc).replace(tzinfo=None),
                            })

                    available_start_time = period_end

                available_end_time = user_tz.localize(
                    datetime.combine(current_date, time.max))
                if available_end_time > available_start_time:
                    deploy_end_time = available_end_time - \
                        timedelta(hours=instance.deploy_duration)
                    if deploy_end_time > available_start_time:
                        instance.available_windows.create({
                            'instance_id': instance.id,
                            'start_time': available_start_time.astimezone(pytz.utc).replace(tzinfo=None),
                            'end_time': deploy_end_time.astimezone(pytz.utc).replace(tzinfo=None),
                        })
            instance.action_delete_past_or_orphan_windows()

    @api.onchange('odoo_version_id')
    def _onchange_odoo_version_id(self):
        if self.odoo_version_id:
            self.module_ids = False
            return {
                'domain': {
                    'module_ids': [('odoo_version_id', '=', self.odoo_version_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'module_ids': []
                }
            }

    def open_instance_url(self):
        self.ensure_one()
        if not self.instance_url:
            raise UserError(("No hay URL para esta instancia."))
        return {
            'type': 'ir.actions.act_url',
            'url': self.instance_url,
            'target': 'new',
        }

    def action_delete_past_or_orphan_windows(self):
        self.env["odoo.instance.window"].delete_past_or_orphan_windows()

    def action_clear_windows(self):
        self.env['odoo.instance.window'].search(
            [('instance_id', '=', self.id)]).unlink()

    def write(self, vals):
        # Si hay cambios en 'functional_configuration_ids'
        if 'functional_configuration_ids' in vals:
            # Consigue las nuevas configuraciones
            new_config_ids = set(vals['functional_configuration_ids'][0][2])
            
            for record in self:
                # Consigue las configuraciones antiguas
                old_config_ids = set(record.functional_configuration_ids.ids)
                
                # Encuentra las configuraciones que se añadieron y se eliminaron
                added_config_ids = new_config_ids - old_config_ids
                removed_config_ids = old_config_ids - new_config_ids

                # Obtiene los nombres de las configuraciones añadidas y eliminadas
                added_config_names = self.env['odoo.instance.functional_configuration'].browse(added_config_ids).mapped('name')
                removed_config_names = self.env['odoo.instance.functional_configuration'].browse(removed_config_ids).mapped('name')

                # Publica mensajes en el chatter
                for config_name in added_config_names:
                    record.message_post(body="Añadida configuración funcional: %s" % config_name)
                for config_name in removed_config_names:
                    record.message_post(body="Eliminada configuración funcional: %s" % config_name)
                
        return super().write(vals)

class OdooInstanceSchedule(models.Model):
    _name = 'odoo.instance.schedule'
    _description = 'Deploy Schedule'

    instance_id = fields.Many2one('odoo.instance', string="Instance")
    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string="Day of the Week", required=True)
    start_time = fields.Float(string="Start Time", required=True)
    end_time = fields.Float(string="End Time", required=True)
    duration = fields.Float(
        string='Duration', default=1.0, help="Duration in hours")


class FunctionalRequirement(models.Model):
    _name = 'odoo.instance.functional_requirement'
    _description = 'Functional Requirement'

    name = fields.Char('Requirement', required=True)
    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('waiting_validation', 'Waiting for Validation')
    ], string='Status', default='not_started', required=True)
    odoo_instance_id = fields.Many2one(
        'odoo.instance', string='Odoo Instance')

class OdooInstanceFunctionalConfiguration(models.Model):
    _name = 'odoo.instance.functional_configuration'
    _description = 'Odoo Instance Functional Configuration'
    name = fields.Char('Configuration', required=True)
    odoo_version_id = fields.Many2one(
        'odoo.version', string="Odoo Version", required=True)
    description = fields.Text('Description')
    required_modules= fields.Many2many(
        'odoo.instance.module', string='Required Modules')
    handbook_url = fields.Text(string='Handbook URL')
    
class OdooInstanceTroubleshooting(models.Model):
    _name = 'odoo.instance.troubleshooting'
    _description = 'Odoo Instance Troubleshooting'

    date = fields.Date(string='Date', default=fields.Date.context_today)
    title = fields.Char(string='Title', required=True)
    url = fields.Char(string='URL')
    type = fields.Selection([
        ('postmortem', 'Post Mortem'),
        ('config', 'Configuration'),
        ('other', 'Other')
    ], string='Type', default='config', required=True)

    instance_id = fields.Many2one(
        'odoo.instance', string='Instance', ondelete='cascade')


class OdooInstanceUnavailableSchedule(models.Model):
    _name = 'odoo.instance.unavailable_schedule'
    _description = 'Unavailable Deploy Schedule'

    instance_id = fields.Many2one('odoo.instance', string="Instance")
    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string="Day of the Week", required=True)
    start_time = fields.Float(string="Start Time", required=True)
    end_time = fields.Float(string="End Time", required=True)

    def get_unavailable_periods(self, current_date, user_tz):
        schedule_hour = int(self.start_time)
        schedule_minute = int((self.start_time % 1) * 60)
        schedule_time = time(schedule_hour, schedule_minute, 0)
        schedule_end_hour = int(self.end_time)
        schedule_end_minute = int((self.end_time % 1) * 60)
        schedule_end_time = time(schedule_end_hour, schedule_end_minute, 0)

        start_time = user_tz.localize(
            datetime.combine(current_date, schedule_time))
        end_time = user_tz.localize(
            datetime.combine(current_date, schedule_end_time))

        return (start_time, end_time)
