from decimal import Decimal
from .metric import Metric

class Currency(Metric):

    def __init__(self, alphabetic_code, numeric_code, ratio_of_subunits_to_unit, international_name, 
                 national_unit_symbol=None, national_subunit_symbol=None, definition=None,
                 fraction_char='.', group_separator_char='\u00A0', separator_positions=(3,6,9,12,15,18),
                 separator_predicate=lambda amount: abs(amount) > 999999
                 ) -> None:
        super().__init__(international_name, alphabetic_code, definition)
        self.numeric_code = numeric_code
        self.ratio_of_subunits_to_unit = ratio_of_subunits_to_unit
        self.national_unit_symbol = national_unit_symbol
        self.national_subunit_symbol = national_subunit_symbol
        self.__calculate_subunit(self.ratio_of_subunits_to_unit)
        self.fraction_char = fraction_char
        self.group_separator_char = group_separator_char
        self.separator_positions = separator_positions
        if separator_predicate:
            self.separator_predicate = separator_predicate
        else:
            self.separator_predicate = lambda _: True

    def raw2amount(self, raw_int_value, new_fraction_char=None, ommit_zero_fraction=False, new_group_separator_char=None, new_separator_positions=None, new_separator_predicate=None):
        ''' Convert raw integer value to the actual amount '''
        if raw_int_value is not int:
            ValueError('input argument must be integer')
        result = str(raw_int_value)
        zero_fraction = bool(raw_int_value % self.ratio_of_subunits_to_unit) == 0
        sign = ''
        if result[0] == '-':
            sign = '-'
            result = result[1:]
        integ_part_str = result[:-self.fraction_pos]
        fract_part_str = result[-self.fraction_pos:]
        if not integ_part_str:
            integ_part_str = "0"
        fract_char = None
        sep_char = None
        sep_pos = None
        sep_pred = None
        if new_fraction_char:
            fract_char = new_fraction_char
        else:
            fract_char = self.fraction_char
        if new_group_separator_char:
            sep_char = new_group_separator_char
        else:
            sep_char = self.group_separator_char
        if new_separator_positions:
            sep_pos = new_separator_positions
        else:
            sep_pos = self.separator_positions
        if new_separator_predicate:
            sep_pred = new_separator_predicate
        else:
            sep_pred = self.separator_predicate
        if sep_char and sep_pos and sep_pred(raw_int_value):
            rev_parts = []
            for idx, c in enumerate(reversed(integ_part_str)):
                if idx in sep_pos:
                    rev_parts.append(sep_char)
                rev_parts.append(c)
            integ_part_str = ''.join(reversed(rev_parts))
        if self.fraction_pos > 0:
            if ommit_zero_fraction and zero_fraction:
                result = ''.join([sign, integ_part_str])
            else:                  
                result = ''.join([sign, integ_part_str, fract_char, fract_part_str])
        return result

    def amount2raw(self, regular_amount, current_fraction_char=None, current_group_separator_char=None):
        ''' Convert regular amount to the "raw integer" value '''
        if isinstance(regular_amount, str):
            if current_group_separator_char:
                regular_amount = regular_amount.replace(current_group_separator_char, "")
            else:
                regular_amount = regular_amount.replace(self.group_separator_char, "")
            fract_char = None
            if current_fraction_char:
                fract_char = current_fraction_char
            else:
                fract_char = self.fraction_char
            if fract_char != '.':
                regular_amount = regular_amount.replace(fract_char, ".")        
            regular_amount = float(regular_amount)
        if self.fraction_pos > 0:
            result = int(round(1.0 * regular_amount * 10**self.fraction_pos, 0))
        else:
            result = int(round(regular_amount, 0))
        if result % self.smallest_value == 0:
            return result
        raise ValueError(f'incorrect fraction part of the amount')

    def __calculate_subunit(self, ratio_of_subunits_to_unit: int):
        for i in range(0, 19):
            if self.__is_valid_dot_position(i, ratio_of_subunits_to_unit):
                self.fraction_pos = i
                self.smallest_value = (10 ** self.fraction_pos) // ratio_of_subunits_to_unit
                return
        raise ValueError('calculate subunit failed - ratio of subunit to unit is not acceptable')

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
    print(f"Dot pos={currency.fraction_pos}")   
    print()
    currency = Currency('أوقية موريتانية', 'MRU', 'Mauritanian Ouguiya', 'MRU', '929', 'أوقية', 'خمس', 5)
    print(currency.definition)
    print(f"1 khoums ({currency.national_subunit_symbol} 1) = {currency.alphabetic_code} 0.{currency.subunit_value} ({currency.national_unit_symbol} 0.{currency.subunit_value})")
    print(f"{currency.ratio_of_subunits_to_unit} khoums ({currency.national_subunit_symbol} {currency.ratio_of_subunits_to_unit}) = {currency.alphabetic_code} 1.0 ({currency.national_unit_symbol} 1.0)")
    print(f"Dot posiion = {currency.fraction_pos}")  
