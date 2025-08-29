# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move"]

    equipment_request_line_ids = fields.Many2many(
        string="Equipment Request Line",
        comodel_name="equipment_request_line",
        relation="rel_equipment_request_line_2_stock_move",
        column1="move_id",
        column2="line_id",
    )
