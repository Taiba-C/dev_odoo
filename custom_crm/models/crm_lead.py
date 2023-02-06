# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Lead(models.Model):
    _inherit = "crm.lead"
    
    is_quotation_created = fields.Boolean('Is quotation created')
    
    def action_sale_quotations_new(self):
        
        res = super(Lead, self).action_sale_quotations_new()

        if self.is_quotation_created == False:
           self.is_quotation_created = True 

        return res
        