# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Product_template(models.Model):
    """inherit product template for customization

    Args:
        models (product_template): custom fields and method
    """
    _inherit = 'product.template'
    
    margin_product = fields.Float('Ratios', digits=(10, 4))
    margin_product_euro = fields.Float('Margin')
    is_bom_parent = fields.Boolean('Is BOM Parent')
    list_price = fields.Float(compute='_compute_list_price', string='Prix de vente')
    
    @api.depends('standard_price', 'margin_product')
    def _compute_list_price(self):
        purchase_price = 0
        total_price_sale = 0
        margin = 0
        for record in self:
            purchase_price = record.standard_price 
                
            if record.margin_product > 0:
                total_price_sale = purchase_price / record.margin_product

                margin = total_price_sale - purchase_price
            
            record.list_price = total_price_sale
            record.margin_product_euro = margin
            self.env['product.product'].search([('product_tmpl_id','=', record.id)]).write({
                                                                                                'margin_product': record.margin_product,
                                                                                            })
            
    @api.onchange('list_price','detailed_type')
    def _onchange_list_price(self):
        if self.detailed_type == 'service':
            self.list_price = 0
class Product_product(models.Model):
    """inherit product template for customization

    Args:
        models (product_template): custom fields and method
    """
    _inherit = 'product.product'
    
    margin_product = fields.Float('Ratios', digits=(10, 4))
    margin_product_euro = fields.Float('Margin')
    
    is_bom_parent = fields.Boolean('Is BOM Parent',related='product_tmpl_id.is_bom_parent')
    
    @api.onchange('margin_product')
    def _onchange_margin_product(self):
        self.env['product.template'].search([('id','=', self._origin.product_tmpl_id.id)]).write({'margin_product': self.margin_product})

        