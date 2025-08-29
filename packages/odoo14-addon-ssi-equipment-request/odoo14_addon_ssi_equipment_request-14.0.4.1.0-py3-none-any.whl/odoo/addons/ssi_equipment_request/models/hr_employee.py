# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    equipment_request_route_ids = fields.One2many(
        string="Equipment Request Routes",
        comodel_name="employee.equipment_request_route",
        inverse_name="employee_id",
    )

    def action_create_equipment_request_route(self):
        for record in self.sudo():
            record._create_equipment_request_route()

    def _create_equipment_request_route(self):
        self.ensure_one()
        criteria = [
            ("company_id", "=", self.env.company.id),
        ]
        Warehouse = self.env["stock.warehouse"]
        Route = self.env["employee.equipment_request_route"]
        for warehouse in Warehouse.search(criteria):
            criteria = [
                ("employee_id", "=", self.id),
                ("warehouse_id", "=", warehouse.id),
            ]
            employee_routes = Route.search(criteria)
            if len(employee_routes) == 0:
                employee_route = Route.create(
                    {
                        "warehouse_id": warehouse.id,
                        "employee_id": self.id,
                    }
                )
                employee_route._create_route()
