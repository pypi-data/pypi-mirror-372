from ya_market_api.base.enum_toolkit import allow_unknown

from enum import Enum


@allow_unknown
class Status(Enum):
	OK = "OK"
	ERROR = "ERROR"


@allow_unknown
class AuthScope(Enum):
	ALL_METHODS = "ALL_METHODS"		# полное управление кабинетом
	ALL_METHODS_READ_ONLY = "ALL_METHODS_READ_ONLY"		# просмотр всей информации в кабинете
	INVENTORY_AND_ORDER_PROCESSING = "INVENTORY_AND_ORDER_PROCESSING"		# обработка заказов и учет товаров
	INVENTORY_AND_ORDER_PROCESSING_READ_ONLY = "INVENTORY_AND_ORDER_PROCESSING_READ_ONLY"		# просмотр информации о заказах
	PRICING = "PRICING"		# управление ценами
	PRICING_READ_ONLY = "PRICING_READ_ONLY"		# просмотр цен
	OFFERS_AND_CARDS_MANAGEMENT = "OFFERS_AND_CARDS_MANAGEMENT"		# управление товарами и карточками
	OFFERS_AND_CARDS_MANAGEMENT_READ_ONLY = "OFFERS_AND_CARDS_MANAGEMENT_READ_ONLY"		# просмотр товаров и карточек
	PROMOTION = "PROMOTION"		# продвижение товаров
	PROMOTION_READ_ONLY = "PROMOTION_READ_ONLY"		# просмотр информации о продвижении товаров
	FINANCE_AND_ACCOUNTING = "FINANCE_AND_ACCOUNTING"		# просмотр финансовой информации и отчётности
	COMMUNICATION = "COMMUNICATION"		# общение с покупателями
	SETTINGS_MANAGEMENT = "SETTINGS_MANAGEMENT"		# настройка магазинов
	SUPPLIES_MANAGEMENT_READ_ONLY = "SUPPLIES_MANAGEMENT_READ_ONLY"		# получение информации по FBY-заявкам


@allow_unknown
class CurrencyType(Enum):
	RUR = "RUR"
	USD = "USD"
	EUR = "EUR"
	UAH = "UAH"
	AUD = "AUD"
	GBP = "GBP"
	BYR = "BYR"
	BYN = "BYN"
	DKK = "DKK"
	ISK = "ISK"
	KZT = "KZT"
	CAD = "CAD"
	CNY = "CNY"
	NOK = "NOK"
	XDR = "XDR"
	SGD = "SGD"
	TRY = "TRY"
	SEK = "SEK"
	CHF = "CHF"
	JPY = "JPY"
	AZN = "AZN"
	ALL = "ALL"
	DZD = "DZD"
	AOA = "AOA"
	ARS = "ARS"
	AMD = "AMD"
	AFN = "AFN"
	BHD = "BHD"
	BGN = "BGN"
	BOB = "BOB"
	BWP = "BWP"
	BND = "BND"
	BRL = "BRL"
	BIF = "BIF"
	HUF = "HUF"
	VEF = "VEF"
	KPW = "KPW"
	VND = "VND"
	GMD = "GMD"
	GHS = "GHS"
	GNF = "GNF"
	HKD = "HKD"
	GEL = "GEL"
	AED = "AED"
	EGP = "EGP"
	ZMK = "ZMK"
	ILS = "ILS"
	INR = "INR"
	IDR = "IDR"
	JOD = "JOD"
	IQD = "IQD"
	IRR = "IRR"
	YER = "YER"
	QAR = "QAR"
	KES = "KES"
	KGS = "KGS"
	COP = "COP"
	CDF = "CDF"
	CRC = "CRC"
	KWD = "KWD"
	CUP = "CUP"
	LAK = "LAK"
	LVL = "LVL"
	SLL = "SLL"
	LBP = "LBP"
	LYD = "LYD"
	SZL = "SZL"
	LTL = "LTL"
	MUR = "MUR"
	MRO = "MRO"
	MKD = "MKD"
	MWK = "MWK"
	MGA = "MGA"
	MYR = "MYR"
	MAD = "MAD"
	MXN = "MXN"
	MZN = "MZN"
	MDL = "MDL"
	MNT = "MNT"
	NPR = "NPR"
	NGN = "NGN"
	NIO = "NIO"
	NZD = "NZD"
	OMR = "OMR"
	PKR = "PKR"
	PYG = "PYG"
	PEN = "PEN"
	PLN = "PLN"
	KHR = "KHR"
	SAR = "SAR"
	RON = "RON"
	SCR = "SCR"
	SYP = "SYP"
	SKK = "SKK"
	SOS = "SOS"
	SDG = "SDG"
	SRD = "SRD"
	TJS = "TJS"
	THB = "THB"
	TWD = "TWD"
	BDT = "BDT"
	TZS = "TZS"
	TND = "TND"
	TMM = "TMM"
	UGX = "UGX"
	UZS = "UZS"
	UYU = "UYU"
	PHP = "PHP"
	DJF = "DJF"
	XAF = "XAF"
	XOF = "XOF"
	HRK = "HRK"
	CZK = "CZK"
	CLP = "CLP"
	LKR = "LKR"
	EEK = "EEK"
	ETB = "ETB"
	RSD = "RSD"
	ZAR = "ZAR"
	KRW = "KRW"
	NAD = "NAD"
	TL = "TL"
	UE = "UE"


@allow_unknown
class RegionType(Enum):
	OTHER = "OTHER"		# неизвестный регион
	CONTINENT = "CONTINENT"		# континент
	REGION = "REGION"		# регион
	COUNTRY = "COUNTRY"		# страна
	COUNTRY_DISTRICT = "COUNTRY_DISTRICT"		# область
	REPUBLIC = "REPUBLIC"		# субъект федерации
	CITY = "CITY"		# крупный город
	VILLAGE = "VILLAGE"		# город
	CITY_DISTRICT = "CITY_DISTRICT"		# район города
	SUBWAY_STATION = "SUBWAY_STATION"		# станция метро
	REPUBLIC_AREA = "REPUBLIC_AREA"		# район субъекта федерации
