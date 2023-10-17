# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Mrp_production(models.Model):
    _inherit = 'mrp.production'    
    
    
    production_duration_expected_hour = fields.Float('Durée attendue (En heures)', compute="_compute_production_duration_expected_hour")
    production_real_duration_hour = fields.Float('Durée réelle totale(En heures)', compute="_compute_production_real_duration_hour")
    
    @api.depends('production_duration_expected')
    def _compute_production_duration_expected_hour(self):
        for record in self:
            record.production_duration_expected_hour = record.production_duration_expected / 60
            
    @api.depends('production_real_duration')
    def _compute_production_real_duration_hour(self):
        for record in self:
            record.production_real_duration_hour = record.production_real_duration / 60