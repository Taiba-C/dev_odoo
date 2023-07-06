# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

 
class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
        
    parent_id = fields.Many2one('product.template', string='Parent')
    
    purchase_price = fields.Float('Purchase price')
    
    margin = fields.Float('Margin €', readonly=True)
    
    margin_product = fields.Float('Ratios', digits=(10, 4))
    
    margin_percent = fields.Float('Margin %', readonly=True)
    
    total_purchase_price = fields.Float('Total purchase price', readonly=True)
    
    order_line_id = fields.Many2one('sale.order.line', string='Order Line')
    
    total_sale_price = fields.Float('Total sale price', readonly=True)
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    planning_id = fields.Many2one('planning.slot', string='Plan', ondelete='cascade')
    
    def create_project_task(self,project ,partner_id):
        for record in self:
            if record.product_id.type == 'service'and record.product_id.categ_id.name == 'Main d\'oeuvre':
                task = self.env['project.task'].create({
                    'name': record.product_id.name + ' ' + record.order_line_id.product_id.name + ' ' + record.order_line_id.display_name,
                    'project_id': project.id,
                    'partner_id': partner_id,
                    'planned_hours': record.quantity,
                })
                record.task_id = task.id
                date_start = datetime.combine(project.date_start, datetime.min.time())
                date_start += timedelta(hours=5)
                overtime=record.quantity
                if overtime == 0:
                    overtime = 1
                planning = self.env['planning.slot'].create({
                    'project_id': project.id,
                    'start_datetime': date_start,
                    'end_datetime': date_start + timedelta(hours=overtime),
                    'task_id': record.task_id.id,
                    'task_name': record.task_id.display_name,
                    
                })
                record.planning_id = planning
                
                
class Planning_slot(models.Model):
    _inherit = 'planning.slot'
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    task_name = fields.Char("Task Name")
    
    @api.depends(
        'start_datetime', 'end_datetime', 'resource_id.calendar_id',
        'company_id.resource_calendar_id', 'allocated_percentage', 'resource_id.flexible_hours')
    def _compute_allocated_hours(self):
        res = super(Planning_slot,self)._compute_allocated_hours()
        for record in self:
            diff = record.end_datetime - record.start_datetime
            record.allocated_hours = diff.total_seconds() / 3600
        return res
