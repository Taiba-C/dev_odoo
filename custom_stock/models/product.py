# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Product_template(models.Model):
    """inherit product template for customization

    Args:
        models (product_template): custom fields and method
    """
    _inherit = "product.template"
    
    margin_product = fields.Float('Taux Com')
    is_bom_parent = fields.Boolean('Is BOM Parent')
class Product_product(models.Model):
    """inherit product template for customization

    Args:
        models (product_template): custom fields and method
    """
    _inherit = "product.product"
    
    is_bom_parent = fields.Boolean('Is BOM Parent')
    