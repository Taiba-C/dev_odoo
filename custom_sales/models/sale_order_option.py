# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

 
class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
        
    parent_id = fields.Many2one('product.template', string='Parent',copy=True)
    
    purchase_price = fields.Float('Purchase price',copy=True)
    
    margin = fields.Float('Margin €', readonly=True,copy=True)
    
    margin_product = fields.Float('Ratios', digits=(10, 4),copy=True)
    
    margin_percent = fields.Float('Margin %', readonly=True,copy=True)
    
    total_purchase_price = fields.Float('Total purchase price', readonly=True,copy=True)
    
    order_line_id = fields.Many2one('sale.order.line', string='Order Line',ondelete='cascade',copy=True)
    
    total_sale_price = fields.Float('Total sale price', readonly=True,copy=True)
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    planning_id = fields.Many2one('planning.slot', string='Plan', ondelete='cascade')
    work_order_id = fields.Many2one('mrp.production', string='Work Order', ondelete='cascade')   
    role_id = fields.Many2one('planning.role', string ='Role', ondelete='cascade')
    
    def create_project_task(self,project ,partner_id):
        for record in self:
            if record.product_id.type == 'service'and record.product_id.categ_id.name == 'Main d\'oeuvre':
                role_task = ''
                if record.product_id.name == 'MO USINAGE':
                    role_task="USINAGE"
                elif record.product_id.name == 'MO DECOUPE':
                     role_task="DECOUPE"
                elif record.product_id.name == 'MO ASSEMBLAGE':
                     role_task="ASSEMBLAGE"
                elif record.product_id.name == 'MO PLAQUAGE DE CHANTS':
                     role_task="PLAQUAGE DE CHANTS"
                elif record.product_id.name == 'MO Etude de fabrication':
                     role_task="Etude de fabrication"
                task = self.env['project.task'].create({
                    'name': record.product_id.name + ' ' + record.order_line_id.product_id.name + ' ' + record.order_line_id.display_name,
                    'project_id': project.id,
                    'partner_id': partner_id,
                    'planned_hours': record.quantity,
                    'role_task': role_task,
                })
                record.task_id = task.id
                date_start = datetime.combine(project.date_start, datetime.min.time())
                date_start += timedelta(hours=5)
                overtime=record.quantity
                if overtime == 0:
                    overtime = 1
               
                role_id = self.env['planning.role'].search([('name', '=', role_task)], limit=1)   
                planning = self.env['planning.slot'].create({
                    'project_id': project.id,
                    'start_datetime': date_start,
                    'end_datetime': date_start + timedelta(hours=overtime),
                    'task_id': record.task_id.id,
                    'task_name': record.task_id.display_name,
                    'role_id':role_id.id,
                })
                
               # work = self.env['mrp.production'].create({
                #    'product_id': record.product_id.id, 
                 #   'name': record.name + ' '+ record.product_id.name + ' ' + record.order_line_id.product_id.name,
                  #  'product_qty': record.quantity, 
               # })
                #record.work_order_id = work
                record.planning_id = planning
     
    @api.onchange('quantity', 'margin_product', 'purchase_price')
    def compute_order_options(self):
        self.total_purchase_price = self.product_id.standard_price * self.quantity
        if self.margin_product > 0:
            self.total_sale_price = self.total_purchase_price / self.margin_product
        self.margin = self.total_sale_price - self.total_purchase_price
        if self.total_sale_price > 0:
            self.margin_percent = self.margin / self.total_sale_price
                
class Planning_slot(models.Model):
    _inherit = 'planning.slot'
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    task_name = fields.Char("Task Name")
    timesheet_id = fields.Many2one('account.analytic.line', string='Timesheet')
    
    @api.depends(
        'start_datetime', 'end_datetime', 'resource_id.calendar_id',
        'company_id.resource_calendar_id', 'allocated_percentage', 'resource_id.flexible_hours')
    def _compute_allocated_hours(self):
        res = super(Planning_slot,self)._compute_allocated_hours()
        for record in self:
            diff = record.end_datetime - record.start_datetime
            record.allocated_hours = diff.total_seconds() / 3600
        return res
    
    def action_planning_publish(self):
        assigned_employee = self.resource_id  # Vérifier si un employé est assigné à la tâche
        if assigned_employee:
            employee_env = self.env(user=assigned_employee.user_id)# Créer un nouvel environnement basé sur l'employé assigné
            timesheet = employee_env['account.analytic.line'].search([('slot_id', '=', self.id)], limit=1)
            if not timesheet:
                timesheet = employee_env['account.analytic.line'].create({
                    'project_id': self.project_id.id,
                    'task_id': self.task_id.id,
                    'slot_id': self.id,
                    'unit_amount': 0,
                })
            else:
                self.timesheet_id = timesheet.id
        return super(Planning_slot, self).action_planning_publish()

    def action_planning_publish_and_send(self):
        assigned_employee = self.resource_id  
        #Vérifier si un employé est assigné à la tâche
        if assigned_employee:
            employee_env = self.env(user=assigned_employee.user_id)
            # Créer un nouvel environnement basé sur l'employé assigné
            timesheet = employee_env['account.analytic.line'].search([('slot_id', '=', self.id)], limit=1)
            if not timesheet:
                timesheet = employee_env['account.analytic.line'].create({
                    # Créer la feuille de temps pour l'employé assigné
                    'project_id': self.project_id.id,
                    'task_id': self.task_id.id,
                    'slot_id': self.id,
                    'unit_amount': 0,
                })
            else:
                self.timesheet_id = timesheet.id
        return super(Planning_slot, self).action_planning_publish_and_send()

    def action_send(self):
        assigned_employee = self.resource_id  
        #Vérifier si un employé est assigné à la tâche
        if assigned_employee:
            employee_env = self.env(user=assigned_employee.user_id)
            # Créer un nouvel environnement basé sur l'employé assigné
            timesheet = employee_env['account.analytic.line'].search([('slot_id', '=', self.id)], limit=1)
            if not timesheet:
                timesheet = employee_env['account.analytic.line'].create({
                    # Créer la feuille de temps pour l'employé assigné
                    'project_id': self.project_id.id,
                    'task_id': self.task_id.id,
                    'slot_id': self.id,
                    'unit_amount': 0,
                })
            else:
                self.timesheet_id = timesheet.id
        return super(Planning_slot, self).action_send()
    
    def action_publish(self):
        assigned_employee = self.resource_id  
        #Vérifier si un employé est assigné à la tâche
        if assigned_employee:
            employee_env = self.env(user=assigned_employee.user_id)
            # Créer un nouvel environnement basé sur l'employé assigné
            timesheet = employee_env['account.analytic.line'].search([('slot_id', '=', self.id)], limit=1)
            if not timesheet:
                timesheet = employee_env['account.analytic.line'].create({
                    # Créer la feuille de temps pour l'employé assigné
                    'project_id': self.project_id.id,
                    'task_id': self.task_id.id,
                    'slot_id': self.id,
                    'unit_amount': 0,
                })
            else:
                self.timesheet_id = timesheet.id
        return super(Planning_slot, self).action_publish()
        
    def action_unpublish(self):
        self.resource_id = None
        return super(Planning_slot, self).action_unpublish()
    
    @api.onchange('role_id')
    def _onchange_role_id(self):
        if self.role_id.name == 'task_role':
            # Mettre à jour la valeur du champ role_id avec la valeur souhaitée pour le rôle "task_role"
            self.role_id = self.env['res.partner'].search([('name', '=', 'task_role')], limit=1)        
                                                        
class Task_custom(models.Model):
    _inherit = 'project.task'

    role_task = fields.Char('Rôle de la tâche')     
       
