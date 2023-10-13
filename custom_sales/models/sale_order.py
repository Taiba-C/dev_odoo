# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES
import json


class Sale_order(models.Model):
    _inherit = 'sale.order'
    
    sale_order_nesil_option_ids = fields.One2many(
        comodel_name='sale.order.option.nesil', inverse_name='order_id',
        string="Optional Products Lines",
        states=READONLY_FIELD_STATES,
        copy=True)
    def _compute_sale_invoice(self):
            for sale in self:
                if sale.state == 'sale':
                    amount = 0
                    for record in sale.invoice_ids:
                        if record.move_type in ('out_invoice','out_refund'):
                            amount += record.amount_total_signed
                    if amount == sale.amount_total:
                        sale.amount_to_pay = 0
                    else:
                        sale.amount_to_pay = sale.amount_total - amount
                else:
                    sale.amount_to_pay = 0

    amount_to_pay = fields.Float(string='Reste à facturer',compute='_compute_sale_invoice')
    total_purchase = fields.Float('Total puchase price', readonly = True, compute="_compute_total_infos")
    total_sale = fields.Float('Total sale price', readonly = True,compute="_compute_total_infos")
    margin = fields.Float('Margin', readonly = True, compute="_compute_total_infos")
    margin_percent = fields.Float('Margin %', readonly = True, compute="_compute_total_infos")
    @api.depends('origin')
    def get_ref_dossier(self):
        for rec in self:
            if rec.opportunity_id:
                if rec.opportunity_id.ensure_one():
                    rec.rfrence_du_dossier = rec.opportunity_id.id
                else:
                    rec.rfrence_du_dossier = None
            else:
                rec.rfrence_du_dossier = None
            order_line_ids = self.env['sale.order.line'].search([('order_id','=',rec.id)])
            sale_order_nesil_option_ids = self.env['sale.order.option.nesil'].search([('order_id','=', rec.id)])
            if len(sale_order_nesil_option_ids) > 0:
                for order_option in sale_order_nesil_option_ids:
                    if order_option.order_line_id:
                        if '-' in order_option.order_line_id.display_name:
                            product_name = order_option.order_line_id.display_name.split('-')[1]
                            old_ref = order_option.order_line_id.display_name.split('-')[0].replace(" ","")
                            if old_ref != rec.name:
                                new_line = rec.name+' -'+product_name
                                for line in order_line_ids:
                                    if new_line in line.display_name:
                                        order_option.order_line_id = line.id

    rfrence_du_dossier = fields.Many2one('crm.lead',string='Référence du dossier',compute='get_ref_dossier')
    date_of_last_version = fields.Datetime(
        string="Date de mis à jour",
        required=True, copy=False,default=fields.Datetime.now,
        help="La date qui apparait dans le rapport à chaque mis à jour du devis")
    def retro_date_of_late_update(self):
        orders =  self.env['sale.order'].search([])
        for order in orders:
            if order.date_order:
                order.date_of_last_version = order.date_order

    version_du_devis = fields.Char(string='Version du devis')
    @api.onchange('sale_order_nesil_option_ids')
    def _get_nomenclature_nesil_name(self):
        last_rec = ''
        for rec in self.sale_order_nesil_option_ids:
            last_rec = rec
        if self.order_line:
            for rec in self.order_line:
                    if rec.product_template_id:
                        bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', rec.product_template_id.id)])
                        for bom_line in bom.bom_line_ids:
                            if last_rec != '':
                                if last_rec.product_id.id == bom_line.product_id.id:
                                    last_rec.order_line_id = rec.id

                                    product_qty = last_rec.quantity
                                    total_price_purchase = 0
                                    total_price_sale = 0
                                    margin = 0
                                    margin_percent = 0         
                                    total_price_purchase = last_rec.product_id.standard_price * product_qty
                
                                    if last_rec.product_id.product_tmpl_id.margin_product > 0:
                                        total_price_sale = total_price_purchase / last_rec.product_id.product_tmpl_id.margin_product

                                        margin = total_price_sale - total_price_purchase
                
                                        if margin > 0:
                                            margin_percent = margin / total_price_sale
                 
                                        last_rec.purchase_price = last_rec.product_id.standard_price
                                        last_rec.margin_product = last_rec.product_id.product_tmpl_id.margin_product
                                        last_rec.margin_percent = margin_percent                                        
                                        last_rec.margin = margin
                                        last_rec.total_purchase_price = total_price_purchase
                                        last_rec.total_sale_price = total_price_sale
                                        
                            
    # @api.onchange('sale_order_option_ids')
    # def _get_nomenclature_name(self):
    #     last_rec = ''
    #     for rec in self.sale_order_option_ids:
    #         last_rec = rec
    #     if self.order_line:
    #         for rec in self.order_line:
    #                 if rec.product_template_id:
    #                     bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', rec.product_template_id.id)])
    #                     for bom_line in bom.bom_line_ids:
    #                         if last_rec != '':
    #                             if last_rec.product_id.id == bom_line.product_id.id:
    #                                 last_rec.order_line_id = rec.id

    #                                 product_qty = last_rec.quantity
    #                                 total_price_purchase = 0
    #                                 total_price_sale = 0
    #                                 margin = 0
    #                                 margin_percent = 0         
    #                                 total_price_purchase = last_rec.product_id.standard_price * product_qty
                
    #                                 if last_rec.product_id.product_tmpl_id.margin_product > 0:
    #                                     total_price_sale = total_price_purchase / last_rec.product_id.product_tmpl_id.margin_product

    #                                     margin = total_price_sale - total_price_purchase
                
    #                                     if margin > 0:
    #                                         margin_percent = margin / total_price_sale
                 
    #                                     last_rec.purchase_price = last_rec.product_id.standard_price
    #                                     last_rec.margin_product = last_rec.product_id.product_tmpl_id.margin_product
    #                                     last_rec.margin_percent = margin_percent                                        
    #                                     last_rec.margin = margin
    #                                     last_rec.total_purchase_price = total_price_purchase
    #                                     last_rec.total_sale_price = total_price_sale

    def write(self, vals):
        res = super(Sale_order, self).write(vals)
        for rec in self:
            if vals.get('version_du_devis'):
                rec.write({'date_of_last_version': datetime.now()}) 

        return res         

    date_of_exhibition = fields.Date('Begin of exhibition')
    validity_quotation = fields.Date('Validity of the quotation')
    
    
    is_bom_generated = fields.Boolean('Is BOm Generated')
    task_option_counts = fields.Float(compute='_get_task_counts')
    project_option_counts = fields.Float(compute='_get_project_counts')
    project_options_id = fields.Many2one('project.project', string='Project option', ondelete='cascade')
    
   
    
    picking_id = fields.Many2one('stock.picking', string='Nomenclature du chiffrage')
    
    mrp_order_id = fields.Many2one('mrp.production', string='MRP Order', ondelete='cascade')  

    work_order = fields.Many2one('mrp.workorder', string='Work Order')  

    work_center = fields.Many2one('mrp.workcenter', string='Work Center')  

    #mrp_production_counts = fields.Float(string='Ordres de fabrication', compute='_get_mrp_production_counts')
    mrp_production_counts = fields.Float(string='Ordres de fabrication')
    

    def generate_bom_order(self, order_line, products=[]):
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
        
        # self.delete_option_without_order_line(self.id)  
        
        self.create_sale_order_option(boms=products, order_id=self.id,  o_l_id=order_line)
          
        # for line in self.order_line:
        #     if line.product_id:
        #         boms = self.get_product_bom(line.product_id.product_tmpl_id.id)
        #         is_generated = self.check_option_generated(line)
        #         if not is_generated:
                    
        #             self.create_sale_order_option(boms, self.id,  line.id)
                    
        
        self.is_bom_generated = True
                
        # self.compute_sale_order_option_ids()
        
    def check_option_generated(self, order_line):
        """
            check if the order line doesn't have generated yet
            it return all id of sale order line 
            we will check the line if 
        """
        
        option_line = self.sale_order_nesil_option_ids.filtered(lambda l: l.order_line_id.id == order_line.id)
        if len(option_line) == 0:
            return False
        else:
            return True
    
    def delete_option_without_order_line(self, order_id):
        """
            Unlink sale order option record if the order line was deleted
        """
        order_options = self.sale_order_nesil_option_ids.filtered(lambda l: l.order_id.id == order_id and l.order_line_id.id == False)
        order_options.unlink()
                
    
    def clear_sale_order_option(self):
        """
            clear sale_order_option every time trigger button add boms
        """
        for rec in self:
            rec.sale_order_nesil_option_ids = [(5,0,0)]         
        
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
                
                self.env['sale.order.option.nesil'].create({
                                
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
                self.compute_order_line_price_unit()
    
    @api.onchange('sale_order_nesil_option_ids')
    def _onchange_sale_order_nesil_option_ids(self):
        self.compute_order_line_price_unit()
        
    def compute_order_line_price_unit(self):
        """
            for each line in order line
            search in order option to update the price unit
        """
        for order_line in self.order_line:
            price_unit = 0
            percentage = 0
            for order_option in self.sale_order_nesil_option_ids:
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
            order_line.set_price_unit()
                          
        
    # def compute_sale_order_option_ids(self):
    #     """
    #         make calcul to get total purchase or sale
    #         it will called more than one
    #     """
    #     total_purchase = 0
    #     total_sale = 0
    #     margin = 0
        
    #     #! parent boms are ids of BOM in order line 
    #     #! it is a object with list of id
    #     parent_boms = self.order_line.product_template_id
    #     boms = self.env['mrp.bom']
    #     list_boms = []
        
    #     for parent_bom in parent_boms:
    #         """
    #             create dict of boms existing in parent_boms
    #             existing in the line of order_line
    #         """            
    #         product_id_lists = []
    #         bom = boms.search([('product_tmpl_id', '=', parent_bom.id)])
    #         for product in bom.bom_line_ids:
    #             product_id_lists.append(product.product_tmpl_id.id)
    #         list_boms.append({
    #             'bom_id':bom.id,
    #             'parent_bom':bom.product_tmpl_id.id,
    #             'bom_products': product_id_lists
    #         })
        
    #     for line in self.sale_order_option_ids:
            
    #         for bom in list_boms:
    #             #! list_bom is list of informations of bom with parent and child
    #             if line.order_line_id.product_template_id.id == bom['parent_bom']:
    #                 if line.product_id.product_tmpl_id.id in bom['bom_products']:
    #                     #! search if product in tab is in the bom products
    #                     #! The purchase price and margin_product will not change
    #                     # quantity_product = self.env['mrp.bom.line'].search([('bom_id', '=', bom['bom_id']),('product_id','=',line.product_id.id)])
                        
    #                     if line.purchase_price != line.product_id.product_tmpl_id.standard_price or line.margin_product != line.product_id.product_tmpl_id.margin_product:
    #                         line.purchase_price = line.product_id.product_tmpl_id.standard_price
    #                         line.margin_product = line.product_id.product_tmpl_id.margin_product                      
    #                         # line.quantity = quantity_product.product_qty      
    #                 else:
    #                     if line.purchase_price == 0 and line.margin_product == 0:
    #                         """
    #                             this condition is to test if it is a new product
    #                             because new product will have purchase price and margin product as 0
    #                             normaly
    #                         """
    #                         line.purchase_price = line.product_id.standard_price
    #                         line.margin_product = line.product_id.margin_product        
                        
    #                 #! prix total achat
    #                 line.total_purchase_price = line.purchase_price * line.quantity
                    
    #                 #! prix total vente
    #                 if line.margin_product > 0:
    #                     line.total_sale_price = line.total_purchase_price / line.margin_product
    #                 if line.margin_product > 1 :
    #                     raise UserError("Vous ne pouvez pas régler la valeur du coefficient sup à 1!")
                    
    #                 #! marge en €
    #                 line.margin = line.total_sale_price - line.total_purchase_price
    #                 if line.margin < 0:
    #                     line.margin = 0
                        
    #                 #! marge %
    #                 if line.total_sale_price > 0:
    #                     line.margin_percent = line.margin / line.total_sale_price
                    
    #                 total_purchase += line.total_purchase_price
    #                 total_sale += line.total_sale_price
    #                 margin += line.margin
    #                 if total_sale > 0:
    #                     self.margin_percent = margin / total_sale
    #                 else:
    #                     self.margin_percent = 0
                
                
                
                
    #     for order_line in self.order_line:
    #         price_unit = 0
    #         percentage = 0
    #         for order_option in self.sale_order_option_ids:
    #             if order_option.order_line_id.id == order_line._origin.id :
    #                 price_unit += order_option.total_sale_price
    #                 pricelist = self.pricelist_id.item_ids.search([('compute_price','=','formula'),
    #                                                                ('applied_on','=','2_product_category'),
    #                                                                ('categ_id','=',order_line.product_template_id.categ_id.id)])
                    
    #                 if pricelist:
    #                     if percentage == 0 :
    #                         percentage = abs(pricelist[0].price_discount)
                        
    #         price_recompute = price_unit + (price_unit * percentage / 100.0)
    #         if price_recompute != price_unit:
    #             order_line.consumable = price_recompute - price_unit
    #         order_line.price_unit = price_recompute
    #         order_line.temp_price_unit = order_line.price_unit
    #         order_line.set_price_unit()
        
        
    #     self.total_purchase = total_purchase
    #     self.total_sale = total_sale
    #     self.margin = margin
    
    @api.depends('sale_order_nesil_option_ids')
    def _compute_total_infos(self):
        for record in self:
            total_purchase = sum(record.sale_order_nesil_option_ids.mapped('total_purchase_price'))
            total_sale = sum(record.sale_order_nesil_option_ids.mapped('total_sale_price'))
            margin = sum(record.sale_order_nesil_option_ids.mapped('margin'))
            if total_sale > 0:
                record.margin_percent = margin / total_sale
            else:
                record.margin_percent = 0
                
            record.total_purchase = total_purchase
            record.total_sale = total_sale
            record.margin = margin
                
    
        
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
            self.date_of_exhibition = self.opportunity_id.dbut_salon
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
    

        
    
    # def action_send_mail(self):

    #     res = super(Sale_order,self).action_send_mail()
        
    #     if self._context['active_model'] == 'sale.order':
    #         self.notify_sended_quotation()
                    
    #     return res
    
    def action_quotation_send(self):
        res = super(Sale_order,self).action_quotation_send()
        
        if self.is_bom_generated == False:
            raise UserError("Vous avez oublié de cliquer sur le bouton de chiffrage")
                    
        return res

        

    def action_confirm(self):
        res = super(Sale_order,self).action_confirm()

        self.delete_option_without_order_line(self.id)


        if self.is_bom_generated == False:
            raise UserError("Vous avez oublié de faire un chiffrage")


        is_service = bool
        for line in self.sale_order_nesil_option_ids:
            if is_service == False:
                if line.product_id.type == 'service':
                    is_service = True

        if is_service:
            project = self.env['project.project'].create({
                    'name': self.name+' '+self.opportunity_id.name,
                    'user_id': self.user_id.id,
                    'partner_id': self.partner_id.id,
                    'date_start': self.date_of_exhibition,
                    'date': self.opportunity_id.fin_salon,
                    'order_id':self.id,
                    })
            self.project_options_id = project.id
            #project.sale_order = self
        for line in self.sale_order_nesil_option_ids:
            line.create_project_task(self.project_options_id, self.partner_id.id)

       # for record in self:
           # i=1
           # for order_line in record.order_line:
               # work = self.env['mrp.production'].create({
               #     'product_id': order_line.product_id.id,
              #      'id_name': record.opportunity_id.name+' '+ order_line.name,
             #       'product_qty': order_line.qty,
            #    })

           # record.write({'mrp_production_ids': [(i, work)] }) # Ajoute l'enregistrement many2one au champ many2many
          #  i=i+1
        date_planned_start = date.today()

        for record in self:
            # works = []
            for order_line in record.order_line:
            # for i, order_line in enumerate(record.order_line, start=0):
                if order_line.product_id.type in ['product', 'consu'] and order_line.product_id.is_subcontracted == False:  # Vérifier le type du produit
                    mrp = self.env['mrp.production'].create({
                        'sale_order': self.id,
                        'product_id': order_line.product_id.id,
                        'description_product': order_line.name,
                        'id_name': record.opportunity_id.name + ' ' + order_line.name,
                        'id_name_description': order_line.name,
                        'opportunity':record.opportunity_id.id,
                        'product_qty': order_line.qty,
                        'origin': record.opportunity_id.name,
                        'project_id':project.id,
                    })

                    move_raw_vals = []
                    for option in record.sale_order_nesil_option_ids:
                        service = False  # Initialiser la variable 'service'
                        work_center = False
                        role = False

                        if option.order_line_id.id == order_line.id and option.quantity > 0:
                            # generate line for move_raw_ids in line mrp
                            for raw_material in option:
                                if raw_material.product_id.detailed_type != 'service':
                                    move_raw_vals.append({
                                        'product_id': raw_material.product_id.id,
                                        'product_uom_qty': raw_material.quantity * order_line.qty,
                                        'name': raw_material.product_id.display_name,
                                        'product_uom': raw_material.product_id.uom_id.id,
                                        'raw_material_production_id': mrp.id,
                                    })

                            if option.product_id.categ_id.name == 'Main d\'oeuvre':
                                if option.product_id.name == 'MO USINAGE':
                                    work_center = self.env['mrp.workcenter'].search([('name', '=', 'MO USINAGE')], limit=1)
                                    role = "USINAGE"

                                elif option.product_id.name == 'MO DECOUPE':
                                    work_center = self.env['mrp.workcenter'].search([('name', '=', 'MO DECOUPE')], limit=1)
                                    role = "DECOUPE"

                                elif option.product_id.name == 'MO PLAQUAGE DE CHANTS':
                                    work_center = self.env['mrp.workcenter'].search([('name', '=', 'MO PLAQUAGE DE CHANTS')], limit=1)
                                    role = "PLAQUAGE DE CHANTS"

                                elif option.product_id.name == 'MO ASSEMBLAGE':
                                    work_center = self.env['mrp.workcenter'].search([('name', '=', 'MO ASSEMBLAGE')], limit=1)
                                    role = "ASSEMBLAGE"


                                elif option.product_id.name == 'MO Etude de fabrication':
                                    work_center = self.env['mrp.workcenter'].search([('name', '=', 'MO Etude de fabrication')], limit=1)
                                    role = "ETUDE DE FABRICATION"



                                if work_center :
                                    work_order = self.env['mrp.workorder'].create({
                                        'product_id': option.product_id.id,
                                        'qty_remaining': option.quantity,
                                        'name': option.name,
                                        'workcenter_id': work_center.id,
                                        'product_uom_id':option.product_id.uom_id.id,
                                        'production_id':mrp.id,
                                        'date_planned_start':date_planned_start,
                                        'duration_expected': option.quantity * 60.0,
                                        'duration_expected_hours': option.quantity,
                                        'opportunity':record.opportunity_id.id,
                                        'opportunity_name':record.opportunity_id.name,
                                        'description_of_order_product':option.order_line_id.display_name,
                                        'project_id':project.id,
                                        'sale_order': self.id,
                                        'sale_order_name': self.name,
                                        'order_name': record.opportunity_id.name + ' ' + order_line.name,
                                        'role':role,
                                    })
                                    #work_order.duration_expected_hours = workcenter.duration_expected / 60.0
                                    # works.append(line.task_id.id)
                                    # works.append((0, 0, {'mrp_production_ids': work.id}))
                                # record.write({'mrp_production_ids': works})
                                     # Recherche de la tâche du projet correspondante
                                    task = project.task_ids.filtered(lambda t: work_order.name in t.display_name)
                                    if task:
                                       work_order.task_id = task[0]

                    move_raw_ids = self.env['stock.move'].create(move_raw_vals)
                    mrp.write({'move_raw_ids': [(6, 0, move_raw_ids.ids)]})

        for order in self:
            picking = self.env['stock.picking'].create({
                'partner_id': order.partner_shipping_id.id,
                'location_id': order.warehouse_id.lot_stock_id.id,
                'location_dest_id': order.partner_shipping_id.property_stock_customer.id,
                'origin': order.name,
                'picking_type_id': order.env.ref('stock.picking_type_out').id,
            })

            for option in order.sale_order_nesil_option_ids.filtered(lambda o: o.product_id):
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
    def temp_action_confirm(self):
        for record in self:
            project_id = self.env['project.project'].search([('order_id', '=', self.id)])
            # works = []
            for order_line in record.order_line:
                # for i, order_line in enumerate(record.order_line, start=0):
                if order_line.product_id.type in ['product', 'consu']:  # Vérifier le type du produit
                    mrp = self.env['mrp.production'].create({
                        'sale_order': self.id,
                        'product_id': order_line.product_id.id,
                        'description_product': order_line.name,
                        'id_name': record.opportunity_id.name + ' ' + order_line.name,
                        'id_name_description': order_line.name,
                        'opportunity': record.opportunity_id.id,
                        'product_qty': order_line.qty,
                        'origin': record.opportunity_id.name,
                        'project_id': project_id.id,
                    })

                    move_raw_vals = []
                    for option in record.sale_order_nesil_option_ids:
                        service = False  # Initialiser la variable 'service'
                        work_center = False
                        role = False

                        if option.order_line_id.id == order_line.id and option.quantity > 0:
                            # generate line for move_raw_ids in line mrp
                            for raw_material in option:
                                if raw_material.product_id.detailed_type != 'service':
                                    move_raw_vals.append({
                                        'product_id': raw_material.product_id.id,
                                        'product_uom_qty': raw_material.quantity * order_line.qty,
                                        'name': raw_material.product_id.display_name,
                                        'product_uom': raw_material.product_id.uom_id.id,
                                        'raw_material_production_id': mrp.id,
                                    })

                            if option.product_id.categ_id.name == 'Main d\'oeuvre':
                                if option.product_id.name == 'MO USINAGE':
                                    work_center = self.env['mrp.workcenter'].search([('name', '=', 'MO USINAGE')],
                                                                                    limit=1)
                                    role = "USINAGE"

                                elif option.product_id.name == 'MO DECOUPE':
                                    work_center = self.env['mrp.workcenter'].search([('name', '=', 'MO DECOUPE')],
                                                                                    limit=1)
                                    role = "DECOUPE"

                                elif option.product_id.name == 'MO PLAQUAGE DE CHANTS':
                                    work_center = self.env['mrp.workcenter'].search(
                                        [('name', '=', 'MO PLAQUAGE DE CHANTS')], limit=1)
                                    role = "PLAQUAGE DE CHANTS"

                                elif option.product_id.name == 'MO ASSEMBLAGE':
                                    work_center = self.env['mrp.workcenter'].search([('name', '=', 'MO ASSEMBLAGE')],
                                                                                    limit=1)
                                    role = "ASSEMBLAGE"


                                elif option.product_id.name == 'MO Etude de fabrication':
                                    work_center = self.env['mrp.workcenter'].search(
                                        [('name', '=', 'MO Etude de fabrication')], limit=1)
                                    role = "ETUDE DE FABRICATION"

                                if work_center:
                                    work_order = self.env['mrp.workorder'].create({
                                        'product_id': option.product_id.id,
                                        'qty_remaining': option.quantity,
                                        'name': option.name,
                                        'workcenter_id': work_center.id,
                                        'product_uom_id': option.product_id.uom_id.id,
                                        'production_id': mrp.id,
                                        'date_planned_start': date.today(),
                                        'duration_expected': option.quantity * 60.0,
                                        'duration_expected_hours': option.quantity,
                                        'opportunity': record.opportunity_id.id,
                                        'opportunity_name': record.opportunity_id.name,
                                        'description_of_order_product': option.order_line_id.display_name,
                                        'project_id': project_id.id,
                                        'sale_order': self.id,
                                        'sale_order_name': self.name,
                                        'order_name': record.opportunity_id.name + ' ' + order_line.name,
                                        'role': role,
                                    })
                                    # work_order.duration_expected_hours = workcenter.duration_expected / 60.0
                                    # works.append(line.task_id.id)
                                    # works.append((0, 0, {'mrp_production_ids': work.id}))
                                    # record.write({'mrp_production_ids': works})
                                    # Recherche de la tâche du projet correspondante
                                    task = project_id.task_ids.filtered(lambda t: work_order.name in t.display_name)
                                    if task:
                                        work_order.task_id = task[0]

                    move_raw_ids = self.env['stock.move'].create(move_raw_vals)
                    mrp.write({'move_raw_ids': [(6, 0, move_raw_ids.ids)]})
    def action_view_task_option_ids(self):
        tasks = []
        for line in self.sale_order_nesil_option_ids:
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
    def action_view_manufacturation_orders(self):
        
        domain = [('sale_order', '=', self.id)]
    
        return {
            'domain': domain,
            'name': 'Ordres de fabrication',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }

    
    def _get_task_counts(self):
        tasks = []
        for line in self.sale_order_nesil_option_ids:
            if line.task_id.id:
                tasks.append(line.task_id.id)
        self.task_option_counts = len(tasks)
        
    def _get_project_counts(self):
        self.project_option_counts = len(self.project_options_id)
    
    # @api.depends('mrp_production_ids')
    # def _get_mrp_production_counts(self):
    #     for order in self:
    #         order.mrp_production_counts = len(order.mrp_production_ids)

        
    def action_view_planning(self):
        # button to return to planning
        # use project_options_id
        return self.project_options_id.action_project_forecast_from_project()

    # retroaction sur le champ rfrence_du_dossier
    def retro_x_studio_fields(self):
        # for x_studio_rfrence_du_dossier
        Sale_orders = self.env['sale.order'].sudo().search([])
        for sale_order in Sale_orders:
            if sale_order.x_studio_version_du_devis:
                # if sale_order.state == "sale":
                #     sale_order.action_cancel()
                #     sale_order.action_draft()
                #     sale_order.write({'rfrence_du_dossier':sale_order.x_studio_rfrence_du_dossier.id,'version_du_devis':sale_order.x_studio_version_du_devis})
                #     sale_order.action_confirm()
                # else:
                sale_order.write({'version_du_devis':sale_order.x_studio_version_du_devis})
    
    def action_show_manufactured_order(self):
       
        # Retrieve the Manufacturing Order objects based on the product IDs
        mos = self.env['mrp.production'].search([('sale_order', '=', self.id)])

        
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        action['domain'] = [('id', 'in', mos.ids)]
        return action

    def get_amount_to_pay(self):
        for rec in self:
            return rec.amount_to_pay

  
  
class ProjectProject(models.Model):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    _inherit = 'project.project'

    order_id = fields.Many2one('sale.order', string="Sale Order")
    bon_de_commande = fields.Many2one('sale.order', string="Sale Order")


class Mrp_Production(models.Model):
    _inherit = 'mrp.production'
    
    id_name = fields.Char("Name of Identification")
    id_name_description = fields.Char("Description")
    opportunity = fields.Many2one('crm.lead', string="Dossier")
    sale_order = fields.Many2one('sale.order', string="Devis")
    project_id = fields.Many2one('project.project', string="Projet")
    description_product = fields.Char("Description", readonly=True)


class Work_Order(models.Model):
    _inherit = 'mrp.workorder'
    
    order_name = fields.Char("Nom de l'ordre de travail")
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=False, store=True, domain="[('planning_role_ids.name', '=', role)]")
    duration_expected_hours = fields.Float(string='Durée prévue (Heures)')
    opportunity = fields.Many2one('crm.lead', string="Dossier", readonly=False, store=True, related='sale_order.rfrence_du_dossier') 
    opportunity_name = fields.Char("Nom du dossier",related='opportunity.name')
    description_of_order_product = fields.Char("Description de l'article")
    project_id = fields.Many2one('project.project', string="Projet")
    task_id = fields.Many2one('project.task', string='Task')
    timesheet_id = fields.Many2one('account.analytic.line', string='Timesheet')
    sale_order = fields.Many2one('sale.order', related='production_id.sale_order', string="Sale Order")
    sale_order_name = fields.Char("Numéro du devis", related='sale_order.name')
    role = fields.Char("Rôle")
    user_id = fields.Many2one('res.users', string="User", related='employee_id.user_id')

    # Champs à ajouter pour le filtrage
    user_assigned = fields.Boolean("Assigné à l'utilisateur", compute='_compute_user_assigned', store=True)

    product_description = fields.Char('Description', related="production_id.description_product")

    @api.depends('employee_id')
    def _compute_user_assigned(self):
        for work_order in self:
            work_order.user_assigned = work_order.employee_id.user_id == self.env.user

   
    def button_start(self):
        timesheet = self.env['account.analytic.line'].create({
            'project_id': self.project_id.id,
            'task_id': self.task_id.id,
            'unit_amount': 0,
            'workorder_id': self.id,
            'employee_id': self.employee_id.id,
        })
        if not timesheet:
            raise UserError("Erreur lors de la création de la feuille de temps.")
        else:
            self.timesheet_id = timesheet.id
             # Envoyez la notification interne à l'employé assigné
             # Envoyez la notification interne à l'employé assigné
            self.sale_order.message_post_with_view(
                views_or_xmlid='mail.message_origin_link_view',
                body="Un nouvel ordre de travail a été démarré.",
                partner_ids=[(4, self.employee_id.user_id.partner_id.id)],
            )
                        
        return super(Work_Order, self).button_start()

    def button_pending(self):
        res = super(Work_Order, self).button_pending()
        timesheet = self.env['account.analytic.line'].search([('workorder_id', '=', self.id)], limit=1)
        if timesheet:
            timesheet.write({'unit_amount': self.duration / 60.0, 'employee_id': self.employee_id.id})
        return res

    def button_finish(self):
        res = super(Work_Order, self).button_finish()
        timesheet = self.env['account.analytic.line'].search([('workorder_id', '=', self.id)], limit=1)
        if timesheet:
            timesheet.write({'unit_amount': self.duration / 60.0, 'employee_id': self.employee_id.id})
        return res


    def action_add_time_to_timesheet(self, project, task, seconds):
        if self:
            timesheet_id = self.create({
                'project_id': project,
                'task_id': task,
                'unit_amount': seconds / 3600,
                'workorder_id': self.id,
            })
        return timesheet_id.id
        
    #@api.onchange('employee_id')
    def notification_employee_id(self):
        message = ""
        if self.sale_order:
            self.ensure_one()  # S'assurer qu'il n'y a qu'un seul enregistrement dans self
            notification_ids = [(0, 0, {
                'res_partner_id': self.employee_id.user_id.partner_id.id,
                'notification_type': 'inbox',
            })]
            if self.sale_order_name == False or self.description_of_order_product == False:
                self.description_of_order_product = ""
                message = f"Vous avez été assignée à la tâche {self.name} {self.description_of_order_product}. Le N° du devis est {self.sale_order.name} et le nom du dossier est {self.sale_order.opportunity_id.name}."
            else:
                message = f"Vous avez été assignée à la tâche {self.name} {self.description_of_order_product}. Le N° du devis est {self.sale_order_name} et le nom du dossier est {self.opportunity_name}."

            # Utiliser self.ensure_one() pour poster le message sur l'enregistrement actuel seulement
            self.ensure_one()
            self.sale_order.message_post(body=message, message_type="notification", subtype_xmlid='mail.mt_note', author_id=self.env.user.partner_id.id, notification_ids=notification_ids)
            
    @api.onchange('workcenter_id')
    def update_fields_in_workorder(self):

        if self.workcenter_id :
            self.sale_order = self.production_id.sale_order.id
            self.sale_order_name = self.production_id.sale_order.name
            self.name = self.workcenter_id.display_name
            self.description_of_order_product = self.production_id.id_name_description
            self.opportunity_name = self.production_id.sale_order.opportunity_id.name

        
            if self.workcenter_id.display_name == 'MO USINAGE':
                self.role = "USINAGE"

            elif self.workcenter_id.display_name == 'MO DECOUPE':
                self.role = "DECOUPE"

            elif self.workcenter_id.display_name == 'MO PLAQUAGE DE CHANTS':
                self.role = "PLAQUAGE DE CHANTS"

            elif self.workcenter_id.display_name == 'MO ASSEMBLAGE':
                self.role = "ASSEMBLAGE"

            elif self.workcenter_id.display_name == 'MO Etude de fabrication':
                self.role = "ETUDE DE FABRICATION"

                                                        
class Timesheet_custom(models.Model):
    _inherit = 'account.analytic.line'

    workorder_id = fields.Many2one('mrp.workorder', string='Work Order')

class Account_move(models.Model):
    _inherit = 'account.move'


    def notify_sent_quotation(self):
        """
            send notifications
        """
        #if self.state == 'sent':
        users =  self.env['res.users'].sudo().search([])
        for user in users:
            for group in user.groups_id:
                if group.name == 'Profil Direction':
                    notification_ids = [(0, 0, {
                        'res_partner_id': user.partner_id.id,
                        'notification_type': 'inbox',
                    })]  
                    message = f"La facture {self.name} est envoyée au client."
                    user.partner_id.message_post(body=message, message_type="notification", subtype_xmlid='mail.mt_note', 
                                    author_id=self.env.user.partner_id.id, 
                                    notification_ids=notification_ids)
    
    def action_invoice_print(self):
        res = super(Account_move,self).action_invoice_print()
        
        #if self._context['params']['model'] == 'account.move':
        self.notify_sent_quotation()
                    
        return res
