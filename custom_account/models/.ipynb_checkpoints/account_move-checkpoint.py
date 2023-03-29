from datetime import datetime, date, timedelta

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit='account.move'
    
    invoice_date = fields.Date(default = date.today())

    invoice_types = fields.Selection([
        ('down_payment_invoice', 'Down payment invoice'),
        ('invoice_of_balance', 'Invoice of Balance')
    ], string='Invoice types', readonly = True)
            