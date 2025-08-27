import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OdooInstanceWindow(models.Model):
    _name = 'odoo.instance.window'
    _description = 'Available Deployment Window'

    instance_id = fields.Many2one(
        'odoo.instance', string='Instance', ondelete='cascade')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')

    def open_calendar_event_wizard(self):
        self.ensure_one()
        wizard = self.env['odoo.instance.window.wizard'].create({
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.instance_id.deploy_duration,
            'attendee_ids': [(6, 0, self.instance_id.technician_ids.ids)],
            'instance_id': self.instance_id.id,
        })
        return {
            'name': 'Create Deploy Event',
            'type': 'ir.actions.act_window',
            'res_model': 'odoo.instance.window.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'instance_name': self.instance_id.name},
        }

    @api.model
    def delete_past_or_orphan_windows(self):
        now = fields.Datetime.now()
        past_windows = self.search([('end_time', '<', now)])
        orphan_windows = self.search([('instance_id', '=', False)])
        to_delete = past_windows + orphan_windows
        to_delete.unlink()

    @api.constrains('date_start', 'window_end_time')
    def _check_date_start(self):
        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise ValidationError("The start date cannot be later than the end time of the available window.")
