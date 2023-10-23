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
            return sale_order.rfrence_du_dossier.name
            
            
    def reminder_four_day_bef_date_due(self):
        
        current_date = fields.Datetime.now().date()
        four_days_ago = (current_date - timedelta(days=3))
        
        four_days_ago_begin = datetime(year=four_days_ago.year, month=four_days_ago.month, day=four_days_ago.day,
                        hour=0, minute=0, second=1)
        four_days_ago_end = datetime(year=four_days_ago.year, month=four_days_ago.month, day=four_days_ago.day,
                        hour=23, minute=59, second=59)
        
        invoices = self.search([
            ('state', '=', 'posted'),
            ('invoice_date_due', '>=', four_days_ago_begin),
            ('invoice_date_due', '<=', four_days_ago_end)
        ])
        
        for invoice in invoices:
            if invoice.invoice_origin:
                related_quotations = self.env['sale.order'].search([
                                        ('name', 'in', invoice.invoice_origin.split(', ')),  # Split if multiple references are stored
                                        ('state', '!=', 'cancel'),  # Exclude canceled sale orders if needed
                                    ])
                
                if invoice.invoice_types == 'invoice_of_balance':
                    template = self.env.ref('custom_account.email_template_invoice_reminder')
                    
                    template_context = {
                        "opportunity_name": related_quotations[0].opportunity_id.name,
                        "signature_malika": self.env['res.users'].search([('name', 'ilike', 'malika')])
                    }   
                    template.with_context(proforma=False, **template_context).send_mail(invoice.id, force_send=True)

                            
            
        
    def invoice_reminder(self):
        pass