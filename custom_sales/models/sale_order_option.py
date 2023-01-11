# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

 
class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
        
    parent_id = fields.Many2one('product.template', string='Parent')
    
    purchase_price = fields.Float('Purchase price')
    
    margin = fields.Float('Margin €', readonly=True)
    
    margin_product = fields.Float('Coefficient')
    
    margin_percent = fields.Float('Margin %', readonly=True)
    
    total_purchase_price = fields.Float('Total purchase price', readonly=True)
    
    total_sale_price = fields.Float('Total sale price', readonly=True)
        
    # @api.onchange('purchase_price')
    # def _onchange_purchase_price(self):
    #     self.update_option_line()
    
    # @api.onchange('quantity')
    # def _onchange_quantity(self):
    #     self.update_option_line()

    
    # @api.onchange('margin_product')
    # def _onchange_margin_product(self):
    #     self.update_option_line()
        
    # def update_option_line(self):
    #     """
    #         update total on change
    #     """
    #     if self.product_id:
    #         if self.product_id.detailed_type != 'service':
    #             # prix total achat
    #             self.total_purchase_price = self.purchase_price * self.quantity
                
    #             # prix total vente
    #             if self.margin_product > 0:
    #                 self.total_sale_price = self.total_purchase_price / self.margin_product
                    
    #             if self.margin_product == 0 :
    #                 raise UserError("You cannot set this value to margin as 0!")
    #             if self.margin_product > 1 :
    #                 raise UserError("You cannot set this value up to 1!")
                    
                
    #             # marge en €
    #             self.margin = self.total_sale_price - self.total_purchase_price
    #             if self.margin < 0:
    #                 self.margin = 0
                
    #             # marge %
    #             if self.total_sale_price > 0:
    #                 self.margin_percent = self.margin / self.total_sale_price
                
    