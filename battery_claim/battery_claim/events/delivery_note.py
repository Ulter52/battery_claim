import frappe

from battery_claim.utils.stock import (
    get_item_serial,
    get_single_item,
)


def on_submit(doc, method=None):
    """
    Update Battery Warranty Claim after Delivery Note
    is successfully submitted.
    """
    frappe.db.after_commit.add(
        lambda: update_claim_from_dn(doc.name)
    )


def on_cancel(doc, method=None):
    """
    Roll back Battery Warranty Claim after
    Delivery Note cancellation.
    """
    frappe.db.after_commit.add(
        lambda: rollback_claim_from_dn(doc.name)
    )


def update_claim_from_dn(dn_name):

    try:

        dn = frappe.get_doc("Delivery Note", dn_name)
        #dn.reload()

        claim_name = dn.battery_warranty_claim
        claim = frappe.get_doc("Battery Warranty Claim", claim_name)

        if not claim_name:
            return

        item = get_single_item(dn)

        issued_serial = get_item_serial(item)

        if not issued_serial:
            frappe.throw(
                f"Unable to determine issued serial number for Delivery Note {dn.name}."
            )

        if claim.purchase_receipt:
            claim_status = "Closed"
        elif claim.warranty_claim_batch:
            claim_status = "Dispatched"
        else:
            claim_status = "Replaced"

        frappe.db.set_value(
            "Battery Warranty Claim",
            claim_name,
            {
                "delivery_note": dn.name,
                "issued_item_code": item.item_code,
                "issued_serial_no": issued_serial,
                "claim_status": claim_status
            },
            update_modified=False
        )

        frappe.db.commit()

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Warranty DN Update Failed"
        )
        raise


def rollback_claim_from_dn(dn_name):

    try:

        dn = frappe.get_doc("Delivery Note", dn_name)
        #dn.reload()

        claim_name = dn.battery_warranty_claim
        claim = frappe.get_doc("Battery Warranty Claim", claim_name)

        if not claim_name:
            return

        if claim.purchase_receipt:
            claim_status = "Stock Received"

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
                "delivery_note": None,
                "issued_item_code": None,
                "issued_serial_no": None,
                "claim_status": claim_status
            },
            update_modified=False
        )

        frappe.db.commit()

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Warranty DN Rollback Failed"
        )
        raise

