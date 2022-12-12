# -*- coding: utf-8 -*-
# from odoo import http


# class CustomAccount(http.Controller):
#     @http.route('/custom_account/custom_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_account/custom_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_account.listing', {
#             'root': '/custom_account/custom_account',
#             'objects': http.request.env['custom_account.custom_account'].search([]),
#         })

#     @http.route('/custom_account/custom_account/objects/<model("custom_account.custom_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_account.object', {
#             'object': obj
#         })
