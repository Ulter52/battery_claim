// Copyright (c) 2026, Dhirendra Sharma and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Warranty Claim Batch", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Warranty Claim Batch Item', {
    project: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Reset
        frappe.model.set_value(cdt, cdn, 'replacement_issued', 0);
        frappe.model.set_value(cdt, cdn, 'issued_item_code', '');
        frappe.model.set_value(cdt, cdn, 'issued_serial_no', '');
        frappe.model.set_value(cdt, cdn, 'delivery_note', '');

        if (!row.project) return;

        frappe.call({
    method: 'battery_claim.battery_claim.doctype.warranty_claim_batch.warranty_claim_batch.get_delivery_note',
    args: {
        project: row.project
    },
    callback: function (r) {
        if (!r.message) return;

        Object.keys(r.message).forEach(key => {
            frappe.model.set_value(cdt, cdn, key, r.message[key]);
        });
    }
});
    }
});
frappe.ui.form.on('Warranty Claim Batch Item', {
    project: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.project) return;

        frappe.db.get_value(
            'Project',
            row.project,
            'project_type',
            function (r) {
                frappe.model.set_value(
                    cdt,
                    cdn,
                    'replacement_point',
                    r.project_type || ''
                );
            }
        );
    }
});

frappe.ui.form.on('Warranty Claim Batch Item', {
    issued_serial_no: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.issued_serial_no) return;

        frappe.db.get_value(
            'Serial No',
            row.issued_serial_no,
            'item_code',
            function (r) {
                if (!r || !r.item_code) {
                    frappe.msgprint({
                        title: __('Invalid Serial No'),
                        message: __('No Item found for Serial No {0}', [row.issued_serial_no]),
                        indicator: 'red'
                    });
                    frappe.model.set_value(cdt, cdn, 'issued_item_code', null);
                    return;
                }

                // Set fetched item
                frappe.model.set_value(cdt, cdn, 'issued_item_code', r.item_code);

                // Mark replacement issued
                frappe.model.set_value(cdt, cdn, 'replacement_issued', 1);
            }
        );
    }
});
