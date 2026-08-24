import frappe

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
        fields=["claim_status"],
    )

    status_counts = {}

    for order in orders:
        status = order.claim_status

        if not status:
            continue

        status_counts[status] = (
            status_counts.get(status, 0) + 1
        )

    # Highest count first
    statuses = sorted(
        status_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    labels = [
        status[0]
        for status in statuses
    ]

    values = [
        status[1]
        for status in statuses
    ]

    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Replacement Orders",
                "values": values,
            }
        ],
        "type": "donut",
    }
