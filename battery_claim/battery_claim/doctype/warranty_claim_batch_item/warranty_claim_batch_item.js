// Copyright (c) 2026, Dhirendra Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warranty Claim Batch Item', {
    project: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Clear fields first (safe reset)
        frappe.model.set_value(cdt, cdn, 'replacement_issued', 0);
        frappe.model.set_value(cdt, cdn, 'issued_item_code', '');
        frappe.model.set_value(cdt, cdn, 'issued_serial_no', '');
        frappe.model.set_value(cdt, cdn, 'delivery_note', '');

        if (!row.project) {
            return;
        }

        // Fetch Delivery Note linked to this Project
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Delivery Note',
                filters: {
                    project: row.project,
                    docstatus: 1
                },
                fields: ['name'],
                limit_page_length: 1
            },
            callback: function (r) {
                if (!r.message || r.message.length === 0) {
                    // No replacement issued yet
                    return;
                }

                let dn_name = r.message[0].name;

                // Fetch Delivery Note Item details
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Delivery Note Item',
                        filters: {
                            parent: dn_name
                        },
                        fields: ['item_code', 'serial_no'],
                        limit_page_length: 1
                    },
                    callback: function (res) {
                        if (!res.message || res.message.length === 0) {
                            return;
                        }

                        let item = res.message[0];

                        frappe.model.set_value(cdt, cdn, 'replacement_issued', 1);
                        frappe.model.set_value(cdt, cdn, 'issued_item_code', item.item_code);
                        frappe.model.set_value(cdt, cdn, 'issued_serial_no', item.serial_no || '');
                        frappe.model.set_value(cdt, cdn, 'delivery_note', dn_name);
                    }
                });
            }
        });
    }
});
