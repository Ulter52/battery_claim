import frappe


def execute():

    rows = frappe.get_all(
        "Warranty Claim Batch Item",
        filters={
            "project": ["is", "set"],
            "defective_serial_no": ["in", ["", None]]
        },
        fields=["name", "project"]
    )

    for row in rows:

        frappe.db.set_value(
            "Warranty Claim Batch Item",
            row.name,
            "defective_serial_no",
            row.project_name,
            update_modified=False
        )

    frappe.db.commit()

    print(f"Updated {len(rows)} Warranty Claim Batch Items.")
