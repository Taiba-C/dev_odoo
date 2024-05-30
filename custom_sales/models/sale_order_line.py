# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    consumable = fields.Float('consumable')
    qty = fields.Float('Quantity costing', default=1)
    temp_price_unit = fields.Float('temp_price_unit', store=True)
    partner_id = fields.Many2one('res.partner', string='Sous traitant')

    action_on_order_line = fields.Selection([
        ('costed', 'Chiffrée'),
        ('option', 'Options'),
        ('subcontracted', 'Sous-traité'),
    ], string='Traitement', compute="_compute_action_on_order_line")
    
    #is_subcontracted = fields.Boolean('Produit sous-traité',related='product_template_id.is_subcontracted')

    def _compute_action_on_order_line(self):
        for record in self:
            costed_product = [costed.order_line_id.id for costed in record.order_id.sale_order_nesil_option_ids]
            subcontracted_product = [subcontract.order_line_id.id for subcontract in record.order_id.sale_order_subcontractor_ids]
            if record.id in costed_product:
                record.action_on_order_line = 'costed'
            elif record.id in subcontracted_product:
                record.action_on_order_line = 'subcontracted'
            else:
                record.action_on_order_line = None

    
    @api.onchange('qty','temp_price_unit')
    def _onchange_qty(self):
        self.product_uom_qty = self.qty
        self.set_price_unit()
    
    def set_price_unit(self):
        self.price_unit = self.temp_price_unit


    @api.model
    def action_order(self):
        current_employee_id = self.env.user.employee_id.id
        domain = [('employee_id', '=', current_employee_id)]
        action = {
            'name': 'Mes Ordres de travail',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.workorder',
            'view_mode': 'tree,form',
            'domain': domain,
        }
        return action

    @api.onchange('discount')
    def _check_discount_limit(self):
        is_user_allowed = False
        for user_group_id in self.env.user.groups_id:
            if user_group_id.name == "Profil Direction":
                is_user_allowed = True
        discount = self.env['nesil.remise'].sudo().search([])
        if discount:
            if discount.ensure_one():
                if discount.active:
                    for order_line in self:
                        if order_line.discount > discount.taux_de_remise*100 and not is_user_allowed:
                            raise models.ValidationError("Vous n'avez pas l'autorisation requise pour attribuer une remise supérieure à "+str(discount.taux_de_remise*100)+"%")
                            
                else:
                    self.discount = 0
            else:
                self.discount = 0
        else:
            self.discount = 0
           
    def action_costing(self):
        self.ensure_one()
        action = self.env.ref('custom_sales.action_component_selection_wizard').read()[0]

        mrp_bom = self.env['mrp.bom'].sudo().search([('product_tmpl_id', '=', self.product_template_id.id)])
        mrp_bom_line = self.env['mrp.bom.line'].sudo().search([('bom_id', '=', mrp_bom.id)]).ids
        if mrp_bom and mrp_bom_line:
            action['context'] = {
                'product_id': self.product_id.id,
                'order_line_id': self.id,
                'mrp_bom_line': mrp_bom_line,
            }
            return action    
        else:
            raise models.ValidationError(f"Veuillez verifier la nomenclature de {self.product_template_id.name}")

    
    def _get_values_to_add_to_nesil_option(self):
            self.ensure_one()
            return {
                #'product_uom_qty': self.quantity,
                'order_id':self.order_id.id,
                'product_id':self.product_id.id,
                #'line_id':self.line_id.id,
                'name':self.name,
                'quantity':self.qty,
                #'uom_id':self.uom_id.id,
                'product_uom_category_id':self.product_uom_category_id.id,
                'price_unit':self.price_unit,
                'discount':self.discount,
                #'is_present':self.is_present,
                #'parent_id':self.parent_id.id,
                #'purchase_price':self.purchase_price,
                # 'margin':self.margin,
                # 'margin_product':self.margin_product,
                # 'margin_percent':self.margin_percent,
                # 'total_purchase_price':self.total_purchase_price,
                # 'order_line_id':self.order_line_id.id,
                # 'nomenclature_name':self.nomenclature_name,
                # 'order_id':self.order_id.id
            }
        
    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'temp_price_unit')
    def _compute_price_unit(self):
        # re write compute price unit because it must retake temp price unit 
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if line.qty_invoiced > 0:
                continue
            if not line.product_uom or not line.product_id:
                line.price_unit = 0.0
            else:
                price = line.with_company(line.company_id)._get_display_price()
                
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=line.temp_price_unit,
                    product_currency=line.currency_id
                )
    # def button_add_to_nesil_option(self):
    #     self.button_add_to_option()

    # def button_add_to_option(self):
    #     self.ensure_one()

    #     sale_order = self.order_id
    #     is_in_options = False
    #     for record in self.order_id.sale_order_option_ids:
    #         if record.product_id.id == self.product_id.id:
    #             is_in_options = True
    #     if sale_order.state not in ['draft', 'sent']:
    #         raise UserError(_('You cannot add options to a confirmed order.'))
    #     if is_in_options == False:
    #         values = self._get_values_to_add_to_nesil_option()
    #         self.env['sale.order.option'].create(values)
    #         self.unlink()
    #     else:
    #         self.unlink()

        #self.write({'line_id': order_line.id})
        # if sale_order:
        #     sale_order.add_option_to_order_with_taxcloud()
    @api.onchange('product_template_id')
    def _onchange_product_template_id_costed(self):
        if self.product_template_id:
            order_option_nesil_ids = set(
                [line.order_line_id.id for line in self.order_id.sale_order_nesil_option_ids])
            
            if self._origin.id in order_option_nesil_ids:
                raise UserError(
                    _('Vous ne pouvez pas changer le produit d\'une ligne de commande qui a déjà été chiffrée.'))

            else:
                self.consumable = 0