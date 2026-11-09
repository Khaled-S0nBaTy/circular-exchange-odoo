from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError, UserError


class MaterialList(models.Model):
    _name = 'material.list'

    name = fields.Char(required=True)
    material_type=fields.Char(required=True)
    available_qty = fields.Float(required=True)
    unit_of_measure = fields.Char(required=True)
    available_date = fields.Date(required=True)
    status = fields.Selection (
        [
        ('draft', 'Draft'),
        ('available', 'Available'),
    ])
    pickup_city=fields.Text()

    material_category_id = fields.Many2one('material.category')
    supplier_id = fields.Many2one('res.partner', domain=[('is_company', '=', True)])
    country_id = fields.Many2one('res.country')

    @api.constrains('available_qty')
    def check_available_qty_zero(self):
        for rec in self:
            if rec.available_qty <= 0:
                raise ValidationError ('Quantity can not be zero')

    def action_create_offer(self):
        self.ensure_one()

        request = self.env['material.request'].browse(self.env.context.get('from_material_request_id')).exists()

        if not request:
            raise UserError("The related material request could not be found.")

        if request.status != 'open':
            raise UserError ("Only 'open' requests can receive offers.")

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'material.offer',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_material_request_id': request.id,
                        'default_material_list_id': self.id,
                        'default_status': 'proposed'},
        }