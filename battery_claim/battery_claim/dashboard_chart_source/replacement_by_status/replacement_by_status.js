frappe.provide("frappe.dashboards");
frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Replacement by Status"] = {
	method: "battery_claim.battery_claim.dashboard_chart_source.replacement_by_status.replacement_by_status.get",

	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
	],
};
