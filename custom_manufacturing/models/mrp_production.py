# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Mrp_production(models.Model):
    _inherit = 'mrp.production'    
    
    
    production_duration_expected_hour = fields.Float('Durée attendue (En heures)', compute="_compute_production_duration_expected_hour")
    production_real_duration_hour = fields.Float('Durée réelle totale(En heures)', compute="_compute_production_real_duration_hour")

    besoin_etude = fields.Boolean(string="Besoin d'étude", default=True)
    bureau_etude_termine = fields.Boolean(string="Bureau d'étude terminé", default=False)
    
    capacite_decoupe = fields.Integer(string="Capacité Découpe", default=1)
    capacite_usinage = fields.Integer(string="Capacité Usinage", default=1)
    capacite_placage = fields.Integer(string="Capacité Placage", default=1)
    capacite_assemblage = fields.Integer(string="Capacité Assemblage", default=1)

    date_salon = fields.Date(string="Date du salon")
    date_limite = fields.Date(string="Date limite")
    etapes_realisees_ids = fields.Many2many('mrp.workorder', string="Étapes Réalisées")
    
    @api.depends('production_duration_expected')
    def _compute_production_duration_expected_hour(self):
        for record in self:
            record.production_duration_expected_hour = record.production_duration_expected / 60
            
    @api.depends('production_real_duration')
    def _compute_production_real_duration_hour(self):
        for record in self:
            record.production_real_duration_hour = record.production_real_duration / 60
            
    def _plan_workorders(self):
        """Plan or reschedule work orders respecting the defined sequence and adjust dates."""
        sequence_order = {
            'MO Etude de fabrication': 1,
            'MO DECOUPE': 2,
            'MO USINAGE': 3,
            'MO PLAQUAGE DE CHANTS': 3,
            'MO ASSEMBLAGE': 4
        }

    def _plan_workorders(self, replan=False):
        """Planifie ou reprogramme les ordres de travail en respectant un séquencement spécifique
        et ajuste les dates pour respecter les heures de travail.
        """
        sequence_order = {
            'MO Etude de fabrication': 1,
            'MO DECOUPE': 2,
            'MO USINAGE': 3,
            'MO PLAQUAGE DE CHANTS': 3,
            'MO ASSEMBLAGE': 4
        }

        for production in self:
            # Récupérer les ordres de travail selon le contexte de replanification
            if replan:
                workorders = production.workorder_ids.filtered(lambda w: w.state in ['ready', 'pending'])
            else:
                workorders = production.workorder_ids

            # Trier les ordres de travail selon la séquence
            sorted_workorders = workorders.sorted(
                key=lambda w: sequence_order.get(w.workcenter_id.name, 99)
            )

            # Vérifier si un calendrier est assigné à chaque centre de travail
            for workorder in sorted_workorders:
                if not workorder.workcenter_id.resource_calendar_id:
                    raise UserError(_(
                        "Le centre de travail %s n'a pas de calendrier défini." % workorder.workcenter_id.name
                    ))

            # Initialiser la date de début pour la planification
            next_start_date = production.date_planned_start or fields.Datetime.now()

            from itertools import groupby
            # Regrouper les ordres de travail par séquence
            groups = []
            for _, group in groupby(sorted_workorders, key=lambda w: sequence_order.get(w.workcenter_id.name, 99)):
                groups.append(list(group))

            # Planifier les groupes séquentiellement
            for group in groups:
                group_max_end = next_start_date
                for workorder in group:
                    calendar = workorder.workcenter_id.resource_calendar_id

                    # Ajuster la date de début au prochain créneau disponible
                    next_start_date = calendar.plan_hours(0, next_start_date)

                    # Calculer la durée de l'ordre de travail en heures
                    work_duration = workorder.duration_expected / 60  # Convertir en heures

                    # Calculer la date de fin planifiée en respectant le calendrier
                    date_planned_finished = calendar.plan_hours(work_duration, next_start_date)

                    # Mettre à jour les dates planifiées de l'ordre de travail
                    workorder.date_planned_start = next_start_date
                    workorder.date_planned_finished = date_planned_finished

                    # Mettre à jour le prochain créneau disponible
                    if date_planned_finished > group_max_end:
                        group_max_end = date_planned_finished

                # Définir la prochaine date de début pour le groupe suivant
                next_start_date = group_max_end

