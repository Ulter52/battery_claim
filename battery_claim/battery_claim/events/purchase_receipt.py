import frappe

from battery_claim.utils.stock import (
    get_item_serial,
    get_single_item,
)


def on_submit(doc, method=None):
    """
    Update Battery Warranty Claim after
    Purchase Receipt is submitted.
    """
    frappe.db.after_commit.add(
        lambda: update_claim_from_pr(doc.name)
    )


def on_cancel(doc, method=None):
    """
    Roll back Battery Warranty Claim after
    Purchase Receipt cancellation.
    """
    frappe.db.after_commit.add(
        lambda: rollback_claim_from_pr(doc.name)
    )


def update_claim_from_pr(pr_name):

    try:

        pr = frappe.get_doc("Purchase Receipt", pr_name)
        pr.reload()

        claim_name = pr.battery_warranty_claim
        
        # Not a Battery Claim Purchase Receipt ignore it.
        if not claim_name:
            return
            
        claim = frappe.get_doc("Battery Warranty Claim", claim_name)

        if not claim_name:
            frappe.throw(
                f"Battery Warranty Claim is not linked with Purchase Receipt {pr.name}."
            )

        item = get_single_item(pr)

        received_serial_no = get_item_serial(item)

        if not received_serial_no:
            frappe.throw(
                f"Unable to determine received serial number for Purchase Receipt {pr.name}."
            )
        
        claim_status = (
            "Closed"
            if claim.delivery_note
            else "Stock Received"
        )    

        frappe.db.set_value(
            "Battery Warranty Claim",
            claim_name,
            {
                "purchase_receipt": pr.name,
                "received_item_code": item.item_code,
                "received_serial_no": received_serial_no,
                "claim_status": claim_status,
            },
            update_modified=False,
        )

        frappe.db.commit()

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "Warranty PR Update Failed"
        )

        raise


def rollback_claim_from_pr(pr_name):

    try:

        pr = frappe.get_doc("Purchase Receipt", pr_name)

        claim_name = pr.battery_warranty_claim

        if not claim_name:
            return
            
        claim = frappe.get_doc("Battery Warranty Claim", claim_name)

        if claim.delivery_note and not claim.warranty_claim_batch:
            claim_status = "Replaced"
        elif claim.warranty_claim_batch:
            claim_status = "Dispatched"
        elif claim.warranty_approval:
            claim_status = "Approved"
        else:
            claim_status = "Approval Pending"

        frappe.db.set_value(
            "Battery Warranty Claim",
            claim_name,
            {
                "purchase_receipt": None,
                "received_item_code": None,
                "received_serial_no": None,
                "claim_status": claim_status,
            },
            update_modified=False,
        )

        frappe.db.commit()

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "Warranty PR Rollback Failed"
        )

        raise
