from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools.populate import compute


class MaterialRequest(models.Model):
    _name = 'material.request'

    name = fields.Char(required=True)
    requested_qty = fields.Float(required=True)
    remaining_qty = fields.Float(compute='_compute_remaining', store=True)
    unit_of_measure = fields.Char(required=True)
    destination_city = fields.Char(required=True)
    needed_date = fields.Date(required=True)
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('fulfilled', 'Fulfilled'),
        ], default='draft')
    buyer_company_id = fields.Many2one('res.partner', domain=[('is_company', '=', True)], required=True)
    material_category_id = fields.Many2one('material.category', required=True)
    material_offer_ids = fields.One2many('material.offer','material_request_id')
    destination_country_id = fields.Many2one('res.country', required=True)

    @api.constrains('requested_qty')
    def check_requested_qty_zero(self):
        for rec in self:
            if rec.requested_qty <= 0:
                raise ValidationError('Quantity can not be zero')

    def action_find_matches(self):
        self.ensure_one()
        if self.status != 'open':
            raise UserError("Only open requests can be matched.")

        matching_listings = self.env['material.list'].search([
            ('status', '=', 'available'),
            ('material_category_id', '=', self.material_category_id.id),
            # for the relations field we use '.id' cuz it gives you that record’s database ID (In Python search() domain, use the ID to compare the stored Many2one link)
            ('available_qty', '>=', self.requested_qty),
            ('unit_of_measure', '=', self.unit_of_measure),
            ('pickup_city', '=', self.destination_city),
            ('country_id', '=', self.destination_country_id.id),
            # for the relations field we use '.id' cuz it gives you that record’s database ID (In Python search() domain, use the ID to compare the stored Many2one link)
            ('available_date', '<=', self.needed_date),
            # in these domains it compares between the values of (material listed) with the values of (material requested), each condition is a tuple containing a field name(material_list), an operator, and a value(material_request). Odoo combines these conditions with AND, so a listing must pass all of them
        ])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Matching Material Listings',
            'res_model': 'material.list',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', matching_listings.ids)],
            'context': {'from_material_request_id': self.id, },
        }

    @api.depends('requested_qty', 'material_offer_ids.proposed_qty', 'material_offer_ids.status')
    def _compute_remaining(self):
        for rec in self:
            already_accepted_qty = 0
            # if self.material_offer_ids.status == 'proposed':
            accepted_offer = self.env['material.offer'].search([
                ('material_request_id', '=', rec.id),
                ('status', '=', 'accepted'),
            ])

            for lop in accepted_offer:
                already_accepted_qty += lop.proposed_qty

            rec.remaining_qty = rec.requested_qty - already_accepted_qty
