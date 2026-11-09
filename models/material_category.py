from odoo import api, fields, models, tools
from odoo.release import description


class MaterialCategory(models.Model):
    _name = 'material.category'

    name = fields.Char(required=True)
    description=fields.Text()
    active = fields.Boolean(default=True)

