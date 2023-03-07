import unittest

from yaerp.model.currency import Currency

class TestCurrency(unittest.TestCase):

    def test_init_currency(self):
        currency = Currency('PLN', '985', 100, 'Polish Złoty', 'zł', 'gr')
        self.assertEqual(currency.symbol, 'PLN')
        self.assertEqual(currency.numeric_code, '985')
        self.assertEqual(currency.ratio_of_subunits_to_unit, 100)
        self.assertEqual(currency.fraction_pos, 2)
        self.assertEqual(currency.smallest_value, 1)
        self.assertEqual(currency.name, 'Polish Złoty')
        self.assertEqual(currency.national_unit_symbol, 'zł')
        self.assertEqual(currency.national_subunit_symbol, 'gr')
        

    def test_init_non_standard_subunits(self):
        currency = Currency('MRU', '929', 5, 'Mauritanian Ouguiya', 'أوقية', 'خمس', definition='أوقية موريتانية') 
        self.assertEqual(currency.symbol, 'MRU')
        self.assertEqual(currency.numeric_code, '929')
        self.assertEqual(currency.ratio_of_subunits_to_unit, 5)
        self.assertEqual(currency.fraction_pos, 1)
        self.assertEqual(currency.smallest_value, 2)
        self.assertEqual(currency.name, 'Mauritanian Ouguiya')
        self.assertEqual(currency.national_unit_symbol, 'أوقية')
        self.assertEqual(currency.national_subunit_symbol, 'خمس') 
        self.assertEqual(currency.definition, 'أوقية موريتانية')

if __name__ == '__main__':
    unittest.main()
