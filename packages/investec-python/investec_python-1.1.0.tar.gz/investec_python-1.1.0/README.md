# investec-python
> A Python wrapper for the Investec Banking API
---
![PyPI - Version](https://img.shields.io/pypi/v/investec-python?style=for-the-badge)
![PyPI - Downloads](https://img.shields.io/pypi/dm/investec-python?style=for-the-badge)
![PyPI - License](https://img.shields.io/pypi/l/investec-python?style=for-the-badge&color=blue)
---
🛣️ [Project Roadmap](https://github.com/users/rameezk/projects/1/views/1?filterQuery=repo%3A%22rameezk%2Finvestec-python%22)

📘 [Documentation](./docs/index.md)

---

## 🚀 Quickstart

Install it:
```shell
pip install investec-python
```

Run it:
```python
from investec_python import Investec

investec = Investec(use_sandbox=True)
accounts = investec.accounts.list()

for account in accounts:
    account_balance = account.balance()
    account_transactions = account.transactions()
```

For interacting with real account data see [here](./docs/index.md#generating-the-client-credentials).

## Goals

- Interact with the Investec Banking API in the most Pythonic way possible
- 100% feature parity with the Investec Banking API
