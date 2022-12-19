# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Product_template(models.Model):
    """inherit product template for customization

    Args:
        models (product_template): custom fields and method
    """
    _inherit = "product.template"
    
    margin_product = fields.Float('Marge')