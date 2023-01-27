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
    
    
    def generate_bom_order(self):
        """
            action by a button
            take each line in order_line
            create line with boms in sale_order_option
        """
        self.clear_sale_order_option()
        
        for line in self.order_line:
            if line.product_id:
                
                boms = self.get_product_bom(line.product_id.product_tmpl_id.id)
                
                self.create_sale_order_option(boms, self.id, line.product_id.product_tmpl_id.id)
        
        self.is_bom_generated = True
                
        self.compute_sale_order_option_ids()
        
    
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
    
    def create_sale_order_option(self, boms, order_id, parent_id):
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
                
                'parent_id' : parent_id,
                
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

                })
    
    @api.onchange('sale_order_option_ids')
    def _onchange_sale_order_option_ids(self):
        self.compute_sale_order_option_ids()
        
    def compute_sale_order_option_ids(self):
        """
            make calcul to get total purchase or sale
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
            
            if line.parent_id not in self.order_line.product_template_id:
                raise UserError(f"{line.parent_id.name} is not in line of quotation")
            
            for bom in list_boms:
                #! list_bom is list of informations of bom with parent and child
                if line.parent_id.id == bom['parent_bom']:
                    if line.product_id.product_tmpl_id.id in bom['bom_products']:
                        #! search if product in tab is in the bom products
                        # quantity_product = self.env['mrp.bom.line'].search([('bom_id', '=', bom['bom_id']),('product_id','=',line.product_id.id)])
                        
                        if line.purchase_price != line.product_id.product_tmpl_id.standard_price or line.margin_product != line.product_id.product_tmpl_id.margin_product:
                            line.purchase_price = line.product_id.product_tmpl_id.standard_price
                            line.margin_product = line.product_id.product_tmpl_id.margin_product                      
                            # line.quantity = quantity_product.product_qty                      
                        
                    #! prix total achat
                    line.total_purchase_price = line.purchase_price * line.quantity
                    
                    #! prix total vente
                    if line.margin_product > 0:
                        line.total_sale_price = line.total_purchase_price / line.margin_product
                    if line.margin_product > 1 :
                        raise UserError("You cannot set coefficient value up to 1!")
                    
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
            total = 0
            for line in self.sale_order_option_ids:
                if order_line.product_template_id == line.parent_id:
                    total += line.total_sale_price
                    order_line.product_uom_qty = 1
                    order_line.price_unit = total
        
        
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
            if value.product_template_id.detailed_type == 'service':
                value.price_subtotal = 0
   
    @api.onchange('date_of_exhibition')
    def _onchange_date_of_exhibition(self):
        if not self.date_of_exhibition:
            self.date_of_exhibition = self.opportunity_id.x_studio_dbut_salon
            self.set_validity_date()
        self.set_validity_date()
        
    @api.model
    def notify_quotation_expired(self):
        quotation_drafts_expired = self.search([('state', '=', 'draft'),('validity_date','<=',date.today())])
        if quotation_drafts_expired:
            notification_ids = []
            for user in quotation_drafts_expired:
                notification_ids = [(0, 0, {
                    'res_partner_id': user.user_id.partner_id.id,
                    'notification_type': 'inbox',
                })]  
                user.message_post(body=f'Le devis {user.name} a éxpiré', message_type="notification", subtype_xmlid='mail.mt_note', 
                                author_id=self.env.user.partner_id.id, 
                                notification_ids=notification_ids)
    
    def action_quotation_send(self):
        res = super(Sale_order,self).action_quotation_send()
        
        if self.is_bom_generated == False:
            raise UserError("You forgot to click on the quote button")

        
        return res

    def action_confirm(self):
        res = super(Sale_order,self).action_confirm()
        
        if self.is_bom_generated == False:
            raise UserError("You forgot to click on the quote button")
        
        return res