# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date, timedelta

class Lead(models.Model):
    _inherit = "crm.lead"
    
    order_ids = fields.One2many('sale.order', 'opportunity_id',copy=True, string='Orders')
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
    remarques = fields.Text(string='Remarques')
    date_de_montage_du = fields.Date(string='Date de montage Du')
    date_de_montage_au = fields.Date(string='Au')
    remarques_montage = fields.Text(string='Remarques')
    date_de_demontage_du = fields.Date(string='Date de démontage Du')
    date_de_demontage_au = fields.Date(string='Au')
    warning_copy = fields.Boolean(copy=False)
    warning_display_time = fields.Integer(compute='check_if_display_warning')
    #@api.depends("warning_copy")
    def check_if_display_warning(self):
        for rec in self:
            if rec.warning_display_time == 1:
                rec.warning_copy = False
                rec.warning_display_time = 0
            else:
                rec.warning_display_time = 1

    
    def action_sale_quotations_new(self):
        
        res = super(Lead, self).action_sale_quotations_new()

        if self.is_quotation_created == False:
           self.is_quotation_created = True 

        return res
    # retroaction fin de salon debut de salon
    def retro_debut_fin_salon(self):
        crm_leads = self.env['crm.lead'].sudo().search([])
        for crm_lead in crm_leads:
            crm_lead.sudo().write({'dbut_salon':crm_lead.x_studio_dbut_salon,'fin_salon':crm_lead.x_studio_fin_salon,'salon':crm_lead.x_studio_salon,
                                   'lieu_du_salon':crm_lead.x_studio_lieu_du_salon,'stand_n':crm_lead.x_studio_stand_n,'hall':crm_lead.x_studio_hall,
                                   'allee':crm_lead.x_studio_alle,'surface_en_m':crm_lead.x_studio_surface_en_m,'remarques':crm_lead.x_studio_remarques,
                                   'date_de_montage_du':crm_lead.x_studio_date_de_montage_1,'date_de_montage_au':crm_lead.x_studio_au,
                                   'remarques_montage':crm_lead.x_studio_remarque_1,'date_de_demontage_du':crm_lead.x_studio_date_de_dmontage_2,
                                   'date_de_demontage_au':crm_lead.x_studio_au_1})
    
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       name=_('%s (copy)', self.name),)
        res = super(Lead, self).copy(default)
        if not res.active:
            res.toggle_active()
        if res.order_ids:
            if res.order_ids.state == "sale":
                res.order_ids.action_cancel()
        #if res.dbut_salon - date.today() > timedelta(0):
        res.warning_copy = True
        res.warning_display_time = 0
        return res
        