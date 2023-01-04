# -*- coding: utf-8 -*-
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    payment_deadline_options = fields.Selection([
        ('end_month', '30 days end of month '),
        ('month', '30 days  '),
        ('receipt', 'In receipt'),
    ], string='Term options')
    
    @api.onchange('payment_deadline_options')
    def _onchange_payment_deadline_options(self):
        """
            For this, the system will propose 3 options to the user: 
                Option 1: 30 Days End Of Month (example if Invoice 15/10/2022, due date will be 30/11/2022, if Invoice 28/10/2022, due date will always be 30/11/2022) 
                Option 2: 30 Days (example if Invoice 15/10/2022, due date will be 15/11/2022, if Invoice 10/01/2023, due date will be 10/02/2023) 
                Option 3: On receipt 
        """
        for val in self:
            if val.payment_deadline_options:
                if val.payment_deadline_options == "month":
                    val.invoice_date_due = val.create_date + relativedelta(months =+ 1)
                elif val.payment_deadline_options == "end_month":
                    one_month= val.create_date 
                    # move to first next month
                    next_month = one_month.replace(day=28) + timedelta(days=4)

                    # Now move to the second next month
                    next_month = next_month.replace(day=28) + timedelta(days=4)
                    
                    # come back to the first next month's last day
                    res = next_month - timedelta(days=next_month.day)
                    
                    val.invoice_date_due = res
                else:
                    val.invoice_date_due = val.create_date