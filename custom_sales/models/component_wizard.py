from odoo import models, fields, api

class ComponentSelectionWizard(models.TransientModel):
    _name = 'component.selection.wizard'
    _description = 'Component Selection Wizard'

    product_id = fields.Many2one('product.product', 'Nomenclature' , default=lambda self: self._get_default_product(), readonly=True)
    bom_id = fields.Many2one('mrp.bom', string='bom', compute="_compute_default_bom_id")
    order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', default=lambda self: self._get_default_order_line_id(), readonly=True)
    component_ids = fields.Many2many('mrp.bom.line', string='Composants')
    
    option_ids = fields.One2many('stock.quantity.line','wizard_id', string='Composants du tableau de chiffrage')
    
    def action_confirm(self):
        product_boms=[]
        
        for line in self.component_ids:
            product_boms.append({'id': line.product_id.id, 'quantity':line.product_qty})
            
        for line in self.option_ids:
            product_boms.append({'id': line.product_id.id, 'quantity':line.quantity})
        
            
        order_line = self.order_line_id
        order_line.order_id.generate_bom_order(products=product_boms, order_line=self.order_line_id.id)
        
        if not self.order_line_id.is_costed:
            self.order_line_id.is_costed = True
        
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

    
    @api.onchange('order_line_id')
    def _onchange_order_line_id(self):
        bom_lines = self.env['sale.order.option'].search([('order_line_id', '=', self.order_line_id.id)])
        
        option_values = []
        for bom_line in bom_lines:
            option_values.append((0, 0, {
                'product_id': bom_line.product_id.id,
                'quantity': bom_line.quantity,
            }))

        self.option_ids = option_values
                
                

class StockQuantityLine(models.TransientModel):
    _name = 'stock.quantity.line'
    _description = 'Stock Quantity Line'

    wizard_id = fields.Many2one(
        comodel_name='component.selection.wizard',
        string='Wizard',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Article',
        store=True,
        readonly=True
    )
    quantity = fields.Float(string='Quantity')
    