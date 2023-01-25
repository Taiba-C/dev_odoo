# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Product_template(models.Model):
    """inherit product template for customization

    Args:
        models (product_template): custom fields and method
    """
    _inherit = 'product.template'
    
    margin_product = fields.Float('Ratios')
    is_bom_parent = fields.Boolean('Is BOM Parent')
    
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
    
    is_bom_parent = fields.Boolean('Is BOM Parent')
    