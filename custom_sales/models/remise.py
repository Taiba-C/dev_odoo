# -*- coding: utf-8 -*-
from odoo import _, fields, models, api

class Remise(models.Model):
    _name = 'custom_sales.remise'
    
    name = fields.Char(string="Nom de remise") 
    taux_de_remise = fields.Float(string='Taux de remise')
    active = fields.Boolean(string='Active',default=True)