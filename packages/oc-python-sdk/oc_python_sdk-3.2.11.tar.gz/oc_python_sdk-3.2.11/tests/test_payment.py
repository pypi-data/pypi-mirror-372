import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest import TestCase

from freezegun import freeze_time
from pydantic.error_wrappers import ValidationError
from pydantic.types import UUID

from oc_python_sdk.models.payment import (
    CurrencyType,
    Document,
    HttpMethodType,
    Links,
    Notify,
    OnlinePaymentBegin,
    Payer,
    PayerType,
    Payment,
    PaymentData,
    PaymentDataSplit,
    PaymentStatus,
    PaymentType,
    Receiver,
    Update,
)

from ._helpers import (
    get_document,
    get_empty_notify_data,
    get_links_data,
    get_links_data_without_cancel_and_confirm,
    get_notify_data,
    get_online_payment_begin_data,
    get_payer_data,
    get_payment_data,
    get_payment_event_data,
    get_receiver,
    get_split_data,
    get_split_data_complete,
    get_split_data_invalid,
    get_update_data,
)

NOW = datetime(2022, 9, 19, 16, 0, 0, tzinfo=timezone.utc)


class PaymentTestCase(TestCase):
    def test_creation(self):
        # Creiamo un oggetto Payment utilizzando il JSON fornito
        payment = Payment(**get_payment_event_data())

        # Verifichiamo che l'oggetto sia stato creato correttamente
        self.assertEqual(payment.id, UUID('bb7044e4-066c-4bf7-915e-87ee97270eae'))
        self.assertEqual(payment.user_id, UUID('f3323b10-db62-4aeb-95de-a87c1f678dad'))
        self.assertEqual(payment.tenant_id, UUID('60e35f02-1509-408c-b101-3b1a28109329'))
        self.assertEqual(payment.remote_id, UUID('218d7772-a747-4d5f-8c56-bbc7cfeab1a0'))
        self.assertEqual(payment.created_at, datetime.fromisoformat('2024-02-19T15:50:23+01:00'))
        self.assertEqual(payment.updated_at, datetime.fromisoformat('2024-02-20T15:05:16+01:00'))
        self.assertEqual(payment.status, PaymentStatus.STATUS_PAYMENT_PENDING)
        self.assertEqual(payment.remote_id, UUID('218d7772-a747-4d5f-8c56-bbc7cfeab1a0'))
        self.assertEqual(payment.reason, 'bla')
        self.assertEqual(payment.payment.transaction_id, None)
        self.assertIsNone(payment.payment.paid_at)
        self.assertEqual(payment.payment.expire_at, datetime.fromisoformat('2023-09-04T11:59:05+02:00'))
        self.assertEqual(payment.payment.amount, 16.50)
        self.assertEqual(payment.payment.currency, CurrencyType.CURRENCY_EUR)
        self.assertEqual(payment.payment.type, PaymentType.TYPE_STAMP)
        self.assertEqual(payment.payment.notice_code, '001550000000024427')
        self.assertEqual(payment.payment.iud, '68dada7823984a11b80a98aaede3371c')
        self.assertEqual(payment.payment.iuv, '550000000024427')
        self.assertEqual(payment.payment.receiver.tax_identification_number, '777777777')
        self.assertEqual(payment.payment.receiver.name, 'Comune di BlaBla')
        self.assertEqual(payment.payment.receiver.iban, 'IT60X0542811101000000123456')
        self.assertEqual(payment.payment.receiver.address, 'Via Del Campo')
        self.assertEqual(payment.payment.receiver.building_number, '12')
        self.assertEqual(payment.payment.receiver.postal_code, '38022')
        self.assertEqual(payment.payment.receiver.town_name, 'Roma')
        self.assertEqual(payment.payment.receiver.country_subdivision, 'RM')
        self.assertEqual(payment.payment.receiver.country, 'IT')
        self.assertEqual(payment.payment.due_type, 'TARI')
        self.assertEqual(payment.payment.pagopa_category, '9/12129/TS')
        self.assertIsNotNone(payment.payment.document)
        self.assertEqual(len(payment.payment.split), 2)
        self.assertEqual(payment.payment.split[0].code, 'c_1')
        self.assertEqual(payment.payment.split[0].amount, 9)
        self.assertEqual(payment.payment.split[0].meta, {})
        self.assertEqual(payment.payment.split[1].code, 'c_2')
        self.assertEqual(payment.payment.split[1].amount, 7.5)
        self.assertEqual(payment.payment.split[1].meta, {})

        # Asserzioni per l'oggetto Links
        self.assertEqual(
            payment.links.online_payment_begin.url,
            'https://example.com/online-payment/0452545f-40a9-4366-99b6-bbfb2b17b405',
        )
        self.assertIsNone(payment.links.online_payment_begin.last_opened_at)
        self.assertEqual(payment.links.online_payment_begin.method, HttpMethodType.HTTP_METHOD_GET)
        self.assertEqual(
            payment.links.online_payment_landing.url,
            'https://example.com/lang/it/pratiche/1a9190cc-25cc-447c-a670-8d828dc0d1ea/detail',
        )
        self.assertIsNone(payment.links.online_payment_landing.last_opened_at)
        self.assertEqual(payment.links.online_payment_landing.method, HttpMethodType.HTTP_METHOD_GET)
        self.assertEqual(
            payment.links.offline_payment.url,
            'https://example.com/notice/0452545f-40a9-4366-99b6-bbfb2b17b405',
        )
        self.assertIsNone(payment.links.offline_payment.last_opened_at)
        self.assertEqual(payment.links.offline_payment.method, HttpMethodType.HTTP_METHOD_GET)
        self.assertEqual(
            payment.links.receipt.url,
            'https://example.com/receipt/0452545f-40a9-4366-99b6-bbfb2b17b405',
        )
        self.assertIsNone(payment.links.receipt.last_opened_at)
        self.assertEqual(payment.links.receipt.method, HttpMethodType.HTTP_METHOD_GET)
        self.assertEqual(
            payment.links.notify[0].url,
            'https://example.com/lang/api/applications/1a9190cc-25cc-447c-a670-8d828dc0d1ea/payment',
        )
        self.assertEqual(payment.links.notify[0].method, HttpMethodType.HTTP_METHOD_POST)
        self.assertIsNone(payment.links.notify[0].sent_at)
        self.assertEqual(payment.links.update.url, None)
        self.assertEqual(payment.links.update.last_check_at, None)
        self.assertEqual(payment.links.update.next_check_at, None)
        self.assertEqual(payment.links.update.method, HttpMethodType.HTTP_METHOD_GET)

        # Asserzioni per gli oggetti Payer e Debtor
        self.assertEqual(payment.payer.type, PayerType.TYPE_HUMAN)
        self.assertEqual(payment.payer.tax_identification_number, 'BNRMHL75C06G702B')
        self.assertEqual(payment.payer.name, 'Michelangelo')
        self.assertEqual(payment.payer.family_name, 'Buonarroti')
        self.assertEqual(payment.payer.street_name, 'Cesare Battisti')
        self.assertEqual(payment.payer.building_number, '')
        self.assertEqual(payment.payer.postal_code, '38010')
        self.assertEqual(payment.payer.town_name, 'Bugliano')
        self.assertEqual(payment.payer.country_subdivision, 'PI')
        self.assertEqual(payment.payer.country, 'IT')
        self.assertEqual(payment.payer.email, 'user@example.com')
        self.assertEqual(payment.debtor.type, PayerType.TYPE_HUMAN)
        self.assertEqual(payment.debtor.tax_identification_number, 'BNRMHL75C06G702B')
        self.assertEqual(payment.debtor.name, 'Michelangelo')
        self.assertEqual(payment.debtor.family_name, 'Buonarroti')
        self.assertEqual(payment.debtor.street_name, 'Cesare Battisti')
        self.assertEqual(payment.debtor.building_number, '')
        self.assertEqual(payment.debtor.postal_code, '38010')
        self.assertEqual(payment.debtor.town_name, 'Bugliano')
        self.assertEqual(payment.debtor.country_subdivision, 'PI')
        self.assertEqual(payment.debtor.country, 'IT')
        self.assertEqual(payment.debtor.email, 'user@example.com')

        # Asserzione per gli attributi relativi all'evento
        self.assertEqual(payment.event_id, UUID('c80a2a33-577a-49a1-b578-0d2267ea5653'))
        self.assertEqual(payment.event_version, '2.0')
        self.assertEqual(payment.event_created_at, datetime.fromisoformat('2024-02-20T15:05:16+01:00'))

        # Asserzione per l'attributo app_id
        self.assertEqual(payment.app_id, 'mypay-payment-proxy:1.8.0')

    def test_payment_reason_length(self):
        with self.assertRaises(ValidationError):
            Payment(
                **get_payment_event_data(
                    reason='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. ',  # noqa
                ),
            )

    def test_payment_event_version(self):
        with self.assertRaises(ValidationError):
            Payment(**get_payment_event_data(event_version='X'))

    def test_iso_date(self):
        with self.assertRaises(ValidationError):
            Payment(**get_payment_event_data(created_at='non-valid-datetime'))

    def test_iso_date_null(self):
        with self.assertRaises(ValidationError):
            PaymentData(**get_payment_data(paid_at='non-valid-datetime'))

    def test_payment_creation(self):
        self.assertTrue(
            Payment(
                **get_payment_event_data(status=PaymentStatus.STATUS_CREATION_PENDING),
            ).is_payment_creation_needed(),
        )
        self.assertFalse(
            Payment(**get_payment_event_data(status=PaymentStatus.STATUS_COMPLETE)).is_payment_creation_needed(),
        )

    def test_update_time(self):
        payment = Payment(**get_payment_event_data())
        with freeze_time(NOW):
            payment.update_time('updated_at')
            self.assertEqual(payment.updated_at, NOW)

    def test_payment_update_time(self):
        payment = Payment(**get_payment_event_data())
        with freeze_time(NOW):
            payment.update_time('links.update.last_check_at')
            self.assertEqual(payment.links.update.last_check_at, NOW)

    def test_payment_update_check_time_missing_last_check_at(self):
        payment = Payment(**get_payment_event_data(created_at=NOW.isoformat()))
        with freeze_time(NOW):
            payment.update_check_time()
            self.assertEqual(payment.links.update.last_check_at, None)

    def test_payment_update_check_time(self):
        payment = Payment(**get_payment_event_data(created_at=NOW.isoformat()))
        with freeze_time(NOW):
            payment.update_time('links.update.last_check_at')
            payment.update_check_time()
            self.assertEqual(payment.links.update.next_check_at, NOW + timedelta(minutes=1))
        with freeze_time(NOW + timedelta(minutes=1)):
            payment.update_time('links.update.last_check_at')
            payment.update_check_time()
            self.assertEqual(payment.links.update.next_check_at, NOW + timedelta(minutes=1 + 1))
        with freeze_time(NOW + timedelta(minutes=15)):
            payment.update_time('links.update.last_check_at')
            payment.update_check_time()
            self.assertEqual(payment.links.update.next_check_at, NOW + timedelta(minutes=15 + 5))
        with freeze_time(NOW + timedelta(days=7)):
            payment.update_time('links.update.last_check_at')
            payment.update_check_time()
            self.assertEqual(payment.links.update.next_check_at, NOW + timedelta(days=7, hours=1))
        with freeze_time(NOW + timedelta(days=30)):
            payment.update_time('links.update.last_check_at')
            payment.update_check_time()
            self.assertEqual(payment.links.update.next_check_at, NOW + timedelta(days=30, hours=6))
        with freeze_time(NOW + timedelta(days=366)):
            payment.update_time('links.update.last_check_at')
            payment.update_check_time()
            self.assertEqual(payment.links.update.next_check_at, None)
            self.assertEqual(payment.status, PaymentStatus.STATUS_EXPIRED)

    def test_payer_country(self):
        with self.assertRaises(ValidationError):
            Payer(**get_payer_data(country='XX'))

    def test_encoders(self):
        payment = Payment(**get_payment_event_data())

        payment_empty_notify = Payment(**get_payment_event_data())
        payment_empty_notify.links.notify = None

        payment_data_with_split = payment.payment
        payment_data_with_split.split = get_split_data_complete()
        payment_with_split = Payment(**get_payment_event_data(payment=payment_data_with_split))

        payment_data = PaymentData(**get_payment_data())
        receiver = Receiver(**get_receiver())
        document = Document(**get_document())
        split = PaymentDataSplit(**get_split_data())
        online_payment_begin = OnlinePaymentBegin(**get_online_payment_begin_data())
        notify = Notify(**get_notify_data())
        notify_no_data = Notify(**get_empty_notify_data())
        update = Update(**get_update_data())
        links = Links(**get_links_data())
        links_without_cancel_and_confirm = Links(**get_links_data_without_cancel_and_confirm())
        payer = Payer(**get_payer_data())

        self.assertEqual(json.loads(payment.json())['id'], 'bb7044e4-066c-4bf7-915e-87ee97270eae')
        self.assertEqual(
            json.loads(payment_with_split.json())['payment']['split'],
            [
                {
                    'code': 'c_1',
                    'amount': 16.0,
                    'meta': {
                        'split_type': 'Tipo c1',
                        'split_code': 'Codice c1',
                        'split_description': 'Descrizione c1',
                        'split_budget_chapter': 'Capitolo di bilancio c1',
                        'split_assessment': 'Accertamento c1',
                    },
                },
                {
                    'code': 'c_2',
                    'amount': 0.5,
                    'meta': {
                        'split_type': 'Tipo c2',
                        'split_code': 'Codice c2',
                        'split_description': 'Descrizione c12',
                        'split_budget_chapter': 'Capitolo di bilancio c2',
                        'split_assessment': 'Accertamento c2',
                    },
                },
            ],
        )
        self.assertEqual(json.loads(payment.json())['created_at'], '2024-02-19T15:50:23+01:00')
        self.assertEqual(json.loads(payment.status.json()), PaymentStatus.STATUS_PAYMENT_PENDING.value)
        self.assertEqual(json.loads(payment.payer.type.json()), PayerType.TYPE_HUMAN.value)
        self.assertEqual(json.loads(payment.payment.currency.json()), CurrencyType.CURRENCY_EUR.value)
        self.assertEqual(json.loads(payment.links.notify[0].method.json()), HttpMethodType.HTTP_METHOD_POST.value)
        self.assertEqual(json.loads(payment_empty_notify.json())['links']['notify'], None)
        self.assertEqual(json.loads(split.json())['code'], 'CODE')
        self.assertEqual(json.loads(payment_data.json())['amount'], 16)
        self.assertEqual(json.loads(receiver.json())['tax_identification_number'], '777777777')
        self.assertEqual(json.loads(document.json())['ref'], 'http://example.com/api/documents/123')
        self.assertEqual(json.loads(online_payment_begin.json())['url'], None)
        self.assertEqual(
            json.loads(notify.json())['url'],
            'https://devsdc.opencontent.it/'
            'comune-di-bugliano/api/applications/'
            'a51cc065-4fb1-4ace-8d3f-e3a70c867472/payment',
        )
        self.assertEqual(json.loads(notify_no_data.json()), {'url': None, 'method': None, 'sent_at': None})
        self.assertEqual(json.loads(update.json())['url'], None)
        self.assertEqual(len(json.loads(links.json())['notify']), 1)
        self.assertEqual(
            json.loads(links_without_cancel_and_confirm.json())['cancel'],
            {'url': None, 'method': None, 'last_opened_at': None},
        )
        self.assertEqual(json.loads(payer.json())['type'], PayerType.TYPE_HUMAN.value)
        with self.assertRaises(ValidationError):
            PaymentData(**get_payment_data(split=None))
        with self.assertRaises(ValidationError):
            PaymentData(**get_payment_data(split=get_split_data_invalid()))
        with self.assertRaises(ValidationError):
            PaymentData(**get_payment_data(split='Lorem ipsum'))

    def test_decimal_amount_parsing_and_cents_from_float(self):
        pd = PaymentData(
            transaction_id=None,
            paid_at=None,
            expire_at='2025-10-10T19:59:02+02:00',
            amount=32.05,  # arriva come float
            currency=CurrencyType.CURRENCY_EUR,
            type=PaymentType.TYPE_STAMP,
            notice_code='303000000004610406',
            iud='68dada7823984a11b80a98aaede3371c',
            iuv='03000000004610406',
            receiver=None,
            due_type='TD_SALE',
            pagopa_category='n/a',
            document=None,
            split=[
                {'code': 'c_bollo_istanza', 'amount': 32, 'meta': {}},
                {'code': 'c_altro_costo', 'amount': 0.05, 'meta': {}},
            ],
        )
        self.assertIsInstance(pd.amount, Decimal)
        self.assertEqual(pd.amount, Decimal('32.05'))
        self.assertEqual(pd.amount_cents, 3205)

        # split
        self.assertIsInstance(pd.split[0].amount, Decimal)
        self.assertEqual(pd.split[0].amount, Decimal('32.00'))
        self.assertEqual(pd.split[0].amount_cents, 3200)
        self.assertEqual(pd.split[1].amount, Decimal('0.05'))
        self.assertEqual(pd.split[1].amount_cents, 5)

    def test_decimal_sum_of_splits_must_match_amount_ok(self):
        pd = PaymentData(
            transaction_id=None,
            paid_at=None,
            expire_at=None,
            amount='10.30',  # arriva come stringa
            currency=CurrencyType.CURRENCY_EUR,
            type=PaymentType.TYPE_STAMP,
            notice_code='303000000004610406',
            iud='68dada7823984a11b80a98aaede3371c',
            iuv='03000000004610406',
            receiver=None,
            due_type=None,
            pagopa_category=None,
            document=None,
            split=[
                {'code': 'A', 'amount': '10.00', 'meta': {}},
                {'code': 'B', 'amount': '0.30', 'meta': {}},
            ],
        )
        self.assertEqual(pd.amount, Decimal('10.30'))
        self.assertEqual(sum(s.amount for s in pd.split if s), Decimal('10.30'))

    def test_decimal_sum_of_splits_must_match_amount_raises(self):
        with self.assertRaises(ValidationError):
            PaymentData(
                transaction_id=None,
                paid_at=None,
                expire_at=None,
                amount=32.05,
                currency=CurrencyType.CURRENCY_EUR,
                type=PaymentType.TYPE_STAMP,
                notice_code='303000000004610406',
                iud='68dada7823984a11b80a98aaede3371c',
                iuv='03000000004610406',
                receiver=None,
                due_type=None,
                pagopa_category=None,
                document=None,
                # 32.00 + 0.04 = 32.04 != 32.05
                split=[
                    {'code': 'A', 'amount': 32, 'meta': {}},
                    {'code': 'B', 'amount': 0.04, 'meta': {}},
                ],
            )

    def test_decimal_rounding_half_up_edge_case_1005(self):
        s = PaymentDataSplit(code='edge', amount='1.005', meta={})
        # con ROUND_HALF_UP → 1.01 e 101 cent
        self.assertEqual(s.amount, Decimal('1.01'))
        self.assertEqual(s.amount_cents, 101)

    def test_decimal_eliminates_float_drift_point1_plus_point2(self):
        # 0.1 + 0.2 = 0.3 (nessuna deriva binaria con Decimal)
        pd = PaymentData(
            transaction_id=None,
            paid_at=None,
            expire_at=None,
            amount=0.3,
            currency=CurrencyType.CURRENCY_EUR,
            type=PaymentType.TYPE_STAMP,
            notice_code=None,
            iud='68dada7823984a11b80a98aaede3371c',
            iuv=None,
            receiver=None,
            due_type=None,
            pagopa_category=None,
            document=None,
            split=[
                {'code': 'A', 'amount': 0.1, 'meta': {}},
                {'code': 'B', 'amount': 0.2, 'meta': {}},
            ],
        )
        self.assertEqual(pd.amount, Decimal('0.30'))
        self.assertEqual(pd.amount_cents, 30)
        self.assertEqual(sum(s.amount for s in pd.split if s), Decimal('0.30'))

    def test_amount_cents_none_when_amount_none(self):
        pd = PaymentData(
            transaction_id=None,
            paid_at=None,
            expire_at=None,
            amount=None,
            currency=CurrencyType.CURRENCY_EUR,
            type=None,
            notice_code=None,
            iud='iud-decimal-5',
            iuv=None,
            receiver=None,
            due_type=None,
            pagopa_category=None,
            document=None,
            split=[],  # vuota: la root validation non scatta
        )
        self.assertIsNone(pd.amount)
        self.assertIsNone(pd.amount_cents)
