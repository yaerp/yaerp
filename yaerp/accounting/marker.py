
from enum import Enum


class Mark(Enum):
    pass

class Marker:
    def __init__(self, *mark_container):
        # self.marks = set(mark_container) 
        self._marks = set()       
        for mark in mark_container:
            self.add(mark)

    def add(self, mark):
        if not isinstance(mark, Mark):
            raise ValueError(f'{mark} ({type(mark)}) is not inherited from {Mark}')
        self._marks.add(mark)

    def remove(self, mark):
        self._marks.remove(mark)

    def remove_type(self, *enum_class):
        while True:
            for mark in self._marks:
                if isinstance(mark, enum_class):
                    self._marks.remove(mark)
                    break
            return

    def has(self, mark):
        return {mark}.issubset(self._marks)

    def has_all(self, *marks):
        return set(marks).issubset(self._marks)

    def has_any(self, *marks):
        for m in marks:
            if {m}.issubset(self._marks):
                return True
        return False

    def has_type(self, *_class):
        for mark in self._marks:
            if isinstance(mark, _class):
                return True
        return False
    
    def __hash__(self):
        return hash(self._marks)
    
    def __eq__(self, other):
        return len(self._marks) == len(self._marks.intersection(other))


class PropertyContainer:
    def __init__(self):
        self._values = dict(Mark)

    def append_property_value(self, property: Mark, property_value: Mark):

        if not property in self._values:
            self._values[property] = [property]
        ancestors = []
        if property_value:
            ancestors = self.get_property_values(property_value)

        if ancestors and property in ancestors:
            # prevent loop-reference
            raise ValueError(f"add value failed - property '{property}' already exist in '{property_value}' ancestors")
        
        if property_value and property_value not in self._values[property]:
                self._values[property].append(property_value)

    def get_property_values(self, property: Mark):
        result = []
        for idx, ancestor in enumerate(self._values[property]):
            result.append(ancestor)
            if idx == 0:
                continue
            result.extend(self.get_property_values(ancestor))
        return result

    def remove_value(self, property: Mark, *values):
        for value in values:
            self._values[property].remove(value)

    def remove_type(self, property: Mark, *_class):
        while True:
            for value in self._values[property]:
                if isinstance(value, _class):
                    if type(property) in _class and property == value:
                        # ommit property instance in _values
                        continue
                    self._values[property].remove(value)
                    break
            return

    def has_value(self, property: Mark, value: Mark):
        return value in self._values[property]
        # return {value}.issubset(self._values[property])

    def has_all_of_values(self, property, *values):
        for value in values:
            if value not in self._values[property]:
                return False
        return True
        # return set(values).issubset(self._values[property])

    def has_any_of_value(self, property, *values):
        for value in values:
            if value in self._values[property]:
                return True
        return False
        # for m in values:
        #     if {m}.issubset(self._values[property]):
        #         return True
        # return False

    def has_type(self, property, *_class):
        for mark in self._values[property]:
            if isinstance(mark, _class):
                return True
        return False

    # def __hash__(self):
    #     return hash(self._markers)
    
    # def __eq__(self, other):
    #     return len(self._markers.values()) == len(set(other._markers.values()).intersection(other))


class BalanceSheet(Enum):
    """ Marker for Balance Sheet accounts """
    ASSETS = 1
    LIABILITIES = 2
    EQUITY = 3


class IncomeStatement(Mark):
    """ Marker for Incoming Sheet accounts """
    REVENUES = 4
    EXPENSES = 5


class Assets(Mark):
    """ Marker for Assets accounts """
    RECEIVABLES = 100       # naleznosci u klientow
    CASH = 110
    BANK = 120    
    TAX_RECEIVABLES = 130   # zobowiazania podatkowe
    STOCK = 160             # asortyment
    STOCK_ADJUSTMENT = 169
    EQUIPMENT = 170         # środki trwałe
    ACCUMULATED_DEPRECIATION_EQUIPMENT = 179
    PREPAID_EXPENSES = 160  # rozl. miedzyokresowe czynne
    ACCRUED_INCOME = 161    # rozl. miedzyokresowe czynne


class Liabilities(Mark):
    """ Marker for Liability accounts """
    PAYABLES = 200          # zobowiazania wobec dostawcow
    TAX_PAYABLES = 230      # naleznosci podatkowe
    ACCRUED_EXPENSES = 260  # rozl. miedzyokresowe bierne
    DEFERRED_INCOME = 261   # rozl. miedzyokresowe bierne

class Equity(Mark):
    """ Marker for Equity accounts """
    OWNERS_CAPITAL = 300
    RETAINED_EARNINGS = 320
    DIVIDENDS = 332
    PROFIT = 350


class Revenues(Mark):
    """ Marker for Revenue accounts """
    SALES = 400
    ''' SALES OF GOODS/SERVICES '''
    OTHER_INCOME = 480


class Expenses(Mark):
    """ Expense accounts """
    COST_OF_GOODS_SOLD = 500 # warość sprzedanych towarów w cenach zakupu / koszt wytworzenia sprzedanych produktów
    SELLING_GENERAL_AND_ADMINISTRATIVE_EXPENSES = 530
    DEPRECIATION_EXPENSE = 560
    OTHER_EXPENSE = 580

class Clearing(Mark):
    ''' Clearing Accounts are the registers used for track and reconcile transactions that are in process '''

    ASSET_CLEARING_ACCOUNT = 971  # rozliczenie naleznosci 
    ''' "Asset Clearing Account" \n
    Usually used for collecting and tracking the partial payments toward a specific invoice(s).
    Example:
    - 1. the payment received, 100$
            - Dr( bank a/c ) Cr( clearing a/c )
    - 2. the invoice for the customer issued, 300$
            - Dr( clearing a/c ) Cr( customer a/c )
    - 3. the payment received, 100$
            - Dr( bank a/c ) Cr( clearing a/c )
    - 4. the last payment received 100$
            - Dr( bank a/c ) Cr( clearing a/c )  
    - 5. the clearing a/c is balanced - the transaction is done
    '''
    
    LIABILITY_CLEARING_ACCOUNT = 972  # rozliczenie zobowiazania
    ''' "Liability Clearing Account" \n
    Usually used for tracking the approved invoices or bills from the contractor that are not yet paid.
    Example:
    - 1. new project just started, 
    - 2. the $100 bill received from the contractor
        - Dr( project a/c ) Cr( clearing a/c )
    - 3. the first payment, $150 was sent to the contractor
        - Dr( clearing a/c ) Cr( bank a/c )    
    - 4. the $200 invoice received from the contractor
        - Dr( project a/c ) Cr( clearing a/c )
    - 5. the $12 final bill received from the contractor
        - Dr( project a/c ) Cr( clearing a/c )
    - 6. the final payment, $162 was send to the contractor
        - Dr( clearing a/c ) Cr( bank a/c )
    - 7. the clearing a/c is balanced and the project should be ready
    '''
    
    PURCHASE_CLEARING_ACCOUNT = 970  # rozliczenie zakupu
    ''' "Purchase Clearing Account" (Goods Recipt/Invoice Recipt)
    - goods that are not yet invoiced have been received from the supplier
            - (increases Liability on Clearing Account)
    - invoice arrive before the the delivery of goods
            - (increases Asset on Clearing Account) \n
    Example:
      - goods received:
            - Dr( inventory a/c ) Cr( clearing a/c )
      - invoice received:
            - Dr( clearing a/c ) Cr( supplier a/c )
      - payment sent:
            - Dr( supplier a/c ) Cr( bank a/c ) '''
    
    SALES_CLEARING_ACCOUNT = 971  # rozliczenie sprzedazy
    ''' "Sales Clearing Account"
    - goods that are not yet invoiced have been shipped to the customer
            - (increases Asset on Clearing Account)
    - invoice send before the shippement
            - (increases Liability on Clearing Account) \n
    Example: \n
      - goods issued:
            - Dr( clearing a/c ) Cr( sales a/c ),
            - Dr( cogs a/c ) Cr( inventory a/c )
      - invoice issued:
            - Dr( customer a/c ) Cr( clearing a/c )
      - payment received: 
            - Dr( bank a/c ) Cr( customer a/c ) '''

    # RECEIVED_NOT_INVOICED = 975  # rozliczenie zakupu
    # ''' Purchase Clearings:\n
    # Goods/Services received but not invoiced by the Supplier''' 
    # INVOICED_NOT_RECEIVED = 976  # rozliczenie zakupu
    # ''' Purchase Clearings:\n
    # Goods/Services invoiced but not delivered by the Supplier'''  
    # INVOICED_NOT_ISSUED = 252  # rozliczenie sprzedazy
    # ''' Sell Clearings:\n
    # Goods/Services invoiced but not issued to the Customer''' 
    # ISSUED_NOT_INVOICED = 152  # rozliczenie sprzedazy
    # ''' Sell Clearings:\n
    # Goods/Services issued to the Customer but not invoiced '''

class Maintenance(Mark):
    """
    Special markers for accounts
    """
    POSTING_NOT_ALLOWED = 980
    CANCEL_POST_NOT_ALLOWED = 981
    UPDATE_ACCOUNT_NOT_ALLOWED = 982
    SUSPENSE_ACCOUNT = 999

if __name__ == "__main__":
    m = Marker(BalanceSheet.ASSETS, Assets.CASH)
    print(m.has_type(Assets, BalanceSheet))
