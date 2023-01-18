from .metric import MetricError
from .quantity import Quantity


class MoneyError(MetricError):
    def __init__(self, message):
        super().__init__(message)

class Money(Quantity):
    def __init__(self, amount: int, one_unit_in_subunits: int) -> None:
        super().__init__()
        self.amount = amount
        self.penny = one_unit_in_subunits
        self.dot_position = 0

    def calculate_subunit(self, one_unit_in_subunits: int):
        if one_unit_in_subunits == 0:
            self.penny = 0
            self.dot_position = 0
        elif one_unit_in_subunits == 1:
            raise MoneyError('Incorrect subunits in unit')
        elif one_unit_in_subunits <= 10:
            self.penny = 10 // one_unit_in_subunits
            self.dot_position = 1
        elif one_unit_in_subunits <= 100:
            self.penny = 100 // one_unit_in_subunits
            self.dot_position = 2
        elif one_unit_in_subunits <= 1000:
            self.penny = 1000 // one_unit_in_subunits
            self.dot_position = 3
        elif one_unit_in_subunits <= 10000:
            self.penny = 10000 // one_unit_in_subunits
            self.dot_position = 4
        else:
            raise MoneyError('Incorrect subunit number')

    def allocate(self, ratios: list) -> list:
        total = 0
        for idx, ratio in enumerate(ratios):
            total += ratios[idx]
        reminder = self.copy()
        results = []
        for idx in enumerate(ratios):
            results.append( self.amount * ratios[idx] // total )
            reminder = reminder - results[idx]

        if reminder < 0:
            raise MoneyError("Money allocate process create more amount than actually got")
        for i in range(reminder, self.penny()):
            reminder = reminder - self.penny()
            results[i] = results[i] + self.penny()
        if reminder > 0:
            raise MoneyError("Money allocate process remains with some unallocated amount")
        return results