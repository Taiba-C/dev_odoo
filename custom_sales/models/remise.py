# -*- coding: utf-8 -*-
from odoo import _, fields, models, api

class Remise(models.Model):
    _name = 'nesil.remise'
    _description = ' custom_sales.remise '
    
    name = fields.Char(string="Nom de remise") 
    taux_de_remise = fields.Float(string='Taux de remise')
    def default_department_name(self):
        return 'direction'
    department_name = fields.Char(default=default_department_name)
    active = fields.Boolean(string='Active',default=True)