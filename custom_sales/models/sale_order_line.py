# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    consumable = fields.Float('consumable')
    qty = fields.Float('Quantity costing', default=1)
    temp_price_unit = fields.Float('temp_price_unit')

    
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
        allowed_department = 'Direction'
        for order in self:
            user_department = order.env.user.employee_id.department_id.name
            if order.discount > 5 and user_department != allowed_department:
                raise models.ValidationError("Vous n'avez pas l'autorisation requise pour attribuer une remise supérieure à 5%")
            
    def action_costing(self):
        action = self.env.ref('custom_sales.action_component_selection_wizard').read()[0]
        
        action['context'] = {
            'product_id': self.product_id.id,
            'order_line_id': self.id,
        }
        return action    
   