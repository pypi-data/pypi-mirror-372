# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EquipmentRequestType(models.Model):
    _name = "equipment_request_type"
    _description = "Equipment Request Type"
    _inherit = [
        "mixin.master_data",
        "mixin.product_category_m2o_configurator",
        "mixin.product_product_m2o_configurator",
    ]

    _product_category_m2o_configurator_insert_form_element_ok = True
    _product_category_m2o_configurator_form_xpath = "//page[@name='product']"
    _product_product_m2o_configurator_insert_form_element_ok = True
    _product_product_m2o_configurator_form_xpath = "//page[@name='product']"

    product_category_ids = fields.Many2many(
        relation="rel_equipment_request_type_2_product_category",
        column1="type_id",
        column2="category_id",
    )
    product_ids = fields.Many2many(
        relation="rel_equipment_request_type_2_product_product",
        column1="type_id",
        column2="product_id",
    )
