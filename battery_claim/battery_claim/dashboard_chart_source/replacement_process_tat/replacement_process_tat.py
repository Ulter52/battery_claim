import frappe

from frappe.utils import date_diff, getdate
from frappe.utils.dashboard import cache_source


@frappe.whitelist()
@cache_source
def get(
    chart_name=None,
    chart=None,
    no_cache=None,
    filters=None,
    from_date=None,
    to_date=None,
    timespan=None,
    time_interval=None,
    heatmap_year=None,
):
    if filters:
        if isinstance(filters, str):
            filters = frappe.parse_json(filters)

        from_date = filters.get("from_date") or from_date
        to_date = filters.get("to_date") or to_date

    # ---------------------------------------------------------
    # Replacement Order filters
    # ---------------------------------------------------------

    order_filters = {
        "docstatus": 1,
    }

    if from_date and to_date:
        order_filters["claim_date"] = [
            "between",
            [from_date, to_date],
        ]

    elif from_date:
        order_filters["claim_date"] = [
            ">=",
            from_date,
        ]

    elif to_date:
        order_filters["claim_date"] = [
            "<=",
            to_date,
        ]

    # ---------------------------------------------------------
    # Get Replacement Orders
    # ---------------------------------------------------------

    claims = frappe.get_all(
        "Battery Warranty Claim",
        filters=order_filters,
        fields=[
            "name",
            "claim_date",
            "warranty_approval",
            "warranty_claim_batch",
            "delivery_note",
            "purchase_receipt",
        ],
    )

    # ---------------------------------------------------------
    # Stage totals and counts
    # ---------------------------------------------------------

    stage_totals = {
        "Approval": 0,
        "Dispatch": 0,
        "Replacement": 0,
        "Stock Received": 0,
        "Overall": 0,
    }

    stage_counts = {
        "Approval": 0,
        "Dispatch": 0,
        "Replacement": 0,
        "Stock Received": 0,
        "Overall": 0,
    }

    # ---------------------------------------------------------
    # Process each Replacement Order
    # ---------------------------------------------------------

    for claim in claims:

        if not claim.claim_date:
            continue

        claim_date = getdate(claim.claim_date)

        approval_date = None
        dispatch_date = None
        dn_date = None
        pr_date = None

        # -----------------------------------------------------
        # Approval Date
        # Battery Warranty Claim
        #     warranty_approval
        #         ↓
        # Warranty Approval.approval_date
        # -----------------------------------------------------

        if claim.warranty_approval:

            approval_date = frappe.db.get_value(
                "Warranty Approval",
                claim.warranty_approval,
                "approval_date",
            )

            if approval_date:
                approval_date = getdate(approval_date)

        # -----------------------------------------------------
        # Dispatch Date
        # Battery Warranty Claim
        #     warranty_claim_batch
        #         ↓
        # Warranty Claim Batch.dispatch_date
        # -----------------------------------------------------

        if claim.warranty_claim_batch:

            dispatch_date = frappe.db.get_value(
                "Warranty Claim Batch",
                claim.warranty_claim_batch,
                "dispatch_date",
            )

            if dispatch_date:
                dispatch_date = getdate(dispatch_date)

        # -----------------------------------------------------
        # Delivery Note Date
        # Battery Warranty Claim
        #     delivery_note
        #         ↓
        # Delivery Note.posting_date
        # -----------------------------------------------------

        if claim.delivery_note:

            dn_date = frappe.db.get_value(
                "Delivery Note",
                claim.delivery_note,
                "posting_date",
            )

            if dn_date:
                dn_date = getdate(dn_date)

        # -----------------------------------------------------
        # Purchase Receipt Date
        # Battery Warranty Claim
        #     purchase_receipt
        #         ↓
        # Purchase Receipt.posting_date
        # -----------------------------------------------------

        if claim.purchase_receipt:

            pr_date = frappe.db.get_value(
                "Purchase Receipt",
                claim.purchase_receipt,
                "posting_date",
            )

            if pr_date:
                pr_date = getdate(pr_date)

        # -----------------------------------------------------
        # Approval TAT
        #
        # Claim Date → Approval Date
        # -----------------------------------------------------

        if approval_date and approval_date >= claim_date:

            days = date_diff(
                approval_date,
                claim_date,
            )

            stage_totals["Approval"] += days
            stage_counts["Approval"] += 1

        # -----------------------------------------------------
        # Dispatch TAT
        #
        # Approval Date → Dispatch Date
        # -----------------------------------------------------

        if (
            approval_date
            and dispatch_date
            and dispatch_date >= approval_date
        ):

            days = date_diff(
                dispatch_date,
                approval_date,
            )

            stage_totals["Dispatch"] += days
            stage_counts["Dispatch"] += 1

        # -----------------------------------------------------
        # Replacement TAT
        #
        # Claim Date → Delivery Note Date
        # -----------------------------------------------------

        if dn_date and dn_date >= claim_date:

            days = date_diff(
                dn_date,
                claim_date,
            )

            stage_totals["Replacement"] += days
            stage_counts["Replacement"] += 1

        # -----------------------------------------------------
        # Stock Received TAT
        #
        # Dispatch Date → Purchase Receipt Date
        # -----------------------------------------------------

        if (
            dispatch_date
            and pr_date
            and pr_date >= dispatch_date
        ):

            days = date_diff(
                pr_date,
                dispatch_date,
            )

            stage_totals["Stock Received"] += days
            stage_counts["Stock Received"] += 1

        # -----------------------------------------------------
        # Overall TAT
        #
        # Claim Date → Later of DN Date / PR Date
        # -----------------------------------------------------

        completion_dates = [
            date
            for date in (
                dn_date,
                pr_date,
            )
            if date
        ]

        if completion_dates:

            completion_date = max(completion_dates)

            if completion_date >= claim_date:

                days = date_diff(
                    completion_date,
                    claim_date,
                )

                stage_totals["Overall"] += days
                stage_counts["Overall"] += 1

    # ---------------------------------------------------------
    # Calculate average TAT for each stage
    # ---------------------------------------------------------

    stages = [
        "Approval",
        "Dispatch",
        "Replacement",
        "Stock Received",
        "Overall",
    ]

    labels = []
    values = []

    for stage in stages:

        labels.append(stage)

        count = stage_counts[stage]

        if count:

            average = round(
                stage_totals[stage] / count,
                1,
            )

        else:

            average = 0

        values.append(average)

    # ---------------------------------------------------------
    # Return Dashboard Chart data
    # ---------------------------------------------------------

    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Average TAT",
                "values": values,
            }
        ],
        "type": "bar",
    }
