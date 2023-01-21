from .exception import YaerpError
from .quantity import Quantity
from .currency import Currency

class MoneyError(YaerpError):
    def __init__(self, message):
        super().__init__(message)

class Money(Quantity):
    def __init__(self, raw_int: int, currency: Currency) -> None:
        super().__init__()
        self.__raw_value = raw_int
        self.currency = currency

    def __str__(self):
        return ''.join([self.currency.symbol, "\u00A0", self.text()])

    def text(self):
        result = str(self.__raw_value)
        if self.currency.dot_position > 0:
            return ''.join([result[:-self.currency.dot_position], ".", result[-self.currency.dot_position:]])
        return result

    def __repr__(self) -> str:
        return ''.join([self.__class__.__name__, '(', str(self.__raw_value), ', ', self.currency.__repr__(), ')'])

    def raw_int(self):
        return self.__raw_value

    def __abs__(self):
        return Money(abs(self.__raw_value), self.currency)

    def __bool__(self):
        return self.__raw_value.__bool__()

    def __neg__(self):
        return Money(-self.__raw_value, self.currency)

    def __add__(self, other):
        if self.currency != other.currency:
            raise MoneyError('cannot add 2 different currencies')
        return Money(self.__raw_value + other.__raw_value, self.currency)

    def __sub__(self, other):
        if self.currency != other.currency:
            raise MoneyError('cannot subtract 2 different currencies')
        return Money(self.__raw_value - other.__raw_value, self.currency)

    def __mul__(self, coefficient):
        result = int(self.__raw_value * coefficient)
        return Money(result, self.currency)

    def __floordiv__(self, factor):
        result = self.__raw_value // factor
        return Money(result, self.currency)

    def __truediv__(self, factor):
        result = round(self.__raw_value / factor, 0)
        return Money(result, self.currency)

    def __lt__(self, other):
        return self.__raw_value < other.__raw_value

    def __le__(self, other):
        return self.__raw_value <= other.__raw_value

    def __eq__(self, other):
        return self.__raw_value == other.__raw_value

    def __ne__(self, other):
        return self.__raw_value != other.__raw_value

    def __ge__(self, other):
        return self.__raw_value >= other.__raw_value

    def __gt__(self, other):
        return self.__raw_value > other.__raw_value

    def allocate(self, ratios: list) -> list:
        total = 0
        penny = self.currency.smallest_value
        for idx, ratio in enumerate(ratios):
            total += ratios[idx]
        reminder = self.__raw_value
        parts = []
        for idx, ratio in enumerate(ratios):
            value = self.__raw_value * ratio // total
            ## round to penny (if penny is not worth 1)
            if value % penny:
                value = (value // penny) * penny
            reminder = reminder - value            
            parts.append(value)
        if reminder < 0:
            raise RuntimeError("Money allocate process create more amount than actually got")

        ## distribute the possible rest
        for idx, part in enumerate(parts):
            if reminder > 0:
                reminder = reminder - penny
                parts[idx] = parts[idx] + penny
                continue
            elif reminder == 0:
                break
            raise RuntimeError(f"Money allocate process failed {parts}")

        if reminder > 0:
            raise RuntimeError("Money allocate process remains with some unallocated amount")
        
        return [Money(raw_amount, self.currency) for raw_amount in parts]
