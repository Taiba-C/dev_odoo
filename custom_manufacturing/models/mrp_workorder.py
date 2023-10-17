# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Mrp_workorder(models.Model):
    _inherit = 'mrp.workorder'    
    
    duration_expected_hour = fields.Float('Durée attendue(En heures)', compute="_compute_duration_expected_hour")
    duration_hour = fields.Float('Durée réelle(En heures)', compute="_compute_duration_hour")
    
    @api.depends('duration_expected')
    def _compute_duration_expected_hour(self):
        for record in self:
            record.duration_expected_hour = record.duration_expected / 60
            
    @api.depends('duration')
    def _compute_duration_hour(self):
        for record in self:
            record.duration_hour = record.duration / 60