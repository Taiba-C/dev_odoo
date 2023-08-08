# -*- coding: utf-8 -*-
from odoo import _, fields, models, api

class Remise(models.Model):
    _name = 'fn.remise'
    _rec_name='remise'
    
    remise = fields.Char(string="Nom de remise")
    taux_de_remise = fields.Float(string='Taux de remise')
    date_de_remise = 