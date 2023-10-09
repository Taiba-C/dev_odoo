# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
 
class SaleOrderOptionNesil(models.Model):
    _name = 'sale.order.option.nesil' 
    _description = "Nesil Options"
    _order = 'sequence, id'

    # FIXME ANVFE wtf is it not required ???
    # TODO related to order.company_id and restrict product choice based on company
    order_id = fields.Many2one('sale.order', 'Sales Order Reference', ondelete='cascade', index=True)
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
                                    print('bom_line.product_id')
                                    print(bom_line.product_id.name)
                                    product_ids.append(bom_line.product_id.id)
                rec.product_id_domain = json.dumps(([('id', 'in', product_ids)]))  

    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True)
    line_id = fields.Many2one(
        comodel_name='sale.order.line', ondelete='set null', copy=False)
    sequence = fields.Integer(
        string='Sequence', help="Gives the sequence order when displaying a list of optional products.")

    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False,
        required=True, precompute=True)

    quantity = fields.Float(
        string="Quantity",
        required=True,
        digits='Product Unit of Measure',
        default=1)
    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_uom_id',
        store=True, readonly=False,
        required=True, precompute=True,
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    price_unit = fields.Float(
        string="Unit Price",
        digits='Product Price',
        compute='_compute_price_unit',
        store=True, readonly=False,
        required=True, precompute=True)
    discount = fields.Float(
        string="Discount (%)",
        digits='Discount',
        compute='_compute_discount',
        store=True, readonly=False, precompute=True)

    is_present = fields.Boolean(
        string="Present on Quotation",
        compute='_compute_is_present',
        search='_search_is_present',
        help="This field will be checked if the option line's product is "
             "already present in the quotation.")

    #=== COMPUTE METHODS ===#

    @api.depends('product_id')
    def _compute_name(self):
        for option in self:
            if not option.product_id:
                continue
            product_lang = option.product_id.with_context(lang=option.order_id.partner_id.lang)
            option.name = product_lang.get_product_multiline_description_sale()

    @api.depends('product_id')
    def _compute_uom_id(self):
        for option in self:
            if not option.product_id or option.uom_id:
                continue
            option.uom_id = option.product_id.uom_id

    @api.depends('product_id', 'uom_id', 'quantity')
    def _compute_price_unit(self):
        for option in self:
            if not option.product_id or not option.order_id.pricelist_id:
                continue
            # To compute the price_unit a so line is created in cache
            values = option._get_values_to_add_to_order()
            new_sol = self.env['sale.order.line'].new(values)
            new_sol._compute_price_unit()
            option.price_unit = new_sol.price_unit
            # Avoid attaching the new line when called on template change
            new_sol.order_id = False

    @api.depends('product_id', 'uom_id', 'quantity')
    def _compute_discount(self):
        for option in self:
            if not option.product_id:
                continue
            # To compute the discount a so line is created in cache
            values = option._get_values_to_add_to_order()
            new_sol = self.env['sale.order.line'].new(values)
            new_sol._compute_discount()
            option.discount = new_sol.discount
            # Avoid attaching the new line when called on template change
            new_sol.order_id = False

    def _get_values_to_add_to_order(self):
        self.ensure_one()
        return {
            'order_id': self.order_id.id,
            'price_unit': self.price_unit,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.uom_id.id,
            'discount': self.discount,
        }

    @api.depends('line_id', 'order_id.sale_order_nesil_option_ids', 'product_id')
    def _compute_is_present(self):
        # NOTE: this field cannot be stored as the line_id is usually removed
        # through cascade deletion, which means the compute would be false
        for option in self:
            option.is_present = bool(option.order_id.sale_order_nesil_option_ids.filtered(lambda l: l.product_id == option.product_id))

    def _search_is_present(self, operator, value):
        if (operator, value) in [('=', True), ('!=', False)]:
            return [('line_id', '=', False)]
        return [('line_id', '!=', False)]

    #=== ACTION METHODS ===#

    def _get_values_to_add_to_option(self):
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
    
    def button_add_to_option(self):
        self.add_option_to_option()

    def add_option_to_option(self):
        self.ensure_one()

        sale_order = self.order_id

        if sale_order.state not in ['draft', 'sent']:
            raise UserError(_('You cannot add options to a confirmed order.'))

        values = self._get_values_to_add_to_option()
        order_line = self.env['sale.order.option'].create(values)
        self.order_id.sale_order_nesil_option_ids.filtered(lambda l: l.product_id == self.product_id).unlink()


        self.write({'line_id': order_line.id})
        if sale_order:
            sale_order.add_option_to_order_with_taxcloud()

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
        res = super(SaleOrderOptionNesil, self).copy(default)
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
    
    def retro_options_nesil_options(self):
        orders = self.env["sale.order"].sudo().search([])
        for order in orders:
            if len(order.sale_order_nesil_option_ids) <= 0 and len(order.sale_order_option_ids) > 0 and order.name == 'NE202300330':
                for option in order.sale_order_option_ids:
                    self.env["sale.order.option.nesil"].sudo().create({'product_id':option.product_id.id,'line_id':option.line_id.id,'name':option.name,
                        'quantity':option.quantity,'uom_id':option.uom_id.id,'product_uom_category_id':option.product_uom_category_id.id,
                        'price_unit':option.price_unit,'discount':option.discount,'is_present':option.is_present,'parent_id':option.parent_id.id,
                        'purchase_price':option.purchase_price,'margin':option.margin,'margin_product':option.margin_product,'margin_percent':option.margin_percent,
                        'total_purchase_price':option.total_purchase_price,'order_line_id':option.order_line_id.id,'nomenclature_name':option.nomenclature_name,
                        'total_sale_price':option.total_sale_price,'task_id':option.task_id.id,'planning_id':option.planning_id.id,'work_order_id':option.work_order_id.id,'role_id':option.role_id.id,'order_id':option.order_id.id})
    def remove_old_options(self):
        options = self.env["sale.order.option"].sudo().search([])
        options.unlink()

    
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
       
