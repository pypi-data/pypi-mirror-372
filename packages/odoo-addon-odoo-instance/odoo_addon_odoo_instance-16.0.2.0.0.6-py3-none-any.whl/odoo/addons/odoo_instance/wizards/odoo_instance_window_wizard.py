import logging
from datetime import timedelta

from odoo import models, fields

_logger = logging.getLogger(__name__)


class OdooInstanceWindowWizard(models.TransientModel):
    _name = 'odoo.instance.window.wizard'
    _description = 'Wizard for creating deployment events'

    start_time = fields.Datetime('Start Time', required=True)
    end_time = fields.Datetime('End Time', required=True)
    description = fields.Text('Description')
    attendee_ids = fields.Many2many('res.users', string='Attendees')
    instance_id = fields.Many2one('odoo.instance', string='Instance', required=True)
    duration = fields.Float('Duration', required=True)
    available_windows = fields.Text('Available Windows', readonly=True)

    def create_calendar_event(self):
        self.ensure_one()
        CalendarEvent = self.env['calendar.event']
        event_name = f"[{self._context.get('instance_name', 'Instance')}] Deploy"

        # Agregar técnicos como participantes del evento
        attendee_ids = [(0, 0, {'partner_id': user.partner_id.id}) for user in self.attendee_ids]
        end_hour = self.start_time + timedelta(hours=self.duration)
        deploy_tag = self.env['calendar.event.type'].search([('name', '=', 'Deploy')], limit=1)
        _logger.debug(f"Creating event with name: {event_name}")
        _logger.debug(f"Attendees: {attendee_ids}")
        _logger.debug(f"Instance: {self.instance_id}")
        vals = {
            'name': event_name,
            'start': self.start_time,
            'stop': end_hour,
            'description': self.description,
            'allday': False,
            'privacy': 'public',
            'event_tz': self.env.user.tz or 'UTC',
            'attendee_ids': attendee_ids,
            'instance_id': self.instance_id.id,
            'categ_ids': [(6, 0, [deploy_tag.id])],
        }
        _logger.debug(f"Creating event with values: {vals}")
        event = CalendarEvent.create(vals)
        _logger.info(f"Event created: {event}")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'res_id': event.id,
            'view_mode': 'form',
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
        }
