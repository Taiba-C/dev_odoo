# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json

 
class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
    
    # product_id_domain = fields.Char(compute='_get_product_in_bom',
    # readonly=True,
    # store=False)
    # @api.depends('order_id.order_line')
    # def _get_product_in_bom(self):
    #     product_ids = []
    #     for rec in self:
    #         if not rec.order_id:
    #                 rec.product_id_domain = json.dumps([('id', 'in',[])])
    #         else:
    #             for record in rec.order_id.order_line:
    #                 if record.product_template_id:
    #                         bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_template_id.id)])
    #                         for bom_line in bom.bom_line_ids:
    #                             if bom_line.product_id:
    #                                 product_ids.append(bom_line.product_id.id)
    #                                 for option in rec.order_id.sale_order_option_ids:
    #                                     if option.product_id.id in product_ids:
    #                                         product_ids.remove(option.product_id.id)
    #             rec.product_id_domain = json.dumps(([('id', 'in', product_ids)]))  
                           
    # is_present = fields.Boolean(
    #     string="Present on Quotation",
    #     compute='_compute_is_present_nesil',
    #     search='_search_is_present_nesil',
    #     help="This field will be checked if the option line's product is "
    #          "already present in the quotation.")


    #is_subcontracted = fields.Boolean('Produit sous-traité',related='product_id.is_subcontracted')
    state = fields.Selection(related='order_id.state')
    parent_id = fields.Many2one('product.template', string='Parent',copy=True)
    
    purchase_price = fields.Float('Purchase price',copy=True)
    
    margin = fields.Float('Margin €', readonly=True,copy=True)
    
    margin_product = fields.Float('Ratios', digits=(10, 4),copy=True)
    
    margin_percent = fields.Float('Margin %', readonly=True,copy=True)
    
    total_purchase_price = fields.Float('Total purchase price', readonly=True,copy=True)
    
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', ondelete="cascade", copy=True)

    nomenclature_name = fields.Char('Nomenclature', compute="_compute_nomenclature_name")
    #nomenclature_name = fields.Char('Nomenclature')
    
    total_sale_price = fields.Float('Total sale price', readonly=True,copy=True)
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    planning_id = fields.Many2one('planning.slot', string='Plan', ondelete='cascade')
    work_order_id = fields.Many2one('mrp.production', string='Work Order', ondelete='cascade')   
    role_id = fields.Many2one('planning.role', string ='Role', ondelete='cascade')
    @api.depends('price_unit','quantity')
    def _compute_subtotal(self):
        for option in self:
            if option.quantity and option.price_unit:
                option.price_subtotal = option.price_unit * option.quantity
            else:
                option.price_subtotal = 0
    price_subtotal = fields.Float(string='sous total',compute='_compute_subtotal')
    @api.depends('product_id', 'uom_id', 'quantity')
    def _compute_price_unit(self):
        for option in self:
            if not option.product_id or not option.order_id.pricelist_id:
                continue
            # To compute the price_unit a so line is created in cache
            values = option._get_values_to_add_to_order()
            new_sol = self.env['sale.order.line'].new(values)
            new_sol._compute_price_unit()
            option.price_unit = option.price_unit
            # Avoid attaching the new line when called on template change
            new_sol.order_id = False
    #  def create_project_task(self,project ,partner_id):
    #     for record in self:
    #         if record.product_id.type == 'service'and record.product_id.categ_id.name == 'Main d\'oeuvre':
    #             role_task = ''
    #             if record.product_id.name == 'MO USINAGE':
    #                 role_task="USINAGE"
    #             elif record.product_id.name == 'MO DECOUPE':
    #                  role_task="DECOUPE"
    #             elif record.product_id.name == 'MO ASSEMBLAGE':
    #                  role_task="ASSEMBLAGE"
    #             elif record.product_id.name == 'MO PLAQUAGE DE CHANTS':
    #                  role_task="PLAQUAGE DE CHANTS"
    #             elif record.product_id.name == 'MO Etude de fabrication':
    #                  role_task="Etude de fabrication"
    #             task = self.env['project.task'].create({
    #                 'name': record.product_id.name + ' ' + record.order_line_id.product_id.name + ' ' + record.order_line_id.display_name,
    #                 'project_id': project.id,
    #                 'partner_id': partner_id,
    #                 'planned_hours': record.quantity,
    #                 'role_task': role_task,
    #             })
    #             record.task_id = task.id
    #             date_start = datetime.combine(project.date_start, datetime.min.time())
    #             date_start += timedelta(hours=5)
    #             overtime=record.quantity
    #             if overtime == 0:
    #                 overtime = 1
               
    #             role_id = self.env['planning.role'].search([('name', '=', role_task)], limit=1)   
    #             planning = self.env['planning.slot'].create({
    #                 'project_id': project.id,
    #                 'start_datetime': date_start,
    #                 'end_datetime': date_start + timedelta(hours=overtime),
    #                 'task_id': record.task_id.id,
    #                 'task_name': record.task_id.display_name,
    #                 'role_id':role_id.id,
    #             })
                
    #            # work = self.env['mrp.production'].create({
    #             #    'product_id': record.product_id.id, 
    #              #   'name': record.name + ' '+ record.product_id.name + ' ' + record.order_line_id.product_id.name,
    #               #  'product_qty': record.quantity, 
    #            # })
    #             #record.work_order_id = work
    #             record.planning_id = planning
     
    # @api.onchange('quantity', 'margin_product', 'purchase_price')
    # def compute_order_options(self):
    #     self.total_purchase_price = self.product_id.standard_price * self.quantity
    #     if self.margin_product > 0:
    #         self.total_sale_price = self.total_purchase_price / self.margin_product
    #     self.margin = self.total_sale_price - self.total_purchase_price
    #     if self.total_sale_price > 0:
    #         self.margin_percent = self.margin / self.total_sale_price
    
    def copy(self, default=None):
        self.ensure_one()
        res = super(SaleOrderOption, self).copy(default)
        res.parent_id = self.parent_id.id if self.parent_id else None
        res.purchase_price = self.purchase_price if self.purchase_price else 0
        res.margin = self.margin if self.margin else 0
        res.total_purchase_price = self.total_purchase_price if self.total_purchase_price else 0
        res.quantity = self.quantity if self.quantity else 0
        return res

    # @api.depends('order_line_id')
    # def _compute_nomenclature_name(self):
    #     for record in self:
    #         if record.order_line_id and record.nomenclature_name != '':
    #             record.nomenclature_name = record.order_line_id.name
    
    def get_consumable(self,order_line):                                    
        price_recompute = 0
        price_unit = 0
        price_unit = self.price_unit
        percentage = 0
        pricelist = self.order_id.pricelist_id.item_ids.search([('compute_price','=','formula'),
                                                        ('applied_on','=','2_product_category'),
                                                        ('categ_id','=',self.product_id.product_tmpl_id.categ_id.id)])
        if pricelist:
            if percentage == 0 :
                percentage = abs(pricelist[0].price_discount)
                
        price_recompute = price_unit + (price_unit * percentage / 100.0)
        if price_recompute != price_unit:
            consumable = price_recompute - price_unit
            return consumable
        else:
            return 0
    def add_option_to_order(self):
        self.ensure_one()

        sale_order = self.order_id

        if sale_order.state not in ['draft', 'sent']:
            raise UserError(_('You cannot add options to a confirmed order.'))

        values = self._get_values_to_add_to_order()
        values['temp_price_unit'] = self.price_unit
        values['price_subtotal']:abs((self.price_unit * self.qty))
        values['qty'] = self.quantity
        order_line = self.env['sale.order.line'].create(values)
        nesil_options = self.env['sale.order.option.nesil'].sudo().search([('option_line_id','=',self.id)])
        for nesil_option in nesil_options:
            nesil_option.write({'order_line_id':order_line.id,'option_line_id':None,'line_type':'','updated_id':nesil_option.option_line_id})
        consumable = self.get_consumable(order_line)
        values['temp_price_unit'] += consumable
        price_subtotal = values['temp_price_unit'] * self.quantity
        discount = (self.discount/100) * (order_line.temp_price_unit+consumable) * self.quantity if self.discount else 0
        price_subtotal += - discount
        order_line.write({'consumable':consumable,'price_subtotal':price_subtotal,'temp_price_unit':order_line.temp_price_unit + consumable})
        self.price_unit = 0
        self.quantity = 1
        self.discount = 0

        self.write({'line_id': order_line.id})
        if sale_order:
            sale_order.add_option_to_order_with_taxcloud()
    def action_costing_option(self):
        self.ensure_one()
        action = self.env.ref('custom_sales.action_component_selection_wizard_option').read()[0]

        mrp_bom = self.env['mrp.bom'].sudo().search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)])
        mrp_bom_line = self.env['mrp.bom.line'].sudo().search([('bom_id', '=', mrp_bom.id)]).ids
        action['context'] = {
            'product_id': self.product_id.id,
            'option_line_id': self.id,
            'mrp_bom_line': list(set(mrp_bom_line)),
        }
        return action
    
    #=== ACTION METHODS ===#

    # def _get_values_to_add_to_nesil_option(self):
    #     self.ensure_one()
    #     return {
    #         #'product_uom_qty': self.quantity,
    #         'product_id':self.product_id.id,
    #         'line_id':self.line_id.id,
    #         'name':self.name,
    #         'quantity':self.quantity,
    #         'uom_id':self.uom_id.id,
    #         'product_uom_category_id':self.product_uom_category_id.id,
    #         'price_unit':self.price_unit,
    #         'discount':self.discount,
    #         'is_present':self.is_present,
    #         'parent_id':self.parent_id.id,
    #         'purchase_price':self.purchase_price,
    #         'margin':self.margin,
    #         'margin_product':self.margin_product,
    #         'margin_percent':self.margin_percent,
    #         'total_purchase_price':self.total_purchase_price,
    #         'order_line_id':self.order_line_id.id,
    #         'nomenclature_name':self.nomenclature_name,
    #         'total_sale_price':self.total_sale_price,
    #         'task_id':self.task_id.id,
    #         'planning_id':self.planning_id.id,
    #         'work_order_id':self.work_order_id.id,
    #         'role_id':self.role_id.id,
    #         'order_id':self.order_id.id
    #     }
    
    # def button_add_to_order(self):
    #     self.add_option_to_order()

    # def add_option_to_order(self):
    #     self.ensure_one()

    #     sale_order = self.order_id

    #     if sale_order.state not in ['draft', 'sent']:
    #         raise UserError(_('You cannot add options to a confirmed order.'))
    #     is_in_lines = False
    #     for option in self.order_id.sale_order_nesil_option_ids:
    #         if self.product_id.id == option.product_id.id:
    #             is_in_lines = True
    #             option.write({'quantity':option.quantity+self.quantity})
    #             self.order_id.sale_order_option_ids.filtered(lambda l: l.product_id == self.product_id).unlink()
    #     if is_in_lines == False:
    #         values = self._get_values_to_add_to_nesil_option()
    #         self.env['sale.order.option.nesil'].create(values)

    #     #self.write({'line_id': order_line.id})
    #     if sale_order:
    #         sale_order.add_option_to_order_with_taxcloud()