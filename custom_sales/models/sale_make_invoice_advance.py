# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.model
    def _create_invoices(self, sale_orders):        
        invoices = super(SaleAdvancePaymentInv, self.with_context(self._context))._create_invoices(sale_orders)
        
        account_invoices = sale_orders.mapped('invoice_ids')
        sum_invoices = round(sum(account_invoices.mapped('amount_total')),2)
        
        amount_order  = sale_orders.amount_total
        invoice_type = self.advance_payment_method
        if invoice_type != "delivered":
            
            rest_of_amount =  amount_order - sum_invoices
            if rest_of_amount > 0:
                invoices.invoice_types = "down_payment_invoice"
            elif rest_of_amount <=0:
                invoices.invoice_types = "invoice_of_balance"
        else:
            if self.deduct_down_payments:
                invoices.invoice_types = "invoice_of_balance"
    
        
        return invoices