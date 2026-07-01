import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_warranty_custom_fields():

    custom_fields = {

        "Delivery Note": [

            {
                "fieldname": "battery_warranty_claim",
                "label": "Battery Warranty Claim",
                "fieldtype": "Link",
                "options": "Battery Warranty Claim",
                "insert_after": "project",
                "read_only": 1,
                "hidden": 1,
                "no_copy": 1,
            }

        ],

        "Purchase Receipt": [

            {
                "fieldname": "battery_warranty_claim",
                "label": "Battery Warranty Claim",
                "fieldtype": "Link",
                "options": "Battery Warranty Claim",
                "insert_after": "project",
                "read_only": 1,
                "hidden": 1,
                "no_copy": 1,
            }

        ]

    }

    create_custom_fields(
        custom_fields,
        ignore_validate=True
    )

    frappe.db.commit()
