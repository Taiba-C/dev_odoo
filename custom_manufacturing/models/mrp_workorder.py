# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import timedelta


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
            'context': {'group_by': 'employee_id'},
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


    

    def _check_employee_schedule(self):
        """
        Vérifie les conflits d'horaires pour l'employé et envoie une notification si nécessaire.
        """
        for workorder in self:
            if workorder.employee_id:
                # Rechercher les ordres de travail en conflit avec l'horaire
                overlapping_workorders = self.env['mrp.workorder'].search([
                    ('id', '!=', workorder.id),
                    ('employee_id', '=', workorder.employee_id.id),
                    ('state', '!=', 'done'),
                    ('date_planned_start', '<', workorder.date_planned_finished),
                    ('date_planned_finished', '>', workorder.date_planned_start),
                ])
                if overlapping_workorders:
                    conflict_names = ", ".join(overlapping_workorders.mapped('name'))
                    message = _(
                        "Conflit détecté : L'employé %s est déjà affecté aux tâches suivantes durant cette période : %s."
                    ) % (workorder.employee_id.name, conflict_names)
                    
                    # Ajouter un message dans le journal de l'ordre de fabrication
                    if workorder.production_id:
                        workorder.production_id.message_post(body=message)


    @api.depends('duration', 'duration_expected')
    def _compute_efficiency_percentage(self):
        for workorder in self:
            workorder.efficiency_percentage = (
                (workorder.duration_expected / workorder.duration) * 100 if workorder.duration else 0
            )