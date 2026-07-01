# Copyright (c) 2026, Dhirendra Sharma and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, nowtime
from erpnext.stock.report.serial_no_ledger.serial_no_ledger import get_data

# ---------------------------------------------------------------------
# Claim statuses that allow a fresh warranty claim
# ---------------------------------------------------------------------

REOPEN_ALLOWED = (
    "Rejected",
    "Cancelled",
)


class BatteryWarrantyClaim(Document):

    def validate(self):
        self.validate_serial_eligibility()

    # -----------------------------------------------------------------
    # Determine business outcome of a previous warranty claim
    # -----------------------------------------------------------------

    @staticmethod
    def get_claim_outcome(claim):

        # Credit Note = permanently settled
        if claim.credit_note_no:
            return "Credit Note"

        # Dealer already installed replacement
        if claim.installed_serial_no:
            return "Dealer Replacement"

        # Store replacement issued
        if claim.issued_serial_no:
            return "Store Replacement"

        # Claim still alive
        if claim.claim_status not in REOPEN_ALLOWED:
            return "Active"

        # Claim failed / cancelled
        return "Reopen Allowed"

    # -----------------------------------------------------------------
    # Validate whether this defective serial can create a new claim
    # -----------------------------------------------------------------

    def validate_serial_eligibility(self):

        if not self.defective_serial_no:
            return

        previous_claims = frappe.get_all(
            "Battery Warranty Claim",
            filters={
                "defective_serial_no": self.defective_serial_no,
                "name": ["!=", self.name],
            },
            fields=[
                "name",
                "claim_status",
                "issued_serial_no",
                "installed_serial_no",
                "credit_note_no",
            ],
            order_by="creation desc",
        )

        for claim in previous_claims:

            outcome = self.get_claim_outcome(claim)

            # ---------------------------------------------------------
            # Store Replacement
            # ---------------------------------------------------------

            if outcome == "Store Replacement":

                frappe.throw(_(
                    f"""
                    <b>This defective battery has already been replaced.</b>

                    <br><br>

                    Previous Claim :
                    <b>{claim.name}</b>

                    <br>

                    Replacement Battery :
                    <b>{claim.issued_serial_no}</b>

                    <br><br>

                    Future warranty claims must be registered
                    using the replacement battery serial number.
                    """
                ))

            # ---------------------------------------------------------
            # Dealer Replacement
            # ---------------------------------------------------------

            elif outcome == "Dealer Replacement":

                frappe.throw(_(
                    f"""
                    <b>Dealer has already replaced this battery.</b>

                    <br><br>

                    Previous Claim :
                    <b>{claim.name}</b>

                    <br>

                    Installed Battery :
                    <b>{claim.installed_serial_no}</b>

                    <br><br>

                    Future warranty claims must be registered
                    using the installed battery serial number.
                    """
                ))

            # ---------------------------------------------------------
            # Credit Note
            # ---------------------------------------------------------

            elif outcome == "Credit Note":

                frappe.throw(_(
                    f"""
                    <b>This battery has already been settled by Credit Note.</b>

                    <br><br>

                    Previous Claim :
                    <b>{claim.name}</b>

                    <br>

                    Credit Note :
                    <b>{claim.credit_note_no}</b>

                    <br><br>

                    This battery is permanently ineligible
                    for future warranty claims.
                    """
                ))

            # ---------------------------------------------------------
            # Existing Active Claim
            # ---------------------------------------------------------

            elif outcome == "Active":

                frappe.throw(_(
                    f"""
                    <b>A warranty claim already exists for this battery.</b>

                    <br><br>

                    Claim :
                    <b>{claim.name}</b>

                    <br>

                    Current Status :
                    <b>{claim.claim_status}</b>

                    <br><br>

                    Please continue processing the existing claim.
                    Multiple active warranty claims are not allowed.
                    """
                ))

            # ---------------------------------------------------------
            # Rejected / Cancelled
            # ---------------------------------------------------------

            # Reopen Allowed
            # Do nothing

@frappe.whitelist()
def get_serial_details(serial_no):

    if not serial_no:
        return {}

    if not frappe.db.exists("Serial No", serial_no):
        return {
            "serial_exists_in_system": 0
        }

    serial_doc = frappe.get_doc("Serial No", serial_no)

    result = {
        "serial_exists_in_system": 1,
        "defective_item_code": serial_doc.item_code,
        "serial_status": serial_doc.status,
        "warranty_expiry_date": serial_doc.warranty_expiry_date,
        "inward_voucher_type": "",
        "inward_voucher_no": "",
        "outward_voucher_type": "",
        "outward_voucher_no": "",
    }

    ledger = get_data(
        frappe._dict({
            "item_code": serial_doc.item_code,
            "serial_no": serial_no,
            "posting_date": today(),
            "posting_time": nowtime(),
        })
    )

    for row in ledger:

        voucher_type = row.get("voucher_type")

        if voucher_type in (
            "Purchase Receipt",
            "Purchase Invoice"
        ):
            result["inward_voucher_type"] = voucher_type
            result["inward_voucher_no"] = row.get("voucher_no")

        elif voucher_type in (
            "Sales Invoice",
            "Delivery Note"
        ):
            result["outward_voucher_type"] = voucher_type
            result["outward_voucher_no"] = row.get("voucher_no")

            customer = frappe.db.get_value(
                "Customer",
                row.get("party"),
                [
                    "name",
                    "customer_name",
                    "mobile_no",
                    "customer_group"
                ],
                as_dict=True
            )

            if customer:
                result.update({
                    "customer": customer.name,
                    "customer_name": customer.customer_name,
                    "mobile_no": customer.mobile_no,
                    "customer_type": get_customer_type(
                        customer.customer_group
                    )
                })

    return result


def get_customer_type(customer_group):

    dealer_groups = [
        "Dealer",
        "Battery Dealer"
    ]

    if customer_group in dealer_groups:
        return "Dealer"

    return "Individual"


@frappe.whitelist()
def create_delivery_note(claim):

    claim = frappe.get_doc(
        "Battery Warranty Claim",
        claim
    )

    if not claim.warranty_approval:
        frappe.throw("Claim must be Approved.")

    if claim.delivery_note:
        frappe.throw("Delivery Note already exists.")

    if not claim.customer:
        frappe.throw("Customer is required.")

    if not claim.approved_item_code:
        frappe.throw("Approved Item Code is required.")

    if (
        claim.fulfillment_method == "Store Stock"
        and not claim.fulfillment_warehouse
    ):
        frappe.throw(
            "Fulfillment Warehouse is required."
        )

    dn = frappe.new_doc("Delivery Note")

    dn.customer = claim.customer

    dn.battery_warranty_claim = claim.name

    dn.append(
        "items",
        {
            "item_code": claim.approved_item_code,
            "qty": 1,
            "warehouse": claim.fulfillment_warehouse,
        }
    )

    dn.insert(ignore_permissions=True)

    return dn.name


@frappe.whitelist()
def create_purchase_receipt(claim):

    claim = frappe.get_doc("Battery Warranty Claim", claim)

    if claim.docstatus != 1:
        frappe.throw("Please submit the Battery Warranty Claim first.")

    if claim.claim_status != "Dispatched":
        frappe.throw("Claim must be Dispatched before creating Purchase Receipt.")

    if claim.purchase_receipt:
        frappe.throw(f"Purchase Receipt {claim.purchase_receipt} already exists.")

    if not claim.supplier:
        frappe.throw("Supplier is mandatory.")

    if not claim.approved_item_code:
        frappe.throw("Approved Item Code is mandatory.")

    pr = frappe.new_doc("Purchase Receipt")

    pr.supplier = claim.supplier
    
    pr.battery_warranty_claim = claim.name

    pr.append(
        "items",
        {
            "item_code": claim.approved_item_code,
            "qty": 1
        }
    )

    pr.insert(ignore_permissions=True)

    return pr.name
