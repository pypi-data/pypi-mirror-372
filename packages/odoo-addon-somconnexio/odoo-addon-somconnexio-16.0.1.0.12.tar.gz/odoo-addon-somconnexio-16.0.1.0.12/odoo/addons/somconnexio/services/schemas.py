from odoo.addons.base_rest_somconnexio.services.validator_helper import (
    boolean_validator,
)

S_ADDRESS_CREATE = {
    "street": {"type": "string", "required": True, "empty": False},
    "street2": {"type": "string"},
    "zip_code": {"type": "string", "required": True, "empty": False},
    "city": {"type": "string", "required": True, "empty": False},
    "country": {"type": "string", "required": True, "empty": False},
    "state": {"type": "string"},
}

S_PREVIOUS_PROVIDER_REQUEST_SEARCH = {
    "mobile": {"type": "string", "check_with": boolean_validator},
    "broadband": {"type": "string", "check_with": boolean_validator},
}

S_PREVIOUS_PROVIDER_RETURN_SEARCH = {
    "count": {"type": "integer"},
    "providers": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "id": {"type": "integer", "required": True},
                "name": {"type": "string", "required": True},
            },
        },
    },
}

S_PRODUCT_CATALOG_REQUEST_SEARCH = {
    "code": {"type": "string"},
    "categ": {
        "type": "string",
        "allowed": ["mobile", "adsl", "fiber", "4G"],
        "excludes": ["product_code"],
    },
    "product_code": {
        "type": "string",
        "excludes": ["categ", "is_company"],
    },
    "is_company": {
        "type": "string",
        "excludes": ["product_code"],
        "check_with": boolean_validator,
    },
}

S_PRODUCT_RETURN_VALUES = {
    "code": {"type": "string", "required": True},
    "name": {"type": "string", "required": True},
    "price": {"type": "number", "required": True},
    "category": {"type": "string", "required": True},
    "minutes": {"type": "integer", "nullable": True, "required": True},
    "data": {"type": "integer", "nullable": True, "required": True},
    "bandwidth": {"type": "integer", "nullable": True, "required": True},
    "has_landline_phone": {"type": "boolean"},
}

S_PRODUCT_CATALOG_RETURN_SEARCH = {
    "pricelists": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "code": {"type": "string", "required": True},
                "products": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "offer": {
                                "type": "dict",
                                "schema": {
                                    "code": {"type": "string", "required": True},
                                    "price": {"type": "number", "required": True},
                                    "name": {"type": "string", "required": True},
                                },
                                "required": False,
                            },
                            **S_PRODUCT_RETURN_VALUES,
                        },
                    },
                },
                "packs": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "code": {"type": "string", "required": True},
                            "name": {"type": "string", "required": True},
                            "price": {"type": "number", "required": True},
                            "category": {"type": "string", "required": True},
                            "mobiles_in_pack": {"type": "number", "required": True},
                            "fiber_bandwidth": {"type": "number", "required": True},
                            "has_land_line": {"type": "boolean", "required": True},
                            "products": {
                                "type": "list",
                                "schema": {
                                    "type": "dict",
                                    "schema": {**S_PRODUCT_RETURN_VALUES},
                                },
                            },
                        },
                    },
                },
            },
        },
    }
}

S_ONE_SHOT_CATALOG_REQUEST_SEARCH = {
    "code": {"type": "string"},
    "product_code": {"type": "string"},
}


S_ONE_SHOT_CATALOG_RETURN_SEARCH = {
    "pricelists": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "code": {"type": "string", "required": True},
                "one_shots": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "code": {"type": "string", "required": True},
                            "name": {"type": "string", "required": True},
                            "price": {"type": "number", "required": True},
                            "minutes": {
                                "type": "integer",
                                "nullable": True,
                                "required": True,
                            },
                            "data": {
                                "type": "integer",
                                "nullable": True,
                                "required": True,
                            },
                        },
                    },
                },
            },
        },
    }
}


S_ACCOUNT_INVOICE_CREATE = {
    "billingAccountCode": {
        "type": "string",
        "required": True,
        "regex": "^[0-9]+_[0-9]+$",
    },
    "invoiceNumber": {"type": "string", "required": True},
    "invoiceDate": {
        "type": "integer",
        "required": True,
    },
    "amountWithoutTax": {"type": "float", "required": True},
    "amountTax": {"type": "float", "required": True},
    "amountWithTax": {"type": "float", "required": True},
    "categoryInvoiceAgregates": {
        "type": "list",
        "required": True,
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": {
                "listSubCategoryInvoiceAgregateDto": {
                    "type": "list",
                    "required": True,
                    "empty": False,
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "description": {"type": "string", "required": True},
                            "accountingCode": {"type": "string", "required": True},
                            "amountWithoutTax": {"type": "float", "required": True},
                            "amountWithTax": {"type": "float", "required": True},
                            "amountTax": {"type": "float", "required": True},
                            "taxCode": {"type": "string", "required": True},
                            "invoiceSubCategoryCode": {
                                "type": "string",
                                "required": True,
                            },
                        },
                    },
                }
            },
        },
    },
    "taxAggregates": {
        "type": "list",
        "required": True,
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": {
                "taxCode": {"type": "string", "required": True},
                "amountTax": {"type": "float", "required": True},
                "amountWithoutTax": {"type": "float", "required": True},
            },
        },
    },
}

S_CONTRACT_IBAN_CHANGE_CREATE = {
    "partner_id": {"type": "string", "required": True},
    "iban": {"type": "string", "required": True},
    "contracts": {"type": "string", "required": False},
    "ticket_id": {"type": "string", "required": False},
}

S_PARTNER_EMAIL_CHANGE_CREATE = {
    "partner_id": {"type": "string", "required": True},
    "email": {"type": "string", "required": True},
    "start_date": {"type": "string"},
    "summary": {"type": "string"},
    "done": {"type": "boolean"},
}

S_CONTRACT_EMAIL_CHANGE_CREATE = {
    "partner_id": {"type": "string", "required": True},
    "email": {"type": "string", "required": True},
    "contracts": {"type": ["dict", "string"], "required": True},
    "start_date": {"type": "string"},
    "summary": {"type": "string"},
    "done": {"type": "boolean"},
}

S_CONTRACT_PAGING = {
    "limit": {
        "type": "string",
    },
    "offset": {
        "type": "string",
    },
    "sortBy": {
        "type": "string",
    },
    "sortOrder": {"type": "string", "dependencies": ["sortBy"]},
}

S_CUSTOMER_CONTRACT_MULTI_FILTER_SEARCH = {
    "customer_ref": {"type": "string", "required": True},
    "phone_number": {
        "type": "string",
        "dependencies": "customer_ref",
    },
    "subscription_type": {
        "type": "string",
        "dependencies": "customer_ref",
        "allowed": ["mobile", "broadband"],
    },
    **S_CONTRACT_PAGING,
}

S_CONTRACT_SEARCH = {
    "customer_ref": {
        "type": "string",
        "excludes": ["code", "partner_vat", "phone_number"],
        "required": True,
    },
    "code": {
        "type": "string",
        "excludes": ["partner_vat", "phone_number", "customer_ref"],
        "required": True,
    },
    "partner_vat": {
        "type": "string",
        "excludes": ["code", "phone_number", "customer_ref"],
        "required": True,
    },
    "phone_number": {
        "type": "string",
        "excludes": ["partner_vat", "code", "customer_ref"],
        "required": True,
    },
    **S_CONTRACT_PAGING,
}

S_CONTRACT_GET_FIBER_CONTRACTS_TO_PACK = {
    "partner_ref": {
        "type": "string",
        "required": True,
    },
    "mobiles_sharing_data": {
        "type": "string",
        "excludes": ["all"],
        "check_with": boolean_validator,
    },
    "all": {
        "type": "string",
        "excludes": ["mobiles_sharing_data"],
        "check_with": boolean_validator,
    },
}

S_TERMINATE_CONTRACT = {
    "code": {
        "type": "string",
        "required": True,
        "empty": False,
    },
    "terminate_date": {
        "type": "string",
        "required": True,
        "empty": False,
    },
    "terminate_reason": {
        "type": "string",
        "required": True,
        "empty": False,
    },
    "terminate_user_reason": {
        "type": "string",
        "required": False,
    },
    "terminate_comment": {
        "type": "string",
        "required": False,
    },
}

S_CONTRACT_ROUTER_MAC_ADDRESS_CREATE = {
    "router_mac_address": {
        "type": "string",
        "required": False,
        "empty": True,
        "regex": "-|^[0-9A-F]{2}([-:]?)[0-9A-F]{2}(\\1[0-9A-F]{2}){4}$",
    },
}
