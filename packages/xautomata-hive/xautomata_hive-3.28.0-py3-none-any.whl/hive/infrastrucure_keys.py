# from types import MappingProxyType

class Keys:
    customer_keys = {
        "univocal": ["code"],
        "mandatory": {"code": {"len": 16, "unique": True},  # unica
                      "company_name": {"len": 128},
                      "address": {"len": 64},
                      "zip_code": {"len": 8},
                      "city": {"len": 32},
                      "country": {"len": 3},
                      "status": {"len": 1}},
        "optional": {"type": {"len": 8},
                     "notes": {"len": 255},
                     "vat_id": {"len": 32},
                     "currency": {"len": 3},
                     "state_province": {"len": 32},
                     "registration_date": {"type": "date"},
                     "paying_customer": {"type": "bool"}}
    }

    virtual_domain_keys = {
        "univocal": ["code"],
        "mandatory": {"code": {"len": 32, "unique": True}},  # unico
        "optional": {"description": {"len": 64}}
    }

    site_keys = {
        "univocal": ["uuid_customer", "code"],
        "backtrace": {"uuid_customer": ["customer code"]},
        "mandatory": {"code": {"len": 16, "unique": True},  # unico
                      "description": {"len": 128},
                      "address": {"len": 64},
                      "zip_code": {"len": 8},
                      "city": {"len": 64},  # recentemente alzato da 32 (26/05/2023)
                      "country": {"len": 3},
                      "state_province": {"len": 32},
                      "status": {"len": 1}},
        "optional": {"type": {"len": 8},
                     "notes": {"len": 255}}
    }

    group_keys = {
        "univocal": ["uuid_site", "uuid_virtual_domain", "name"],
        "backtrace": {"uuid_site": ["customer code", "site code"], "uuid_virtual_domain": ["virtual_domain code"]},
        "mandatory": {"type": {"len": 8},
                      "name": {"len": 255, "unique": True},  # univo con la tripla uuid_stie, uuid_vd
                      "description": {"len": 255},
                      "status": {"len": 8}},
        "optional": {"automata_domain": {"type": 'list'}}
    }

    object_keys = {
        "univocal": ["name"],
        "mandatory": {"name": {"len": 255, "unique": True},  # unico
                      "profile": {"len": 64},
                      "status": {"len": 1}},
        "optional": {"description": {"len": 255},
                     "feedback_for_operator": {"len": 255},
                     "ip_cidr": {"type": "dict"},
                     "data_profile": {"type": "dict"}}
    }

    metric_type_keys = {
        # uuid_object -> relazione NON univoca
        "univocal": ["uuid_object", "name"],
        "backtrace": {"uuid_object": ["object name"]},
        "mandatory": {"name": {"len": 255},
                      "profile": {"len": 64},
                      "status": {"len": 1}},
        "optional": {"description": {"len": 255},
                     "feedback_for_operator": {"len": 255},
                     "data_profile": {"type": "dict"}}
    }

    metric_keys = {
        # uuid_metric_type -> relazione NON univoca
        "univocal": ["uuid_metric_type", "name"],
        "backtrace": {"uuid_metric_type": ["object name", "metric_type name"]},
        "mandatory": {"name": {"len": 255},
                      "profile": {"len": 64},
                      "status": {"len": 1}},
        "optional": {"description": {"len": 255},
                     "feedback_for_operator": {"len": 255},
                     "data_profile": {"type": "dict"}}
    }

    service_keys = {
        # uuid_parend?
        "univocal": ['uuid_customer', 'name', 'profile'],
        "backtrace": {"uuid_customer": ["customer code"]},
        "mandatory": {'profile': {'len': 64},
                      'name': {'len': 255},
                      'description': {'len': 255},
                      'status': {'len': 1}},
        "optional": {'uuid_parent': {'type': 'uuid'},
                     'automata_domain': {'type': 'list'},
                     'rule': {'type': 'list'}
                     }
    }