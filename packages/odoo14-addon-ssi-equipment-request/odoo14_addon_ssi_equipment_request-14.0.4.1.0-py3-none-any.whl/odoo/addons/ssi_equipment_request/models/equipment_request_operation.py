# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EquipmentRequestOperation(models.Model):
    _name = "equipment_request_operation"
    _description = "Equipment Request Operation"
    _inherit = ["mixin.master_data"]

    assign_policy_id = fields.Many2one(
        comodel_name="equipment_request_policy",
        string="Assign Policy",
        required=False,
        ondelete="restrict",
    )
    return_policy_id = fields.Many2one(
        comodel_name="equipment_request_policy",
        string="Return Policy",
        required=False,
        ondelete="restrict",
    )
