from .exception import YaerpError
from .metric import Metric

class CurrencyError(YaerpError):
    def __init__(self, message):
        super().__init__(message)

class Currency(Metric):

    def __init__(self, alphabetic_code, numeric_code, ratio_of_subunits_to_unit, international_name, national_unit_symbol=None, national_subunit_symbol=None, definition=None) -> None:
        super().__init__(international_name, alphabetic_code, definition)
        self.numeric_code = numeric_code
        self.ratio_of_subunits_to_unit = ratio_of_subunits_to_unit
        self.national_unit_symbol = national_unit_symbol
        self.national_subunit_symbol = national_subunit_symbol
        self.__calculate_subunit(self.ratio_of_subunits_to_unit)

    def raw2str(self, raw_int_value):
        ''' Convert raw integer value to the actual amount '''
        if raw_int_value is not int:
            ValueError('input argument must be integer')
        result = str(raw_int_value)
        if self.dot_position > 0:
            return ''.join([result[:-self.dot_position], ".", result[-self.dot_position:]])
        return result

    def amount2raw(self, amount):
        ''' Convert amount to raw integer value '''
        if self.dot_position > 0:
            return int(round(1.0 * amount * 10**self.dot_position, 0))
        return int(round(amount, 0))

    def __calculate_subunit(self, ratio_of_subunits_to_unit: int):
        for i in range(0, 19):
            if self.__is_valid_dot_position(i, ratio_of_subunits_to_unit):
                self.dot_position = i
                self.smallest_value = (10 ** self.dot_position) // ratio_of_subunits_to_unit
                return
        raise CurrencyError('calculate subunit failed - ratio of subunit to unit is not acceptable')

    def __is_valid_dot_position(self, dot_position, ratio_of_subunits_to_unit):
        unit = 10 ** dot_position
        subunit = unit // ratio_of_subunits_to_unit
        if subunit == 0:
            return False
        if (subunit * ratio_of_subunits_to_unit) == unit:
            return True
        return False 

    def __str__(self) -> str:
        return self.symbol


if __name__ == '__main__':
    currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 100)
    print(currency.definition)    
    print(f"1 grosz (1{currency.national_subunit_symbol}) = 0.0{currency.subunit_value} {currency.alphabetic_code} (0.0{currency.subunit_value}{currency.national_unit_symbol})")
    print(f"{currency.ratio_of_subunits_to_unit} groszy ({currency.ratio_of_subunits_to_unit}{currency.national_subunit_symbol}) = 1.00 {currency.alphabetic_code} (1{currency.national_unit_symbol})")
    print(f"Dot pos={currency.dot_position}")   
    print()
    currency = Currency('أوقية موريتانية', 'MRU', 'Mauritanian Ouguiya', 'MRU', '929', 'أوقية', 'خمس', 5)
    print(currency.definition)
    print(f"1 khoums ({currency.national_subunit_symbol} 1) = {currency.alphabetic_code} 0.{currency.subunit_value} ({currency.national_unit_symbol} 0.{currency.subunit_value})")
    print(f"{currency.ratio_of_subunits_to_unit} khoums ({currency.national_subunit_symbol} {currency.ratio_of_subunits_to_unit}) = {currency.alphabetic_code} 1.0 ({currency.national_unit_symbol} 1.0)")
    print(f"Dot posiion = {currency.dot_position}")  
