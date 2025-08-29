from ya_market_api.base.const import CurrencyType
from ya_market_api.base.dataclass import Region, GPS
from ya_market_api.base.convert import (
	optional_str_time_to_optional_time, optional_str_date_to_optional_arrow, str_date_to_arrow,
	optional_str_datetime_to_optional_arrow, str_datetime_to_arrow,
)
from ya_market_api.order.const import (
	PaymentMethod, PaymentType, OrderStatus, OrderSubstatus, OrderTaxSystem, OrderBuyerType, OrderSubsidyType,
	OrderVatType, OrderItemTag, OrderItemInstanceType, OrderDeliveryPartnerType, OrderDeliveryType,
	OrderDeliveryDispatchType, OrderDeliveryEacType, OrderLiftType, OrderItemStatusType, OrderPromoType,
	OrderItemSubsidyType,
)

from decimal import Decimal
from typing import List, Optional
from datetime import time

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict
from pydantic.functional_validators import field_validator
from arrow import Arrow


class Request(BaseModel):
	order_id: int


class OrderBuyer(BaseModel):
	id: Optional[str] = None
	type: OrderBuyerType
	first_name: Optional[str] = Field(default=None, validation_alias="firstName")
	last_name: Optional[str] = Field(default=None, validation_alias="lastName")
	middle_name: Optional[str] = Field(default=None, validation_alias="middleName")


class OrderDeliveryDates(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	from_date: Arrow = Field(validation_alias="fromDate")
	from_time: Optional[time] = Field(default=None, validation_alias="fromTime")
	real_delivery_date: Optional[Arrow] = Field(default=None, validation_alias="realDeliveryDate")
	to_date: Optional[Arrow] = Field(default=None, validation_alias="toDate")
	to_time: Optional[time] = Field(default=None, validation_alias="toTime")

	@field_validator("from_date", mode="before")
	@classmethod
	def dates_must_be_arrow(cls, value: str) -> Arrow:
		return str_date_to_arrow(value)

	@field_validator("from_time", "to_time", mode="before")
	@classmethod
	def optional_times_must_be_optional_time(cls, value: Optional[str]) -> Optional[time]:
		return optional_str_time_to_optional_time(value)

	@field_validator("real_delivery_date", "to_date", mode="before")
	@classmethod
	def optional_dates_must_be_optional_arrow(cls, value: Optional[str]) -> Optional[Arrow]:
		return optional_str_date_to_optional_arrow(value)


class OrderDeliveryAddress(BaseModel):
	apartment: Optional[str] = None
	block: Optional[str] = None
	building: Optional[str] = None
	city: Optional[str] = None
	country: Optional[str] = None
	district: Optional[str] = None
	entrance: Optional[str] = None
	entryphone: Optional[str] = None
	estate: Optional[str] = None
	floor: Optional[str] = None
	gps: Optional[GPS] = None
	house: Optional[str] = None
	phone: Optional[str] = None
	postcode: Optional[str] = None
	recipient: Optional[str] = None
	street: Optional[str] = None
	subway: Optional[str] = None


class OrderCourier(BaseModel):
	full_name: Optional[str] = Field(default=None, validation_alias="fullName")
	phone: Optional[str] = None
	phone_extension: Optional[str] = Field(default=None, validation_alias="phoneExtension")
	vehicle_description: Optional[str] = Field(default=None, validation_alias="vehicleDescription")
	vehicle_number: Optional[str] = Field(default=None, validation_alias="vehicleNumber")


class OrderTrack(BaseModel):
	delivery_service_id: int = Field(validation_alias="deliveryServiceId")
	track_code: Optional[str] = Field(default=None, validation_alias="trackCode")


class OrderParcelBox(BaseModel):
	id: int
	fulfilment_id: str = Field(validation_alias="fulfilmentId")


class OrderShipment(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	id: Optional[int] = None
	boxes: List[OrderParcelBox] = Field(default_factory=list)
	shipment_date: Optional[Arrow] = Field(default=None, validation_alias="shipmentDate")
	shipment_time: Optional[time] = Field(default=None, validation_alias="shipmentTime")
	tracks: List[OrderTrack] = Field(default_factory=list)

	@field_validator("shipment_date", mode="before")
	@classmethod
	def optional_dates_must_be_optional_arrow(cls, value: Optional[str]) -> Optional[Arrow]:
		return optional_str_date_to_optional_arrow(value)

	@field_validator("shipment_time", mode="before")
	@classmethod
	def optional_times_must_be_optional_time(cls, value: Optional[str]) -> Optional[time]:
		return optional_str_time_to_optional_time(value)


class OrderDelivery(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	dates: OrderDeliveryDates
	delivery_partner_type: OrderDeliveryPartnerType = Field(validation_alias="deliveryPartnerType")
	delivery_service_id: int = Field(validation_alias="deliveryServiceId")
	service_name: str = Field(validation_alias="serviceName")
	type: OrderDeliveryType
	address: Optional[OrderDeliveryAddress] = None
	courier: Optional[OrderCourier] = None
	dispatch_type: Optional[OrderDeliveryDispatchType] = Field(default=None, validation_alias="dispatchType")
	eac_code: Optional[str] = Field(default=None, validation_alias="eacCode")
	eac_type: Optional[OrderDeliveryEacType] = Field(default=None, validation_alias="eacType")
	estimated: Optional[bool] = None
	id: Optional[str] = Field(default=None, deprecated=True)
	lift_price: Optional[Decimal] = Field(default=None, decimal_places=2, validation_alias="liftPrice")
	lift_type: Optional[OrderLiftType] = Field(default=None, validation_alias="liftType")
	outlet_code: Optional[str] = Field(default=None, validation_alias="outletCode")
	outlet_storage_limit_date: Optional[Arrow] = Field(default=None, validation_alias="outletStorageLimitDate")
	price: Optional[Decimal] = Field(default=None, deprecated=True, decimal_places=2)
	region: Optional[Region] = None
	shipments: List[OrderShipment] = Field(default_factory=list)
	tracks: List[OrderTrack] = Field(default_factory=list)
	vat: Optional[OrderVatType] = None

	@field_validator("outlet_storage_limit_date", mode="before")
	@classmethod
	def optional_dates_must_be_optional_arrow(cls, value: Optional[str]) -> Optional[Arrow]:
		return optional_str_date_to_optional_arrow(value)


class OrderItemDetail(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	item_count: int = Field(validation_alias="itemCount")
	item_status: OrderItemStatusType = Field(validation_alias="itemStatus")
	updated_at: Arrow = Field(validation_alias="updateDate")

	@field_validator("updated_at", mode="before")
	@classmethod
	def dates_must_be_arrow(cls, value: str) -> Arrow:
		return str_date_to_arrow(value)


class OrderItemInstance(BaseModel):
	cis: Optional[str] = None
	cis_full: Optional[str] = Field(default=None, validation_alias="cisFull")
	country_code: Optional[str] = Field(default=None, validation_alias="countryCode")
	gtd: Optional[str] = None
	rnpt: Optional[str] = None
	uin: Optional[str] = None


class OrderItemPromo(BaseModel):
	subsidy: Decimal = Field(decimal_places=2)
	type: OrderPromoType
	discount: Optional[Decimal] = Field(default=None, decimal_places=2)
	market_promo_id: Optional[str] = Field(default=None, validation_alias="marketPromoId")
	shop_promo_id: Optional[str] = Field(default=None, validation_alias="shopPromoId")


class OrderItemSubsidy(BaseModel):
	amount: Decimal = Field(decimal_places=2)
	type: OrderItemSubsidyType


class OrderItem(BaseModel):
	buyer_price: Decimal = Field(decimal_places=2, validation_alias="buyerPrice")
	buyer_price_before_discount: Decimal = Field(decimal_places=2, validation_alias="buyerPriceBeforeDiscount")
	count: int
	id: int
	offer_id: str = Field(validation_alias="offerId")
	offer_name: str = Field(validation_alias="offerName")
	price: Decimal = Field(decimal_places=2)
	vat: OrderVatType
	details: List[OrderItemDetail] = Field(default_factory=list, deprecated=True)
	instances: List[OrderItemInstance] = Field(default_factory=list)
	partner_warehouse_id: Optional[str] = Field(default=None, deprecated=True, validation_alias="partnerWarehouseId")
	price_before_discount: Optional[Decimal] = Field(
		default=None, decimal_places=2, deprecated=True, validation_alias="priceBeforeDiscount",
	)
	promos: List[OrderItemPromo] = Field(default_factory=list)
	required_instance_types: List[OrderItemInstanceType] = Field(
		default_factory=list, validation_alias="requiredInstanceTypes",
	)
	shop_sku: Optional[str] = Field(default=None, deprecated=True, validation_alias="shopSku")
	subsidies: List[OrderItemSubsidy] = Field(default_factory=list)
	subsidy: Optional[Decimal] = Field(default=None, deprecated=True, decimal_places=2)
	tags: List[OrderItemTag] = Field(default_factory=list)


class OrderSubsidy(BaseModel):
	amount: Decimal = Field(decimal_places=2)
	type: OrderSubsidyType


class Order(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	id: int
	buyer: OrderBuyer
	buyer_items_total_before_discount: Decimal = Field(
		decimal_places=2,
		validation_alias="buyerItemsTotalBeforeDiscount",
	)
	created_at: Arrow = Field(validation_alias="creationDate")
	currency: CurrencyType
	delivery: OrderDelivery
	delivery_total: Decimal = Field(decimal_places=2, validation_alias="deliveryTotal")
	fake: bool
	items: List[OrderItem]
	items_total: Decimal = Field(decimal_places=2, validation_alias="itemsTotal")
	payment_method: PaymentMethod = Field(validation_alias="paymentMethod")
	payment_type: PaymentType = Field(validation_alias="paymentType")
	status: OrderStatus
	substatus: OrderSubstatus
	tax_system: OrderTaxSystem = Field(validation_alias="taxSystem")
	buyer_items_total: Optional[Decimal] = Field(
		default=None, decimal_places=2, deprecated=True, validation_alias="buyerItemsTotal",
	)
	buyer_total: Optional[Decimal] = Field(
		default=None, decimal_places=2, deprecated=True, validation_alias="buyerTotal",
	)
	buyer_total_before_discount: Optional[Decimal] = Field(
		default=None,
		decimal_places=2,
		deprecated=True,
		validation_alias="buyerTotalBeforeDiscount",
	)
	cancel_requested: Optional[bool] = Field(default=None, validation_alias="cancelRequested")
	# Format in docs: YYYY-MM-DD, but example contains time, so we use only date
	expired_at: Optional[Arrow] = Field(default=None, validation_alias="expiryDate")
	external_order_id: Optional[str] = Field(default=None, validation_alias="externalOrderId")
	notes: Optional[str] = None
	subsidies: List[OrderSubsidy] = Field(default_factory=list)
	updated_at: Optional[Arrow] = Field(default=None, validation_alias="updatedAt")

	@field_validator("created_at", mode="before")
	@classmethod
	def datetimes_must_be_arrow(cls, value: str) -> Arrow:
		return str_datetime_to_arrow(value)

	@field_validator("expired_at", mode="before")
	@classmethod
	def optional_dates_must_be_optional_arrow(cls, value: Optional[str]) -> Optional[Arrow]:
		return optional_str_date_to_optional_arrow(value)

	@field_validator("updated_at", mode="before")
	@classmethod
	def optional_datetimes_must_be_optional_arrow(cls, value: Optional[str]) -> Optional[Arrow]:
		return optional_str_datetime_to_optional_arrow(value)


class Response(BaseModel):
	order: Optional[Order] = None
