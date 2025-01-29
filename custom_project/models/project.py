# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    _inherit = 'project.project'
    
    order_id = fields.Many2one('sale.order', string="Sale Order", compute="_compute_order_id", inverse="_inverse_order_id")
    bon_de_commande = fields.Many2one('sale.order', string="Sale Order", store=True)
    work_order_qty = fields.Float('Work ORder Qty', compute="_compute_work_order_qty", store=True)
    work_order_percentage_done = fields.Float('Work ORder Percent done', compute="_compute_work_order_percentage_done")
    work_order_percentage_not_done = fields.Float('Work ORder Percent not done', compute="_compute_work_order_percentage_not_done")
    work_order_percentage_in_progress = fields.Float('Work ORder Percent in progress', compute="_compute_work_order_percentage_in_progress")

    assembly_date_start = fields.Date('assembly_date_start', compute="_compute_date_assembly_desassembly", inverse="_inverse_assembly_date_start")
    assembly_date_end = fields.Date('assembly_date_end', compute="_compute_date_assembly_desassembly", inverse="_inverse_assembly_date_start")

    disassembly_date_start = fields.Date('Disassembly Date start', compute="_compute_date_assembly_desassembly", inverse="_inverse_assembly_date_start")
    disassembly_date_end = fields.Date('Disassembly Date end', compute="_compute_date_assembly_desassembly", inverse="_inverse_assembly_date_start")

    # salon
    show_name = fields.Char('Show Name', compute="_compute_show_informations", inverse='_inverse_show_name')
    # date de salon
    show_dates = fields.Char('Show Dates', compute="_compute_show_informations", inverse="_inverse_show_dates")
    # localisation
    show_localisation = fields.Char('Localisation', compute="_compute_show_informations", inverse="_inverse_show_localisation")
    # hall
    show_hall_name = fields.Char('Hall Name', compute="_compute_show_informations", inverse="_inverse_show_hall_name")
    # stand
    show_stand_name = fields.Char('Stand Name', compute="_compute_show_informations", inverse="_inverse_show_stand_name")    
    # surface
    show_surface = fields.Char('Surface', compute="_compute_show_informations", inverse="_inverse_show_surface")
    # commerciaux
    show_commercials = fields.Char('Commercials', compute="_compute_show_informations", inverse="_inverse_show_commercials")

    opportunity_id = fields.Many2one('crm.lead', string="Opportunity", compute="_compute_opportunity", store=True)
    origin = fields.Char(string="Origine", compute="_compute_origin", store=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    work_order_details = fields.Html(string="Work Order Details", compute="_compute_work_order_details")
    workorder_type_progression = fields.Text(string="Workorder Type Progression", compute="_compute_workorder_type_progression")
    type_of_event = fields.Selection([('main', 'Main Event'),('assembly', 'Assembly'),('disassembly', 'Disassembly')], string="Type of Event", default='main')
    calendar_events = fields.One2many('project.calendar.event', compute="_compute_calendar_events")
    calendar_event_ids = fields.One2many(
        'project.calendar.event', 'project_id',
        string="Calendar Events"
    )

    @api.depends('order_id')
    def _compute_origin(self):
        for record in self:
            mrp_production = self.env['mrp.production'].search([('sale_order', '=', record.order_id.id)], limit=1)
            record.origin = mrp_production.origin if mrp_production else ''

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


    @api.depends('order_id')
    def _compute_show_informations(self):
        """
        Compute and update the show information fields based on the order's opportunity information.
        """
        for record in self:
            start = record.order_id.opportunity_id.dbut_salon
            end = record.order_id.opportunity_id.fin_salon

            record.show_name = record.order_id.opportunity_id.name
            record.show_commercials = record.order_id.opportunity_id.user_id.name
            record.show_surface = record.order_id.opportunity_id.surface_en_m
            record.show_stand_name = record.order_id.opportunity_id.stand_n
            record.show_hall_name = record.order_id.opportunity_id.hall
            record.show_localisation = record.order_id.opportunity_id.lieu_du_salon
            record.assembly_date_start = record.order_id.opportunity_id.date_de_montage_du
            record.assembly_date_end = record.order_id.opportunity_id.date_de_montage_au
            record.disassembly_date_start = record.order_id.opportunity_id.date_de_demontage_du
            record.disassembly_date_end = record.order_id.opportunity_id.date_de_demontage_au
            if start and end:
                record.show_dates = f"{start.strftime('%d')} au {end.strftime('%d %B %Y')}"
            else:
                record.show_dates = f"{start} {end}"

    def create(self, vals):
        """
        Surcharge de la méthode create pour générer les événements après la création d'un projet.
        """
        project = super(ProjectProject, self).create(vals)
        project.create_events_for_calendar()
        return project

    def write(self, vals):
        """
        Surcharge de la méthode write pour mettre à jour les événements après modification d'un projet.
        """
        res = super(ProjectProject, self).write(vals)
        self.create_events_for_calendar()
        return res


    def _compute_order_id(self):
        for record in self:
            order_id = self.env['sale.order'].search([('project_options_id', '=', record.id)], limit=1)
            record.order_id = order_id.id
    
    
    @api.depends('order_id')
    def _compute_work_order_qty(self):
        """
        Compute the work order quantity based on the order state.

        If the order is in 'draft', 'sent', or 'sale' state, it counts the number of work orders
        associated with the order and assigns the count to the 'work_order_qty' field.
        Otherwise, it sets the 'work_order_qty' field to 0.0.

        :return: None
        """
        for record in self:
            if record.order_id and record.order_id.state in ['draft', 'sent', 'sale']:
                record.work_order_qty = self.env['mrp.production'].search_count([('sale_order', '=', record.order_id.id)])
            else:
                record.work_order_qty = 0.0

    #@api.depends('order_id')
    #def _compute_work_order_percentage_done(self):
    #    """
    #    Compute the percentage of work orders done for the project.
#
    #    This method calculates the percentage of work orders that are marked as 'done'
    #    out of the total number of work orders associated with the project's sale order.
#
    #    :return: None
    #    """
    #    for record in self:
    #        if record.order_id:
    #            if record.order_id and record.order_id.state in ['draft', 'sent', 'sale']:
    #                manufacturing_orders = self.env['mrp.production'].search([('sale_order', '=', record.order_id.id)])
#
    #                total_completed_count = 0
    #                total_total_count = 0
    #                for order in manufacturing_orders:
    #                    work_order_states = [work_order.state for work_order in order.workorder_ids]
    #                    completed_count = work_order_states.count('done')
    #                    total_count = len(work_order_states)
    #                    total_completed_count += completed_count
    #                    total_total_count += total_count
    #                if total_total_count > 0:
    #                    record.work_order_percentage_done = (total_completed_count / total_total_count)
    #                else:
    #                    record.work_order_percentage_done = 0.0
    #        else:
    #            record.work_order_percentage_done = 0.0
#
    #    
    #@api.depends('order_id')
    #def _compute_work_order_percentage_not_done(self):
    #    """
    #    Compute the percentage of work orders that are not done for each record.
#
    #    This method calculates the percentage of work orders that are in the 'waiting' or 'pending' state
    #    out of the total number of work orders associated with the record's sale order.
#
    #    :return: None
    #    """
    #    for record in self:
    #        if record.order_id:
    #            if record.order_id and record.order_id.state in ['draft', 'sent', 'sale']:
    #                manufacturing_orders = self.env['mrp.production'].search([('sale_order', '=', record.order_id.id)])
    #                total_draft_pending_count = 0
    #                total_total_count = 0
    #                for order in manufacturing_orders:
    #                    work_order_states = [work_order.state for work_order in order.workorder_ids]
    #                    draft_pending_count = work_order_states.count('waiting') + work_order_states.count('pending')
    #                    total_count = len(work_order_states)
    #                    total_draft_pending_count += draft_pending_count
    #                    total_total_count += total_count
    #                if total_total_count > 0:
    #                    record.work_order_percentage_not_done = (total_draft_pending_count / total_total_count)
    #                else:
    #                    record.work_order_percentage_not_done = 0.0
    #        else:
    #            record.work_order_percentage_not_done = 0.0
#
#
    #@api.depends('order_id')
    #def _compute_work_order_percentage_in_progress(self):
    #    """
    #    Compute the percentage of work orders in progress for the current project.
#
    #    This method calculates the percentage of work orders in progress for the current project
    #    based on the associated sale order. It iterates through all the manufacturing orders
    #    linked to the sale order and counts the number of work orders in progress. The percentage
    #    is then calculated by dividing the number of completed work orders by the total number
    #    of work orders.
#
    #    Returns:
    #        None
    #    """
    #    for record in self:
    #        if record.order_id:
    #            if record.order_id and record.order_id.state in ['draft','sent','sale']:
    #                manufacturing_orders = self.env['mrp.production'].search([('sale_order', '=', record.order_id.id)])
#
    #                total_completed_count = 0
    #                total_total_count = 0
    #                for order in manufacturing_orders:
    #                    work_order_states = [work_order.state for work_order in order.workorder_ids]
    #                    completed_count = work_order_states.count('progress')
    #                    total_count = len(work_order_states)
    #                    total_completed_count += completed_count
    #                    total_total_count += total_count
    #                if total_total_count > 0:
    #                    record.work_order_percentage_in_progress = (total_completed_count / total_total_count)
    #                else:
    #                    record.work_order_percentage_in_progress = 0.0
    #        else:
    #            record.work_order_percentage_in_progress = 0.0


    @api.depends('order_id')
    def _compute_work_order_details(self):
        """
        Génère un résumé des ordres de travail par état.
        """
        for record in self:
            details = {"done": [], "in_progress": [], "not_done": []}
            if record.order_id:
                manufacturing_orders = self.env['mrp.production'].search([('sale_order', '=', record.order_id.id)])
                for order in manufacturing_orders:
                    for work_order in order.workorder_ids:
                        state = work_order.state
                        # Classes CSS pour les noms spécifiques des ordres de travail
                        badge_classes = {
                            "Usinage": "badge-usinage",
                            "Assemblage": "badge-assemblage",
                            "Découpe": "badge-decoupe",
                            "Plaquages de chants": "badge-plaquage",
                            "Etude de fabrication": "badge-etude",
                        }
                        
                        # Identifier le type d'ordre de travail basé sur son nom
                        work_order_name = work_order.name
                        badge_class = "badge-default"  # Classe par défaut
                        for keyword, css_class in badge_classes.items():
                            if keyword.lower() in work_order_name.lower():
                                badge_class = css_class
                                break
                        
                        # Générer le badge HTML
                        badge_html = f"<span class='badge {badge_class}'>{work_order.name}</span>"

                        if state == 'done':
                            details["done"].append(f"<span class='badge badge-done'>{work_order.name}</span>")
                        elif state == 'progress':
                            details["in_progress"].append(f"<span class='badge badge-in-progress'>{work_order.name}</span>")
                        else:
                            details["not_done"].append(f"<span class='badge badge-not-done'>{work_order.name}</span>")
        
            # Formattez les données en une chaîne HTML lisible
            record.work_order_details = (
                #f"<ul>"
                #f"<li><strong>En cours:</strong> {' '.join(details['in_progress'])}</li>"
                #f"<li><strong>Terminés:</strong> {' '.join(details['done'])}</li>"
                #f"<li><strong>Non commencés:</strong> {' '.join(details['not_done'])}</li>"
                #f"</ul>"
            )

    @api.depends('order_id')
    def _compute_workorder_type_progression(self):
        """
        Compute the efficiency percentage of workorder tasks by type.
    
        This method calculates the efficiency percentage of each workorder type:
        - Découpe (Cutting)
        - Assemblage (Assembly)
        - Usinage (Machining)
        - Plaquage de chants (Edge Banding)
    
        For each type, it computes:
        - Total efficiency percentage (weighted average by task duration).
        """
        for record in self:
            if not record.order_id or record.order_id.state not in ['draft', 'sent', 'sale']:
                record.workorder_type_progression = "No active work orders"
                continue
    
            # Define the workorder types we want to track
            workorder_types = {
                'Découpe': ['Découpe', 'DECOUPE', 'MO DECOUPE'],
                'Assemblage': ['Assemblage', 'ASSEMBLAGE', 'MO ASSEMBLAGE'],
                'Usinage': ['Usinage', 'USINAGE', 'MO USINAGE'],
                'Plaquage de chants': ['Plaquage de chants', 'PLAQUAGE DE CHANTS', 'MO PLAQUAGE DE CHANTS']
            }
    
            # Prepare a dictionary to store efficiency details
            efficiency_details = {}
    
            # Search for manufacturing orders related to this sale order
            manufacturing_orders = self.env['mrp.production'].search([
                ('sale_order', '=', record.order_id.id)
            ])
    
            # Iterate through each manufacturing order
            for order in manufacturing_orders:
                for work_order in order.workorder_ids:
                    for wtype, keywords in workorder_types.items():
                        if any(keyword.lower() in work_order.name.lower() for keyword in keywords):
                            if wtype not in efficiency_details:
                                efficiency_details[wtype] = {
                                    'total_efficiency': 0.0,
                                    'total_duration': 0.0
                                }
                            # Calculate weighted efficiency
                            if work_order.duration and work_order.efficiency_percentage:
                                efficiency_details[wtype]['total_efficiency'] += (
                                    work_order.efficiency_percentage * work_order.duration
                                )
                                efficiency_details[wtype]['total_duration'] += work_order.duration
    
            # Format the efficiency details into a readable text
            if efficiency_details:
                efficiency_text = "<ul>"
                for wtype, details in efficiency_details.items():
                    total_efficiency = details['total_efficiency']
                    total_duration = details['total_duration']
                    efficiency_percentage = (
                        total_efficiency / total_duration if total_duration > 0 else 0
                    )
                    
                    efficiency_text += (
                        f"<li><strong>{wtype}</strong>: "
                        f"{efficiency_percentage:.1f}%</li>"
                    )
                efficiency_text += "</ul>"
                record.workorder_type_progression = efficiency_text
            else:
                record.workorder_type_progression = "Aucune tâche de travail trouvée"


    @api.depends('order_id')
    def _compute_date_assembly_desassembly(self):
        for record in self:
            if record.order_id:
                record.assembly_date_start = record.order_id.opportunity_id.date_de_montage_du
                record.assembly_date_end = record.order_id.opportunity_id.date_de_montage_au
                record.disassembly_date_start = record.order_id.opportunity_id.date_de_demontage_du
                record.disassembly_date_end = record.order_id.opportunity_id.date_de_demontage_au





#    @api.model
#    def create_events_for_calendar(self):
#        """
#        Crée des enregistrements d'événements pour le montage et le démontage en fonction du projet principal.
#        """
#        for project in self:
#            # Ajouter l'événement principal
#            self.env['project.project'].create({
#                'name': f"{project.name} - Main Event",
#                'date_start': project.date_start,
#                'date_stop': project.date,
#                'type_of_event': 'main',
#            })
#
#            # Ajouter l'événement de montage
#            if project.assembly_date_start and project.assembly_date_end:
#                self.env['project.project'].create({
#                    'name': f"{project.name} - Assembly",
#                    'date_start': project.assembly_date_start,
#                    'date_stop': project.assembly_date_end,
#                    'type_of_event': 'assembly',
#                })
#
#            # Ajouter l'événement de démontage
#            if project.disassembly_date_start and project.disassembly_date_end:
#                self.env['project.project'].create({
#                    'name': f"{project.name} - Disassembly",
#                    'date_start': project.disassembly_date_start,
#                    'date_stop': project.disassembly_date_end,
#                    'type_of_event': 'disassembly',
#                })
#
#    @api.model
#    def create(self, vals):
#        project = super(ProjectProject, self).create(vals)
#        project._create_or_update_calendar_events()
#        return project
#
#    def write(self, vals):
#        result = super(ProjectProject, self).write(vals)
#        self._create_or_update_calendar_events()
#        return result
#
#    def unlink(self):
#        for project in self:
#            project.calendar_event_ids.unlink()
#        return super(ProjectProject, self).unlink()
#
#    def _create_or_update_calendar_events(self):
#        event_model = self.env['project.calendar.event']
#        for project in self:
#            # Create or update main event
#            main_event = event_model.search([('project_id', '=', project.id), ('type_of_event', '=', 'main')], limit=1)
#            if project.date_start and project.date:
#                if main_event:
#                    main_event.write({
#                        'date_start': project.date_start,
#                        'date_stop': project.date,
#                    })
#                else:
#                    event_model.create({
#                        'name': f"{project.name} - Main Event",
#                        'date_start': project.date_start,
#                        'date_stop': project.date,
#                        'type_of_event': 'main',
#                        'project_id': project.id,
#                    })
#
#            # Create or update assembly event
#            assembly_event = event_model.search([('project_id', '=', project.id), ('type_of_event', '=', 'assembly')], limit=1)
#            if project.assembly_date_start and project.assembly_date_end:
#                if assembly_event:
#                    assembly_event.write({
#                        'date_start': project.assembly_date_start,
#                        'date_stop': project.assembly_date_end,
#                    })
#                else:
#                    event_model.create({
#                        'name': f"{project.name} - Assembly",
#                        'date_start': project.assembly_date_start,
#                        'date_stop': project.assembly_date_end,
#                        'type_of_event': 'assembly',
#                        'project_id': project.id,
#                    })
#
#            # Create or update disassembly event
#            disassembly_event = event_model.search([('project_id', '=', project.id), ('type_of_event', '=', 'disassembly')], limit=1)
#            if project.disassembly_date_start and project.disassembly_date_end:
#                if disassembly_event:
#                    disassembly_event.write({
#                        'date_start': project.disassembly_date_start,
#                        'date_stop': project.disassembly_date_end,
#                    })
#                else:
#                    event_model.create({
#                        'name': f"{project.name} - Disassembly",
#                        'date_start': project.disassembly_date_start,
#                        'date_stop': project.disassembly_date_end,
#                        'type_of_event': 'disassembly',
#                        'project_id': project.id,
#                    })

    def create(self, vals):
        project = super(ProjectProject, self).create(vals)
        project._create_or_update_calendar_events()
        return project

    def write(self, vals):
        result = super(ProjectProject, self).write(vals)
        self._create_or_update_calendar_events()
        return result

    def unlink(self):
        for project in self:
            self.env['project.calendar.event'].search([('project_id', '=', project.id)]).unlink()
        return super(ProjectProject, self).unlink()

    def _create_or_update_calendar_events(self):
        event_model = self.env['project.calendar.event']
        for project in self:
            _logger.info(f"Processing project: {project.name}")
            existing_events = event_model.search([('project_id', '=', project.id)])
            
            # Création d'un dictionnaire pour les événements existants par type
            event_map = {event.type_of_event: event for event in existing_events}

            # Liste des événements à créer ou mettre à jour
            event_data = [
                {
                    'name': f"{project.name} ",
                    'date_start': project.date_start,
                    'date_stop': project.date,
                    'type_of_event': 'main',
                },
                {
                    'name': f"{project.name} - Montage",
                    'date_start': project.assembly_date_start,
                    'date_stop': project.assembly_date_end,
                    'type_of_event': 'assembly',
                },
                {
                    'name': f"{project.name} - Démontage",
                    'date_start': project.disassembly_date_start,
                    'date_stop': project.disassembly_date_end,
                    'type_of_event': 'disassembly',
                }
            ]

            for data in event_data:
                if data['date_start'] and data['date_stop']:
                    event = event_map.get(data['type_of_event'])
                    if event:
                        # Mise à jour si les données ont changé
                        if (event.date_start != data['date_start'] or 
                            event.date_stop != data['date_stop'] or
                            event.name != data['name']):
                            event.write({
                                'date_start': data['date_start'],
                                'date_stop': data['date_stop'],
                                'name': data['name']
                            })
                    else:
                        # Création d'un nouvel événement si non existant
                        data.update({'project_id': project.id})
                        event_model.create(data)

            # Supprimer les événements obsolètes
            for event in existing_events:
                _logger.info(f"Existing event found: {event.name} - {event.date_start} to {event.date_stop}")
                if event.type_of_event not in [e['type_of_event'] for e in event_data]:
                    event.unlink()


    @api.depends('date_start', 'date', 'assembly_date_start', 'assembly_date_end', 'disassembly_date_start', 'disassembly_date_end')
    def _compute_calendar_events(self):
        self._create_or_update_calendar_events()


    def _inverse_assembly_date_start(self):
        pass

    def _inverse_show_name(self):
        pass

    def _inverse_show_dates(self):
        pass

    def _inverse_show_localisation(self):
        pass

    def _inverse_show_hall_name(self):
        pass

    def _inverse_show_stand_name(self):
        pass

    def _inverse_show_surface(self):
        pass

    def _inverse_show_commercials(self):
        pass

    def _inverse_order_id(self):
        pass


class ProjectCalendarEvent(models.Model):
    _name = 'project.calendar.event'
    _description = 'Project Calendar Event'

    name = fields.Char(string="Event Name", required=True)
    date_start = fields.Datetime(string="Start Date", required=True)
    date_stop = fields.Datetime(string="End Date", required=True)
    type_of_event = fields.Selection([
        ('main', 'Main Event'),
        ('assembly', 'Montage'),
        ('disassembly', 'Démontage')
    ], string="Event Type", required=True)
    project_id = fields.Many2one(
        'project.project', string="Project",
        ondelete='cascade', required=True
    )
    origin = fields.Char(string="Origine", related='project_id.origin', store=True)

    show_name = fields.Char(string="Show Name", related='project_id.show_name', store=True)
    show_dates = fields.Char(string="Show Dates", related='project_id.show_dates', store=True)
    show_localisation = fields.Char(string="Localisation", related='project_id.show_localisation', store=True)
    show_hall_name = fields.Char(string="Hall Name", related='project_id.show_hall_name', store=True)
    show_stand_name = fields.Char(string="Stand Name", related='project_id.show_stand_name', store=True)
    show_surface = fields.Char(string="Surface", related='project_id.show_surface', store=True)
    show_commercials = fields.Char(string="Commercials", related='project_id.show_commercials', store=True)
    opportunity_id = fields.Many2one('crm.lead', string="Opportunity", store=True)
