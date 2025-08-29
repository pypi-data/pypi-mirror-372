from dataclasses import dataclass

from .get_account_summary import GetAccountSummary
from .get_account_summaries import GetAccountSummaries

@dataclass(frozen=True)
class Account(
  GetAccountSummary,
  GetAccountSummaries,
):
  ...