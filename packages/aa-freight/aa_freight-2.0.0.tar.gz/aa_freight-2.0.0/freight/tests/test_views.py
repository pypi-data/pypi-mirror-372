from http import HTTPStatus
from unittest.mock import Mock, patch

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from esi.models import Token

from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils
from app_utils.testing import add_new_token, json_response_to_python

from freight import constants, views
from freight.app_settings import (
    FREIGHT_OPERATION_MODE_MY_ALLIANCE,
    FREIGHT_OPERATION_MODE_MY_CORPORATION,
)
from freight.models import Contract, ContractHandler, Location

from .testdata.factories import create_pricing
from .testdata.factories_2 import (
    ContractFactory,
    UserMainDefaultFactory,
    UserMainManagerFactory,
)
from .testdata.helpers import create_contract_handler_w_contracts

MODULE_PATH = "freight.views"


def json_response_to_python_dict(response) -> dict:
    return {x["id"]: x for x in json_response_to_python(response)["data"]}


class TestCalculator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _, cls.user = create_contract_handler_w_contracts()
        cls.user = AuthUtils.add_permission_to_user_by_name(
            "freight.use_calculator", cls.user
        )
        jita = Location.objects.get(id=60003760)
        amamake = Location.objects.get(id=1022167642188)
        cls.pricing = create_pricing(
            start_location=jita, end_location=amamake, price_base=500000000
        )
        Contract.objects.update_pricing()
        cls.factory = RequestFactory()

    def test_index(self):
        request = self.factory.get(reverse("freight:index"))
        request.user = self.user
        response = views.index(request)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("freight:calculator"))

    def test_calculator_access_with_permission(self):
        request = self.factory.get(reverse("freight:calculator"))
        request.user = self.user
        response = views.calculator(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_calculator_no_access_without_permission(self):
        request = self.factory.get(reverse("freight:calculator"))
        request.user = AuthUtils.create_user("Lex Luthor")
        response = views.calculator(request)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)


class TestCalculator2(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        cls.user = UserMainDefaultFactory()

    def test_can_render_calculator_without_handler(self):
        # given
        request = self.factory.get(reverse("freight:calculator"))
        request.user = self.user
        # when
        response = views.calculator(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestContractList(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        _, cls.user_1 = create_contract_handler_w_contracts()
        cls.user_1 = AuthUtils.add_permission_to_user_by_name(
            "freight.basic_access", cls.user_1
        )
        cls.user_1 = AuthUtils.add_permission_to_user_by_name(
            "freight.use_calculator", cls.user_1
        )
        cls.user_1 = AuthUtils.add_permission_to_user_by_name(
            "freight.view_contracts", cls.user_1
        )
        jita = Location.objects.get(id=60003760)
        amamake = Location.objects.get(id=1022167642188)
        cls.pricing = create_pricing(
            start_location=jita, end_location=amamake, price_base=500000000
        )
        Contract.objects.update_pricing()
        cls.user_2 = AuthUtils.create_user("Lex Luthor")
        cls.user_2 = AuthUtils.add_permission_to_user_by_name(
            "freight.basic_access", cls.user_2
        )

    def test_should_open_all_contracts_page(self):
        # given
        request = self.factory.get(reverse("freight:contract_list_all"))
        request.user = self.user_1
        # when
        response = views.contract_list_all(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_no_access_without_permission(self):
        request = self.factory.get(reverse("freight:contract_list_all"))
        request.user = self.user_2
        response = views.contract_list_all(request)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_should_return_all_contracts(self):
        # given
        request = self.factory.get(
            reverse("freight:contract_list_data", args={constants.CONTRACT_LIST_ALL})
        )
        request.user = self.user_1
        # when
        response = views.contract_list_data(request, constants.CONTRACT_LIST_ALL)
        # then
        all_contract_ids = set(Contract.objects.values_list("contract_id", flat=True))
        contract_ids_in_response = {
            obj["contract_id"] for obj in json_response_to_python(response)["data"]
        }
        self.assertSetEqual(contract_ids_in_response, all_contract_ids)

    # TODO
    """ issue with setting permission
    def test_active_access_with_permission(self):
        request = self.factory.get(reverse('freight:contract_list_active'))
        request.user = self.user_1

        response = views.contract_list_active(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
    """

    def test_active_data_has_all_contracts(self):
        # given
        request = self.factory.get(
            reverse("freight:contract_list_data", args={constants.CONTRACT_LIST_ACTIVE})
        )
        request.user = self.user_1
        # when
        response = views.contract_list_data(request, constants.CONTRACT_LIST_ACTIVE)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json_response_to_python(response)["data"]
        contract_ids = {x["contract_id"] for x in data}
        self.assertSetEqual(
            contract_ids,
            {
                149409005,
                149409014,
                149409006,
                149409015,
                149409016,
                149409064,
                149409061,
                149409062,
                149409063,
                149409017,
                149409018,
                149409019,
            },
        )

    def test_data_invalid_category(self):
        request = self.factory.get(
            reverse("freight:contract_list_data", args={"this_is_not_valid"})
        )
        request.user = self.user_1

        with self.assertRaises(ValueError):
            views.contract_list_data(request, "this_is_not_valid")

    def test_user_no_access_without_permission(self):
        request = self.factory.get(reverse("freight:contract_list_user"))
        request.user = self.user_2
        response = views.contract_list_user(request)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_user_access_with_permission(self):
        request = self.factory.get(reverse("freight:contract_list_user"))
        request.user = self.user_1

        response = views.contract_list_user(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_access_with_permission_and_no_main(self):
        # given
        user = AuthUtils.create_user("John Doe")
        user = AuthUtils.add_permission_to_user_by_name("freight.basic_access", user)
        user = AuthUtils.add_permission_to_user_by_name("freight.use_calculator", user)
        request = self.factory.get(reverse("freight:contract_list_user"))
        request.user = user
        # when
        response = views.contract_list_user(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_data_user_no_access_without_permission_1(self):
        request = self.factory.get(
            reverse("freight:contract_list_data", args={constants.CONTRACT_LIST_USER})
        )
        request.user = self.user_2
        response = views.contract_list_data(request, constants.CONTRACT_LIST_USER)
        data = json_response_to_python(response)["data"]
        self.assertListEqual(data, [])

    def test_data_user_no_access_without_permission_2(self):
        request = self.factory.get(
            reverse("freight:contract_list_data", args={constants.CONTRACT_LIST_ACTIVE})
        )
        request.user = self.user_2
        response = views.contract_list_data(request, constants.CONTRACT_LIST_ACTIVE)
        data = json_response_to_python(response)["data"]
        self.assertListEqual(data, [])

    def test_data_user_no_access_without_permission_3(self):
        request = self.factory.get(
            reverse("freight:contract_list_data", args={constants.CONTRACT_LIST_ALL})
        )
        request.user = self.user_2
        response = views.contract_list_data(request, constants.CONTRACT_LIST_ALL)
        data = json_response_to_python(response)["data"]
        self.assertListEqual(data, [])

    def test_data_user(self):
        request = self.factory.get(
            reverse("freight:contract_list_data", args={constants.CONTRACT_LIST_USER})
        )
        request.user = self.user_1

        response = views.contract_list_data(request, constants.CONTRACT_LIST_USER)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json_response_to_python(response)["data"]
        contract_ids = {x["contract_id"] for x in data}
        self.assertSetEqual(
            contract_ids,
            {
                149409016,
                149409061,
                149409062,
                149409063,
                149409064,
            },
        )


class TestContractListData(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        cls.user = UserMainManagerFactory()

    def test_should_return_contract(self):
        # given
        ContractFactory(status=Contract.Status.IN_PROGRESS, contract_id=123456789)
        request = self.factory.get(
            reverse("freight:contract_list_data", args={constants.CONTRACT_LIST_ALL})
        )
        request.user = self.user
        # when
        response = views.contract_list_data(request, constants.CONTRACT_LIST_ALL)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json_response_to_python(response)["data"]
        obj = data[0]
        self.assertEqual(obj["contract_id"], 123456789)
        self.assertEqual(obj["status"], "in_progress")


class TestSetupContractHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _, cls.user = create_contract_handler_w_contracts([])
        cls.user = AuthUtils.add_permission_to_user_by_name(
            "freight.setup_contract_handler", cls.user
        )
        jita = Location.objects.get(id=60003760)
        amamake = Location.objects.get(id=1022167642188)
        cls.pricing = create_pricing(
            start_location=jita, end_location=amamake, price_base=500000000
        )
        Contract.objects.update_pricing()
        cls.factory = RequestFactory()

    @patch(MODULE_PATH + ".FREIGHT_OPERATION_MODE", FREIGHT_OPERATION_MODE_MY_ALLIANCE)
    @patch(MODULE_PATH + ".messages", autospec=True)
    @patch(MODULE_PATH + ".tasks.run_contracts_sync", autospec=True)
    def test_normal(self, mock_run_contracts_sync, mock_message_plus):
        ContractHandler.objects.all().delete()
        token = Mock(spec=Token)
        token.character_id = self.user.profile.main_character.character_id
        request = self.factory.post(
            reverse("freight:setup_contract_handler"), data={"_token": 1}
        )
        request.user = self.user
        request.token = token

        orig_view = views.setup_contract_handler.__wrapped__.__wrapped__.__wrapped__

        response = orig_view(request, token)
        self.assertEqual(mock_run_contracts_sync.delay.call_count, 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("freight:index"))

    @patch(MODULE_PATH + ".FREIGHT_OPERATION_MODE", FREIGHT_OPERATION_MODE_MY_ALLIANCE)
    @patch(MODULE_PATH + ".messages", autospec=True)
    @patch(MODULE_PATH + ".tasks.run_contracts_sync", autospec=True)
    def test_error_no_alliance_member(self, mock_run_contracts_sync, mock_message_plus):
        ContractHandler.objects.all().delete()

        token = Mock(spec=Token)
        token_char = EveCharacter.objects.get(character_id=90000005)
        token.character_id = token_char.character_id
        request = self.factory.post(
            reverse("freight:setup_contract_handler"), data={"_token": 1}
        )
        request.user = self.user
        request.token = token

        orig_view = views.setup_contract_handler.__wrapped__.__wrapped__.__wrapped__

        response = orig_view(request, token)
        self.assertEqual(mock_message_plus.error.call_count, 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("freight:index"))

    @patch(
        MODULE_PATH + ".FREIGHT_OPERATION_MODE", FREIGHT_OPERATION_MODE_MY_CORPORATION
    )
    @patch(MODULE_PATH + ".messages", autospec=True)
    @patch(MODULE_PATH + ".tasks.run_contracts_sync", autospec=True)
    def test_error_character_not_owned(
        self, mock_run_contracts_sync, mock_message_plus
    ):
        ContractHandler.objects.all().delete()
        token = Mock(spec=Token)
        token_char = EveCharacter.objects.get(character_id=90000005)
        token.character_id = token_char.character_id
        request = self.factory.post(
            reverse("freight:setup_contract_handler"), data={"_token": 1}
        )
        request.user = self.user
        request.token = token

        orig_view = views.setup_contract_handler.__wrapped__.__wrapped__.__wrapped__

        response = orig_view(request, token)
        self.assertEqual(mock_message_plus.error.call_count, 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("freight:index"))

    @patch(
        MODULE_PATH + ".FREIGHT_OPERATION_MODE", FREIGHT_OPERATION_MODE_MY_CORPORATION
    )
    @patch(MODULE_PATH + ".messages", autospec=True)
    @patch(MODULE_PATH + ".tasks.run_contracts_sync", autospec=True)
    def test_error_wrong_operation_mode(
        self, mock_run_contracts_sync, mock_message_plus
    ):
        token = Mock(spec=Token)
        token.character_id = self.user.profile.main_character.character_id
        request = self.factory.post(
            reverse("freight:setup_contract_handler"), data={"_token": 1}
        )
        request.user = self.user
        request.token = token

        orig_view = views.setup_contract_handler.__wrapped__.__wrapped__.__wrapped__

        response = orig_view(request, token)
        self.assertEqual(mock_message_plus.error.call_count, 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("freight:index"))


class TestStatistics(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _, cls.user = create_contract_handler_w_contracts()
        # expected contracts to load: 149409118, 149409218, 149409318
        cls.user = AuthUtils.add_permission_to_user_by_name(
            "freight.basic_access", cls.user
        )
        cls.user = AuthUtils.add_permission_to_user_by_name(
            "freight.view_statistics", cls.user
        )
        jita = Location.objects.get(id=60003760)
        amamake = Location.objects.get(id=1022167642188)
        cls.pricing = create_pricing(
            start_location=jita, end_location=amamake, price_base=500000000
        )
        Contract.objects.update_pricing()
        cls.factory = RequestFactory()

    def test_should_open_statistics_page(self):
        # given
        request = self.factory.get(reverse("freight:statistics"))
        request.user = self.user
        # when
        response = views.statistics(request)
        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_statistics_routes_data(self):
        request = self.factory.get(reverse("freight:statistics_routes_data"))
        request.user = self.user

        response = views.statistics_routes_data(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json_response_to_python(response)["data"]
        self.assertListEqual(
            data,
            [
                {
                    "contracts": 3,
                    "rewards": 300000000,
                    "collaterals": 3000000000,
                    "volume": 345000.0,
                    "pilots": 1,
                    "name": "Jita <-> Amamake",
                    "customers": 1,
                }
            ],
        )

    def test_statistics_pilots_data(self):
        request = self.factory.get(reverse("freight:statistics_pilots_data"))
        request.user = self.user

        response = views.statistics_pilots_data(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json_response_to_python(response)["data"]

        self.assertListEqual(
            data,
            [
                {
                    "rewards": 300000000,
                    "collaterals": 3000000000,
                    "volume": 345000.0,
                    "corporation": "Wayne Enterprise",
                    "contracts": 3,
                    "name": "Bruce Wayne",
                }
            ],
        )

    def test_statistics_pilot_corporations_data(self):
        request = self.factory.get(
            reverse("freight:statistics_pilot_corporations_data")
        )
        request.user = self.user

        response = views.statistics_pilot_corporations_data(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json_response_to_python(response)["data"]

        self.assertListEqual(
            data,
            [
                {
                    "name": "Wayne Enterprise",
                    "rewards": 300000000,
                    "collaterals": 3000000000,
                    "volume": 345000.0,
                    "alliance": "",
                    "contracts": 3,
                }
            ],
        )

    def test_statistics_customer_data(self):
        request = self.factory.get(reverse("freight:statistics_customer_data"))
        request.user = self.user

        response = views.statistics_customer_data(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json_response_to_python(response)["data"]

        self.assertListEqual(
            data,
            [
                {
                    "rewards": 300000000,
                    "collaterals": 3000000000,
                    "volume": 345000.0,
                    "corporation": "Wayne Enterprise",
                    "contracts": 3,
                    "name": "Robin",
                }
            ],
        )


class TestAddLocation(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _, cls.user = create_contract_handler_w_contracts([])
        cls.factory = RequestFactory()

    @patch(MODULE_PATH + ".FREIGHT_OPERATION_MODE", FREIGHT_OPERATION_MODE_MY_ALLIANCE)
    @patch(MODULE_PATH + ".messages", autospec=True)
    @patch(MODULE_PATH + ".Location.objects.update_or_create_esi", autospec=True)
    def test_normal(self, mock_update_or_create_from_esi, mock_message_plus):
        location_id = 1022167642188
        location = Location.objects.get(id=location_id)
        mock_update_or_create_from_esi.return_value = location, False

        my_character = self.user.profile.main_character
        token = add_new_token(
            user=self.user, character=my_character, scopes=["publicData"]
        )
        request = self.factory.post(
            reverse("freight:add_location_2"), data={"location_id": location_id}
        )
        request.user = self.user
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        request.session[views.ADD_LOCATION_TOKEN_TAG] = token.pk
        request.session.save()

        orig_view = views.add_location_2.__wrapped__.__wrapped__

        response = orig_view(request)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("freight:add_location_2"))
        self.assertEqual(mock_message_plus.success.call_count, 1)
        self.assertEqual(mock_message_plus.error.call_count, 0)

    @patch(MODULE_PATH + ".FREIGHT_OPERATION_MODE", FREIGHT_OPERATION_MODE_MY_ALLIANCE)
    @patch(MODULE_PATH + ".messages", autospec=True)
    @patch(MODULE_PATH + ".Location.objects.update_or_create_esi", autospec=True)
    def test_fetching_location_fails(
        self, mock_update_or_create_from_esi, mock_message_plus
    ):
        location_id = 1022167642188
        Location.objects.get(id=location_id)
        mock_update_or_create_from_esi.side_effect = OSError("Test exception")

        my_character = self.user.profile.main_character
        token = add_new_token(
            user=self.user, character=my_character, scopes=["publicData"]
        )
        request = self.factory.post(
            reverse("freight:add_location_2"), data={"location_id": location_id}
        )
        request.user = self.user
        middleware = SessionMiddleware(Mock())
        middleware.process_request(request)
        request.session[views.ADD_LOCATION_TOKEN_TAG] = token.pk
        request.session.save()

        orig_view = views.add_location_2.__wrapped__.__wrapped__

        response = orig_view(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(mock_message_plus.success.call_count, 0)
        self.assertEqual(mock_message_plus.error.call_count, 1)
