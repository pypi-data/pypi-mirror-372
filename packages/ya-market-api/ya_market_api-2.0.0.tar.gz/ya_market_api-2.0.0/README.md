# ya-market-api [![codecov](https://codecov.io/gh/Kirill-Lekhov/ya-market-api/graph/badge.svg?token=2S6OTYCJF8)](https://codecov.io/gh/Kirill-Lekhov/ya-market-api)
Python3 client for public API of yandex market

## Installation
```shell
# Sync only mode
pip install ya-market-api[sync]
# Async only mode
pip install ya-market-api[async]
# All modes
pip install ya-market-api[all]
```

## Instantiating
There are several ways to work with the API (synchronous and asynchronous). Both interfaces have the same signatures, the only difference is the need to use async/await keywords.

```python
from ya_market_api.sync_api import SyncAPI		# Sync mode
from ya_market_api.async_api import AsyncAPI		# Async mode


def main() -> None:
	api = SyncAPI.build(
		api_key="...",
		base_url=...,		# (optional) may be used for test circuits
		business_id=...,		# (optional) required for the Feedback API
		campaign_id=...,		# (optional) required for the Order API
	)

	# Do things here...


async def main() -> None:
	api = await AsyncAPI.build(
		api_key="...",
		base_url=...,		# (optional) may be used for test circuits
		business_id=...,		# (optional) required for the Feedback API
		campaign_id=...,		# (optional) required for the Order API
	)

	# Do things here...

	await api.close()
```

## Where can I get api key?
See [official docs](https://yandex.ru/dev/market/partner-api/doc/ru/concepts/api-key).

## Guide API
### Get token info
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI


api = SyncAPI.build(...)
response = api.guide.get_token_info()
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/auth/getAuthTokenInfo

### Get delivery services
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI


api = SyncAPI.build(...)
response = api.guide.get_delivery_services()
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/orders/getDeliveryServices

## Guide Region API
### Get region countries
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI


api = SyncAPI.build(...)
response = api.guide.region.get_region_countries()
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/regions/getRegionsCodes

### Search region
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.guide.region.dataclass import RegionSearchRequest


api = SyncAPI.build(...)
request = RegionSearchRequest(name="Москва", limit=100, page_token=None)
response = api.guide.region.search_region(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/regions/searchRegionsByName

### Get region info
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.guide.region.dataclass import RegionInfoRequest


api = SyncAPI.build(...)
request = RegionInfoRequest(region_id=1)
response = api.guide.region.get_region_info(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/regions/searchRegionsById

### Get region children
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.guide.region.dataclass import RegionChildrenRequest


api = SyncAPI.build(...)
request = RegionChildrenRequest(region_id=1, page=1, page_size=10)
response = api.guide.region.get_region_children(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/regions/searchRegionChildren

## Feedback API
### Get feedback list
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.feedback.dataclass import FeedbackListRequest

from arrow import get


api = SyncAPI.build(...)
response = api.feedback.get_feedback_list()
# or
request = FeedbackListRequest(datetime_from=get(2025, 1, 1), date_to=get(2025, 1, 31))
response = api.feedback.get_feedback_list(request)
```

See signature of the FeedbackListRequest class and the docs to get info about all available params.

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/goods-feedback/getGoodsFeedbacks

### Get feedback comment list
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.feedback.dataclass import FeedbackCommentListRequest


api = SyncAPI.build(...)
request = FeedbackCommentListRequest(feedback_id=512)
response = api.feedback.get_feedback_comment_list(request)
```

See signature of the FeedbackCommentListRequest class and the docs to get info about all available params.

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/goods-feedback/getGoodsFeedbackComments

### Add feedback comment
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.feedback.dataclass import FeedbackCommentAddRequest


api = SyncAPI.build(...)
request = FeedbackCommentAddRequest.create(feedback_id=512, text="COMMENT_TEXT", parent_id=1024)
response = api.feedback.add_feedback_comment(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/goods-feedback/updateGoodsFeedbackComment

### Update feedback comment
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.feedback.dataclass import FeedbackCommentUpdateRequest


api = SyncAPI.build(...)
request = FeedbackCommentUpdateRequest.create(feedback_id=512, comment_id=2048, text="COMMENT_TEXT")
response = api.feedback.update_feedback_comment(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/goods-feedback/updateGoodsFeedbackComment

### Delete feedback comment
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.feedback.dataclass import FeedbackCommentDeleteRequest


api = SyncAPI.build(...)
request = FeedbackCommentDeleteRequest(id=512)
response = api.feedback.delete_comment_feedback(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/goods-feedback/deleteGoodsFeedbackComment

### Skip feedback reaction
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.feedback.dataclass import FeedbackReactionSkipRequest


api = SyncAPI.build(...)
request = FeedbackReactionSkipRequest(feedback_ids=(64, 128, 256))
response = api.feedback.skip_feedback_reaction(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/goods-feedback/skipGoodsFeedbacksReaction

## Offer API
### Get offer list by business id
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.offer.dataclass import OfferListByBusinessRequest


api = SyncAPI.build(...)
response = api.offer.get_offer_list_by_business()
# or
request = OfferListByBusinessRequest(category_ids=[1, 2, 3], limit=10)
response = api.offer.get_offer_list_by_business(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/business-assortment/getOfferMappings

## Campaign API
### Get campaign list
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.campaign.dataclass import CampaignListRequest


api = SyncAPI.build(...)
response = api.campaign.get_campaign_list()
# or
request = CampaignListRequest(page=1)
response = api.campaign.get_campaign_list(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/campaigns/getCampaigns

## Order API
### Get order
```python
# Sync mode
from ya_market_api.sync_api import SyncAPI
from ya_market_api.order.dataclass import OrderGetRequest


api = SyncAPI.build(...)
request = OrderGetRequest(order_id=...)
response = api.order.get_order(request)
```

Docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/orders/getOrder
