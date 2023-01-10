# -*- coding: utf-8 -*-
# from odoo import http


# class CustomDocument(http.Controller):
#     @http.route('/custom_document/custom_document', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_document/custom_document/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_document.listing', {
#             'root': '/custom_document/custom_document',
#             'objects': http.request.env['custom_document.custom_document'].search([]),
#         })

#     @http.route('/custom_document/custom_document/objects/<model("custom_document.custom_document"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_document.object', {
#             'object': obj
#         })
