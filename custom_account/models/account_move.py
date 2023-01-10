from datetime import datetime, date, timedelta

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit='account.move'
    
    invoice_date = fields.Date(default = date.today())
