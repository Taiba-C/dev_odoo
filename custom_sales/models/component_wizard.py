from odoo import models, fields, api


class ComponentSelectionWizard(models.TransientModel):
    _name = 'component.selection.wizard'
    _description = 'Component Selection Wizard'

    product_id = fields.Many2one('product.product', 'Nomenclature', default=lambda self: self._get_default_product(),
                           readonly=True)
    product_image = fields.Binary(string='Product Image', related='product_id.image_1920')

    bom_id = fields.Many2one('mrp.bom', string='bom', compute="_compute_default_bom_id")
    option_line_id = fields.Many2one('sale.order.option', string='Order option', ondelete="cascade", copy=True)
    order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line',
                                    default=lambda self: self._get_default_order_line_id(), readonly=True)
    component_ids = fields.Many2many('mrp.bom.line', string='Composants')
    

    option_ids = fields.One2many('stock.quantity.line', 'wizard_id', string='Composants du tableau de chiffrage',
                                 default=lambda self: self._get_default_option_ids())

    def action_confirm(self):
        product_boms = self.set_product_boms()
        if len(product_boms) > 0:
            order_line = self.order_line_id
            order_line.order_id.generate_bom_order(products=product_boms, order_line=self.order_line_id.id,option_line=None)
        else:
            self.order_line_id.temp_price_unit = 0
        return {'type': 'ir.actions.act_window_close'}
    
    def set_product_boms(self):
        product_boms = []

        order_options = self.env['sale.order.option.nesil'].search([('order_line_id', '=', self.order_line_id.id)])
        order_options.unlink()

        for line in self.option_ids:
            if line.selected_product:
                product_boms.append({'id': line.product_id.id, 'quantity': line.quantity})
        return product_boms

    def _get_default_product(self):
        return self._context.get('product_id')

    def _get_default_order_line_id(self):
        return self._context.get('order_line_id')

    @api.depends('product_id')
    def _compute_default_bom_id(self):
        for record in self:
            if record.product_id:
                bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)])

                record.bom_id = bom
            else:
                record.bom_id = False

    def _get_default_option_ids(self):
        ctx_mrp_bom_line = self.env.context.get('mrp_bom_line')
        mrp_bom_line = self._bom_line_without_duplicated_product(ctx_mrp_bom_line)
        order_line = self.env.context.get('order_line_id')
        lines = []
        options = self.env['sale.order.option.nesil'].search([('order_line_id', '=', order_line)])
        products = []
        lst_options = []

        for option in options:
            if option.product_id.id not in products:
                products.append(option.product_id.id)
                lst_options.append(option)
                

        options_info = []
        if len(options) > 0:
            for option in lst_options:
                options_info.append({
                    'product_id': option.product_id.id,
                    'quantity': option.quantity,
                })

        for bom in mrp_bom_line:
            bom_lines = bom
            for bom_line in bom_lines:
                if len(options) == 0:
                    lines.append((0, 0, {
                        'product_id': bom_line.product_id.id,
                        'quantity': bom_line.product_qty,
                        'selected_product': True if bom_line.product_qty > 0 else False,

                        # Add other fields as needed
                    }))
                else:
                    product_options_ids = [x['product_id'] for x in options_info]

                    if bom_line.product_id.id in product_options_ids:
                        for line in options_info:
                            if bom_line.product_id.id == line['product_id'] and bom_line.product_qty != line['quantity'] and bom_line.product_id.active == True:
                                lines.append((0, 0, {
                                        'product_id': line['product_id'],
                                        'quantity': line['quantity'],
                                        'updated': True,
                                        'selected_product': True,
                                        # Add other fields as needed
                                    }))
                            elif bom_line.product_id.id == line['product_id'] and bom_line.product_id.active == True:
                                lines.append((0, 0, {
                                    'product_id': line['product_id'],
                                    'quantity': line['quantity'],
                                    'selected_product': True,
                                    'updated': True,
                                    # Add other fields as needed
                                }))
                    elif bom_line.product_id.active == True:
                        lines.append((0, 0, {
                            'product_id': bom_line.product_id.id,
                            'quantity': bom_line.product_qty,
                            # Add other fields as needed
                        }))

        return lines
    
    def _bom_line_without_duplicated_product(self, bom_line_ids):
        bom_lines = self.env['mrp.bom.line'].search([('id', 'in', bom_line_ids)])
        result = []
        products = []
        for line in bom_lines:
            if line.product_id.id not in products:
                products.append(line.product_id.id)
                result.append(line)

        return result


class StockQuantityLine(models.TransientModel):
    _name = 'stock.quantity.line'
    _description = 'Stock Quantity Line'

    wizard_id = fields.Many2one(
        comodel_name='component.selection.wizard',
        string='Wizard',
    )

    wizard_id_option = fields.Many2one(
        comodel_name='component.selection.wizard.option',
        string='Wizard option',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Article',
    )
    product_id_visible = fields.Many2one(
        comodel_name='product.product',
        string='Article',
        compute="_compute_product_id_visible",
        readonly=True,
        store=True
    )

    product_image = fields.Binary('Photo', related="product_id_visible.image_1920")
    quantity = fields.Float(string='Quantité')

    updated = fields.Boolean("Modifié")

    selected_product = fields.Boolean('Selection')

    @api.depends('product_id')
    def _compute_product_id_visible(self):
        for record in self:
            record.product_id_visible = record.product_id

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if not self.selected_product and self.quantity > 0:
            self.selected_product = True
        elif self.selected_product and self.quantity == 0:
            self.selected_product = False