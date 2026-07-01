import frappe


ELIGIBLE_BATCH_STATUSES = (
    "Approved",
    "Replaced",
)

SNAPSHOT_FIELDS = {

    "defective_item_code": "Defective Item",

    "defective_serial_no": "Defective Serial",

    "replacement_issued": "Replacement Issued",

    "replacement_point": "Replacement Point",

    "issued_item_code": "Replacement Item",

    "issued_serial_no": "Replacement Serial",

    "delivery_note": "Delivery Note",

}



def get_replacement_details(claim):
    """
    Returns the battery currently installed at customer.

    Dealer Replacement
        -> Installed Item / Serial

    Store Replacement
        -> Issued Item / Serial
    """

    if claim.dealer_has_replaced:
        return {
            "replacement_point": "Dealer Replacement",
            "issued_item_code": claim.installed_item_code,
            "issued_serial_no": claim.installed_serial_no,
        }

    return {
        "replacement_point": "Store Replacement",
        "issued_item_code": claim.issued_item_code,
        "issued_serial_no": claim.issued_serial_no,
    }


def build_batch_snapshot(claim):
    """
    Build Warranty Claim Batch Item snapshot
    from Battery Warranty Claim.
    """

    replacement = get_replacement_details(claim)
    
    replacement_issued = int(
        bool(
            claim.dealer_has_replaced
            or claim.issued_serial_no
            or claim.installed_serial_no
        )
    )

    return {
        "project": claim.project,

        "battery_warranty_claim": claim.name,

        "defective_item_code": claim.defective_item_code,
        "defective_serial_no": claim.defective_serial_no,

        "replacement_issued": replacement_issued,
        "replacement_point": replacement["replacement_point"],

        "issued_item_code": replacement["issued_item_code"],
        "issued_serial_no": replacement["issued_serial_no"],

        "delivery_note": claim.delivery_note,

        "remarks": claim.remarks or ""
    }


def validate_claim_eligibility(claim):

    if claim.docstatus != 1:
        frappe.throw(
            f"Battery Warranty Claim <b>{claim.name}</b> must be submitted."
        )

    if claim.claim_status not in ELIGIBLE_BATCH_STATUSES:

        frappe.throw(
            f"""
            Battery Warranty Claim
            <b>{claim.name}</b>

            is currently

            <b>{claim.claim_status}</b>

            Only Approved or Replaced claims
            can be added to Warranty Claim Batch.
            """
        )

def validate_duplicate_rows(doc):

    seen = set()

    for row in doc.item_claim:

        if not row.battery_warranty_claim:
            continue

        if row.battery_warranty_claim in seen:

            frappe.throw(
                f"""
                Battery Warranty Claim
                <b>{row.battery_warranty_claim}</b>
                appears more than once in this batch.
                """
            )

        seen.add(row.battery_warranty_claim)


def validate_existing_batch(doc):

    for row in doc.item_claim:

        if not row.battery_warranty_claim:
            continue

        existing = frappe.db.get_value(

            "Warranty Claim Batch Item",

            {
                "battery_warranty_claim": row.battery_warranty_claim,
                "parent": ["!=", doc.name],
                "docstatus": ["!=", 2]
            },

            ["parent"],

            as_dict=True

        )

        if existing:

            frappe.throw(
                f"""
                Battery Warranty Claim
                <b>{row.battery_warranty_claim}</b>

                already belongs to Warranty Claim Batch

                <b>{existing.parent}</b>.
                """
            )


def validate_snapshot(doc):

    for row in doc.item_claim:

        if not row.battery_warranty_claim:
            continue

        claim = frappe.get_doc(
            "Battery Warranty Claim",
            row.battery_warranty_claim
        )

        snapshot = build_batch_snapshot(claim)

        changed = []

        for field, label in SNAPSHOT_FIELDS.items():

            batch_value = row.get(field)
            claim_value = snapshot.get(field)

            if (batch_value or "") != (claim_value or ""):

                changed.append(
                    f"{label}<br>"
                    f"Batch : <b>{batch_value}</b><br>"
                    f"Claim : <b>{claim_value}</b>"
                )

        if changed:

            frappe.throw(
                f"""
                Battery Warranty Claim

                <b>{claim.name}</b>

                has changed since it was added to the batch.

                <br><br>

                {'<hr>'.join(changed)}

                <br><br>

                Please refresh this row before submitting.
                """
            )


def compare_snapshot(batch_row, snapshot):
    """
    Compare Warranty Claim Batch row with
    current Battery Warranty Claim snapshot.

    Returns:
        List of changed fields.
    """

    changes = []

    for field, label in SNAPSHOT_FIELDS.items():

        batch_value = batch_row.get(field) or ""
        snapshot_value = snapshot.get(field) or ""

        if str(batch_value) != str(snapshot_value):

            changes.append(
                {
                    "field": field,
                    "label": label,
                    "batch": batch_value,
                    "claim": snapshot_value,
                }
            )

    return changes
