from math import floor
from .quantity import Quantity
from .currency import Currency

class Money(Quantity):

    def __init__(self, currency: Currency, amount, *, raw: int = 0 ) -> None:
        if amount and raw:
            ValueError("'amount' should be set to zero if 'raw' parameter is in use")
        super().__init__()
        self.currency = currency
        if amount:        
            self.__raw_value = self.currency.amount2raw(amount)
        else:
            self.__raw_value = raw

    def __str__(self):
        return ''.join([self.currency.symbol, "\u00A0", self.text()])

    def text(self):
        # result = str(self.__raw_value)
        # if self.currency.fraction_pos > 0:
        #     return ''.join([result[:-self.currency.fraction_pos], ".", result[-self.currency.fraction_pos:]])
        # return result
        return self.currency.raw2amount(self.__raw_value)

    def __repr__(self) -> str:
        return ''.join([
            self.__class__.__name__, 
            '(', self.currency.raw2amount(self.__raw_value), 
            ', ', self.currency.__repr__(), 
            ')'
        ])

    def raw_int(self):
        return self.__raw_value

    def __abs__(self):
        return Money(self.currency, 0, raw=abs(self.__raw_value))

    def __bool__(self):
        return self.__raw_value.__bool__()

    def __neg__(self):
        return Money(self.currency, 0, raw=-self.__raw_value)

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError('attempt to add two different currencies')
        return Money(self.currency, 0, raw=(self.__raw_value + other.__raw_value))

    def __sub__(self, other):
        if self.currency != other.currency:
            raise ValueError('attempt to subtract 2 different currencies')
        return Money(self.currency, 0, raw=(self.__raw_value - other.__raw_value))

    def __mul__(self, coefficient):
        result = self._raw_mul(coefficient)
        return Money(self.currency, 0, raw=result)

    def _raw_mul(self, coefficient):
        if self.currency.ratio_of_subunits_to_unit % 10 == 0:
            result = int(self.__raw_value * coefficient)
        else:
            result = int(round(self.__raw_value * self.currency.ratio_of_subunits_to_unit * coefficient / 10**self.currency.fraction_pos, 0))
            result = result * 10**self.currency.fraction_pos // self.currency.ratio_of_subunits_to_unit
        return result

    def __floordiv__(self, factor):
        if self.currency.ratio_of_subunits_to_unit % 10 == 0:
            result = self.__raw_value // factor
        else:
            result = int(floor(self.__raw_value * self.currency.ratio_of_subunits_to_unit / factor / 10**self.currency.fraction_pos))
            result = result * 10**self.currency.fraction_pos // self.currency.ratio_of_subunits_to_unit
        return Money(self.currency, 0, raw=result)

    def __truediv__(self, factor):
        if self.currency.ratio_of_subunits_to_unit % 10 == 0:
            result = int(round(self.__raw_value / factor, 0))
        else:
            result = int(round(self.__raw_value * self.currency.ratio_of_subunits_to_unit / factor / 10**self.currency.fraction_pos, 0))
            result = result * 10**self.currency.fraction_pos // self.currency.ratio_of_subunits_to_unit
        return Money(self.currency, 0, raw=result)

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
            value = int(self._raw_mul(ratio) // total)
            # value = int(self.__raw_value * ratio // total)


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
        
        return [Money(self.currency, 0, raw=raw_amount) for raw_amount in parts]
