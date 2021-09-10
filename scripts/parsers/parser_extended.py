from dataclasses import dataclass, field
from typing import Any


@dataclass
class Parser:

    data: dict = field(init=True)
    mapping: dict = field(init=True, default=None)

    def _get_borrower_first_name(self, k: int = 1) -> str:
        return self.data[f"borrower_{k}_first_name"]

    def _get_borrower_last_name(self, k: int = 1) -> str:
        return self.data[f"borrower_{k}_last_name"]

    def _get_borrower_age(self, k: int = 1) -> str:
        return self.data[f"borrower_{k}_age"]

    def _get_loan_amount(self) -> float:
        return self.data["loan_amount"]

    def __getattr__(self, name: str) -> Any:
        if self.mapping:
            return self.__getattribute__(self.mapping[name])
        return self.__getattribute__(f"_{name}")
