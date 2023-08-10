# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Lead(models.Model):
    _inherit = "crm.lead"
    
    is_quotation_created = fields.Boolean('Is quotation created')
    # champs de l'onglet salon
    salon = fields.Char(string="Salon")
    lieu_du_salon = fields.Char(string="Lieu dun salon")
    stand_n = fields.Char(string='Stand N°')
    hall = fields.Char(string="Hall")
    allee = fields.Char(string="Allée")
    surface_en_m = fields.Char(string="Surface (en m²)")
    dbut_salon = fields.Date(string='Début Salon')
    fin_salon = fields.Date(string='Fin Salon')

    
    def action_sale_quotations_new(self):
        
        res = super(Lead, self).action_sale_quotations_new()

        if self.is_quotation_created == False:
           self.is_quotation_created = True 

        return res
    # retroaction fin de salon debut de salon
    def retro_debut_fin_salon(self):
        crm_leads = self.env['crm.salon'].sudo().search([])
        for crm_lead in crm_leads:
            crm_lead.sudo().write({'dbut_salon':crm_lead.x_studio_dbut_salon,'fin_salon':crm_lead.x_studio_fin_salon,'salon':crm_lead.x_studio_salon,
                                   'lieu_du_salon':crm_lead.x_studio_lieu_du_salon,'stand_n':crm_lead.x_studio_stand_n,'hall':crm_lead.x_studio_hall,
                                   'allee':crm_lead.x_studio_alle,'surface_en_m':crm_lead.x_studio_surface_en_m})
        