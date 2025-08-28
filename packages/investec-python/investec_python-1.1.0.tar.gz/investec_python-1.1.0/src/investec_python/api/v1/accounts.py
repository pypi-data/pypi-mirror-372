from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from investec_python.api.api import API, APIMixin


class Balance(BaseModel):
    account_id: int = Field(alias="accountId")
    current_balance: float = Field(alias="currentBalance")
    available_balance: float = Field(alias="availableBalance")
    budget_balance: float = Field(alias="budgetBalance")
    straight_balance: float = Field(alias="straightBalance")
    cash_balance: float = Field(alias="cashBalance")
    currency: Optional[str] = Field(alias="currency")


class Transaction(BaseModel):
    account_id: str = Field(alias="accountId")
    uuid: str = Field(alias="uuid")
    type: str
    transaction_type: Optional[str] = Field(alias="transactionType")
    status: str
    description: str
    card_number: Optional[str] = Field(alias="cardNumber")
    posted_order: int = Field(alias="postedOrder")
    posting_date: date = Field(alias="postingDate")
    value_date: Optional[date] = Field(alias="valueDate")
    action_date: date = Field(alias="actionDate")
    transaction_date: date = Field(alias="transactionDate")
    amount: float
    running_balance: float = Field(alias="runningBalance")


class PendingTransaction(BaseModel):
    account_id: str = Field(alias="accountId")
    type: str
    status: str
    description: str
    transaction_date: date = Field(alias="transactionDate")
    amount: float


def _to_api_date(d: Union[date, datetime, str]) -> str:
    """Normalise to 'YYYY-MM-DD' for the API."""
    if isinstance(d, datetime):
        d = d.date()
    return d if isinstance(d, str) else d.isoformat()


class Account(APIMixin, BaseModel):
    account_id: str = Field(alias="accountId")
    account_number: str = Field(alias="accountNumber")
    account_name: str = Field(alias="accountName")
    product_name: str = Field(alias="productName")
    profile_id: str = Field(alias="profileId")
    profile_name: str = Field(alias="profileName")

    def balance(self) -> Balance:
        response = self.api.get(f"za/pb/v1/accounts/{self.account_id}/balance")
        balance = response["data"]
        return Balance(**balance)

    def transactions(
        self,
        from_date: Optional[Union[date, datetime, str]] = None,
        to_date: Optional[Union[date, datetime, str]] = None,
        transaction_type: Optional[str] = None,
    ) -> List[Transaction]:
        params = {}
        if from_date:
            params["fromDate"] = _to_api_date(from_date)
        if to_date:
            params["toDate"] = _to_api_date(to_date)
        if transaction_type:
            params["transactionType"] = transaction_type
        response = self.api.get(f"za/pb/v1/accounts/{self.account_id}/transactions", params=params)
        transactions = response["data"]["transactions"]
        return [Transaction(**transaction) for transaction in transactions]

    def pending_transactions(self) -> List[PendingTransaction]:
        response = self.api.get(f"za/pb/v1/accounts/{self.account_id}/pending-transactions")
        transactions = response["data"]["transactions"]
        return [PendingTransaction(**transaction) for transaction in transactions]


class AccountsManager:
    _api: API

    def __init__(self, api: API):
        self._api = api

    def list(self) -> List[Account]:
        response = self._api.get("za/pb/v1/accounts")
        accounts = response["data"]["accounts"]
        return [Account(**account) for account in accounts]
