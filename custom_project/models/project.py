# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

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
            if start and end:
                record.show_dates = f"{start.strftime('%d')} au {end.strftime('%d %B %Y')}"
            else:
                record.show_dates = f"{start} {end}"

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

    @api.depends('order_id')
    def _compute_work_order_percentage_done(self):
        """
        Compute the percentage of work orders done for the project.

        This method calculates the percentage of work orders that are marked as 'done'
        out of the total number of work orders associated with the project's sale order.

        :return: None
        """
        for record in self:
            if record.order_id:
                if record.order_id and record.order_id.state in ['draft', 'sent', 'sale']:
                    manufacturing_orders = self.env['mrp.production'].search([('sale_order', '=', record.order_id.id)])

                    total_completed_count = 0
                    total_total_count = 0
                    for order in manufacturing_orders:
                        work_order_states = [work_order.state for work_order in order.workorder_ids]
                        completed_count = work_order_states.count('done')
                        total_count = len(work_order_states)
                        total_completed_count += completed_count
                        total_total_count += total_count
                    if total_total_count > 0:
                        record.work_order_percentage_done = (total_completed_count / total_total_count)
                    else:
                        record.work_order_percentage_done = 0.0
            else:
                record.work_order_percentage_done = 0.0

        
    @api.depends('order_id')
    def _compute_work_order_percentage_not_done(self):
        """
        Compute the percentage of work orders that are not done for each record.

        This method calculates the percentage of work orders that are in the 'waiting' or 'pending' state
        out of the total number of work orders associated with the record's sale order.

        :return: None
        """
        for record in self:
            if record.order_id:
                if record.order_id and record.order_id.state in ['draft', 'sent', 'sale']:
                    manufacturing_orders = self.env['mrp.production'].search([('sale_order', '=', record.order_id.id)])
                    total_draft_pending_count = 0
                    total_total_count = 0
                    for order in manufacturing_orders:
                        work_order_states = [work_order.state for work_order in order.workorder_ids]
                        draft_pending_count = work_order_states.count('waiting') + work_order_states.count('pending')
                        total_count = len(work_order_states)
                        total_draft_pending_count += draft_pending_count
                        total_total_count += total_count
                    if total_total_count > 0:
                        record.work_order_percentage_not_done = (total_draft_pending_count / total_total_count)
                    else:
                        record.work_order_percentage_not_done = 0.0
            else:
                record.work_order_percentage_not_done = 0.0


    @api.depends('order_id')
    def _compute_work_order_percentage_in_progress(self):
        """
        Compute the percentage of work orders in progress for the current project.

        This method calculates the percentage of work orders in progress for the current project
        based on the associated sale order. It iterates through all the manufacturing orders
        linked to the sale order and counts the number of work orders in progress. The percentage
        is then calculated by dividing the number of completed work orders by the total number
        of work orders.

        Returns:
            None
        """
        for record in self:
            if record.order_id:
                if record.order_id and record.order_id.state in ['draft','sent','sale']:
                    manufacturing_orders = self.env['mrp.production'].search([('sale_order', '=', record.order_id.id)])

                    total_completed_count = 0
                    total_total_count = 0
                    for order in manufacturing_orders:
                        work_order_states = [work_order.state for work_order in order.workorder_ids]
                        completed_count = work_order_states.count('progress')
                        total_count = len(work_order_states)
                        total_completed_count += completed_count
                        total_total_count += total_count
                    if total_total_count > 0:
                        record.work_order_percentage_in_progress = (total_completed_count / total_total_count)
                    else:
                        record.work_order_percentage_in_progress = 0.0
            else:
                record.work_order_percentage_in_progress = 0.0

    @api.depends('order_id')
    def _compute_date_assembly_desassembly(self):
        for record in self:
            if record.order_id:
                record.assembly_date_start = record.order_id.opportunity_id.date_de_montage_du
                record.assembly_date_end = record.order_id.opportunity_id.date_de_montage_au
                record.disassembly_date_start = record.order_id.opportunity_id.date_de_demontage_du
                record.disassembly_date_end = record.order_id.opportunity_id.date_de_demontage_au
    
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