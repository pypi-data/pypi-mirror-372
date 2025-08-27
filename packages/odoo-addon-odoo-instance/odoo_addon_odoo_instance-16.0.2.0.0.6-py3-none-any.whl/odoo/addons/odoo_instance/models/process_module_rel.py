from odoo import models, fields


class ProcessModuleRel(models.Model):
    _name = "process.module.rel"
    _description = "Process Module Relation"

    process_id = fields.Many2one("odoo.instance.process", string="Process", required=True, ondelete='cascade')
    module_id = fields.Many2one("odoo.instance.module", string="Module", required=True, ondelete='cascade')
    instance_id = fields.Many2one("odoo.instance", string="Instance", required=True, ondelete='cascade')
