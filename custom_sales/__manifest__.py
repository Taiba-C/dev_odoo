# -*- coding: utf-8 -*-
{
    'name': "custom_sales",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ranoarison rajoniaina tsiky",
    'website': "https://tsikydev.odoo.com/",
    'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'sale',
                'sale_management',
                'product',
                'industry_fsm_sale',
                'custom_stock',
                'account_payment',
                'custom_manufacturing',
                'planning',
                'crm',
                ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/sale_order.xml',
        'views/sale_management.xml',
        'views/reference_quote.xml',
        'views/quotation_expired.xml',
        # scheduled tasks
        'views/data/notify_quotation.xml',
        'views/planning_slot_gantt.xml',
        'views/sale_order_portal_content_custom.xml',
        'views/mrp_planning_view.xml',
        'views/view_workorder_tree.xml',
        # report
        # 'report/ir_actions_report_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
