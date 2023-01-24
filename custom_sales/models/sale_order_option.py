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
    
                
    