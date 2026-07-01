import frappe

from battery_claim.utils.lifecycle import (
    get_available_actions as lifecycle_actions,
)


@frappe.whitelist()
def get_available_actions(claim):
    """
    Wrapper around lifecycle actions.
    """
    return lifecycle_actions(claim)
