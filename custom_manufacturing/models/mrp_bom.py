# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Mrp_bom(models.Model):
    _inherit = "mrp.bom"    
    
    @api.model
    def create(self, vals):
        """
            change product template and product product as bom parent
        """
        res = super(Mrp_bom, self).create(vals)
        
        self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])]).write({'is_bom_parent': True})
        self.env['product.product'].search([('product_tmpl_id', '=', vals['product_tmpl_id'])]).write({'is_bom_parent': True})
        
            
        return res
    
    def unlink(self):
        """
            change product template and product product as bom parent
        """
        
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})
        self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})
        
        return super(Mrp_bom, self).unlink()

    def write(self, vals):
        """
            change product template and product product as bom parent
        """
        
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})
        self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})

        res = super(Mrp_bom, self).write(vals)
        
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': True})
        self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': True})
  
        return res  
    
