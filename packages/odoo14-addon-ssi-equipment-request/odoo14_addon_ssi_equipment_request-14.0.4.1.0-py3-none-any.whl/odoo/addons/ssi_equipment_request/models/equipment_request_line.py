# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class EquipmentRequestLIne(models.Model):
    _name = "equipment_request_line"
    _description = "Equipment Request Line"
    _inherit = [
        "mixin.product_line_price",
    ]

    request_id = fields.Many2one(
        comodel_name="equipment_request",
        string="# Equipment Request",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Sequence", required=True, default=10)
    stock_move_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Stock Moves",
        relation="rel_equipment_request_line_2_stock_move",
        column1="line_id",
        column2="move_id",
        copy=False,
    )
    product_id = fields.Many2one(
        required=False,
    )
    uom_id = fields.Many2one(
        required=False,
    )

    # Assignment Fields
    qty_to_assign = fields.Float(
        string="Qty to Assign",
        compute="_compute_qty_to_assign",
        store=True,
    )
    qty_assigning = fields.Float(
        string="Qty Assigning",
        compute="_compute_qty_assigning",
        store=True,
    )
    qty_assigned = fields.Float(
        string="Qty Assigned",
        compute="_compute_qty_assigned",
        store=True,
    )
    need_assignment = fields.Boolean(
        string="Need Assignment",
        related="request_id.need_assignment",
        store=True,
    )
    percent_assignment = fields.Float(
        string="Percent Assignment",
        compute="_compute_percent_assignment",
        store=True,
    )
    assign_complete = fields.Boolean(
        string="Assignment Complete",
        compute="_compute_assign_complete",
        store=True,
    )

    # Return
    qty_to_return = fields.Float(
        string="Qty to Return",
        compute="_compute_qty_to_return",
        store=True,
    )
    qty_returning = fields.Float(
        string="Qty Returning",
        compute="_compute_qty_returning",
        store=True,
    )
    qty_returned = fields.Float(
        string="Qty Returned",
        compute="_compute_qty_returned",
        store=True,
    )
    need_return = fields.Boolean(
        string="Need Return",
        related="request_id.need_return",
        store=True,
    )
    percent_return = fields.Float(
        string="Percent Return",
        compute="_compute_percent_return",
        store=True,
    )
    return_complete = fields.Boolean(
        string="Return Complete",
        compute="_compute_return_complete",
        store=True,
    )

    @api.model
    def _get_qty_field_trigger(self):
        result = [
            "request_id",
            "request_id.operation_id",
            "uom_quantity",
            "qty_assigned",
            "qty_returned",
        ]
        return result

    @api.depends(lambda self: self._get_qty_field_trigger())
    def _compute_qty_to_assign(self):
        for record in self:
            result = 0.0
            if (
                record.request_id.operation_id
                and record.request_id.operation_id.assign_policy_id
            ):
                policy = record.request_id.operation_id.assign_policy_id
                result = policy._compute_quantity(record)
            record.qty_to_assign = result

    @api.depends(
        "need_assignment",
        "percent_assignment",
    )
    def _compute_assign_complete(self):
        for record in self:
            result = False
            if (
                record.need_assignment and record.percent_assignment == 1.0
            ) or not record.need_assignment:
                result = True
            record.assign_complete = result

    @api.depends(
        "need_return",
        "percent_return",
    )
    def _compute_return_complete(self):
        for record in self:
            result = False
            if (
                record.need_return and record.percent_return == 1.0
            ) or not record.need_return:
                result = True
            record.return_complete = result

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
        "stock_move_ids.picking_id",
        "stock_move_ids.picking_id.picking_type_category_id",
        "request_id.state",
    )
    def _compute_qty_assigning(self):
        for record in self:
            states = [
                "draft",
                "confirmed",
                "partially_available",
                "assigned",
            ]
            picking_type_category = self.env.ref(
                "ssi_stock_equipment_operation.picking_category_eqo"
            )
            record.qty_assigning = record._get_move_qty(states, picking_type_category)

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
        "stock_move_ids.picking_id",
        "stock_move_ids.picking_id.picking_type_category_id",
        "request_id.state",
    )
    def _compute_qty_assigned(self):
        for record in self:
            states = [
                "done",
            ]
            picking_type_category = self.env.ref(
                "ssi_stock_equipment_operation.picking_category_eqo"
            )
            record.qty_assigned = record._get_move_qty(states, picking_type_category)

    @api.depends(lambda self: self._get_qty_field_trigger())
    def _compute_qty_to_return(self):
        for record in self:
            result = 0.0
            if (
                record.request_id.operation_id
                and record.request_id.operation_id.return_policy_id
            ):
                policy = record.request_id.operation_id.return_policy_id
                result = policy._compute_quantity(record)
            record.qty_to_return = result

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
        "stock_move_ids.picking_id",
        "stock_move_ids.picking_id.picking_type_category_id",
        "request_id.state",
    )
    def _compute_qty_returning(self):
        for record in self:
            states = [
                "draft",
                "confirmed",
                "partially_available",
                "assigned",
            ]
            picking_type_category = self.env.ref(
                "ssi_stock_equipment_operation.picking_category_eqi"
            )
            record.qty_returning = record._get_move_qty(states, picking_type_category)

    @api.depends(
        "stock_move_ids",
        "stock_move_ids.state",
        "stock_move_ids.product_qty",
        "stock_move_ids.picking_id",
        "stock_move_ids.picking_id.picking_type_category_id",
        "request_id.state",
    )
    def _compute_qty_returned(self):
        for record in self:
            states = [
                "done",
            ]
            picking_type_category = self.env.ref(
                "ssi_stock_equipment_operation.picking_category_eqi"
            )
            record.qty_returned = record._get_move_qty(states, picking_type_category)

    @api.depends(
        "uom_quantity",
        "qty_assigned",
    )
    def _compute_percent_assignment(self):
        for record in self:
            result = 0.0
            try:
                result = record.qty_assigned / record.uom_quantity
            except ZeroDivisionError:
                result = 0.0
            record.percent_assignment = result

    @api.depends(
        "uom_quantity",
        "qty_returned",
    )
    def _compute_percent_return(self):
        for record in self:
            result = 0.0
            try:
                result = record.qty_returned / record.uom_quantity
            except ZeroDivisionError:
                result = 0.0
            record.percent_return = result

    @api.onchange(
        "product_id",
    )
    def onchange_name(self):
        pass

    def _get_move_qty(self, states, picking_type_category):
        result = 0.0
        for move in self.stock_move_ids.filtered(
            lambda m: m.state in states
            and m.picking_type_id.category_id.id == picking_type_category.id
        ):
            result += move.product_qty
        return result

    def _create_assignment(self):
        self.ensure_one()
        group = self.request_id.procurement_group_id
        qty = self.qty_to_assign
        values = self._get_assignment_procurement_data()

        procurements = []
        try:
            procurement = group.Procurement(
                self.product_id,
                qty,
                self.uom_id,
                values.get("location_id"),
                values.get("origin"),
                values.get("origin"),
                self.env.company,
                values,
            )

            procurements.append(procurement)
            self.env["procurement.group"].with_context(rma_route_check=[True]).run(
                procurements
            )
        except UserError as error:
            raise UserError(error)

    def _create_return(self):
        self.ensure_one()
        group = self.request_id.procurement_group_id
        qty = self.qty_to_return
        values = self._get_return_procurement_data()

        procurements = []
        try:
            procurement = group.Procurement(
                self.product_id,
                qty,
                self.uom_id,
                values.get("location_id"),
                values.get("origin"),
                values.get("origin"),
                self.env.company,
                values,
            )

            procurements.append(procurement)
            self.env["procurement.group"].with_context(rma_route_check=[True]).run(
                procurements
            )
        except UserError as error:
            raise UserError(error)

    def _get_assignment_procurement_data(self):
        group = self.request_id.procurement_group_id
        origin = self.request_id.name
        warehouse = self.request_id.warehouse_id
        location = self.request_id.employee_id.location_id
        route = self.request_id.route_id
        result = {
            "name": origin,
            "group_id": group,
            "origin": origin,
            "warehouse_id": warehouse,
            "date_planned": fields.Datetime.now(),
            "product_id": self.product_id.id,
            "product_qty": self.qty_to_assign,
            "partner_id": False,
            "product_uom": self.uom_id.id,
            "location_id": location,
            "route_ids": route,
            "equipment_request_line_ids": [(4, self.id)],
        }
        return result

    def _get_return_procurement_data(self):
        group = self.request_id.procurement_group_id
        origin = self.request_id.name
        warehouse = self.request_id.warehouse_id
        location = self.request_id.warehouse_id.lot_stock_id
        route = self.request_id.route_id
        result = {
            "name": origin,
            "group_id": group,
            "origin": origin,
            "warehouse_id": warehouse,
            "date_planned": fields.Datetime.now(),
            "product_id": self.product_id.id,
            "product_qty": self.qty_to_return,
            "partner_id": False,
            "product_uom": self.uom_id.id,
            "location_id": location,
            "route_ids": route,
            "equipment_request_line_ids": [(4, self.id)],
        }
        return result
