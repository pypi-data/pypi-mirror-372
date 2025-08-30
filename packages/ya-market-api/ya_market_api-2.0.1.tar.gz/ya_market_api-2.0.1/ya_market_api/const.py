from enum import Enum
from typing import Final


BASE_URL: Final[str] = "https://api.partner.market.yandex.ru"


class Header(Enum):
	API_KEY = "Api-Key"
