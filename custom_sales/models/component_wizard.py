from odoo import models, fields, api

class ComponentSelectionWizard(models.TransientModel):
    _name = 'component.selection.wizard'
    _description = 'Component Selection Wizard'

    product_id = fields.Many2one('product.product', 'Nomenclature' , default=lambda self: self._get_default_product(), readonly=True)
    bom_id = fields.Many2one('mrp.bom', string='bom', compute="_compute_default_bom_id")
    order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', default=lambda self: self._get_default_order_line_id(), readonly=True)
    component_ids = fields.Many2many('mrp.bom.line', string='Composants')

    def action_confirm(self):
        product_boms=[]
        for line in self.component_ids:
            product_boms.append({'id': line.product_id.id, 'quantity':line.product_qty})
        order_line = self.order_line_id
        order_line.order_id.generate_bom_order(products=product_boms, order_line=self.order_line_id.id)
        # order_line.write({
        #     'component_ids': [(6, 0, self.component_ids.ids)],
        # })
        return {'type': 'ir.actions.act_window_close'}

    def _get_default_product(self):
        return self._context.get('product_id')
    
    def _get_default_order_line_id(self):
        return self._context.get('order_line_id')
    
    @api.depends('product_id')
    def _compute_default_bom_id(self):
        for record in self:
            if record.product_id:
                bom= self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)])
                
                record.bom_id = bom
            else:
                record.bom_id = False
                