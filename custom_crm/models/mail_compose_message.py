# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MailComposer(models.TransientModel):
    """ Generic message composition wizard. You may inherit from this wizard
        at model and view levels to provide specific features.

        The behavior of the wizard depends on the composition_mode field:
        - 'comment': post on a record. The wizard is pre-populated via ``get_record_data``
        - 'mass_mail': wizard in mass mailing mode where the mail details can
            contain template placeholders that will be merged with actual data
            before being sent to each recipient.
    """
    _inherit = 'mail.compose.message'
    
    def action_send_mail(self):
        """ 
            Used for action button that do not accept arguments.
            here to change the state of the CRM opportunity
        """
        res = super(MailComposer,self).action_send_mail()
        
        
        if self._context['active_model'] == 'sale.order':
            if self._context['active_id']:
                current_order_id = self.env['sale.order'].search([('id', '=', self._context['active_id'])])
                if current_order_id :
                    current_order_id.opportunity_id.write({'stage_id':2})
                    
        
        return res