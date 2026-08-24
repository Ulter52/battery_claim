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
        fields=["defective_item_code"],
    )

    item_counts = {}

    for order in orders:

        item_code = order.defective_item_code

        if not item_code:
            continue

        item_counts[item_code] = (
            item_counts.get(item_code, 0) + 1
        )

    # Highest replacement count first
    items = sorted(
        item_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    labels = [
        item[0]
        for item in items
    ]

    values = [
        item[1]
        for item in items
    ]

    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Replacement Orders",
                "values": values,
            }
        ],
        "type": "bar",
    }
