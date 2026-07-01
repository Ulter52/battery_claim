import frappe

from erpnext.stock.serial_batch_bundle import get_serial_or_batch_nos


def get_item_serial(item):
    """
    Returns serial number from a stock transaction item.

    Lookup order:
        1. Item.serial_no
        2. Serial & Batch Bundle
        3. None
    """

    # --------------------------------------------------
    # Direct Serial No
    # --------------------------------------------------

    if getattr(item, "serial_no", None):
        return item.serial_no.strip()

    # --------------------------------------------------
    # Serial & Batch Bundle
    # --------------------------------------------------

    bundle = getattr(item, "serial_and_batch_bundle", None)

    if bundle:

        serials = get_serial_or_batch_nos(bundle)

        if serials:

            # Helper may return string or list depending on ERPNext version

            if isinstance(serials, str):
                return serials.strip()

            if isinstance(serials, (list, tuple)):
                return serials[0].strip() if serials else None

    # --------------------------------------------------
    # Last Fallback
    # --------------------------------------------------

    return None


def get_single_item(doc):

    if len(doc.items) != 1:
        frappe.throw(
            f"{doc.doctype} {doc.name} must contain exactly one item."
        )

    return doc.items[0]

def update_claim_fields(claim_name, values):
    """
    Update Battery Warranty Claim fields
    and commit immediately.
    """

    frappe.db.set_value(
        "Battery Warranty Claim",
        claim_name,
        values,
        update_modified=False,
    )

    frappe.db.commit()
