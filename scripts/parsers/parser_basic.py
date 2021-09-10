from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Parser:

    data: dict = field(init=True)
    mapping: dict = field(init=True, default=None)

    def _get_borrower_first_name(self, k: int = 1) -> str:
        return self.data["borrower_first_name"]

    def _get_borrower_last_name(self, k: int = 1) -> str:
        return self.data["borrower_last_name"]

    def _get_borrower_age(self, k: int = 1) -> str:
        return self.data["borrower_age"]

    def _get_loan_amount(self) -> float:
        return self.data["loan_amount"]

    def __post_init__(self):

        # verify schema here
        if self._get_loan_amount() > 900000:
            raise Exception("Too expensive!")

    def __getattr__(self, name: str) -> Any:
        """Provide an alternative route to the private methods."""
        if self.mapping:
            return self.__getattribute__(self.mapping[name])
        return self.__getattribute__(f"_{name}")
