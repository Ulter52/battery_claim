import frappe
from frappe.utils import getdate, today, date_diff


def get_replacement_orders(filters=None):
    """
    Get submitted Replacement Orders (currently Battery Warranty Claim).

    Cancelled Replacement Orders are excluded.
    """
    filters = filters or {}

    order_filters = {
        "docstatus": 1
    }

    if filters.get("from_date") and filters.get("to_date"):
        order_filters["claim_date"] = [
            "between",
            [filters["from_date"], filters["to_date"]]
        ]
    elif filters.get("from_date"):
        order_filters["claim_date"] = [">=", filters["from_date"]]
    elif filters.get("to_date"):
        order_filters["claim_date"] = ["<=", filters["to_date"]]

    if filters.get("customer"):
        order_filters["customer"] = filters["customer"]

    if filters.get("supplier"):
        order_filters["supplier"] = filters["supplier"]

    if filters.get("item_code"):
        order_filters["defective_item_code"] = filters["item_code"]

    if filters.get("status"):
        order_filters["claim_status"] = filters["status"]

    return frappe.get_all(
        "Battery Warranty Claim",
        filters=order_filters,
        fields=[
            "name",
            "claim_date",
            "customer",
            "supplier",
            "defective_item_code",
            "defective_serial_no",
            "claim_status",
            "delivery_note",
            "purchase_receipt",
        ],
        order_by="claim_date desc, name desc",
    )


def get_dn_details(delivery_note):
    """
    Return Delivery Note posting date and docstatus.
    """
    if not delivery_note:
        return None

    return frappe.db.get_value(
        "Delivery Note",
        delivery_note,
        ["posting_date", "docstatus"],
        as_dict=True,
    )


def get_pr_details(purchase_receipt):
    """
    Return Purchase Receipt posting date and docstatus.
    """
    if not purchase_receipt:
        return None

    return frappe.db.get_value(
        "Purchase Receipt",
        purchase_receipt,
        ["posting_date", "docstatus"],
        as_dict=True,
    )


def is_dn_submitted(delivery_note):
    """
    True only when the linked Delivery Note is submitted.
    """
    dn = get_dn_details(delivery_note)

    return bool(
        dn
        and dn.docstatus == 1
    )


def is_pr_submitted(purchase_receipt):
    """
    True only when the linked Purchase Receipt is submitted.
    """
    pr = get_pr_details(purchase_receipt)

    return bool(
        pr
        and pr.docstatus == 1
    )


def is_replacement_closed(order):
    """
    A Replacement Order is considered closed for reporting
    only when BOTH Delivery Note and Purchase Receipt are submitted.
    """
    return (
        is_dn_submitted(order.delivery_note)
        and is_pr_submitted(order.purchase_receipt)
    )


def get_completion_date(order):
    """
    Completion Date is the later of:
        - submitted Delivery Note posting date
        - submitted Purchase Receipt posting date

    Returns None if either transaction is missing/not submitted.
    """
    dn = get_dn_details(order.delivery_note)
    pr = get_pr_details(order.purchase_receipt)

    if not dn or not pr:
        return None

    if dn.docstatus != 1 or pr.docstatus != 1:
        return None

    if not dn.posting_date or not pr.posting_date:
        return None

    return max(
        getdate(dn.posting_date),
        getdate(pr.posting_date),
    )


def get_tat(order):
    """
    Return completed TAT in days.

    TAT is calculated only for completed Replacement Orders.
    """
    completion_date = get_completion_date(order)

    if not completion_date or not order.claim_date:
        return None

    return date_diff(
        completion_date,
        getdate(order.claim_date),
    )


def get_aging(order):
    """
    Return current aging in days for an open Replacement Order.

    Closed orders return None.
    """
    if is_replacement_closed(order):
        return None

    if not order.claim_date:
        return None

    return date_diff(
        getdate(today()),
        getdate(order.claim_date),
    )


def get_replacement_summary(filters=None):
    """
    Return the main Replacement Management dashboard figures.

    Returns:
        total
        open
        closed
        dn_pending
        pr_pending
        average_tat
    """
    orders = get_replacement_orders(filters)

    total = len(orders)
    closed = 0
    open_orders = 0
    dn_pending = 0
    pr_pending = 0

    tat_values = []

    for order in orders:

        dn_submitted = is_dn_submitted(order.delivery_note)
        pr_submitted = is_pr_submitted(order.purchase_receipt)

        # ---------------------------------------------------------
        # Closed
        # ---------------------------------------------------------

        if dn_submitted and pr_submitted:
            closed += 1

            tat = get_tat(order)

            if tat is not None:
                tat_values.append(tat)

        # ---------------------------------------------------------
        # Open
        # ---------------------------------------------------------

        else:
            open_orders += 1

        # ---------------------------------------------------------
        # DN Pending
        # ---------------------------------------------------------

        if not dn_submitted:
            dn_pending += 1

        # ---------------------------------------------------------
        # PR Pending
        # ---------------------------------------------------------

        if not pr_submitted:
            pr_pending += 1

    average_tat = (
        round(sum(tat_values) / len(tat_values), 1)
        if tat_values
        else 0
    )

    return {
        "total": total,
        "open": open_orders,
        "closed": closed,
        "dn_pending": dn_pending,
        "pr_pending": pr_pending,
        "average_tat": average_tat,
    }



@frappe.whitelist()
def get_number_card_data():
    return get_replacement_summary()
