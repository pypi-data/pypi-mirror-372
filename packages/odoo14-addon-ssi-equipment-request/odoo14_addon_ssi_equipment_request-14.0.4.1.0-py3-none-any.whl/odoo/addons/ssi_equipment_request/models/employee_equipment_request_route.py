# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, fields, models
from odoo.exceptions import UserError


class EmployeeEquipmentRequestRoute(models.Model):
    _name = "employee.equipment_request_route"
    _description = "Employee - Equipment Request Route"

    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        required=True,
        ondelete="cascade",
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        required=True,
        ondelete="restrict",
    )
    route_id = fields.Many2one(
        string="Route",
        comodel_name="stock.location.route",
        required=False,
        ondelete="restrict",
    )

    def _create_route(self):
        self.ensure_one()
        Route = self.env["stock.location.route"]
        data = self._prepare_route()
        route = Route.create(data)
        self.write(
            {
                "route_id": route.id,
            }
        )
        self._create_equipment_request_assignment_rule()
        self._create_equipment_request_return_rule()

    def _prepare_route(self):
        self.ensure_one()
        route_name = "%s - %s" % (self.warehouse_id.name, self.employee_id.name)
        return {
            "name": route_name,
            "product_selectable": False,
            "product_categ_selectable": False,
            "warehouse_selectable": True,
            "warehouse_ids": [(4, self.warehouse_id.id)],
        }

    def _create_equipment_request_assignment_rule(self):
        self.ensure_one()
        Rule = self.env["stock.rule"]
        data = self._prepare_equipment_request_assignment_rule()
        Rule.create(data)

    def _create_equipment_request_return_rule(self):
        self.ensure_one()
        Rule = self.env["stock.rule"]
        data = self._prepare_equipment_request_return_rule()
        Rule.create(data)

    def _prepare_equipment_request_assignment_rule(self):
        self.ensure_one()
        category = self.env.ref("ssi_stock_equipment_operation.picking_category_eqo")
        criteria = [
            ("category_id", "=", category.id),
            ("warehouse_id", "=", self.warehouse_id.id),
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
                % (self.employee_id.id)
            )
            raise UserError(error_message)

        picking_type = picking_types[0]

        return {
            "route_id": self.route_id.id,
            "name": _("Assignment"),
            "action": "pull",
            "picking_type_id": picking_type.id,
            "location_src_id": self.employee_id.current_warehouse_id.lot_stock_id.id,
            "location_id": self.employee_id.location_id.id,
        }

    def _prepare_equipment_request_return_rule(self):
        self.ensure_one()
        category = self.env.ref("ssi_stock_equipment_operation.picking_category_eqi")
        criteria = [
            ("category_id", "=", category.id),
            ("warehouse_id", "=", self.warehouse_id.id),
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
                % (self.employee_id.id)
            )
            raise UserError(error_message)

        picking_type = picking_types[0]

        return {
            "route_id": self.route_id.id,
            "name": _("Return"),
            "action": "pull",
            "picking_type_id": picking_type.id,
            "location_id": self.employee_id.current_warehouse_id.lot_stock_id.id,
            "location_src_id": self.employee_id.location_id.id,
        }
