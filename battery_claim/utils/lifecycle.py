# Copyright (c) 2026, Dhirendra Sharma and contributors
# For license information, please see license.txt

import frappe


def get_available_actions(claim):
    """
    Returns all actions currently available for a
    Battery Warranty Claim.

    Accepts either a document or document name.
    """

    if isinstance(claim, str):
        claim = frappe.get_doc("Battery Warranty Claim", claim)

    actions = {
        # ----------------------------
        # Actions
        # ----------------------------
        "can_create_approval": False,
        "can_create_delivery_note": False,
        "can_add_to_batch": False,
        "can_create_purchase_receipt": False,

        "can_open_approval": False,
        "can_open_delivery_note": False,
        "can_open_batch": False,
        "can_open_purchase_receipt": False,

        # ----------------------------
        # Linked Documents
        # ----------------------------
        "warranty_approval": claim.warranty_approval,
        "delivery_note": claim.delivery_note,
        "warranty_claim_batch": claim.warranty_claim_batch,
        "purchase_receipt": claim.purchase_receipt,
    }

    # -----------------------------------------
    # Warranty Approval
    # -----------------------------------------

    if (
        claim.claim_status == "Approval Pending"
        and not claim.warranty_approval
    ):
        actions["can_create_approval"] = True

    if claim.warranty_approval:
        actions["can_open_approval"] = True

    # -----------------------------------------
    # Delivery Note
    # -----------------------------------------

    if (
        claim.fulfillment_method != "Credit Note"
        and claim.warranty_approval
        and not claim.delivery_note
    ):
        actions["can_create_delivery_note"] = True

    if claim.delivery_note:
        actions["can_open_delivery_note"] = True

    # -----------------------------------------
    # Warranty Claim Batch
    # -----------------------------------------

    if (
        claim.delivery_note
        and not claim.warranty_claim_batch
    ):
        actions["can_add_to_batch"] = True

    if claim.warranty_claim_batch:
        actions["can_open_batch"] = True

    # -----------------------------------------
    # Purchase Receipt
    # -----------------------------------------

    if claim.purchase_receipt:
        actions["can_open_purchase_receipt"] = True

    elif (
        claim.fulfillment_method != "Credit Note"
        and claim.warranty_claim_batch
        and not claim.purchase_receipt
    ):
        actions["can_create_purchase_receipt"] = True

    return actions
