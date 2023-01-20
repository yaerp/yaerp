import unittest

from yaerp.model.currency import Currency
from yaerp.model.money import Money


class TestMoney(unittest.TestCase):

    def test_init_money(self):
        currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 100)
        money = Money(12300, currency) ## 123zł 00gr
        self.assertEqual(money.raw_int(), 12300)
        self.assertEqual(money.currency, currency)

    def test_allocate(self):
        currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 100)
        money = Money(1, currency) ## 0.01 PLN
        parts = money.allocate((1, 1)) # split amount into two "half" parts
        self.assertEqual(parts[0].raw_int(), 1)
        self.assertEqual(parts[1].raw_int(), 0) 
        money = Money(2, currency) ## 0.02 PLN
        parts = money.allocate((1, 1)) # split amount into two "half" parts
        self.assertEqual(parts[0].raw_int(), 1)
        self.assertEqual(parts[1].raw_int(), 1) 
        money = Money(3, currency) ## 0.03 PLN
        parts = money.allocate((1, 1)) # split amount into two "half" parts
        self.assertEqual(parts[0].raw_int(), 2)
        self.assertEqual(parts[1].raw_int(), 1)  
        money = Money(4, currency) ## 0.04 PLN
        parts = money.allocate((1, 1)) # split amount into two "half" parts
        self.assertEqual(parts[0].raw_int(), 2)
        self.assertEqual(parts[1].raw_int(), 2)


        money = Money(12300, currency) ## 123zł 00gr      
        parts = money.allocate((2,5)) # split amount into two parts: 2/7 and 5/7
        self.assertEqual(parts[0].raw_int(), 3515)
        self.assertEqual(parts[1].raw_int(), 8785)        
        parts = money.allocate((5,2)) # split amount into two parts: 5/7 and 2/7
        self.assertEqual(parts[0].raw_int(), 8786)
        self.assertEqual(parts[1].raw_int(), 3514) 
     
        parts = money.allocate((23,77)) # split amount into two parts: 23 % and 77 %
        self.assertEqual(parts[0].raw_int(), 2829) # 28.29 PLN
        self.assertEqual(parts[1].raw_int(), 9471) # 94.71 PLN 

        vat = (100, 23)    
        parts = money.allocate(vat) # split gross (brutto) into net (netto) and tax (podatek)
        self.assertEqual(parts[0].raw_int(), 10000) 
        self.assertEqual(parts[1].raw_int(), 2300) 

    def test_allocate_non_standard_subunits(self):
        currency = Currency('أوقية موريتانية', 'MRU', 'Mauritanian Ouguiya', 'MRU', '929', 'أوقية', 'خمس', 5)
        money = Money(1230, currency) ## MRU 123.0
        parts = money.allocate((2,5)) # split amount into 2/7 and 5/7
        self.assertEqual(parts[0].raw_int(), 352)
        self.assertEqual(parts[1].raw_int(), 878)   
        parts = money.allocate((5,2)) # split amount into 2/7 and 5/7
        self.assertEqual(parts[0].raw_int(), 880)
        self.assertEqual(parts[1].raw_int(), 350) 

        money = Money(2, currency) ## 0.2 MRU, the smallest possible amount
        parts = money.allocate((1, 1)) # "half" parts
        self.assertEqual(parts[0].raw_int(), 2)
        self.assertEqual(parts[1].raw_int(), 0) 
        money = Money(4, currency) ## 0.4 MRU
        parts = money.allocate((1, 1)) # "half" parts
        self.assertEqual(parts[0].raw_int(), 2)
        self.assertEqual(parts[1].raw_int(), 2) 
        money = Money(6, currency) ## 0.4 MRU
        parts = money.allocate((1, 1)) # "half" parts
        self.assertEqual(parts[0].raw_int(), 4)
        self.assertEqual(parts[1].raw_int(), 2)

    def test_operators(self):
        currency = Currency('złoty', 'PLN', 'Polski Złoty', 'PLN', '985', 'zł', 'gr', 100)
        a = Money(0, currency) ## 123zł 00gr
        b = Money(12300, currency) ## 123zł 00gr
        c = Money(12300, currency) ## 123zł 00gr
        d = Money(12301, currency) ## 123zł 00gr
        self.assertTrue(a < b)
        self.assertFalse(b < a)
        self.assertFalse(b < c)       
        self.assertTrue(a <= b)
        self.assertTrue(b <= c)
        self.assertFalse(b <= a)
        self.assertTrue(b == b)
        self.assertTrue(b == c)
        self.assertFalse(a == b)
        self.assertTrue(a == a)
        self.assertFalse(a >= b)
        self.assertTrue(b >= c)
        self.assertTrue(b >= a)
        self.assertFalse(a > b)
        self.assertTrue(b > a)
        self.assertFalse(b > c)
        self.assertEqual(a+a, a)
        self.assertEqual((a+b).raw_int(), 12300)
        self.assertEqual((b+a).raw_int(), 12300)
        self.assertEqual((c-d).raw_int(), -1)
        self.assertEqual((d-c).raw_int(), 1)
        self.assertEqual((abs(a-b)).raw_int(), 12300)
        self.assertEqual((a/3).raw_int(), 0)
        self.assertEqual((b/333).raw_int(), 37)
        self.assertEqual((b//333).raw_int(), 36)
        self.assertEqual((b/123).raw_int(), 100)
        self.assertEqual((b//123).raw_int(), 100) 
        self.assertEqual((-b).raw_int(), -12300)
        self.assertEqual((-(-b)).raw_int(), 12300)
        self.assertFalse(a)
        self.assertTrue(b)
        self.assertTrue(-b)

if __name__ == '__main__':
    unittest.main()
