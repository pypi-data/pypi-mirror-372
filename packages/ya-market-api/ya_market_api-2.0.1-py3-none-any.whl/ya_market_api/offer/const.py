from ya_market_api.base.enum_toolkit import allow_unknown

from enum import Enum


@allow_unknown
class CatalogLanguageType(Enum):
	RU = "RU"		# русский
	UZ = "UZ"		# узбекский


@allow_unknown
class OfferCardStatusType(Enum):
	HAS_CARD_CAN_NOT_UPDATE = "HAS_CARD_CAN_NOT_UPDATE"		# Карточка Маркета.
	HAS_CARD_CAN_UPDATE = "HAS_CARD_CAN_UPDATE"		# Можно дополнить.
	HAS_CARD_CAN_UPDATE_ERRORS = "HAS_CARD_CAN_UPDATE_ERRORS"		# Изменения не приняты.
	HAS_CARD_CAN_UPDATE_PROCESSING = "HAS_CARD_CAN_UPDATE_PROCESSING"		# Изменения на проверке.
	NO_CARD_NEED_CONTENT = "NO_CARD_NEED_CONTENT"		# Создайте карточку.
	NO_CARD_MARKET_WILL_CREATE = "NO_CARD_MARKET_WILL_CREATE"		# Создаст Маркет.
	NO_CARD_ERRORS = "NO_CARD_ERRORS"		# Не создана из-за ошибки.
	NO_CARD_PROCESSING = "NO_CARD_PROCESSING"		# Проверяем данные.
	NO_CARD_ADD_TO_CAMPAIGN = "NO_CARD_ADD_TO_CAMPAIGN"		# Разместите товар в магазине.


@allow_unknown
class AgeUnit(Enum):
	YEAR = "YEAR"
	MONTH = "MONTH"


@allow_unknown
class CampaignStatusType(Enum):
	PUBLISHED = "PUBLISHED"		# Готов к продаже
	CHECKING = "CHECKING"		# На проверке
	DISABLED_BY_PARTNER = "DISABLED_BY_PARTNER"		# Скрыт вами
	DISABLED_AUTOMATICALLY = "DISABLED_AUTOMATICALLY"		# Отклонен
	REJECTED_BY_MARKET = "REJECTED_BY_MARKET"		# Исправьте ошибки
	CREATING_CARD = "CREATING_CARD"		# Создается карточка
	NO_CARD = "NO_CARD"		# Нужна карточка
	NO_STOCKS = "NO_STOCKS"		# Нет на складе
	ARCHIVED = "ARCHIVED"		# В архиве


@allow_unknown
class CommodityCodeType(Enum):
	CUSTOMS_COMMODITY_CODE = "CUSTOMS_COMMODITY_CODE"
	IKPU_CODE = "IKPU_CODE"


@allow_unknown
class OfferConditionQualityType(Enum):
	PERFECT = "PERFECT"		# идеальный
	EXCELLENT = "EXCELLENT"		# отличный
	GOOD = "GOOD"		# хороший
	NOT_SPECIFIED = "NOT_SPECIFIED"		# не выбран


@allow_unknown
class OfferConditionType(Enum):
	PREOWNED = "PREOWNED"		# бывший в употреблении товар, раньше принадлежал другому человеку
	SHOWCASESAMPLE = "SHOWCASESAMPLE"		# витринный образец
	REFURBISHED = "REFURBISHED"		# повторная продажа товара
	REDUCTION = "REDUCTION"		# товар с дефектами
	RENOVATED = "RENOVATED"		# восстановленный товар
	NOT_SPECIFIED = "NOT_SPECIFIED"		# не выбран


@allow_unknown
class TimeUnit(Enum):
	HOUR = "HOUR"		# час
	DAY = "DAY"		# сутки
	WEEK = "WEEK"		# неделя
	MONTH = "MONTH"		# месяц
	YEAR = "YEAR"		# год


@allow_unknown
class MediaFileUploadState(Enum):
	UPLOADING = "UPLOADING"		# загружается
	UPLOADED = "UPLOADED"		# успешно загружен
	FAILED = "FAILED"		# при загрузке произошла ошибка. Повторите попытку позже


@allow_unknown
class SellingProgramType(Enum):
	FBY = "FBY"		# FBY
	FBS = "FBS"		# FBS
	DBS = "DBS"		# DBS
	EXPRESS = "EXPRESS"		# Экспресс


@allow_unknown
class SellingProgramStatusType(Enum):
	FINE = "FINE"		# доступно
	REJECT = "REJECT"		# недоступно


@allow_unknown
class OfferType(Enum):
	DEFAULT = "DEFAULT"		# товары, для которых вы передавали особый тип ранее и хотите убрать его
	MEDICINE = "MEDICINE"		# лекарства
	BOOK = "BOOK"		# бумажные и электронные книги
	AUDIOBOOK = "AUDIOBOOK"		# аудиокниги
	ARTIST_TITLE = "ARTIST_TITLE"		# музыкальная и видеопродукция
	ON_DEMAND = "ON_DEMAND"		# товары на заказ
	ALCOHOL = "ALCOHOL"		# алкоголь


@allow_unknown
class ShowcaseType(Enum):
	B2B = "B2B"
	B2C = "B2C"
