# -*- coding: utf-8 -*-
from odoo import _, fields, models, api

class Remise(models.Model):
    _name = 'fn.remise'
    _rec_name='remise'
    
    remise = fields.float('res.currency', string="remise")
    taux_de_remise = fields.Float(string='Taux de remise')