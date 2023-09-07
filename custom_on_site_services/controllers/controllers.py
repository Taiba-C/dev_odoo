# -*- coding: utf-8 -*-
# from odoo import http


# class CustomOnSiteServices(http.Controller):
#     @http.route('/custom_on_site_services/custom_on_site_services', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_on_site_services/custom_on_site_services/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_on_site_services.listing', {
#             'root': '/custom_on_site_services/custom_on_site_services',
#             'objects': http.request.env['custom_on_site_services.custom_on_site_services'].search([]),
#         })

#     @http.route('/custom_on_site_services/custom_on_site_services/objects/<model("custom_on_site_services.custom_on_site_services"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_on_site_services.object', {
#             'object': obj
#         })
