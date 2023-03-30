from datetime import datetime, date, timedelta

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit='account.move'
    
    invoice_date = fields.Date(default = date.today())

    invoice_types = fields.Selection([
        ('down_payment_invoice', 'Down payment invoice'),
        ('invoice_of_balance', 'Invoice of Balance')
    ], string='Invoice types', readonly = True)
            
    def get_order_source(self, source):
        if source:
            sale_order = self.env['sale.order'].search([('name', '=', source)])
            return sale_order.x_studio_rfrence_du_dossier.name
            