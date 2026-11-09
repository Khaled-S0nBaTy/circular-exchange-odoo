from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class MaterialOffer(models.Model):
    _name = 'material.offer'
    _description = 'Material Offer'

    material_request_id = fields.Many2one("material.request")
    material_list_id = fields.Many2one("material.list")
    proposed_qty = fields.Float(required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('proposed', 'Proposed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='draft')

    @api.constrains('proposed_qty', 'material_list_id', 'material_request_id')
    def check_validation(self):
        for rec in self:
            if (
                    rec.proposed_qty <= 0
                    or rec.proposed_qty > rec.material_list_id.available_qty
                    or rec.proposed_qty > rec.material_request_id.requested_qty
            ):
                raise ValidationError(
                    "Proposed quantity must be greater than zero and cannot exceed "
                    "the listing or request quantity."
                )
            if (
                    rec.material_list_id.material_category_id != rec.material_request_id.material_category_id
            ):
                raise ValidationError(
                    "Proposed category does not match material category."
                )

            if self.proposed_qty > self.material_request_id.remaining_qty:
                raise ValidationError('This offer overfills the remaining requested quantity')

    def accept_offer(self):
        self.ensure_one()
        already_accepted_qty = 0
        if self.status == 'proposed':
            # accepted_offer = self.env['material.offer'].search([
            #     ('material_request_id', '=', self.material_request_id.id),
            #     ('status', '=', 'accepted'),
            # ])
            #
            # for rec in accepted_offer:
            #     already_accepted_qty += rec.proposed_qty
            #
            # remaining_qty = self.material_request_id.requested_qty - already_accepted_qty

            if self.material_list_id.available_qty < self.proposed_qty:
                raise UserError('Listing has insufficient stock')

            # elif self.proposed_qty > self.material_request_id.remaining_qty:
            #     raise ValidationError('This offer overfills the request')

            elif self.proposed_qty < self.material_request_id.remaining_qty:
                self.material_list_id.available_qty -= self.proposed_qty
                self.status = 'accepted'
            elif self.proposed_qty == self.material_request_id.remaining_qty:
                self.material_list_id.available_qty -= self.proposed_qty
                self.material_request_id.status = 'fulfilled'
                self.status = 'accepted'

    def reject_offer(self):
        for rec in self:
            if rec.status == 'proposed':
                rec.status = 'rejected'
