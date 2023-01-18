# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Mrp_bom(models.Model):
    _inherit = 'mrp.bom'    
    
    @api.model_create_multi
    def create(self, val_lists):
        """
            change product template and product product as bom parent
        """
        for vals in val_lists:
            if self.check_existing_bom(vals['product_tmpl_id']) == False:
                res = super(Mrp_bom, self).create(vals)
                
                self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])]).write({'is_bom_parent': True})
                self.env['product.product'].search([('product_tmpl_id', '=', vals['product_tmpl_id'])]).write({'is_bom_parent': True})
                    
                return res
            else:
                raise UserError("This BOM are already exist, try to create new product!")
    
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
        # TODO: search function to verify if user change product_templ_id
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})
        self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})

        res = super(Mrp_bom, self).write(vals)
        
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': True})
        self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': True})

        return res  
    
    def check_existing_bom(self,product_tmpl_id):
        """
            check if bom is already exist and return boolean
        """
        if product_tmpl_id:
            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_tmpl_id)])
            if len(bom) == 0:
                return False
            else:
                return True
            