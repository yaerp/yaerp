import unittest

from yaerp.model.currency import Currency

class TestCurrency(unittest.TestCase):

    def test_init_currency(self):
        currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 100)
        self.assertEqual(currency.alphabetic_code, 'PLN')
        self.assertEqual(currency.definition, "Polski Złoty")
        self.assertEqual(currency.dot_position, 2)
        self.assertEqual(currency.name, 'złoty')
        self.assertEqual(currency.numeric_code, '985')
        self.assertEqual(currency.penny, 1)
        self.assertEqual(currency.ratio_of_subunits_to_unit, 100)
        self.assertEqual(currency.subunit_symbol, 'gr')
        self.assertEqual(currency.symbol, 'PLN')
        self.assertEqual(currency.unit_symbol, 'zł')

    def test_init_non_standard_subunits(self):
        currency = Currency('أوقية موريتانية', 'MRU', 'Mauritanian Ouguiya', 'MRU', '929', 'أوقية', 'خمس', 5)
        self.assertEqual(currency.alphabetic_code, 'MRU')
        self.assertEqual(currency.definition, "Mauritanian Ouguiya")
        self.assertEqual(currency.dot_position, 1)
        self.assertEqual(currency.name, 'أوقية موريتانية')
        self.assertEqual(currency.numeric_code, '929')
        self.assertEqual(currency.penny, 2)
        self.assertEqual(currency.ratio_of_subunits_to_unit, 5)
        self.assertEqual(currency.subunit_symbol, 'خمس')
        self.assertEqual(currency.symbol, 'MRU')
        self.assertEqual(currency.unit_symbol, 'أوقية') 

if __name__ == '__main__':
    unittest.main()
