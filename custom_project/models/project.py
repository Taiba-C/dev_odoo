# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectProject(models.Model):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    _inherit = 'project.project'
    
    order_id = fields.Many2one('sale.order', string="Sale Order")
    bon_de_commande = fields.Many2one('sale.order', string="Sale Order")
    work_order_qty = fields.Float('Work ORder Qty', compute="_compute_work_order_qty", store=True)
    work_order_percentage_done = fields.Float('Work ORder Percent done', compute="_compute_work_order_percentage_done")
    work_order_percentage_not_done = fields.Float('Work ORder Percent not done', compute="_compute_work_order_percentage_not_done")
    work_order_percentage_in_progress = fields.Float('Work ORder Percent in progress', compute="_compute_work_order_percentage_in_progress")

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

        This method calculates the percentage of work orders that are not done for each record in the model.
        It iterates over the records and checks if there is an associated order. If there is, it retrieves the
        manufacturing orders related to that order and calculates the completed and total count of work orders.
        It then calculates the percentage of work orders that are not done and assigns it to the
        `work_order_percentage_not_done` field of the record.

        If there is no associated order, the `work_order_percentage_not_done` field is set to 0.0.

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

                    not_done_count = total_total_count - total_completed_count
                    if total_total_count > 0:
                        record.work_order_percentage_not_done = (not_done_count / total_total_count)
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