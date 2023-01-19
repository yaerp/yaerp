from .metric import MetricError
from .quantity import Quantity


class MoneyError(MetricError):
    def __init__(self, message):
        super().__init__(message)

class Money(Quantity):
    def __init__(self, amount: int, currency) -> None:
        super().__init__()
        self.amount = amount
        self.currency = currency

    def allocate(self, ratios: list) -> list:
        total = 0
        penny = self.currency.penny
        for idx, ratio in enumerate(ratios):
            total += ratios[idx]
        reminder = self.amount
        parts = []
        for idx, ratio in enumerate(ratios):
            value = self.amount * ratio // total
            ## round to penny (if penny is not worth 1)
            if value % penny:
                value = (value // penny) * penny
            reminder = reminder - value            
            parts.append(value)
        if reminder < 0:
            raise MoneyError("Money allocate process create more amount than actually got")

        ## distribute the possible rest
        for idx, part in enumerate(parts):
            if reminder > 0:
                reminder = reminder - penny
                parts[idx] = parts[idx] + penny
                continue
            elif reminder == 0:
                break
            raise MoneyError(f"Money allocate process failed {parts}")

        if reminder > 0:
            raise MoneyError("Money allocate process remains with some unallocated amount")
        return parts

if __name__ == '__main__':
    from currency import Currency
    currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 5)
    money = Money(12300, currency=currency)
    print(money.allocate([7741, 2321]))