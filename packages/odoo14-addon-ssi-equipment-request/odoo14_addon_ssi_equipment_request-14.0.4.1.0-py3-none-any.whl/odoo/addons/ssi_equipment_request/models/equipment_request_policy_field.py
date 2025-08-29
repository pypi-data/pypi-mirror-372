# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EquipmentRequestPolicyField(models.Model):
    _name = "equipment_request_policy_field"
    _description = "Equipment Request Policy Field"
    _inherit = ["mixin.master_data"]
