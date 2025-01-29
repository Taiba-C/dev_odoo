{
    'name': 'Custom Project Calendar',
    'version': '1.0',
    'summary': 'Module to display project calendar events',
    'description': 'This module provides a calendar view for project events (main, assembly, disassembly).',
    'author': 'Your Name',
    'category': 'Project Management',
    'depends': ['project','custom_project','custom_crm'],
    'images': ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_calendar_event_views.xml',
    ],
    'installable': True,
    'application': True,
}
