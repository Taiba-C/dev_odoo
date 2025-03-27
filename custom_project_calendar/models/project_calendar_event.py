from odoo import models, fields, api

class ProjectCalendarEvent(models.Model):
    
    _inherit = 'project.calendar.event'
    _description = 'Project Calendar Event'

    name = fields.Char(string="Event Name", required=True)
    date_start = fields.Date(string="Start Date", required=True)
    date_stop = fields.Date(string="End Date", required=True)
    type_of_event = fields.Selection([
        ('main', 'Main Event'),
        ('assembly', 'Montage'),
        ('disassembly', 'Démontage')
    ], string="Event Type", required=True)
    project_id = fields.Many2one('project.project', string="Project", ondelete='cascade', required=True)

    color = fields.Integer(string="Color", compute="_compute_event_color", store=True)


    @api.depends('type_of_event')
    def _compute_event_color(self):
        color_mapping = {
            'main': 2,         # Bleu
            'assembly': 4,     # Vert
            'disassembly': 1,  # Rouge
        }
        for event in self:
            event.color = color_mapping.get(event.type_of_event, 0)  # 0 par défaut