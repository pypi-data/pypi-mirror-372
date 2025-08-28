import datetime


class TestInvestec:
    def test_api_url(self, investec_client):
        assert investec_client.api_url == "https://openapisandbox.investec.com"

    def test_account_list(self, investec_client):
        accounts = investec_client.accounts.list()

        assert len(accounts) > 0
        for account in accounts:
            assert account.account_id is not None

    def test_account_balance(self, investec_client):
        account = investec_client.accounts.list()[0]
        balance = account.balance()

        assert balance.current_balance is not None

    def test_account_transactions(self, investec_client):
        account = investec_client.accounts.list()[0]
        transactions = account.transactions()

        assert len(transactions) > 0
        assert transactions[0].amount is not None

    def test_account_transactions_date_range(self, investec_client):
        account = investec_client.accounts.list()[0]
        from_date = datetime.date(2025, 5, 28)
        to_date = datetime.date(2025, 5, 29)
        transactions = account.transactions(from_date=from_date, to_date=to_date)

        assert len(transactions) > 0
        for transaction in transactions:
            assert transaction.amount is not None
            assert transaction.transaction_date is not None
            assert transaction.transaction_date >= from_date
            assert transaction.transaction_date <= to_date

    def test_account_transactions_transaction_type(self, investec_client):
        account = investec_client.accounts.list()[0]
        transactions = account.transactions(transaction_type="CardPurchases")
        assert len(transactions) > 0
        for transaction in transactions:
            assert transaction.transaction_type == "CardPurchases"

    def test_pending_transactions(self, investec_client):
        account = investec_client.accounts.list()[0]
        transactions = account.pending_transactions()
        assert len(transactions) > 0
