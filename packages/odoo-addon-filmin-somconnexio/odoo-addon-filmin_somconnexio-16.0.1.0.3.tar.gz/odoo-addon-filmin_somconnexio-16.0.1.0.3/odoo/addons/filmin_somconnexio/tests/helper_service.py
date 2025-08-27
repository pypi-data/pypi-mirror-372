from odoo.addons.somconnexio.tests.helper_service import contract_create_data


def contract_filmin_create_data(odoo_env, partner):
    vals = contract_create_data(partner)
    vals.update(
        {
            "name": "Test Contract Filmin",
            "service_technology_id": odoo_env.ref(
                "multimedia_somconnexio.service_technology_multimedia"
            ).id,
            "service_supplier_id": odoo_env.ref(
                "filmin_somconnexio.service_supplier_filmin"
            ).id,
        }
    )
    return vals
