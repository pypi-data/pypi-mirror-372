from odoo import fields, models


class InstanceCalendarEvent(models.Model):
    _inherit = 'calendar.event'
    instance_id = fields.Many2one(
        'odoo.instance', string='Instance', ondelete='cascade')
