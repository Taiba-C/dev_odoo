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
            
            
    def reminder_invoice_of_balance_before(self):
        """
            FACTURE DE SOLDE RAPPEL 1 :  4 JOUR AVANT LA DATE D’ECHEANCE 
        """
        current_date = fields.Datetime.now().date()
        date_before_date_due = (current_date + timedelta(days=4))
        
        
        date_before_date_due_begin = datetime(year=date_before_date_due.year, month=date_before_date_due.month, day=date_before_date_due.day,
                        hour=0, minute=0, second=1)
        date_before_date_due_end = datetime(year=date_before_date_due.year, month=date_before_date_due.month, day=date_before_date_due.day,
                        hour=23, minute=59, second=59)
        
        invoices = self.search([
            ('state', '=', 'posted'),
            ('invoice_date_due', '>=', date_before_date_due_begin),
            ('invoice_date_due', '<=', date_before_date_due_end)
        ])
        print(date_before_date_due)
        print(invoices)
        
        for invoice in invoices:
            if invoice.invoice_origin:
                related_quotations = self.env['sale.order'].search([
                                        ('name', 'in', invoice.invoice_origin.split(', ')),  # Split if multiple references are stored
                                        ('state', '!=', 'cancel'),  # Exclude canceled sale orders if needed
                                    ])
                
                if invoice.invoice_types == 'invoice_of_balance':
                    template = self.env.ref('custom_account.email_template_invoice_reminder_before')
                    
                    template_context = {
                        "opportunity_name": related_quotations[0].opportunity_id.name,
                        "signature_malika": self.env['res.users'].search([('name', 'ilike', 'malika')])
                    }   
                    
                    template.with_context(proforma=False, **template_context).send_mail(invoice.id, force_send=True)

    def reminder_invoice_of_balance_later(self):
        """
            Facture DE SOLDE RELANCE 1 : 4 JOURS APRES LA DATE D’ECHEANCE
        """
        current_date = fields.Datetime.now().date()
        date_later_date_due = (current_date - timedelta(days=4))
    
    
        date_later_date_due_begin = datetime(year=date_later_date_due.year, month=date_later_date_due.month, day=date_later_date_due.day,
                        hour=0, minute=0, second=1)
        date_later_date_due_end = datetime(year=date_later_date_due.year, month=date_later_date_due.month, day=date_later_date_due.day,
                        hour=23, minute=59, second=59)
        
        invoices = self.search([
            ('state', '=', 'posted'),
            ('invoice_date_due', '>=', date_later_date_due_begin),
            ('invoice_date_due', '<=', date_later_date_due_end)
        ])
        print(date_later_date_due)
        print(invoices)
        for invoice in invoices:
            if invoice.invoice_origin:
                related_quotations = self.env['sale.order'].search([
                                        ('name', 'in', invoice.invoice_origin.split(', ')),  # Split if multiple references are stored
                                        ('state', '!=', 'cancel'),  # Exclude canceled sale orders if needed
                                    ])
                
                if invoice.invoice_types == 'invoice_of_balance':
                    template = self.env.ref('custom_account.email_template_invoice_reminder_later')
                    
                    template_context = {
                        "opportunity_name": related_quotations[0].opportunity_id.name,
                        "signature_malika": self.env['res.users'].search([('name', 'ilike', 'malika')])
                    }   
                    
                    template.with_context(proforma=False, **template_context).send_mail(invoice.id, force_send=True)

                            
            
        
    def invoice_reminder(self):
        self.reminder_invoice_of_balance_before()
        self.reminder_invoice_of_balance_later()