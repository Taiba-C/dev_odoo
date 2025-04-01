# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import timedelta
import logging
import json

_logger = logging.getLogger(__name__)


class Mrp_workorder(models.Model):
    _inherit = 'mrp.workorder'    
    
    
    duration_expected_hour = fields.Float('Durée attendue(En heures)', compute="_compute_duration_expected_hour")
    duration_hour = fields.Float('Durée réelle(En heures)', compute="_compute_duration_hour")    

    time_remaining = fields.Float(
        string="Temps restant (heures)",
        compute="_compute_time_remaining",
        store=True
    )
    is_overdue = fields.Boolean(
        string="En retard",
        compute="_compute_time_remaining",
        store=True
    )
    efficiency_percentage = fields.Float(
        string="Efficiency Percentage",
        compute="_compute_efficiency_percentage",  # Si calculé
        store=True,
    )

    opportunity_id = fields.Many2one('crm.lead', string="Opportunity", store=True)
    sequence = fields.Integer(
        string="Sequence",
        help="Détermine l'ordre de planification des ordres de travail.",
        default=0
    )

    show_json_popover = fields.Boolean(
        string="Show JSON Popover",
        compute="_compute_json_popover",
        store=True
    )
    json_popover = fields.Char(
        string="JSON Popover",
        compute="_compute_json_popover",
        store=True
    )



#    date_of_exhibition = fields.Date(
#        string="Date of Exhibition",
#        compute="_compute_date_of_exhibition",
#        store=True
#    )
#
#    @api.depends('opportunity_id')
#    def _compute_date_of_exhibition(self):
#        """
#        Compute the date_of_exhibition from related sale order.
#        """
#        SaleOrder = self.env.get('sale.order')
#        if not SaleOrder:
#            raise UserError(_("Le modèle 'sale.order' est introuvable. Assurez-vous que le module de vente est bien installé."))
#
#        for record in self:
#            if record.opportunity_id:
#                sale_order = SaleOrder.search([('opportunity_id', '=', record.opportunity_id.id)], limit=1)
#                if sale_order:
#                    record.date_of_exhibition = sale_order.date_of_exhibition
#                else:
#                    record.date_of_exhibition = False
#            else:
#                record.date_of_exhibition = False

    
    @api.depends('order_id')
    def _compute_opportunity(self):
        """
        Compute the opportunity linked to the sale order.
        """
        for record in self:
            if record.order_id:
                record.opportunity_id = record.order_id.opportunity_id
            else:
                record.opportunity_id = False


    @api.depends('duration_expected')
    def _compute_duration_expected_hour(self):
        for record in self:
            record.duration_expected_hour = record.duration_expected / 60
            
    @api.depends('duration')
    def _compute_duration_hour(self):
        for record in self:
            record.duration_hour = record.duration / 60
            
    def action_view_workload(self):
        """
        Ouvre une vue graphique ou pivot pour afficher la charge de travail de l'employé assigné.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Workload',
            'view_mode': 'gantt',
            'res_model': 'mrp.workorder',
            'domain': [('employee_id', '=', self.employee_id.id), ('state', '!=', 'done')],
            'context': {
                'group_by': 'employee_id',
                'default_scale': 'week',
                'gantt_display': 'fit',  # Ajuste la taille automatiquement
            },
            'target': 'new',
        }

    @api.depends('duration', 'duration_expected', 'duration_hour', 'duration_expected_hour')
    def _compute_time_remaining(self):
        """
        Calcule le temps restant pour chaque ordre de travail en utilisant les champs duration et duration_expected.
        """
        for work_order in self:
            # Utiliser les valeurs des champs basés sur la priorité
            duration_in_hours = work_order.duration_hour if work_order.duration_hour else work_order.duration / 60
            duration_expected_in_hours = work_order.duration_expected_hour if work_order.duration_expected_hour else work_order.duration_expected / 60
    
            # Calculer le temps restant
            remaining_time = duration_expected_in_hours - duration_in_hours
            work_order.time_remaining = max(remaining_time, 0)  # Si négatif, définir à 0
            work_order.is_overdue = remaining_time <= 0


    




    @api.depends('duration', 'duration_expected')
    def _compute_efficiency_percentage(self):
        for workorder in self:
            workorder.efficiency_percentage = (
                (workorder.duration / workorder.duration_expected) * 100 if workorder.duration_expected else 0
            )

    def action_replan(self):
        """Replanifie les ordres de travail en respectant la séquence définie."""
        # Récupérer la production associée
        production = self.production_id
        
        # Appeler la méthode de replanification de la production
        production._plan_workorders(replan=True)
        
        # Forcer la fermeture du popover
        self.write({
            'show_json_popover': False,
            'json_popover': False
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.depends('date_planned_start', 'date_planned_finished', 'user_id')
    def _compute_json_popover(self):
        """Calcule les informations à afficher dans le popover."""
        for workorder in self:
            infos = []
            
            # Vérifier les conflits d'emploi du temps
            if workorder.date_planned_start and workorder.date_planned_finished and workorder.user_id:
                # Ne vérifier les conflits que pour les enregistrements existants
                if not isinstance(workorder.id, models.NewId):
                    overlapping_workorders = self.env['mrp.workorder'].search([
                        ('id', '!=', workorder.id),
                        ('user_id', '=', workorder.user_id.id),
                        ('date_planned_start', '<', workorder.date_planned_finished),
                        ('date_planned_finished', '>', workorder.date_planned_start),
                    ])

                    if overlapping_workorders:
                        infos.append({
                            'color': 'text-danger',
                            'msg': _("Conflit d'emploi du temps pour l'utilisateur %s avec l'ordre de travail %s") % (
                                workorder.user_id.name,
                                overlapping_workorders[0].name
                            )
                        })

            # Vérifier si l'ordre est en retard
            if workorder.date_planned_finished and workorder.date_planned_finished < fields.Datetime.now():
                infos.append({
                    'color': 'text-warning',
                    'msg': _("L'ordre de travail est en retard")
                })

            # Mettre à jour le popover
            color_icon = infos and infos[-1]['color'] or False
            workorder.show_json_popover = bool(color_icon)
            workorder.json_popover = json.dumps({
                'popoverTemplate': 'mrp.workorderPopover',
                'infos': infos,
                'color': color_icon,
                'icon': 'fa-exclamation-triangle' if color_icon in ['text-warning', 'text-danger'] else 'fa-info-circle',
                'replan': color_icon not in [False, 'text-primary']
            })