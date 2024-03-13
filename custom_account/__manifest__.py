# -*- coding: utf-8 -*-
{
    'name': "custom_account",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ranoarison rajoniaina tsiky",
    'website': "https://tsikydev.odoo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'mail',
                'contacts',
                'account',
                'account_accountant',
                'sale',
                'documents',
                'crm',
                'planning'
                ],

    'license': 'AGPL-3',
    
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_move.xml',
        
        'data/mail_template_invoice_reminder.xml',
        'data/notify_reminder_invoice.xml',
        
        # report
        'report/report_invoice_with_payments.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    
    'auto_install': True,
    'sequence': -1,
    'installable': True,
    'application': True,
}
