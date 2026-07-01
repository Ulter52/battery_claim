// Copyright (c) 2026, Dhirendra Sharma and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Battery Warranty Claim", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Battery Warranty Claim", {

	refresh(frm) {

		update_ui(frm);

		toggle_customer_fields(
			frm,
			frm.doc.serial_exists_in_system
		);

		if (frm.is_new()) {
			return;
		}

		// Reload once if Delivery Note automation
		// has not yet updated the issued serial.
		if (
			frm.doc.docstatus === 1 &&
			frm.doc.delivery_note &&
			!frm.doc.issued_serial_no &&
			!frm.__reload_once
		) {

			frm.__reload_once = true;
			frm.reload_doc();
			return;
		}

		load_lifecycle(frm);
	},

	claim_type(frm) {
		update_ui(frm);
	},

	dealer_has_replaced(frm) {
		update_ui(frm);
	},

	fulfillment_method(frm) {
		update_ui(frm);
	},

	existing_serial_no(frm) {

		if (!frm.doc.existing_serial_no) {
			return;
		}

		frm.set_value(
			"defective_serial_no",
			frm.doc.existing_serial_no
		);

		lookup_serial(frm);

	}

});


// ----------------------------------------------------
// UI
// ----------------------------------------------------

function update_ui(frm) {

	update_dealer_ui(frm);

	update_fulfillment_ui(frm);

	update_credit_note_ui(frm);

}


function update_dealer_ui(frm) {

	const dealer_replacement =
		frm.doc.claim_type === "Dealer Replacement";

	frm.toggle_display(
		"dealer_has_replaced",
		dealer_replacement
	);

	const dealer_replaced =
		dealer_replacement &&
		frm.doc.dealer_has_replaced;

	if (dealer_replaced) {

		frm.set_value(
			"fulfillment_method",
			"Dealer Stock"
		);

		frm.set_value(
			"customer_type",
			"Dealer"
		);

		frm.set_df_property(
			"fulfillment_method",
			"read_only",
			1
		);

	}
	else {

		frm.set_df_property(
			"fulfillment_method",
			"read_only",
			0
		);

	}

	[
		"installed_item_code",
		"installed_serial_no",
		"installed_date"
	].forEach(field => {

		frm.toggle_display(
			field,
			dealer_replaced
		);

	});

	frm.set_df_property(
		"installed_item_code",
		"reqd",
		dealer_replaced
	);

	frm.set_df_property(
		"installed_serial_no",
		"reqd",
		dealer_replaced
	);

}


function update_fulfillment_ui(frm) {

	const store_stock =
		frm.doc.fulfillment_method === "Store Stock" &&
		!(
			frm.doc.claim_type === "Dealer Replacement" &&
			frm.doc.dealer_has_replaced
		);

	frm.toggle_display(
		"fulfillment_warehouse",
		store_stock
	);

}


function update_credit_note_ui(frm) {

	const credit_note =
		frm.doc.fulfillment_method === "Credit Note";

	[
		"credit_note_no",
		"credit_amount",
		"credit_date"
	].forEach(field => {

		frm.toggle_display(
			field,
			credit_note
		);

	});

}


// ----------------------------------------------------
// Serial Lookup
// ----------------------------------------------------

function lookup_serial(frm) {

	if (!frm.doc.defective_serial_no) {
		return;
	}

	frappe.call({

		method:
			"battery_claim.battery_claim.doctype.battery_warranty_claim.battery_warranty_claim.get_serial_details",

		args: {
			serial_no: frm.doc.defective_serial_no
		},

		callback(r) {

			if (!r.message) {
				return;
			}

			populate_serial_history(
				frm,
				r.message
			);

			populate_customer(
				frm,
				r.message
			);

			toggle_customer_fields(
				frm,
				r.message.serial_exists_in_system
			);

			frappe.show_alert({

				message:
					r.message.serial_exists_in_system
						? __("Serial found.")
						: __("Serial not found."),

				indicator:
					r.message.serial_exists_in_system
						? "green"
						: "orange"

			});

		}

	});

}


// ----------------------------------------------------
// Serial History
// ----------------------------------------------------

function populate_serial_history(frm, data) {

	frm.set_value(
		"serial_exists_in_system",
		data.serial_exists_in_system || 0
	);

	frm.set_value(
		"defective_item_code",
		data.defective_item_code || ""
	);

	frm.set_value(
		"warranty_expiry_date",
		data.warranty_expiry_date || ""
	);

	frm.set_value(
		"inward_voucher_type",
		data.inward_voucher_type || ""
	);

	frm.set_value(
		"inward_voucher_no",
		data.inward_voucher_no || ""
	);

	frm.set_value(
		"outward_voucher_type",
		data.outward_voucher_type || ""
	);

	frm.set_value(
		"outward_voucher_no",
		data.outward_voucher_no || ""
	);

}


// ----------------------------------------------------
// Customer
// ----------------------------------------------------

function populate_customer(frm, data) {

	frm.set_value(
		"customer",
		data.customer || ""
	);

	frm.set_value(
		"customer_name",
		data.customer_name || ""
	);

	frm.set_value(
		"customer_type",
		data.customer_type || ""
	);

	frm.set_value(
		"customer_mobile_no",
		data.mobile_no || ""
	);

}


// ----------------------------------------------------
// Read Only
// ----------------------------------------------------

function toggle_customer_fields(frm, found) {

	[
		"customer",
		"customer_name",
		"customer_type",
		"customer_mobile_no",
		"defective_item_code"
	].forEach(field => {

		frm.set_df_property(
			field,
			"read_only",
			found ? 1 : 0
		);

	});

}


// ----------------------------------------------------
// Lifecycle
// ----------------------------------------------------

function load_lifecycle(frm) {

	frappe.call({

		method:
			"battery_claim.api.battery_warranty_claim_wrapper.get_available_actions",

		args: {
			claim: frm.doc.name
		},

		callback(r) {

			frm.lifecycle = r.message || {};

			add_create_buttons(frm);

			add_view_buttons(frm);

		}

	});

}


// ----------------------------------------------------
// Create Buttons
// ----------------------------------------------------

function add_create_buttons(frm) {

	const actions = frm.lifecycle || {};

	// -----------------------------------
	// Warranty Approval
	// -----------------------------------

	if (actions.can_create_approval) {

		frm.add_custom_button(

			__("Warranty Approval"),

			function () {

				frappe.new_doc(
					"Warranty Approval",
					{
						battery_warranty_claim: frm.doc.name
					}
				);

			},

			__("Create")

		);

	}

	// -----------------------------------
	// Delivery Note
	// -----------------------------------

	if (actions.can_create_delivery_note) {

		frm.add_custom_button(

			__("Delivery Note"),

			function () {

				frappe.call({

					method:
						"battery_claim.battery_claim.doctype.battery_warranty_claim.battery_warranty_claim.create_delivery_note",

					args: {
						claim: frm.doc.name
					},

					callback(r) {

						if (r.message) {

							frappe.set_route(
								"Form",
								"Delivery Note",
								r.message
							);

						}

					}

				});

			},

			__("Create")

		);

	}

	// -----------------------------------
	// Purchase Receipt
	// -----------------------------------

	if (actions.can_create_purchase_receipt) {

		frm.add_custom_button(

			__("Purchase Receipt"),

			function () {

				frappe.call({

					method:
						"battery_claim.battery_claim.doctype.battery_warranty_claim.battery_warranty_claim.create_purchase_receipt",

					args: {
						claim: frm.doc.name
					},

					callback(r) {

						if (r.message) {

							frappe.set_route(
								"Form",
								"Purchase Receipt",
								r.message
							);

						}

					}

				});

			},

			__("Create")

		);

	}

}


// ----------------------------------------------------
// View Buttons
// ----------------------------------------------------

function add_view_buttons(frm) {

	const actions = frm.lifecycle || {};

	// -----------------------------------
	// Warranty Approval
	// -----------------------------------

	if (
		actions.can_open_approval &&
		actions.warranty_approval
	) {

		frm.add_custom_button(

			__("Warranty Approval"),

			function () {

				frappe.set_route(
					"Form",
					"Warranty Approval",
					actions.warranty_approval
				);

			},

			__("View")

		);

	}

	// -----------------------------------
	// Delivery Note
	// -----------------------------------

	if (
		actions.can_open_delivery_note &&
		actions.delivery_note
	) {

		frm.add_custom_button(

			__("Delivery Note"),

			function () {

				frappe.set_route(
					"Form",
					"Delivery Note",
					actions.delivery_note
				);

			},

			__("View")

		);

	}

	// -----------------------------------
	// Warranty Claim Batch
	// -----------------------------------

	if (
		actions.can_open_batch &&
		actions.warranty_claim_batch
	) {

		frm.add_custom_button(

			__("Warranty Claim Batch"),

			function () {

				frappe.set_route(
					"Form",
					"Warranty Claim Batch",
					actions.warranty_claim_batch
				);

			},

			__("View")

		);

	}

	// -----------------------------------
	// Purchase Receipt
	// -----------------------------------

	if (
		actions.can_open_purchase_receipt &&
		actions.purchase_receipt
	) {

		frm.add_custom_button(

			__("Purchase Receipt"),

			function () {

				frappe.set_route(
					"Form",
					"Purchase Receipt",
					actions.purchase_receipt
				);

			},

			__("View")

		);

	}

}
