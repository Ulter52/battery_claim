// Copyright (c) 2026, Dhirendra Sharma and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Warranty Claim Batch", {
// 	refresh(frm) {

// 	},
// });


const SNAPSHOT_FIELDS = [
    "defective_item_code",
    "defective_serial_no",
    "replacement_issued",
    "replacement_point",
    "delivery_note",
    "issued_item_code",
    "issued_serial_no",
    "remarks"
];

/**
 * Reset all snapshot fields in the child row.
 */
function reset_claim_snapshot(cdt, cdn) {

    SNAPSHOT_FIELDS.forEach(field => {
        frappe.model.set_value(cdt, cdn, field, null);
    });

}

/**
 * Populate snapshot values returned by the server.
 */
function populate_claim_snapshot(cdt, cdn, snapshot) {

    Object.entries(snapshot).forEach(([field, value]) => {

        frappe.model.set_value(
            cdt,
            cdn,
            field,
            value
        );

    });

}

/**
 * Fetch latest Battery Warranty Claim snapshot.
 */
function load_claim_snapshot(claim_name, callback) {

    frappe.call({

        method:
            "battery_claim.battery_claim.doctype.warranty_claim_batch.warranty_claim_batch.get_claim_snapshot",

        args: {
            claim_name: claim_name
        },

        freeze: true,

        callback: callback

    });

}


frappe.ui.form.on("Warranty Claim Batch Item", {

    battery_warranty_claim(frm, cdt, cdn) {

        const row = locals[cdt][cdn];

        reset_claim_snapshot(cdt, cdn);

        if (!row.battery_warranty_claim) {
            return;
        }

        load_claim_snapshot(
            row.battery_warranty_claim,
            function (r) {

                if (!r.message) {
                    return;
                }

                populate_claim_snapshot(
                    cdt,
                    cdn,
                    r.message
                );

            }
        );

    }

});
