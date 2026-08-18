# Copyright (c) 2026, Dhirendra Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, today, date_diff


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": _("Replacement Order"),
            "fieldname": "replacement_order",
            "fieldtype": "Link",
            "options": "Battery Warranty Claim",
            "width": 160,
        },
        {
            "label": _("Order Date"),
            "fieldname": "order_date",
            "fieldtype": "Date",
            "width": 95,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 160,
        },
        {
            "label": _("Supplier"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 130,
        },
        {
            "label": _("Serial No"),
            "fieldname": "serial_no",
            "fieldtype": "Link",
            "options": "Serial No",
            "width": 140,
        },
        {
            "label": _("Status"),
            "fieldname": "claim_status",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Delivery Note"),
            "fieldname": "delivery_note",
            "fieldtype": "Link",
            "options": "Delivery Note",
            "width": 150,
        },
        {
            "label": _("DN Date"),
            "fieldname": "dn_date",
            "fieldtype": "Date",
            "width": 90,
        },
        {
            "label": _("Purchase Receipt"),
            "fieldname": "purchase_receipt",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "width": 150,
        },
        {
            "label": _("PR Date"),
            "fieldname": "pr_date",
            "fieldtype": "Date",
            "width": 90,
        },
        {
            "label": _("Completion Date"),
            "fieldname": "completion_date",
            "fieldtype": "Date",
            "width": 105,
        },
        {
            "label": _("TAT (Days)"),
            "fieldname": "tat_days",
            "fieldtype": "Int",
            "width": 85,
        },
        {
            "label": _("Aging (Days)"),
            "fieldname": "aging_days",
            "fieldtype": "Int",
            "width": 90,
        },
    ]


def get_data(filters):
    order_filters = {}

    if filters.get("from_date"):
        order_filters["claim_date"] = [">=", filters["from_date"]]

    if filters.get("to_date"):
        if "claim_date" in order_filters:
            order_filters["claim_date"] = [
                "between",
                [filters["from_date"], filters["to_date"]],
            ]
        else:
            order_filters["claim_date"] = ["<=", filters["to_date"]]

    if filters.get("customer"):
        order_filters["customer"] = filters["customer"]

    if filters.get("supplier"):
        order_filters["supplier"] = filters["supplier"]

    if filters.get("item_code"):
        order_filters["defective_item_code"] = filters["item_code"]

    if filters.get("status"):
        order_filters["claim_status"] = filters["status"]

    orders = frappe.get_all(
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

    data = []

    for order in orders:
        dn_date = None
        pr_date = None

        dn_submitted = False
        pr_submitted = False

        # ---------------------------------------------------------
        # Delivery Note
        # ---------------------------------------------------------

        if order.delivery_note:
            dn = frappe.db.get_value(
                "Delivery Note",
                order.delivery_note,
                ["posting_date", "docstatus"],
                as_dict=True,
            )

            if dn:
                dn_date = dn.posting_date
                dn_submitted = dn.docstatus == 1

        # ---------------------------------------------------------
        # Purchase Receipt
        # ---------------------------------------------------------

        if order.purchase_receipt:
            pr = frappe.db.get_value(
                "Purchase Receipt",
                order.purchase_receipt,
                ["posting_date", "docstatus"],
                as_dict=True,
            )

            if pr:
                pr_date = pr.posting_date
                pr_submitted = pr.docstatus == 1

        # ---------------------------------------------------------
        # Completion
        #
        # Both DN and PR must be submitted.
        # ---------------------------------------------------------

        completion_date = None
        tat_days = None
        aging_days = None

        order_date = getdate(order.claim_date) if order.claim_date else None

        if dn_submitted and pr_submitted and dn_date and pr_date:
            completion_date = max(
                getdate(dn_date),
                getdate(pr_date),
            )

            if order_date:
                tat_days = date_diff(
                    completion_date,
                    order_date,
                )

        elif order_date:
            aging_days = date_diff(
                getdate(today()),
                order_date,
            )

        data.append(
            {
                "replacement_order": order.name,
                "order_date": order.claim_date,
                "customer": order.customer,
                "supplier": order.supplier,
                "item_code": order.defective_item_code,
                "serial_no": order.defective_serial_no,
                "claim_status": order.claim_status,
                "delivery_note": order.delivery_note,
                "dn_date": dn_date,
                "purchase_receipt": order.purchase_receipt,
                "pr_date": pr_date,
                "completion_date": completion_date,
                "tat_days": tat_days,
                "aging_days": aging_days,
            }
        )

    return data
