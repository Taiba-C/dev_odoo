# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Sale_order(models.Model):
    _inherit = 'sale.order'
    
    total_purchase = fields.Float('Total puchase price', readonly = True)
    total_sale = fields.Float('Total sale price', readonly = True)
    margin = fields.Float('Margin', readonly = True)
    margin_percent = fields.Float('Margin %', readonly = True)
    
    date_of_exhibition = fields.Date('Begin of exhibition')
    validity_quotation = fields.Date('Validity of the quotation')
    
    
    is_bom_generated = fields.Boolean('Is BOm Generated')
    task_option_counts = fields.Float(compute='_get_task_counts')
    project_option_counts = fields.Float(compute='_get_project_counts')
    project_options_id = fields.Many2one('project.project', string='Project option', ondelete='cascade')
    
    picking_id = fields.Many2one('stock.picking', string='Nomenclature du chiffrage')
    
    
    def generate_bom_order(self):
        """
            action by a button
            take each line in order_line
            create line with boms in sale_order_option
        """
        
        if len(self.order_line) == 0:
            """
                test if o2m order_line does not have any record yet
            """
            self.clear_sale_order_option()
        
        self.delete_option_without_order_line(self.id)  
          
        for line in self.order_line:
            if line.product_id:
                boms = self.get_product_bom(line.product_id.product_tmpl_id.id)
                is_generated = self.check_option_generated(line)
                if not is_generated:
                    
                    self.create_sale_order_option(boms, self.id,  line.id)
                    
        
        self.is_bom_generated = True
                
        self.compute_sale_order_option_ids()
        
    def check_option_generated(self, order_line):
        """
            check if the order line doesn't have generated yet
            it return all id of sale order line 
            we will check the line if 
        """
        
        option_line = self.sale_order_option_ids.filtered(lambda l: l.order_line_id.id == order_line.id)
        if len(option_line) == 0:
            return False
        else:
            return True
    
    def delete_option_without_order_line(self, order_id):
        """
            Unlink sale order option record if the order line was deleted
        """
        order_options = self.sale_order_option_ids.filtered(lambda l: l.order_id.id == order_id and l.order_line_id.id == False)
        order_options.unlink()
                
    
    def clear_sale_order_option(self):
        """
            clear sale_order_option every time trigger button add boms
        """
        for rec in self:
            rec.sale_order_option_ids = [(5,0,0)]         
        
    def get_product_bom(self, id):
        """
            retrieve boms of a specific product per orderline
        """
        product_boms=[]
        boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', id)])
        
        for line in boms.bom_line_ids:
            
            id = line.product_id.id
            quantity = line.product_qty
            
            product_boms.append({'id': id, 'quantity':quantity})
            
        return product_boms
    
    def create_sale_order_option(self, boms, order_id, o_l_id):
        """
            create in model sale order option
            each line is from product as a bom's parent
        """
        for data in boms:
            product_id = self.env['product.product'].search([('id', '=', data['id'])])
            product_qty = data['quantity']
            
            total_price_purchase = 0
            total_price_sale = 0
            margin = 0
            margin_percent = 0
                        
            if product_id:
                
                total_price_purchase = product_id.standard_price * product_qty
                
                if product_id.product_tmpl_id.margin_product > 0:
                    total_price_sale = total_price_purchase / product_id.product_tmpl_id.margin_product

                    margin = total_price_sale - total_price_purchase
                
                if margin > 0:
                    margin_percent = margin / total_price_sale
                
                self.env['sale.order.option'].create({
                                
                'product_id': product_id.id,

                'order_id': order_id,

                'name': product_id.name,

                'price_unit':  product_id.lst_price,
                
                'quantity':  product_qty,
                
                'purchase_price':  product_id.standard_price,
                
                'margin_product':  product_id.product_tmpl_id.margin_product,
                
                'margin_percent':  margin_percent,
                
                'margin':  margin,
                
                'total_purchase_price':  total_price_purchase,
                
                'total_sale_price':  total_price_sale,
                
                'order_line_id':  o_l_id,

                })
    
    @api.onchange('sale_order_option_ids')
    def _onchange_sale_order_option_ids(self):
        self.compute_sale_order_option_ids()
        
    def compute_sale_order_option_ids(self):
        """
            make calcul to get total purchase or sale
            it will called more than one
        """
        total_purchase = 0
        total_sale = 0
        margin = 0
        
        #! parent boms are ids of BOM in order line 
        #! it is a object with list of id
        parent_boms = self.order_line.product_template_id
        boms = self.env['mrp.bom']
        list_boms = []
        
        for parent_bom in parent_boms:
            """
                create dict of boms existing in parent_boms
                existing in the line of order_line
            """            
            product_id_lists = []
            bom = boms.search([('product_tmpl_id', '=', parent_bom.id)])
            for product in bom.bom_line_ids:
                product_id_lists.append(product.product_tmpl_id.id)
            list_boms.append({
                'bom_id':bom.id,
                'parent_bom':bom.product_tmpl_id.id,
                'bom_products': product_id_lists
            })
        
        for line in self.sale_order_option_ids:
            
            for bom in list_boms:
                #! list_bom is list of informations of bom with parent and child
                if line.order_line_id.product_template_id.id == bom['parent_bom']:
                    if line.product_id.product_tmpl_id.id in bom['bom_products']:
                        #! search if product in tab is in the bom products
                        #! The purchase price and margin_product will not change
                        # quantity_product = self.env['mrp.bom.line'].search([('bom_id', '=', bom['bom_id']),('product_id','=',line.product_id.id)])
                        
                        if line.purchase_price != line.product_id.product_tmpl_id.standard_price or line.margin_product != line.product_id.product_tmpl_id.margin_product:
                            line.purchase_price = line.product_id.product_tmpl_id.standard_price
                            line.margin_product = line.product_id.product_tmpl_id.margin_product                      
                            # line.quantity = quantity_product.product_qty      
                    else:
                        if line.purchase_price == 0 and line.margin_product == 0:
                            """
                                this condition is to test if it is a new product
                                because new product will have purchase price and margin product as 0
                                normaly
                            """
                            line.purchase_price = line.product_id.standard_price
                            line.margin_product = line.product_id.margin_product        
                        
                    #! prix total achat
                    line.total_purchase_price = line.purchase_price * line.quantity
                    
                    #! prix total vente
                    if line.margin_product > 0:
                        line.total_sale_price = line.total_purchase_price / line.margin_product
                    if line.margin_product > 1 :
                        raise UserError("Vous ne pouvez pas régler la valeur du coefficient sup à 1!")
                    
                    #! marge en €
                    line.margin = line.total_sale_price - line.total_purchase_price
                    if line.margin < 0:
                        line.margin = 0
                        
                    #! marge %
                    if line.total_sale_price > 0:
                        line.margin_percent = line.margin / line.total_sale_price
                    
                    total_purchase += line.total_purchase_price
                    total_sale += line.total_sale_price
                    margin += line.margin
                    if total_sale > 0:
                        self.margin_percent = margin / total_sale
                    else:
                        self.margin_percent = 0
                
                
                
                
        for order_line in self.order_line:
            price_unit = 0
            percentage = 0
            for order_option in self.sale_order_option_ids:
                if order_option.order_line_id.id == order_line._origin.id :
                    price_unit += order_option.total_sale_price
                    pricelist = self.pricelist_id.item_ids.search([('compute_price','=','formula'),
                                                                   ('applied_on','=','2_product_category'),
                                                                   ('categ_id','=',order_line.product_template_id.categ_id.id)])
                    
                    if pricelist:
                        if percentage == 0 :
                            percentage = abs(pricelist[0].price_discount)
                        
            price_recompute = price_unit + (price_unit * percentage / 100.0)
            if price_recompute != price_unit:
                order_line.consumable = price_recompute - price_unit
            order_line.price_unit = price_recompute
            order_line.temp_price_unit = order_line.price_unit
            order_line._onchange_qty()
        
        
        self.total_purchase = total_purchase
        self.total_sale = total_sale
        self.margin = margin
        
    def set_validity_date(self):
        """
            use field validity date existing in Odoo to calculate validity of a quotation
            based on date of exhibition
            to show it Configuration > set true Default validity of the quote
        """
        for event in self:
            if event.date_order and event.date_of_exhibition:
                duration = self._get_duration(event.date_order.date(), event.date_of_exhibition)
                
                if duration >= 0:
                    if duration >= 45:
                        event.validity_date = event.date_order + timedelta(days = 14)
                    if duration < 45:
                        event.validity_date = event.date_order + timedelta(days = 7)
                        
                else:
                    event.validity_date = date.today()
                    
                    
            else:
                event.validity_date = date.today()
    
    def _get_duration(self, start, stop):
        """ 
            Get the duration value between the 2 given dates. 
        """
        
        nb_day = stop - start
        
        if not start or not stop:
            return 0
        duration = nb_day.days+1
        return duration
    
    @api.onchange('order_line')
    def _onchange_order_line(self):
        for value in self.order_line:
            if value.product_template_id and value.product_template_id.detailed_type == 'service':
                value.price_subtotal = 0
   
    @api.onchange('date_of_exhibition')
    def _onchange_date_of_exhibition(self):
        """
            populate field date of exhibition as date in CRM opportunity
        """
        if not self.date_of_exhibition:
            self.date_of_exhibition = self.opportunity_id.x_studio_dbut_salon
            self.set_validity_date()
        self.set_validity_date()
        
    @api.model
    def notify_quotation_expired(self):
        """
            send notifications
        """
        quotation_drafts_expired = self.search([('state', '=', 'draft'),('validity_date','<=',date.today()),('opportunity_id.won_status', '!=', 'lost')])
        if quotation_drafts_expired :
            
            notification_ids = []
            for user in quotation_drafts_expired:
                notification_ids = [(0, 0, {
                    'res_partner_id': user.user_id.partner_id.id,
                    'notification_type': 'inbox',
                })]  
                message = f"Le devis {user.name} a expiré. Veuillez marquer l'opportunité comme Perdu si le devis a été refusé par le client."
                user.message_post(body=message, message_type="notification", subtype_xmlid='mail.mt_note', 
                                author_id=self.env.user.partner_id.id, 
                                notification_ids=notification_ids)
        
    
    def action_quotation_send(self):
        res = super(Sale_order,self).action_quotation_send()
        
        if self.is_bom_generated == False:
            raise UserError("Vous avez oublié de cliquer sur le bouton de chiffrage")

        
        return res

    def action_confirm(self):
        res = super(Sale_order,self).action_confirm()
        
        self.delete_option_without_order_line(self.id)  
        
        if self.is_bom_generated == False:
            raise UserError("Vous avez oublié de cliquer sur le bouton de chiffrage")
        
        is_service = bool
        for line in self.sale_order_option_ids:
            if is_service == False:
                if line.product_id.type == 'service':
                    is_service = True
                    
        if is_service:       
            project = self.env['project.project'].create({
                    'name': self.name+' '+self.opportunity_id.name,
                    'user_id': self.user_id.id,
                    'partner_id': self.partner_id.id,
                    'date_start': self.date_of_exhibition,
                    'date': self.opportunity_id.x_studio_fin_salon,
                    'bon_de_commande':self.id, 
                    })
            
            self.project_options_id = project.id
            #project.sale_order = self
        for line in self.sale_order_option_ids:
            line.create_project_task(self.project_options_id, self.partner_id.id)
        
        for order in self:
            picking = self.env['stock.picking'].create({
                'partner_id': order.partner_shipping_id.id,
                'location_id': order.warehouse_id.lot_stock_id.id,
                'location_dest_id': order.partner_shipping_id.property_stock_customer.id,
                'origin': order.name,
                'picking_type_id': order.env.ref('stock.picking_type_out').id,
            })

            for option in order.sale_order_option_ids.filtered(lambda o: o.product_id):
                move = self.env['stock.move'].create({
                    'product_id': option.product_id.id,
                    'product_uom_qty': option.quantity,
                    'name': option.name,
                    'location_id': order.warehouse_id.lot_stock_id.id,
                    'picking_id': picking.id,
                    'location_dest_id': order.partner_shipping_id.property_stock_customer.id,
                    'origin': order.name,
                    
                })
                move._action_confirm()
            self.picking_id = picking.id
        return res

    def action_view_task_option_ids(self):
        tasks = []
        for line in self.sale_order_option_ids:
            if line.task_id.id:
                tasks.append(line.task_id.id)
        domain = [('id', 'in', tasks)]
        
        return {
            'domain': domain,
            'name': 'Taches',
            'view_mode': 'tree,form,kanban',
            'res_model': 'project.task',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
        
    def action_view_project_option_ids(self):
        
        domain = [('id', '=', self.project_options_id.id)]
        
        return {
            'domain': domain,
            'name': 'Projet',
            'view_mode': 'kanban,tree,form',
            'res_model': 'project.project',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
        
    def _get_task_counts(self):
        tasks = []
        for line in self.sale_order_option_ids:
            if line.task_id.id:
                tasks.append(line.task_id.id)
        self.task_option_counts = len(tasks)
        
    def _get_project_counts(self):
        self.project_option_counts = len(self.project_options_id)
        
    def action_view_planning(self):
        # button to return to planning
        # use project_options_id
        return self.project_options_id.action_project_forecast_from_project()
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    consumable = fields.Float('consumable')
    qty = fields.Float('Quantity costing', default=1)
    temp_price_unit = fields.Float('temp_price_unit')
    
    @api.onchange('qty', 'temp_price_unit')
    def _onchange_qty(self):
        self.price_unit = self.qty * self.temp_price_unit


    def name_get(self):
        res = []
        for line in self:
            name = line.name
            res.append((line.id, name))
        return res
    
class ProjectProject(models.Model):
    _inherit = 'project.project'

    bon_de_commande = fields.Many2one('sale.order', string="Sale Order")
    
