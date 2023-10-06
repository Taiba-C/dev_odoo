# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Sale_order(models.Model):
    _inherit = 'sale.order'
    
    def action_confirm(self):
        res = super(Sale_order,self).action_confirm()
        
        self.opportunity_id.write({'stage_id':3})
        
        return res
    

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.model
    def _create_invoices(self, sale_orders):        
        invoices = super(SaleAdvancePaymentInv, self.with_context(self._context))._create_invoices(sale_orders)
        order = self.env['sale.order'].search([('id','=', self._context['active_id'])])
        if len(order.invoice_ids) == 1:
            # check state of opportunity
            order.opportunity_id.write({'stage_id':4})
    
        
        return invoices