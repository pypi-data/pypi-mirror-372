import clearskies
from clearskies import columns, validators

import clearskies_akeyless_custom_producer
from clearskies_akeyless_custom_wiz.create import create
from clearskies_akeyless_custom_wiz.rotate import rotate

class PayloadSchema(clearskies.Schema):
    clientId = columns.String(
        validators=[validators.Required()]
    )
    clientSecret = columns.String(
        validators=[validators.Required()]
    )

def build_wiz_producer(url: str = "") -> clearskies_akeyless_custom_producer.endpoints.NoInput:
    return clearskies_akeyless_custom_producer.endpoints.NoInput(
        create_callable=create,
        rotate_callable=rotate,
        payload_schema=PayloadSchema,
        url=url,
    )
