# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, fields, models
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _name = "stock.warehouse"
    _inherit = ["stock.warehouse"]

    equipment_request_route_ids = fields.One2many(
        string="Equipment Request Routes",
        comodel_name="employee.equipment_request_route",
        inverse_name="warehouse_id",
    )

    def _prepare_equipment_request_route(self, employee):
        self.ensure_one()
        route_name = "%s - %s" % (self.name, employee.name)
        return {
            "name": route_name,
            "product_selectable": False,
            "product_categ_selectable": False,
            "warehouse_selectable": True,
            "warehouse_ids": [(4, self.id)],
        }

    def _create_equipment_request_assignment_rule(self, employee, route):
        self.ensure_one()
        Rule = self.env["stock.rule"]
        data = self._prepare_equipment_request_assignment_rule(employee, route)
        Rule.create(data)

    def _create_equipment_request_return_rule(self, employee, route):
        self.ensure_one()
        Rule = self.env["stock.rule"]
        data = self._prepare_equipment_request_return_rule(employee, route)
        Rule.create(data)

    def _prepare_equipment_request_assignment_rule(self, employee, route):
        self.ensure_one()
        category = self.env.ref("ssi_stock_equipment_operation.picking_category_eqo")
        criteria = [
            ("category_id", "=", category.id),
            ("warehouse_id", "=", self.id),
        ]
        picking_types = self.env["stock.picking.type"].search(criteria)
        if len(picking_types) == 0:
            error_message = _(
                """
            Context: Create equipment request route
            Database ID: %s
            Problem: Warehouse does not have equipment out picking type
            Solution: Create equipment out for said warehouse
            """
                % (self.id)
            )
            raise UserError(error_message)

        picking_type = picking_types[0]

        return {
            "route_id": route.id,
            "name": _("Assignment"),
            "action": "pull",
            "picking_type_id": picking_type.id,
            "location_src_id": employee.current_warehouse_id.lot_stock_id.id,
            "location_id": employee.location_id.id,
        }

    def _prepare_equipment_request_return_rule(self, employee, route):
        self.ensure_one()
        category = self.env.ref("ssi_stock_equipment_operation.picking_category_eqi")
        criteria = [
            ("category_id", "=", category.id),
            ("warehouse_id", "=", self.id),
        ]
        picking_types = self.env["stock.picking.type"].search(criteria)
        if len(picking_types) == 0:
            error_message = _(
                """
            Context: Create equipment request route
            Database ID: %s
            Problem: Warehouse does not have equipment in picking type
            Solution: Create equipment in for said warehouse
            """
                % (self.id)
            )
            raise UserError(error_message)

        picking_type = picking_types[0]

        return {
            "route_id": route.id,
            "name": _("Return"),
            "action": "pull",
            "picking_type_id": picking_type.id,
            "location_id": employee.current_warehouse_id.lot_stock_id.id,
            "location_src_id": employee.location_id.id,
        }
