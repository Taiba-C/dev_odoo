# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Mrp_bom(models.Model):
    _inherit = 'mrp.bom'    
    
    @api.onchange('bom_line_ids')
    def _check_duplicated_bom_line_ids(self):
        for record in self:
            existing_product_list = []
            duplicate_product = []
            for bom in record.bom_line_ids:
                if bom.product_id.id in existing_product_list:
                    duplicate_product.append("* " + bom.product_id.name)
                elif len(duplicate_product) == 0:
                    existing_product_list.append(bom.product_id.id)
            if len(duplicate_product) > 0:
                products = '\n'.join(duplicate_product)
                raise UserError(f"Ces articles existent déjà dans la nomenclature de {record.product_tmpl_id.name}: \n"
                                f"{products}")
    
    def find_duplicated(self):
        """
            Find all BOM with duplicate product in line
        """
        boms = self.env['mrp.bom'].sudo().search([])
        # import pudb; pudb.set_trace()

        has_duplicated_product = []
        for bom in boms:
            print(bom.product_tmpl_id.name)
            print(len(bom.bom_line_ids.ids))
            print(len(list(set(bom.bom_line_ids.ids))))
            print("******")

            ids = len(bom.bom_line_ids.ids)
            set_ids = len(list(set(bom.bom_line_ids.ids)))
            duplicated_product = []
            if ids != set_ids:
                duplicated_product.append(bom.product_tmpl_id.name )
        
        # message = '/n'.join(has_duplicated_product)
        print("####")
        print("####")
        print (has_duplicated_product)
        print("####")
        print("####")


    @api.model_create_multi
    def create(self, val_lists):
        """
            change product template and product product as bom parent
        """
        for vals in val_lists:
            if self.check_existing_bom(vals['product_tmpl_id']) == False:
                res = super(Mrp_bom, self).create(vals)
                is_subcontracted = res.check_ifsubcontracted_bom()
                self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])]).write({'is_bom_parent': True,'is_subcontracted':is_subcontracted})
                self.env['product.product'].search([('product_tmpl_id', '=', vals['product_tmpl_id'])]).write({'is_bom_parent': True,'is_subcontracted':is_subcontracted})

                    
                return res
            else:
                raise UserError("This BOM are already exist, try to create new product!")
    
    def unlink(self):
        """
            change product template and product product as bom parent
        """
        
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False,'is_subcontracted':False})
        self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False,'is_subcontracted':False})
        
        return super(Mrp_bom, self).unlink()

    def write(self, vals):
        """
            change product template and product product as bom parent
        """
        # TODO: search function to verify if user change product_templ_id
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})
        self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': False})

        res = super(Mrp_bom, self).write(vals)
        
        is_subcontracted = self.check_ifsubcontracted_bom()
        self.env['product.template'].search([('id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': True,'is_subcontracted':is_subcontracted})
        self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).write({'is_bom_parent': True,'is_subcontracted':is_subcontracted})

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
            
    def check_ifsubcontracted_bom(self):
        """
            check if the bom is subcontracted and return boolean
        """
        if self.type == 'subcontract':
            return True
        else:
            return False
            