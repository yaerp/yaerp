from metric import Metric, MetricError

class CurrencyError(MetricError):
    def __init__(self, message):
        super().__init__(message)

class Currency(Metric):
    def __init__(self, name, symbol, definition, alphabetic_code, numeric_code, unit_symbol, subunit_symbol, ratio_of_subunits_to_unit) -> None:
        super().__init__(name, symbol, definition)
        self.alphabetic_code = alphabetic_code
        self.numeric_code = numeric_code
        self.unit_symbol = unit_symbol
        self.subunit_symbol = subunit_symbol
        self.ratio_of_subunits_to_unit = ratio_of_subunits_to_unit
        self.__calculate_subunit(self.ratio_of_subunits_to_unit)

    def __calculate_subunit(self, ratio_of_subunits_to_unit: int):
        for i in range(0, 19):
            if self.__is_valid_dot_position(i, ratio_of_subunits_to_unit):
                self.dot_position = i
                self.penny = (10 ** self.dot_position) // ratio_of_subunits_to_unit
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


if __name__ == '__main__':
    currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 100)
    print(currency.definition)    
    print(f"1 grosz (1{currency.subunit_symbol}) = 0.0{currency.penny} {currency.alphabetic_code} (0.0{currency.penny}{currency.unit_symbol})")
    print(f"{currency.ratio_of_subunits_to_unit} groszy ({currency.ratio_of_subunits_to_unit}{currency.subunit_symbol}) = 1.00 {currency.alphabetic_code} (1{currency.unit_symbol})")
    print(f"Dot pos={currency.dot_position}")   
    print()
    currency = Currency('أوقية موريتانية', 'MRU', 'Mauritanian Ouguiya', 'MRU', '929', 'أوقية', 'خمس', 5)
    print(currency.definition)
    print(f"1 khoums ({currency.subunit_symbol} 1) = {currency.alphabetic_code} 0.{currency.penny} ({currency.unit_symbol} 0.{currency.penny})")
    print(f"{currency.ratio_of_subunits_to_unit} khoums ({currency.subunit_symbol} {currency.ratio_of_subunits_to_unit}) = {currency.alphabetic_code} 1.0 ({currency.unit_symbol} 1.0)")
    print(f"Dot posiion = {currency.dot_position}")  
