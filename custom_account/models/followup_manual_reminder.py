from odoo import api, fields, models, Command

class FollowupManualReminder(models.TransientModel):
    _inherit = 'account_followup.manual_reminder'

    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        template_id = self.env['mail.template'].search([('name','=','Payment Reminder')]).id
        if template_id:
            defaults['template_id'] = template_id
        return defaults