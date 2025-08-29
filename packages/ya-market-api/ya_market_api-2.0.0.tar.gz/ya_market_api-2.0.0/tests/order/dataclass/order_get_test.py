from ya_market_api.order.dataclass.order_get import (
	OrderDeliveryDates, OrderShipment, OrderDelivery, OrderItemDetail, Order,
)

from unittest.mock import patch


class TestOrderDeliveryDates:
	def test_dates_must_be_arrow(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.str_date_to_arrow",
			spec=True,
		) as str_date_to_arrow_mock:
			OrderDeliveryDates.dates_must_be_arrow("31-12-2025")
			str_date_to_arrow_mock.assert_called_once_with("31-12-2025")

	def test_optional_times_must_be_optional_time(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.optional_str_time_to_optional_time",
			spec=True,
		) as optional_str_time_to_optional_time_mock:
			OrderDeliveryDates.optional_times_must_be_optional_time("12:30")
			optional_str_time_to_optional_time_mock.assert_called_once_with("12:30")

	def test_optional_dates_must_be_optional_arrow(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.optional_str_date_to_optional_arrow",
			spec=True,
		) as optional_str_date_to_optional_arrow_mock:
			OrderDeliveryDates.optional_dates_must_be_optional_arrow("31-12-2025 12:30:15")
			optional_str_date_to_optional_arrow_mock.assert_called_once_with("31-12-2025 12:30:15")


class TestOrderShipment:
	def test_optional_dates_must_be_optional_arrow(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.optional_str_date_to_optional_arrow",
			spec=True,
		) as optional_str_date_to_optional_arrow_mock:
			OrderShipment.optional_dates_must_be_optional_arrow("31-12-2025")
			optional_str_date_to_optional_arrow_mock.assert_called_once_with("31-12-2025")

	def test_optional_times_must_be_optional_time(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.optional_str_time_to_optional_time",
			spec=True,
		) as optional_str_time_to_optional_time_mock:
			OrderShipment.optional_times_must_be_optional_time("12:30")
			optional_str_time_to_optional_time_mock.assert_called_once_with("12:30")


class TestOrderDelivery:
	def test_optional_dates_must_be_optional_arrow(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.optional_str_date_to_optional_arrow",
			spec=True,
		) as optional_str_date_to_optional_arrow_mock:
			OrderDelivery.optional_dates_must_be_optional_arrow("31-12-2025")
			optional_str_date_to_optional_arrow_mock.assert_called_once_with("31-12-2025")


class TestOrderItemDetail:
	def test_dates_must_be_arrow(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.str_date_to_arrow",
			spec=True,
		) as str_date_to_arrow_mock:
			OrderItemDetail.dates_must_be_arrow("31-12-2025")
			str_date_to_arrow_mock.assert_called_once_with("31-12-2025")


class TestOrder:
	def test_datetimes_must_be_arrow(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.str_datetime_to_arrow",
			spec=True,
		) as str_datetime_to_arrow_mock:
			Order.datetimes_must_be_arrow("31-12-2025 12:30:15")
			str_datetime_to_arrow_mock.assert_called_once_with("31-12-2025 12:30:15")

	def test_optional_dates_must_be_optional_arrow(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.optional_str_date_to_optional_arrow",
			spec=True,
		) as optional_str_date_to_optional_arrow_mock:
			Order.optional_dates_must_be_optional_arrow("31-12-2025")
			optional_str_date_to_optional_arrow_mock.assert_called_once_with("31-12-2025")

	def test_optional_datetimes_must_be_optional_arrow(self):
		with patch(
			"ya_market_api.order.dataclass.order_get.optional_str_datetime_to_optional_arrow",
			spec=True,
		) as optional_str_datetime_to_optional_arrow_mock:
			Order.optional_datetimes_must_be_optional_arrow("31-12-2025 12:30:15")
			optional_str_datetime_to_optional_arrow_mock.assert_called_once_with("31-12-2025 12:30:15")
