from ya_market_api.base.router import Router


class FeedbackRouter(Router):
	def feedback_list(self, business_id: int) -> str:
		return f"{self.base_url}/businesses/{business_id}/goods-feedback"

	def feedback_comment_list(self, business_id: int) -> str:
		return f"{self.base_url}/businesses/{business_id}/goods-feedback/comments"

	def feedback_comment_add(self, business_id: int) -> str:
		return f"{self.base_url}/businesses/{business_id}/goods-feedback/comments/update"

	def feedback_comment_update(self, business_id: int) -> str:
		return f"{self.base_url}/businesses/{business_id}/goods-feedback/comments/update"

	def feedback_comment_delete(self, business_id: int) -> str:
		return f"{self.base_url}/businesses/{business_id}/goods-feedback/comments/delete"

	def feedback_reaction_skip(self, business_id: int) -> str:
		return f"{self.base_url}/businesses/{business_id}/goods-feedback/skip-reaction"
