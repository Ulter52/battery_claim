frappe.dashboards.chart_sources["Replacement Trend"] = {
    method: "battery_claim.battery_claim.dashboard_chart_source.replacement_trend.replacement_trend.get",

    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(
                frappe.datetime.get_today(),
                -12
            ),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
    ],
};
