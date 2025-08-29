import json
from datetime import datetime, timezone
from unittest import TestCase

from pydantic import ValidationError
from pydantic.types import UUID

from oc_python_sdk.models.application import APaymentData, Applicant, Application

from ._helpers import (
    get_application_data,
    get_application_minimal_applicant_data,
    get_application_payment_data,
    get_split_data_invalid,
)

NOW = datetime(2022, 9, 19, 16, 0, 0, tzinfo=timezone.utc)


class ApplicationTestCase(TestCase):
    def test_creation(self):
        application = Application(**get_application_data())
        payment_data_v2 = APaymentData(**get_application_payment_data(split=get_split_data_invalid()))
        application_v2 = Application(**get_application_data(payment_data=payment_data_v2))
        payment_data_empty_split = APaymentData(**get_application_payment_data(split=[]))
        payment_data_empty_stamps = APaymentData(**get_application_payment_data(stamps=[]))
        applicant_minimal_data = Applicant(**get_application_minimal_applicant_data())
        self.assertEqual(application.id, UUID('3c819c1d-6587-448d-8ba4-3b6f23e87ed4'))
        self.assertEqual(application_v2.payment_data.split, {'c_1': 14.0, 'c_2': None})
        self.assertEqual(payment_data_empty_split.split, [])
        self.assertEqual(payment_data_empty_stamps.stamps, [])
        with self.assertRaises(ValidationError):
            APaymentData(
                **get_application_payment_data(
                    split='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt '
                    'ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco '
                    'laboris nisi ut aliquip ex ea commodo consequat.',
                ),
            )
        self.assertEqual(
            json.loads(applicant_minimal_data.json()),
            {
                'email_address': None,
                'natoAIl': None,
                'place_of_birth': None,
                'gender': None,
                'address': None,
                'house_number': None,
                'municipality': None,
                'county': None,
                'postal_code': None,
                'name': 'Vittorino',
                'surname': 'Coliandro',
                'fiscal_code': 'CLNVTR76P01G822Q',
            },
        )
