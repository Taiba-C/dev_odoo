# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date, timedelta
from odoo.exceptions import ValidationError
from odoo.osv import expression

class Lead(models.Model):
    _inherit = "crm.lead"
    
    order_ids = fields.One2many('sale.order', 'opportunity_id', string='Orders')
    is_quotation_created = fields.Boolean('Is quotation created')
    # champs de l'onglet salon
    salon = fields.Char(string="Salon", tracking=True)
    lieu_du_salon = fields.Char(string="Lieu du salon", tracking=True)
    stand_n = fields.Char(string='Stand N°', tracking=True)
    hall = fields.Char(string="Hall", tracking=True)
    allee = fields.Char(string="Allée", tracking=True)
    surface_en_m = fields.Char(string="Surface (en m²)", tracking=True)
    dbut_salon = fields.Date(string='Début Salon',required=True, tracking=True)
    fin_salon = fields.Date(string='Fin Salon',required=True, tracking=True)
    remarques = fields.Text(string='Remarques', tracking=True)
    date_de_montage_du = fields.Date(string='Date de montage Du', tracking=True)
    date_de_montage_au = fields.Date(string='Au', tracking=True)
    remarques_montage = fields.Text(string='Remarques', tracking=True)
    date_de_demontage_du = fields.Date(string='Date de démontage Du', tracking=True)
    date_de_demontage_au = fields.Date(string='Au', tracking=True)
    warning_copy = fields.Boolean(copy=False)
    
    @api.depends("warning_copy")
    def check_if_display_warning(self):
        for rec in self:
            if rec.warning_copy:
                if rec.warning_display_time == 0:
                    rec.warning_display_time = 1
                    rec.warning_copy = False
                else:
                    rec.warning_display_time = 1
                    rec.warning_copy = False
            else:
                rec.warning_display_time = 1
    warning_display_time = fields.Integer(compute='check_if_display_warning')

    
    def action_sale_quotations_new(self):
        
        res = super(Lead, self).action_sale_quotations_new()

        if self.is_quotation_created == False:
            if len(self.partner_id) == 0:
                raise ValidationError(
                    "Veuillez renseigner le champ client")
            else:
                self.is_quotation_created = True

        return res
    # retroaction fin de salon debut de salon
    def retro_debut_fin_salon(self):
        crm_leads = self.env['crm.lead'].sudo().search([])
        for crm_lead in crm_leads:
            crm_lead.sudo().write({'dbut_salon':crm_lead.x_studio_dbut_salon,'fin_salon':crm_lead.x_studio_fin_salon,'salon':crm_lead.x_studio_salon,
                                   'lieu_du_salon':crm_lead.x_studio_lieu_du_salon,'stand_n':crm_lead.x_studio_stand_n,'hall':crm_lead.x_studio_hall,
                                   'allee':crm_lead.x_studio_alle,'surface_en_m':crm_lead.x_studio_surface_en_m,'remarques':crm_lead.x_studio_remarque,
                                   'date_de_montage_du':crm_lead.x_studio_date_de_montage_1,'date_de_montage_au':crm_lead.x_studio_au,
                                   'remarques_montage':crm_lead.x_studio_remarque_1,'date_de_demontage_du':crm_lead.x_studio_date_de_dmontage_2,
                                   'date_de_demontage_au':crm_lead.x_studio_au_1})
    
    def copy(self, default=None):
        """
        Duplicate the current record with optional default values.

        :param default: A dictionary of default values for the duplicated record.
        :type default: dict
        :return: The duplicated record.
        :rtype: odoo.models.Model
        :raises: ValidationError if the CRM contains multiple quotes.
        """
        self.ensure_one()
        default = dict(default or {},
                       name=_('%s (copy)', self.name),)
        res = super(Lead, self).copy(default)
        if self.order_ids and len(self.order_ids) == 1:
            # TODO: create new order
            order_id = self.order_ids[0].copy()
            order_id.rfrence_du_dossier = res.id
            order_id.opportunity_id = res.id
            order_id.origin = res.name
            
            # prepare orderline and sale order nesil options
            order_id.order_line.unlink()
            order_id.sale_order_nesil_option_ids.unlink()

            for line in self.order_ids[0].order_line:
                option_ids = self.order_ids[0].sale_order_nesil_option_ids.search([('order_line_id', '=', line.id)])
                subcontractor_ids = self.order_ids[0].sale_order_nesil_option_ids.search([('order_line_id', '=', line.id)])
                
                if line.display_type not in ['line_section', 'line_note'] and not option_ids:
                    if line.action_on_order_line not in ['subcontracted','option']:
                        new_order_line = order_id.order_line.create({
                            'product_id': line.product_id.id,
                            'product_template_id': line.product_template_id.id,
                            'name': line.name,
                            'product_uom_qty': line.product_uom_qty,
                            'qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,
                            'price_unit': line.price_unit,
                            'temp_price_unit': line.temp_price_unit,
                            'discount': line.discount,
                            'order_id': order_id.id,
                            'sequence': line.sequence,
                            'action_on_order_line': line.action_on_order_line,
                            'consumable': line.consumable,
                        })

                elif line.display_type in ['line_section', 'line_note']:
                    new_order_line = order_id.order_line.create({
                        'name': line.name,
                        'display_type': line.display_type,
                        'sequence': line.sequence,
                        'order_id': order_id.id,
                    })

                elif option_ids:
                    new_order_line = order_id.order_line.create({
                        'product_id': line.product_id.id,
                        'product_template_id': line.product_template_id.id,
                        'name': line.name,
                        'product_uom_qty': line.product_uom_qty,
                        'qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'price_unit': line.price_unit,
                        'temp_price_unit': line.temp_price_unit,
                        'discount': line.discount,
                        'order_id': order_id.id,
                        'sequence': line.sequence,
                        'action_on_order_line': line.action_on_order_line,
                        'consumable': line.consumable,
                    })
                    for option in option_ids:
                        op=option.copy()
                        op.order_line_id = new_order_line.id
                        op.order_id = new_order_line.order_id.id
                
            if len(self.order_ids[0].sale_order_subcontractor_ids) > 0:
                for line in self.order_ids[0].sale_order_subcontractor_ids:
                    if line.order_line_created:
                        new_subcontractor = line.copy()
                        new_subcontractor.order_id = order_id.id
                        new_subcontractor.action_create_order_line()
                    else:
                        new_subcontractor = line.copy()
                        new_subcontractor.order_id = order_id.id
                                                       
            
            if not res.active:
                res.toggle_active()
            if res.order_ids:
                if res.order_ids.state == "sale":
                    res.order_ids.action_cancel()
            if res.dbut_salon:
                if res.dbut_salon - date.today() < timedelta(0):
                    res.warning_copy = True
                    res.warning_display_time = 0
            return res
        else:
            raise ValidationError("Ce CRM contient plusieurs devis, veuillez supprimer les devis en trop avant de le dupliquer.")

    def duplicate_for_new_order(self, crm_lead_id):
        pass

    
    
    def action_set_lost(self, **additional_values):
        """ Lost semantic: probability = 0 or active = False """
        res = self.action_archive()
        if additional_values:
            self.write(dict(additional_values))
        if self.order_ids:
            self.order_ids.action_cancel()
        return res
    
    def toggle_active(self):
        """ When archiving: mark probability as 0. When re-activating
        update probability again, for leads and opportunities. """
        res = super(Lead, self).toggle_active()
        if self.order_ids:
            self.order_ids.action_draft()
        return res      
        
    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if len(self.order_ids) == 1 and self.stage_id.name == 'Nouveau':
            if self.order_ids[0]._origin.partner_id != self.partner_id:
                return {
                    'warning': {
                            'title': "Info",
                            'tag': 'display_notification',
                            'message': "En changeant le client, vous modifiez aussi celui du devis.", 
                            'type': 'notification',
                            },
                    }


    def write(self, vals):
        res = super(Lead, self).write(vals)
        if len(self.order_ids) == 1 and self.stage_id.name == 'Nouveau':
            # Change partner name in order id in relation in the lead when then change it in lead
            if self.order_ids[0]._origin.partner_id != self.partner_id:
                self.order_ids[0]._origin.write({
                    'partner_id': self.partner_id
                })
            
        return res
