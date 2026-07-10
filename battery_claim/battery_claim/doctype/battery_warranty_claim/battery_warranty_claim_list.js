frappe.listview_settings["Battery Warranty Claim"] = {
        add_fields: ["claim_status"],
	get_indicator(doc) {
		//add_fields: ["claim_status"],
		const colors = {
			"Approval Pending": "gray",
			"Approved": "blue",
			"Replaced": "purple",
			"Dispatched": "orange",
			"Stock Received": "cyan",
			"Closed": "green",
			"Credit Note Issued": "pink",
			"Cancelled": "red"
		};

		return [
			__(doc.claim_status),
			colors[doc.claim_status] || "gray",
			`claim_status,=,${doc.claim_status}`
		];

	}

};
