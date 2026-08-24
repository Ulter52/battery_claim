frappe.provide("frappe.dashboards");
frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Replacement Process TAT"] = {
	method: "battery_claim.battery_claim.dashboard_chart_source.replacement_process_tat.replacement_process_tat.get",

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
