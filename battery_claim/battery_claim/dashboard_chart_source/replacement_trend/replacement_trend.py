import frappe

from frappe.utils import getdate
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

    orders = frappe.get_all(
        "Battery Warranty Claim",
        filters=order_filters,
        fields=["claim_date"],
        order_by="claim_date asc",
    )

    monthly_counts = {}

    for order in orders:
        if not order.claim_date:
            continue

        month_key = getdate(order.claim_date).strftime("%Y-%m")

        monthly_counts[month_key] = (
            monthly_counts.get(month_key, 0) + 1
        )

    month_keys = sorted(monthly_counts.keys())

    labels = [
        getdate(f"{month}-01").strftime("%b %Y")
        for month in month_keys
    ]

    values = [
        monthly_counts[month]
        for month in month_keys
    ]

    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Replacement Orders",
                "values": values,
            }
        ],
        "type": "line",
    }
