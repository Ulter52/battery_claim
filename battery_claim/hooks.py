app_name = "battery_claim"
app_title = "Battery Claim"
app_publisher = "Dhirendra Sharma"
app_description = "Track battery claim through native project and its DN and PR and reconcile the claim."
app_email = "dhirendrasharm1305@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "battery_claim",
# 		"logo": "/assets/battery_claim/logo.png",
# 		"title": "Battery Claim",
# 		"route": "/battery_claim",
# 		"has_permission": "battery_claim.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/battery_claim/css/battery_claim.css"
# app_include_js = "/assets/battery_claim/js/battery_claim.js"

# include js, css files in header of web template
# web_include_css = "/assets/battery_claim/css/battery_claim.css"
# web_include_js = "/assets/battery_claim/js/battery_claim.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "battery_claim/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "battery_claim/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "battery_claim.utils.jinja_methods",
# 	"filters": "battery_claim.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "battery_claim.install.before_install"
# after_install = "battery_claim.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "battery_claim.uninstall.before_uninstall"
# after_uninstall = "battery_claim.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "battery_claim.utils.before_app_install"
# after_app_install = "battery_claim.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "battery_claim.utils.before_app_uninstall"
# after_app_uninstall = "battery_claim.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "battery_claim.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
doc_events = {
    "Purchase Receipt": {
        "on_submit": "battery_claim.battery_claim.doctype.warranty_claim_batch.warranty_claim_batch.update_warranty_claim_batch_from_pr",
        "on_cancel": "battery_claim.battery_claim.doctype.warranty_claim_batch.warranty_claim_batch.rollback_warranty_claim_batch_from_pr",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"battery_claim.tasks.all"
# 	],
# 	"daily": [
# 		"battery_claim.tasks.daily"
# 	],
# 	"hourly": [
# 		"battery_claim.tasks.hourly"
# 	],
# 	"weekly": [
# 		"battery_claim.tasks.weekly"
# 	],
# 	"monthly": [
# 		"battery_claim.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "battery_claim.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "battery_claim.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "battery_claim.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "battery_claim.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["battery_claim.utils.before_request"]
# after_request = ["battery_claim.utils.after_request"]

# Job Events
# ----------
# before_job = ["battery_claim.utils.before_job"]
# after_job = ["battery_claim.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"battery_claim.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

