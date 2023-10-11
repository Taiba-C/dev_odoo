# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json

 
class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
    
    product_id_domain = fields.Char(compute='_get_product_in_bom',
    readonly=True,
    store=False)
    @api.depends('order_id.order_line')
    def _get_product_in_bom(self):
        product_ids = []
        for rec in self:
            if not rec.order_id:
                    rec.product_id_domain = json.dumps([('id', 'in',[])])
            else:
                for record in rec.order_id.order_line:
                    if record.product_template_id:
                            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_template_id.id)])
                            for bom_line in bom.bom_line_ids:
                                if bom_line.product_id:
                                    product_ids.append(bom_line.product_id.id)
                rec.product_id_domain = json.dumps(([('id', 'in', product_ids)]))  
                           
    is_present = fields.Boolean(
        string="Present on Quotation",
        compute='_compute_is_present_nesil',
        search='_search_is_present_nesil',
        help="This field will be checked if the option line's product is "
             "already present in the quotation.")
    
    @api.depends('line_id', 'order_id.sale_order_nesil_option_ids', 'product_id')
    def _compute_is_present_nesil(self):
        # NOTE: this field cannot be stored as the line_id is usually removed
        # through cascade deletion, which means the compute would be false
        for option in self:
            option.is_present = bool(option.order_id.sale_order_nesil_option_ids.filtered(lambda l: l.product_id == option.product_id))

    def _search_is_present_nesil(self, operator, value):
        if (operator, value) in [('=', True), ('!=', False)]:
            return [('line_id', '=', False)]
        return [('line_id', '!=', False)]
    parent_id = fields.Many2one('product.template', string='Parent',copy=True)
    
    purchase_price = fields.Float('Purchase price',copy=True)
    
    margin = fields.Float('Margin €', readonly=True,copy=True)
    
    margin_product = fields.Float('Ratios', digits=(10, 4),copy=True)
    
    margin_percent = fields.Float('Margin %', readonly=True,copy=True)
    
    total_purchase_price = fields.Float('Total purchase price', readonly=True,copy=True)
    
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', ondelete="cascade", copy=True)

    nomenclature_name = fields.Char('Nomenclature', compute="_compute_nomenclature_name", store=True, readonly=True)
    
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
    
    #=== ACTION METHODS ===#

    def _get_values_to_add_to_nesil_option(self):
        self.ensure_one()
        return {
            #'product_uom_qty': self.quantity,
            'product_id':self.product_id.id,
            'line_id':self.line_id.id,
            'name':self.name,
            'quantity':self.quantity,
            'uom_id':self.uom_id.id,
            'product_uom_category_id':self.product_uom_category_id.id,
            'price_unit':self.price_unit,
            'discount':self.discount,
            'is_present':self.is_present,
            'parent_id':self.parent_id.id,
            'purchase_price':self.purchase_price,
            'margin':self.margin,
            'margin_product':self.margin_product,
            'margin_percent':self.margin_percent,
            'total_purchase_price':self.total_purchase_price,
            'order_line_id':self.order_line_id.id,
            'nomenclature_name':self.nomenclature_name,
            'total_sale_price':self.total_sale_price,
            'task_id':self.task_id.id,
            'planning_id':self.planning_id.id,
            'work_order_id':self.work_order_id.id,
            'role_id':self.role_id.id,
            'order_id':self.order_id.id
        }
    
    def button_add_to_order(self):
        self.add_option_to_order()

    def add_option_to_order(self):
        self.ensure_one()

        sale_order = self.order_id

        if sale_order.state not in ['draft', 'sent']:
            raise UserError(_('You cannot add options to a confirmed order.'))

        values = self._get_values_to_add_to_nesil_option()
        self.env['sale.order.option.nesil'].create(values)
        self.order_id.sale_order_option_ids.filtered(lambda l: l.product_id == self.product_id).unlink()


        #self.write({'line_id': order_line.id})
        if sale_order:
            sale_order.add_option_to_order_with_taxcloud()