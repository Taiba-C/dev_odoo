# -*- coding: utf-8 -*-
{
    'name': "saleOrder_inInvoice_field_module",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Axeneo",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    #'depends': ['base'],
    #'depends': ['base','account'],
    'depends': ['base','account','calendar'],
    'test': ['tests/test_calendar.py'], # Spécifier le chemin vers votre test personnalisé
    'installable': True,
    'auto_install': False,
    'sequence': 10, # Définir la priorité de votre module
    
    'license': 'LGPL-3',
    
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
