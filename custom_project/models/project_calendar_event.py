# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProjectCalendarEvent(models.Model):
    _inherit = 'project.calendar.event'
    _description = 'Project Calendar Event'

    name = fields.Char(string="Event Name", required=True)
    date_start = fields.Datetime(string="Start Date", required=True)
    date_stop = fields.Datetime(string="End Date", required=True)
    color = fields.Integer(string="Color", compute="_compute_event_color", store=True, default=0)
    type_of_event = fields.Selection([
        ('main', 'Main Event'),
        ('assembly', 'Montage'),
        ('disassembly', 'Démontage')
    ], string="Event Type", required=True)
    project_id = fields.Many2one(
        'project.project', string="Project",
        ondelete='cascade', required=True
    )



#    @api.depends('type_of_event')
#    def _compute_event_color(self):
#        color_mapping = {
#            'main': 2,         # Bleu
#            'assembly': 4,     # Vert
#            'disassembly': 1,  # Rouge
#        }
#        for event in self:
#            event.color = color_mapping.get(event.type_of_event, 0)  # 0 par défaut
#
#    @api.model
#    def create_event_for_project(self, project):
#        """
#        Creates events for a given project, including the main event,
#        assembly, and disassembly, if applicable.
#        """
#        events = []
#        if project.date_start and project.date:
#            events.append(self.create({
#                'name': f"{project.name} - Main Event",
#                'date_start': project.date_start,
#                'date_stop': project.date,
#                'type_of_event': 'main',
#                'project_id': project.id,
#            }))
#
#        if project.assembly_date_start and project.assembly_date_end:
#            events.append(self.create({
#                'name': f"{project.name} - Montage",
#                'date_start': project.assembly_date_start,
#                'date_stop': project.assembly_date_end,
#                'type_of_event': 'assembly',
#                'project_id': project.id,
#            }))
#
#        if project.disassembly_date_start and project.disassembly_date_end:
#            events.append(self.create({
#                'name': f"{project.name} - Démontage",
#                'date_start': project.disassembly_date_start,
#                'date_stop': project.disassembly_date_end,
#                'type_of_event': 'disassembly',
#                'project_id': project.id,
#            }))
#
#        return events
#
#    @api.model
#    def sync_project_events(self):
#        """
#        Synchronizes events for all projects to ensure the calendar is up to date.
#        """
#        projects = self.env['project.project'].search([])
#        for project in projects:
#            self.search([('project_id', '=', project.id)]).unlink()  # Remove existing events
#            self.create_event_for_project(project)  # Recreate events
