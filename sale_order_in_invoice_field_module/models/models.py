#-*- coding: utf-8 -*-
# Version qui fonctionne mais créer un bug car probablement le module compta pas installer( à corriger)
from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    @api.depends('invoice_origin')
    def _compute_sale_order(self):
        for record in self:
            sale_order = self.env['sale.order'].search([('name','=',record.invoice_origin)], limit=1)
            record.x_studio_bc = sale_order.id if sale_order else False

    x_studio_bc = fields.Many2one('sale.order', string='Sale Order', compute='_compute_sale_order')
