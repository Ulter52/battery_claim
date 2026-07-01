# Copyright (c) 2026, Dhirendra Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class WarrantyApproval(Document):

    def validate(self):
        self.validate_amendment()

    def before_save(self):
        if not self.approval_date:
            self.approval_date = today()

    def before_submit(self):
        self.validate_duplicate_approval()
        self.validate_claim_status()
        self.validate_claim_batch()
        self.validate_approved_item()

    def on_submit(self):
        frappe.db.set_value(
            "Battery Warranty Claim",
            self.battery_warranty_claim,
            {
                "warranty_approval": self.name,
                "approved_item_code": self.approved_item_code,
                "supplier": self.supplier,
                "claim_status": "Approved",
            },
            update_modified=False,
        )

    def on_cancel(self):
        claim = frappe.get_doc(
            "Battery Warranty Claim",
            self.battery_warranty_claim,
        )

        # Clear only if this approval is still linked
        if claim.warranty_approval == self.name:
            frappe.db.set_value(
                "Battery Warranty Claim",
                self.battery_warranty_claim,
                {
                    "warranty_approval": None,
                    "approved_item_code": None,
                    "supplier": None,
                    "claim_status": "Approval Pending",
                },
                update_modified=False,
            )

    def validate_duplicate_approval(self):
        if not self.battery_warranty_claim:
            return

        existing = frappe.db.get_value(
            "Warranty Approval",
            {
                "battery_warranty_claim": self.battery_warranty_claim,
                "docstatus": 1,
                "name": ["!=", self.name],
            },
            "name",
        )

        if existing:
            frappe.throw(
                _(
                    "Battery Warranty Claim <b>{0}</b> already has submitted Warranty Approval <b>{1}</b>."
                ).format(
                    self.battery_warranty_claim,
                    existing,
                )
            )

    def validate_claim_status(self):
        status = frappe.db.get_value(
            "Battery Warranty Claim",
            self.battery_warranty_claim,
            "claim_status",
        )

        if status != "Approval Pending":
            frappe.throw(
                _(
                    "Battery Warranty Claim <b>{0}</b> is in status <b>{1}</b>. "
                    "Only claims in <b>Approval Pending</b> can be approved."
                ).format(
                    self.battery_warranty_claim,
                    status,
                )
            )

    def validate_claim_batch(self):
        batch = frappe.db.get_value(
            "Battery Warranty Claim",
            self.battery_warranty_claim,
            "warranty_claim_batch",
        )

        if batch:
            frappe.throw(
                _(
                    "Battery Warranty Claim <b>{0}</b> already belongs to Warranty Claim Batch <b>{1}</b>."
                ).format(
                    self.battery_warranty_claim,
                    batch,
                )
            )

    def validate_approved_item(self):
        if not self.approved_item_code:
            frappe.throw(
                _("Approved Item Code is mandatory.")
            )

    def validate_amendment(self):
        if self.amended_from and not self.reason_of_cancellation:
            frappe.throw(
                _("Reason of Cancellation is mandatory for amended approvals.")
            )
