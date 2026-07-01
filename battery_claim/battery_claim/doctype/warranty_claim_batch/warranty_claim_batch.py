# Copyright (c) 2026, Dhirendra Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.serial_batch_bundle import get_serial_or_batch_nos
from battery_claim.utils.serials_and_batch_bundle_utils import get_serials_from_bundle
from battery_claim.utils.warranty_claim_utils import (
    build_batch_snapshot,
    validate_claim_eligibility,
    compare_snapshot,
)
from battery_claim.utils.stock import get_item_serial


ALLOWED_CLAIM_STATUS = (
    "Approved",
    "Replaced",
)

class WarrantyClaimBatch(Document):

    def validate(self):

        self.validate_duplicate_rows()

        self.validate_existing_batch()

        self.validate_claim_status()

        self.validate_snapshot()

    def validate_duplicate_rows(self):

        seen = {}

        for row in self.item_claim:

            if not row.battery_warranty_claim:
                continue

            if row.battery_warranty_claim in seen:

                frappe.throw(
                    f"""
                    Battery Warranty Claim
                    <b>{row.battery_warranty_claim}</b>

                    is entered more than once.

                    Row {seen[row.battery_warranty_claim]}
                    and Row {row.idx}.
                    """
                )

            seen[row.battery_warranty_claim] = row.idx


    def validate_existing_batch(self):

        for row in self.item_claim:

            if not row.battery_warranty_claim:
                continue

            existing = frappe.db.sql("""
                SELECT
                    wcb.name
                FROM
                    `tabWarranty Claim Batch Item` wcbi
                INNER JOIN
                    `tabWarranty Claim Batch` wcb
                    ON wcbi.parent = wcb.name
                WHERE
                    wcbi.battery_warranty_claim=%s
                    AND wcb.docstatus < 2
                    AND wcb.name != %s
                LIMIT 1
            """, (
                row.battery_warranty_claim,
                self.name or ""
            ), as_dict=True)

            if existing:

                frappe.throw(
                    f"""
                    Battery Warranty Claim

                    <b>{row.battery_warranty_claim}</b>
 
                    already belongs to

                    <b>{existing[0].name}</b>.
                    """
                )


    def validate_claim_status(self):

        for row in self.item_claim:

            if not row.battery_warranty_claim:
                continue

            status = frappe.db.get_value(
                "Battery Warranty Claim",
                row.battery_warranty_claim,
                "claim_status"
            )

            if status not in ALLOWED_CLAIM_STATUS:

                frappe.throw(
                    f"""
                    Claim

                    <b>{row.battery_warranty_claim}</b>

                    is

                    <b>{status}</b>

                    Only Approved or Replaced
                    claims can be added.
                    """
                )

    def validate_snapshot(self):

        for row in self.item_claim:

            if not row.battery_warranty_claim:
                continue

            claim = frappe.get_doc(
                "Battery Warranty Claim",
                row.battery_warranty_claim
            )

            snapshot = build_batch_snapshot(claim)

            changes = compare_snapshot(row, snapshot)

            if not changes:
                continue

            message = ""

            for d in changes:

                message += f"""
                <tr>
                    <td>{d['label']}</td>
                    <td>{d['batch']}</td>
                    <td>{d['claim']}</td>
                </tr>
                """

            frappe.throw(f"""
                <h4>
                    Battery Warranty Claim
                    {claim.name}
                    has changed.
                </h4>

                <p>
                    Please refresh this row before submitting.
                </p>

                <table class="table table-bordered">

                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Batch</th>
                            <th>Current Claim</th>
                        </tr>
                    </thead>

                    <tbody>

                        {message}

                    </tbody>

                </table>
            """)


@frappe.whitelist()
def get_claim_snapshot(claim_name):

    if not claim_name:
        return {}

    claim = frappe.get_doc(
        "Battery Warranty Claim",
        claim_name
    )

    validate_claim_eligibility(claim)

    return build_batch_snapshot(claim)
	

def on_submit(self):

    for row in self.item_claim:

        if not row.battery_warranty_claim:
            continue

        frappe.db.set_value(
            "Battery Warranty Claim",
            row.battery_warranty_claim,
            {
                "warranty_claim_batch": self.name,
                "claim_status": "Dispatched",
            },
            update_modified=False
        )

def on_cancel(self):

    for row in self.item_claim:

        if not row.battery_warranty_claim:
            continue

        frappe.db.set_value(
            "Battery Warranty Claim",
            row.battery_warranty_claim,
            {
                "warranty_claim_batch": None,
                "claim_status": "Replaced",
            },
            update_modified=False
        )
