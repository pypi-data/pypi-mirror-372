from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    instance_ids = fields.One2many('odoo.instance', 'project_id', string='Instances')
