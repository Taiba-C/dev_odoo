# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
class Sale_order_subcontractor(models.Model):
    _name="sale.order.subcontractor"
    _inherit = ['mail.thread']
    _rec_name = "partner_id"

    order_id = fields.Many2one('sale.order', string='order id')

    partner_id = fields.Many2one('res.partner', string='Sous-traitant', required=True)
    unit_price = fields.Float('Coût unitaire', required=True)
    product_template_id = fields.Many2one('product.template', string='Article')
    
    product_id = fields.Many2one(
        string='product',
        comodel_name='product.product',
        compute = "_compute_product_id",
        ondelete='restrict',
    )
    
    order_line_id = fields.Many2one('sale.order.line', string='order line link', ondelete='cascade')

    order_line_created = fields.Boolean('Order LIne Created')

    state = fields.Selection(
        related='order_id.state',
        string="Status du devis",
        copy=False, store=True, precompute=True)

    def set_unit_price_with_margin(self):
        result = (self.unit_price * self.partner_id.subcontractor_margin) + self.unit_price
        return result

    def action_create_order_line(self):
        unit_price_with_margin = self.set_unit_price_with_margin()
        # Create a new record for sale order line
        order_line = self.env['sale.order.line'].create({
            'order_id': self.order_id.id,
            'temp_price_unit': unit_price_with_margin,
            'name': self.product_template_id.name,
            'product_id': self.product_id.id,
            'product_uom_qty': 1,
        })

        # Link the created sale order line with subcontractor
        self.order_line_id = order_line.id

        # Set the flag to indicate order line creation
        self.order_line_created = True

    @api.depends('product_template_id')
    def _compute_product_id(self):
        for record in self:
            record.product_id = self.env['product.product'].search([('product_tmpl_id', '=', record.product_template_id.id)], limit=1).id

    def unlink(self):
        """
            change product template and product product as bom parent
        """
        if self.order_line_created:
            order_line = self.env['sale.order.line'].search([('id', '=', self.order_line_id.id)])
            order_line.unlink()
        return super(Sale_order_subcontractor, self).unlink()
