# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Sale_order(models.Model):
    _inherit = "sale.order"
    
    total_purchase = fields.Float('Total puchase price', readonly = True)
    total_sale = fields.Float('Total sale price', readonly = True)
    margin = fields.Float('Margin', readonly = True)
    margin_percent = fields.Float('Margin %', readonly = True)
    date_of_exhibition = fields.Datetime('Date of exhibition')
    
    validity_quotation = fields.Char('Validity of the quotation', compute='_compute_duration')
    duration = fields.Integer('Duration', compute='_compute_duration')
    
    def generate_bom_order(self):
        """
            action by a button
            take each line in order_line
            create line with boms in sale_order_option
        """
        self.clear_sale_order_option()
        
        for line in self.order_line:
            if line.product_id:
                last_product = len(line.product_id) -1
                
                boms = self.get_product_bom(line.product_id[last_product].id)
                
                self.create_sale_order_option(boms, self.id, line.product_id.id)
                
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
        for line in self.sale_order_option_ids:
            
            if line.product_id.detailed_type != 'service':
                total_purchase += line.total_purchase_price
                total_sale += line.total_sale_price
                margin += line.margin
                if total_sale > 0:
                    self.margin_percent = margin / total_sale
                else:
                    self.margin_percent = 0
            else:
                if line.purchase_price != line.product_id.product_tmpl_id.standard_price or line.margin_product != line.product_id.product_tmpl_id.margin_product:
                    line.purchase_price = line.product_id.product_tmpl_id.standard_price
                    line.margin_product = line.product_id.product_tmpl_id.margin_product
                
                
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
        
    @api.depends('date_order', 'date_of_exhibition')
    def _compute_duration(self):
        for event in self:
            event.duration = self._get_duration(event.date_order, event.date_of_exhibition)
            
            if event.duration >= 45:
                event.validity_quotation = "2 weeks"
            if event.duration < 45:
                event.validity_quotation = "1 week"
    
    def _get_duration(self, start, stop):
        """ Get the duration value between the 2 given dates. """
        if not start or not stop:
            return 0
        duration = (((stop - start).total_seconds() / 3600)/24)+1
        return round(duration, 2)
    
    
class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'
        
    parent_id = fields.Many2one('product.template', string='Parent')
    
    purchase_price = fields.Float('Purchase price')
    
    margin = fields.Float('Margin €', readonly=True)
    
    margin_product = fields.Float('Coefficient')
    
    margin_percent = fields.Float('Margin %', readonly=True)
    
    total_purchase_price = fields.Float('Total purchase price', readonly=True)
    
    total_sale_price = fields.Float('Total sale price', readonly=True)
        
    @api.onchange('purchase_price')
    def _onchange_purchase_price(self):
        self.update_option_line()
    
    @api.onchange('quantity')
    def _onchange_quantity(self):
        self.update_option_line()

    
    @api.onchange('margin_product')
    def _onchange_margin_product(self):
        self.update_option_line()
        
    def update_option_line(self):
        """
            update total on change
        """
        if self.product_id:
            if self.product_id.detailed_type != 'service':
                # prix total achat
                self.total_purchase_price = self.purchase_price * self.quantity
                
                # prix total vente
                if self.margin_product > 0:
                    self.total_sale_price = self.total_purchase_price / self.margin_product
                    
                if self.margin_product == 0 :
                    raise UserError("You cannot set this value to margin as 0!")
                if self.margin_product > 1 :
                    raise UserError("You cannot set this value up to 1!")
                    
                
                # marge en €
                self.margin = self.total_sale_price - self.total_purchase_price
                if self.margin < 0:
                    self.margin = 0
                
                # marge %
                if self.total_sale_price > 0:
                    self.margin_percent = self.margin / self.total_sale_price
                
    