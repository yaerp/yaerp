import unittest

from yaerp.model.currency import Currency
from yaerp.model.money import Money


class TestMoney(unittest.TestCase):

    def test_init_money(self):
        currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 100)
        money = Money(12300, currency) ## 123zł 00gr
        self.assertEqual(money.amount, 12300)
        self.assertEqual(money.currency, currency)

    def test_allocate(self):
        currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 100)
        money = Money(1, currency) ## 0.01 PLN
        parts = money.allocate((1, 1)) # split amount into two "half" parts
        self.assertEqual(parts[0], 1)
        self.assertEqual(parts[1], 0) 
        money = Money(2, currency) ## 0.02 PLN
        parts = money.allocate((1, 1)) # split amount into two "half" parts
        self.assertEqual(parts[0], 1)
        self.assertEqual(parts[1], 1) 
        money = Money(3, currency) ## 0.03 PLN
        parts = money.allocate((1, 1)) # split amount into two "half" parts
        self.assertEqual(parts[0], 2)
        self.assertEqual(parts[1], 1)  
        money = Money(4, currency) ## 0.04 PLN
        parts = money.allocate((1, 1)) # split amount into two "half" parts
        self.assertEqual(parts[0], 2)
        self.assertEqual(parts[1], 2)


        money = Money(12300, currency) ## 123zł 00gr      
        parts = money.allocate((2,5)) # split amount into two parts: 2/7 and 5/7
        self.assertEqual(parts[0], 3515)
        self.assertEqual(parts[1], 8785)        
        parts = money.allocate((5,2)) # split amount into two parts: 5/7 and 2/7
        self.assertEqual(parts[0], 8786)
        self.assertEqual(parts[1], 3514) 
     
        parts = money.allocate((23,77)) # split amount into two parts: 23 % and 77 %
        self.assertEqual(parts[0], 2829) # 28.29 PLN
        self.assertEqual(parts[1], 9471) # 94.71 PLN 

        vat = (100, 23)    
        parts = money.allocate(vat) # split gross (brutto PL) into net (netto PL) and tax (podatek VAT)
        self.assertEqual(parts[0], 10000) 
        self.assertEqual(parts[1], 2300) 

    def test_allocate_non_standard_subunits(self):
        currency = Currency('أوقية موريتانية', 'MRU', 'Mauritanian Ouguiya', 'MRU', '929', 'أوقية', 'خمس', 5)
        money = Money(1230, currency) ## MRU 123.0
        parts = money.allocate((2,5)) # split amount into 2/7 and 5/7
        self.assertEqual(parts[0], 3515)
        self.assertEqual(parts[1], 8785)        
        parts = money.allocate((5,2)) # split amount into 5/7 and 2/7
        self.assertEqual(parts[0], 8786)
        self.assertEqual(parts[1], 3514)  




if __name__ == '__main__':
    unittest.main()
