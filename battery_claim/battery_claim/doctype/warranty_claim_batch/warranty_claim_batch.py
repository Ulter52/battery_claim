# Copyright (c) 2026, Dhirendra Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.serial_batch_bundle import get_serial_or_batch_nos
from battery_claim.utilities.serials_and_batch_bundle_utils import get_serials_from_bundle

class WarrantyClaimBatch(Document):

    def validate(self):
        ALLOWED_REPLACEMENT_TYPES = (
            "Store Replacement",
            "Dealer Replacement",
        )

        for idx, row in enumerate(self.item_claim, start=1):
            if not row.project:
                continue

            replacement_type = frappe.db.get_value(
                "Project",
                row.project,
                "project_type"
            )

            if not replacement_type:
                frappe.throw(
                    f"Row {idx}: Project <b>{row.project}</b> must have a Replacement Type defined."
                )

            if replacement_type not in ALLOWED_REPLACEMENT_TYPES:
                frappe.throw(
                    f"Row {idx}: Project <b>{row.project}</b> has invalid Replacement Type "
                    f"(<b>{replacement_type}</b>)."
                )

	

@frappe.whitelist()
def get_delivery_note(project):
    """
    Fetch replacement details from Delivery Note for a given Project
    Supports Serial No and Serial & Batch Bundle (ERPNext v15+)
    """

    if not project:
        return {}

    dn_name = frappe.db.get_value(
        "Delivery Note",
        {
            "project": project,
            "docstatus": 1
        },
        "name"
    )

    if not dn_name:
        return {}

    dn = frappe.get_doc("Delivery Note", dn_name)

    if not dn.items:
        return {}

    # Assumption (valid in your workflow): one replacement per project
    item = dn.items[0]

    serials = ""
    if item.serial_no:
        serials = item.serial_no
    elif item.serial_and_batch_bundle:
        serials = get_serial_or_batch_nos(item.serial_and_batch_bundle)

    return {
        "replacement_issued": 1,
        "delivery_note": dn_name,
        "issued_item_code": item.item_code,
        "issued_serial_no": serials
    }

@frappe.whitelist()
def update_warranty_claim_batch_from_pr(doc, method):
    """
    Schedule warranty update AFTER PR submit transaction commits
    """
    frappe.db.after_commit.add(
        lambda: _update_warranty_claim_batch_from_pr(doc.name)
    )


@frappe.whitelist()
def _update_warranty_claim_batch_from_pr(pr_name):
    frappe.msgprint(pr_name)
    doc = frappe.get_doc("Purchase Receipt", pr_name)
    project = doc.project
    item_code = ""
    serial_no = ""
    for row in doc.items:
        item_code = row.item_code
        serial_no = get_serials_from_bundle(row.serial_and_batch_bundle)

        # Find open Warranty Claim Batch Item for this project
    batch_item = frappe.db.get_value(
        "Warranty Claim Batch Item",
        {
            "project": project,
            "purchase_receipt": ["is", "not set"]
        },
        ["name", "parent"],
        as_dict=True
    )

    if not batch_item:
        return 

    # Update Warranty Claim Batch Item
    frappe.db.set_value(
        "Warranty Claim Batch Item",
        batch_item.name,
        {
            "supplier_item_code": item_code,
            "supplier_serial_no": serial_no,
            "purchase_receipt": doc.name
        }
    )
    frappe.db.commit()

    batch_name = batch_item.parent

    # Update Batch Status
    update_status(batch_name)
    return { 
        "status": "found", 
        "project": project, 
        "item_code": item_code, 
        "serial_no": serial_no, 
        "batch_item_name": batch_item.name, 
        "batch_parent": batch_item.parent
    }

def update_status(batch_name):
    """
    Recalculate and update Warranty Claim Batch status.

    Rules:
    - Open: no items settled
    - Partially Settled: some settled, some pending
    - Settled: all items settled
    """

    total = frappe.db.count(
        "Warranty Claim Batch Item",
        {"parent": batch_name}
    )

    settled = frappe.db.count(
        "Warranty Claim Batch Item",
        {
            "parent": batch_name,
            "purchase_receipt": ["is", "set"]
        }
    )

    pending = total - settled

    status = ""

    if settled == 0:
        status = "Open"
    elif pending == 0:
        status = "Settled"
    else:
        status = "Partially Settled"

    try:
        frappe.db.set_value(
            "Warranty Claim Batch",
            batch_name,
            "status", 
            status,
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Failed to update status to {status} of {batch_name}" )
        frappe.throw(_("Failed to update Warranty Claim Batch status"))
        
    return {
        "Total": total,
        "Pending": pending,
        "Settled": settled,
        "Final Status": status
    }

@frappe.whitelist()
def rollback_warranty_claim_batch_from_pr(doc, method):

    if not doc.project:
        return

    # Find the batch item linked to this PR
    batch_item = frappe.db.get_value(
        "Warranty Claim Batch Item",
        {
            "project": doc.project,
            "purchase_receipt": doc.name
        },
        ["name", "parent"],
        as_dict=True
    )

    if not batch_item:
        return

    # Clear snapshot fields
    frappe.db.set_value(
        "Warranty Claim Batch Item",
        batch_item.name,
        {
            "supplier_item_code": None,
            "supplier_serial_no": None,
            "purchase_receipt": None
        }
    )

    # Recalculate batch status
    update_warranty_claim_batch_status(batch_item.parent)
