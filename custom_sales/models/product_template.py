# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Product_template(models.Model):
    _inherit = "product.template"
    
    # function to open the form view for a specific record
    def open_form_view_product(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
            }