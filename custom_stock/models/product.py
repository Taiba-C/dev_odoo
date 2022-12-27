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
    
class Mrp_bom(models.Model):
    _inherit = "mrp.bom"
    
    @api.model
    def create(self, vals):
        res = super(Mrp_bom, self).create(vals)
        
        self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])]).write({'is_bom_parent': True})
        
            
        return res
    
    def unlink(self):
        
        self.env['product.template'].search([('id', '=', self.product_tmpl_id)]).write({'is_bom_parent': False})
        
        return super(Mrp_bom, self).unlink()

    def write(self, vals):
        
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})

        res = super(Mrp_bom, self).write(vals)
        
        self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])]).write({'is_bom_parent': True})
  
        return res  
    
