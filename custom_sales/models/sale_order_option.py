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
    
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', ondelete="cascade", copy=True)

    nomenclature_name = fields.Char('Nomenclature', compute="_compute_nomenclature_name")
    
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
    
    def copy(self, default=None):
        self.ensure_one()
        res = super(SaleOrderOption, self).copy(default)
        res.parent_id = self.parent_id.id if self.parent_id else None
        res.purchase_price = self.purchase_price if self.purchase_price else 0
        res.margin = self.margin if self.margin else 0
        res.total_purchase_price = self.total_purchase_price if self.total_purchase_price else 0
        res.quantity = self.quantity if self.quantity else 0
        return res

    @api.depends('order_line_id')
    def _compute_nomenclature_name(self):
        for record in self:
            record.nomenclature_name = record.order_line_id.name
    