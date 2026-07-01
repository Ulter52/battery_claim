import frappe


def get_serials_from_bundle(bundle_name):
    """
    Return plain-text serial numbers from Serial and Batch Bundle.
    """

    if not bundle_name:
        return ""

    bundle = frappe.get_cached_doc("Serial and Batch Bundle", bundle_name)

    serials = []
    for row in bundle.entries:
        if row.serial_no:
            serials.append(row.serial_no)

    return ", ".join(serials)
