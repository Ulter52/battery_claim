from battery_claim.custom_fields import create_warranty_custom_fields


def after_install():

    create_warranty_custom_fields()
