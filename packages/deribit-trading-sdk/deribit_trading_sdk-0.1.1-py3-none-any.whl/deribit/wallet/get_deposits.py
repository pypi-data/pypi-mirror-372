from typing_extensions import TypedDict, Literal, NotRequired
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import AuthedClientMixin, ApiResponse, validator

ClearanceState = Literal['in_progress', 'pending_admin_decision', 'pending_user_input', 'success', 'failed', 'cancelled', 'refund_initiated', 'refunded']
DepositState = Literal['pending', 'completed', 'rejected', 'replaced']

class Deposit(TypedDict):
  address: str
  amount: Decimal
  clearance_state: ClearanceState
  currency: str
  note: NotRequired[str]
  received_timestamp: int
  refund_transaction_id: NotRequired[str]
  source_address: str
  state: DepositState
  transaction_id: NotRequired[str]
  updated_timestamp: NotRequired[int]

class DepositsResponse(TypedDict):
  count: int
  data: list[Deposit]

validate_response = validator(DepositsResponse)

@dataclass(frozen=True)
class GetDeposits(AuthedClientMixin):
  async def get_deposits(
    self, currency: str, *,
    count: int | None = None,
    offset: int | None = None,
    validate: bool = True,
  ) -> ApiResponse[DepositsResponse]:
    """Get your deposit history.
    
    - `currency`: The currency to get the deposits of.
    - `count`: Number of requested items (default: 10, max: 1000)
    - `offset`: The offset for pagination (default: 0)
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#private-get_deposits)
    """
    params: dict = {'currency': currency}
    if count is not None:
      params['count'] = count
    if offset is not None:
      params['offset'] = offset
    r = await self.authed_request('/private/get_deposits', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  