# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    consumable = fields.Float('consumable')
    qty = fields.Float('Quantity costing', default=1)
    temp_price_unit = fields.Float('temp_price_unit')
    
    is_costed = fields.Boolean('A été chiffré')

    
    @api.onchange('qty', 'temp_price_unit')
    def _onchange_qty(self):
        self.set_price_unit()
        
    def set_price_unit(self):
        self.price_unit = self.qty * self.temp_price_unit


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
            if user_group_id.name == "Profil direction":
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
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'warning',
                            'message': _("Impossible d'appliquer une remise"),
                            'sticky': False,
                            }
                        }
            else:
                self.discount = 0
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Impossible d'appliquer une remise"),
                        'sticky': False,
                        }
                    }
        else:
            self.discount = 0
            return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': _("Impossible d'appliquer une remise"),
                        'sticky': False,
                        }
                    }
           
    def action_costing(self):
        self.ensure_one()
        action = self.env.ref('custom_sales.action_component_selection_wizard').read()[0]
        
        action['context'] = {
            'product_id': self.product_id.id,
            'order_line_id': self.id,
        }
        return action    
   