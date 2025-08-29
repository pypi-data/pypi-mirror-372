# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class EquipmentRequest(models.Model):
    _name = "equipment_request"
    _description = "Equipment Request"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_terminate",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_ready",
        "mixin.transaction_confirm",
        "mixin.transaction_date_due",
        "mixin.many2one_configurator",
        "mixin.employee_document",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "ready"
    _approval_state = "confirm"
    _after_approved_method = "action_ready"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_ready_policy_fields = False
    _automatically_insert_ready_button = False
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,confirm,ready,open"
    _policy_field_order = [
        "confirm_ok",
        "ready_ok",
        "open_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_open",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "%(ssi_transaction_terminate_mixin.base_select_terminate_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_ready",
        "dom_open",
        "dom_reject",
        "dom_done",
        "dom_terminate",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "ready"

    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    type_id = fields.Many2one(
        comodel_name="equipment_request_type",
        string="Type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    operation_id = fields.Many2one(
        comodel_name="equipment_request_operation",
        string="Operation",
        required=False,
        ondelete="restrict",
        readonly=True,
        states={"ready": [("readonly", False), ("required", True)]},
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        required=False,
        readonly=True,
        states={"ready": [("readonly", False), ("required", True)]},
    )
    route_id = fields.Many2one(
        string="Route",
        comodel_name="stock.location.route",
        required=False,
        readonly=True,
        states={"ready": [("readonly", False), ("required", True)]},
    )
    allowed_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Allowed Products",
        compute="_compute_allowed_product_ids",
        store=False,
        compute_sudo=True,
    )
    allowed_product_category_ids = fields.Many2many(
        comodel_name="product.category",
        string="Allowed Product Category",
        compute="_compute_allowed_product_category_ids",
        store=False,
        compute_sudo=True,
    )
    procurement_group_id = fields.Many2one(
        string="Procurement Group",
        comodel_name="procurement.group",
        readonly=True,
        copy=False,
    )
    line_ids = fields.One2many(
        comodel_name="equipment_request_line",
        inverse_name="request_id",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "ready": [("readonly", False)],
        },
        copy=True,
    )

    # Assignment Fields
    need_assignment = fields.Boolean(
        string="Need Assignment",
        compute="_compute_need_assignment",
        store=True,
    )
    qty_to_assign = fields.Float(
        string="Qty To Assign",
        compute="_compute_qty_to_assign",
        store=True,
    )
    qty_assigned = fields.Float(
        string="Qty Assigned",
        compute="_compute_qty_assigned",
        store=True,
    )
    qty_assigning = fields.Float(
        string="Qty Assigning",
        compute="_compute_qty_assigning",
        store=True,
    )
    assign_ok = fields.Boolean(
        string="Assign Ok",
        compute="_compute_assign_ok",
        store=True,
    )
    assign_complete = fields.Boolean(
        string="Assigment Complete",
        compute="_compute_assign_complete",
        store=True,
    )

    # Return Fields
    need_return = fields.Boolean(
        string="Need Return",
        compute="_compute_need_return",
        store=True,
    )
    qty_to_return = fields.Float(
        string="Qty To Return",
        compute="_compute_qty_to_return",
        store=True,
    )
    qty_returned = fields.Float(
        string="Qty Returned",
        compute="_compute_qty_returned",
        store=True,
    )
    qty_returning = fields.Float(
        string="Qty Returning",
        compute="_compute_qty_returning",
        store=True,
    )
    return_ok = fields.Boolean(
        string="Return Ok",
        compute="_compute_return_ok",
        store=True,
    )
    return_complete = fields.Boolean(
        string="Return Complete",
        compute="_compute_return_complete",
        store=True,
    )

    uom_quantity = fields.Float(
        string="UoM Quantity",
        compute="_compute_uom_quantity",
        store=True,
    )
    resolve_ok = fields.Boolean(
        string="Resolve Ok",
        compute="_compute_resolve_ok",
        store=True,
    )

    @api.depends(
        "line_ids",
        "line_ids.assign_complete",
    )
    def _compute_assign_complete(self):
        for record in self:
            result = False
            if len(record.line_ids) > 0:
                if len(record.line_ids) == len(
                    record.line_ids.filtered(lambda r: r.assign_complete)
                ):
                    result = True
            record.assign_complete = result

    @api.depends(
        "line_ids",
        "line_ids.return_complete",
    )
    def _compute_return_complete(self):
        for record in self:
            result = False
            if len(record.line_ids) > 0:
                if len(record.line_ids) == len(
                    record.line_ids.filtered(lambda r: r.return_complete)
                ):
                    result = True
            record.return_complete = result

    @api.depends(
        "operation_id",
    )
    def _compute_need_assignment(self):
        for record in self:
            result = False
            if record.operation_id and record.operation_id.assign_policy_id:
                result = True
            record.need_assignment = result

    @api.depends(
        "operation_id",
    )
    def _compute_need_return(self):
        for record in self:
            result = False
            if record.operation_id and record.operation_id.return_policy_id:
                result = True
            record.need_return = result

    @api.depends(
        "qty_to_assign",
        "state",
    )
    def _compute_assign_ok(self):
        for record in self:
            result = False
            if record.qty_to_assign > 0.0 and record.state == "open":
                result = True
            record.assign_ok = result

    @api.depends(
        "qty_to_return",
        "state",
    )
    def _compute_return_ok(self):
        for record in self:
            result = False
            if record.qty_to_return > 0.0 and record.state == "open":
                result = True
            record.return_ok = result

    def _get_resolve_ok_trigger(self):
        return [
            "assign_complete",
            "return_complete",
            "operation_id",
        ]

    @api.depends(lambda self: self._get_resolve_ok_trigger())
    def _compute_resolve_ok(self):
        for record in self:
            result = True
            if not record.operation_id:
                result = False

            for field_name in record._get_resolve_ok_trigger():
                if not getattr(record, field_name):
                    result = False
            record.resolve_ok = result

    @api.depends(
        "line_ids",
        "line_ids.uom_quantity",
    )
    def _compute_uom_quantity(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.uom_quantity
            record.uom_quantity = result

    @api.depends(
        "line_ids",
        "line_ids.qty_to_return",
    )
    def _compute_qty_to_return(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.qty_to_return
            record.qty_to_return = result

    @api.depends(
        "line_ids",
        "line_ids.qty_delivered",
    )
    def _compute_qty_delivered(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.qty_delivered
            record.qty_delivered = result

    @api.depends(
        "line_ids",
        "line_ids.qty_returning",
    )
    def _compute_qty_returning(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.qty_returning
            record.qty_returning = result

    @api.depends(
        "line_ids",
        "line_ids.qty_to_assign",
    )
    def _compute_qty_to_assign(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.qty_to_assign
            record.qty_to_assign = result

    @api.depends(
        "line_ids",
        "line_ids.qty_assigned",
    )
    def _compute_qty_assigned(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.qty_assigned
            record.qty_assigned = result

    @api.depends(
        "line_ids",
        "line_ids.qty_assigning",
    )
    def _compute_qty_assigning(self):
        for record in self:
            result = 0.0
            for line in record.line_ids:
                result += line.qty_assigning
            record.qty_assigning = result

    @api.depends("type_id")
    def _compute_allowed_product_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.product",
                    method_selection=record.type_id.product_selection_method,
                    manual_recordset=record.type_id.product_ids,
                    domain=record.type_id.product_domain,
                    python_code=record.type_id.product_python_code,
                )
            record.allowed_product_ids = result

    @api.depends("type_id")
    def _compute_allowed_product_category_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.category",
                    method_selection=record.type_id.product_category_selection_method,
                    manual_recordset=record.type_id.product_category_ids,
                    domain=record.type_id.product_category_domain,
                    python_code=record.type_id.product_category_python_code,
                )
            record.allowed_product_category_ids = result

    @api.onchange(
        "employee_id",
    )
    def onchange_warehouse_id(self):
        self.warehouse_id = False
        if self.employee_id:
            self.warehouse_id = self.employee_id.current_warehouse_id

    @api.onchange(
        "employee_id",
        "warehouse_id",
    )
    def onchange_route_id(self):
        self.route_id = False
        Route = self.env["employee.equipment_request_route"]
        if self.employee_id and self.warehouse_id:
            criteria = [
                ("employee_id", "=", self.employee_id.id),
                ("warehouse_id", "=", self.warehouse_id.id),
            ]
            routes = Route.search(criteria)
            if len(routes) > 0:
                self.route_id = routes[0].route_id

    @api.onchange(
        "type_id",
    )
    def onchange_policy_template_id(self):
        template_id = self._get_template_policy()
        self.policy_template_id = template_id

    def action_create_assignment(self):
        for record in self.sudo():
            record._create_assignment()

    def action_create_return(self):
        for record in self.sudo():
            record._create_return()

    def _create_return(self):
        self.ensure_one()
        for line in self.line_ids:
            line._create_return()

    def _create_assignment(self):
        self.ensure_one()
        for line in self.line_ids:
            line._create_assignment()

    @ssi_decorator.post_open_action()
    def _01_create_procurement_group(self):
        self.ensure_one()

        if self.procurement_group_id:
            return True

        PG = self.env["procurement.group"]
        group = PG.create(self._prepare_create_procurement_group())
        self.write(
            {
                "procurement_group_id": group.id,
            }
        )

    def _prepare_create_procurement_group(self):
        self.ensure_one()
        return {
            "name": self.name,
        }

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()

        policy_field = [
            "confirm_ok",
            "approve_ok",
            "cancel_ok",
            "open_ok",
            "ready_ok",
            "terminate_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
