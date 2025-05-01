from copy import copy
from datetime import date, datetime
from decimal import Decimal
import locale
import operator
from yaerp.accounting.lib3 import AccountTypes, GeneralJournal, GeneralLedger
from yaerp.accounting.ledger3 import Ledger
from yaerp.accounting.journal3 import Journal
from yaerp.accounting.journal3 import JournalEntry
from yaerp.accounting.account3 import Account
from yaerp.accounting.account3 import AccountSide
from yaerp.accounting.account3 import AccountRecord
from yaerp.accounting.marker import Assets, BalanceSheet, Clearing, Equity, Expenses, IncomeStatement, Liabilities, Revenues
from yaerp.accounting.reports.t_account import T_account, render_journal_entries, render_journal_entries2, render_journal_entry, render_journal_entry2, render_layout
from yaerp.accounting.tree3 import AccountTree
from yaerp.model.money import Money
from yaerp.model.currency import Currency
from yaerp.report.typesetting.columns import simultaneous_column_generator as typeset
from yaerp.tools.sid import SID

class AccountingSystem:

    def __init__(self):
        self.general_ledger = None
        self.currencies = dict()
        self.accounts = dict()
        # self.charts_of_accounts = dict()
        self.coa = AccountTree(None, None)
        self.journals = dict()
        self.selected = dict()

    def add_currency(self, code: str, currency_id: str, subunits_in_one_unit: int, 
                     international_name: str, national_unit_symbol: str, national_subunit_symbol: str):
        new_currency = Currency(code, currency_id, subunits_in_one_unit, 
                           international_name, national_unit_symbol, national_subunit_symbol)
        if self.currencies.get(new_currency.symbol, None):
            raise ValueError("Currency already exist")
        self.currencies[code] = new_currency

    def get_currency(self, code: str) -> Currency:
        currency = self.currencies.get(code, None)
        if not currency:
            raise ValueError(f"Currency '{code}' not found")
        return currency

    def add_account(self, tag: str, ledger: str, currency_code, name = None):
        if self.accounts.get(tag, None):
            raise ValueError("Tag found in an existing account")
        currency = self.currencies.get(currency_code, None)
        if not currency:
            raise ValueError("Currency not found")
        new_account = Account(tag, self.general_ledger, currency, name)
        self.accounts[tag] = new_account

    def get_account(self, tag: str) -> Account:
        account = self.accounts.get(tag, None)
        if not account:
            raise ValueError(f"Account '{tag}' not found")
        return account

    def add_chart_of_accounts(self, name: str):
        coa = AccountTree(None, None)
        self.charts_of_accounts[name] = coa

    def get_chart_of_accounts(self, name: str) -> AccountTree:
        return self.charts_of_accounts[name]

    def del_chart_of_accounts(self, name: str):
        coa_to_del = self.get_chart_of_accounts(name)
        has_posts = False
        for _ in coa_to_del.internal_posts_iter():
            has_posts = True
            break
        if has_posts:
            raise ValueError(f"The Chart of Accounts '{name}' contains account entries. Delete is not possible.")
        del self.charts_of_accounts[name]

    def add_node(self, coa_name: str, account_tag: str, parent_account_tag: str = None):
        if parent_account_tag:
            parent_node = self.coa.get_node(account_tag=parent_account_tag)
        else:
            parent_node = self.coa
        ac = self.get_account(account_tag)
        AccountTree(ac, parent_node)

    def get_node(self, coa_name: str, account_tag: str = None, account_name: str = None, account_guid: str = None):
        # coa = self.get_chart_of_accounts(coa_name)
        return self.coa.get_node(account_tag, account_name, account_guid)

    def move_node(self, coa_name: str, account_tag: str, new_parent_account_tag: str = None):
        acn = self.get_node(None, account_tag)
        if new_parent_account_tag:
            new_parent_node = self.get_node(coa_name, account_tag=new_parent_account_tag)
            if not new_parent_node:
                raise ValueError(f'parent account {new_parent_account_tag} not found')
            if acn in new_parent_node.get_node_path():
                raise ValueError('attemt to move node in the same node path')
        else:
            new_parent_node = self.coa
        if acn.parent:
            acn.parent.children.remove(acn)
            acn.parent = new_parent_node
            # acn.parent.children.insert(acn)
            acn.parent.append_child(acn)
            # AccountTree(acn.account, parent=new_parent_node)
        else:
            raise ValueError(f"Attempt to move root node.")

    def delete_node(self, coa_name: str, account_tag: str):
        node_to_del = self.get_node(coa_name, tag=account_tag)
        has_posts = False
        for _ in node_to_del.internal_posts_iter():
            has_posts = True
            break
        if has_posts:
            raise ValueError('Cannot delete node containing account entries')
        if not node_to_del.parent:
            raise ValueError('Cannot delete root node. Use "delete chart-of-accounts" command to do so.')
        node_to_del.parent.children.remove(node_to_del)
        
    def add_journal(self, tag: str, fields_definition: dict):

        class NewJournal(Journal):
            def initialize_fields(self, journal_entry):
                return fields_definition.copy()
        
        journal = self.journals.get(tag, None)
        if journal:
            raise ValueError(f"Journal '{tag}' already exist")
        new_journal = NewJournal(tag, self.general_ledger)
        self.journals[tag] = new_journal

    def get_journal(self, tag: str) -> Journal:
        journal = self.journals.get(tag, None)
        if not journal:
            raise ValueError(f"Journal tag '{tag}' not found")
        return journal

    def delete_journal(self, tag: str):
        journal = self.get_journal(tag)
        if journal.journal_entries:
            raise ValueError(f"Journal '{tag}' is not empty. Delete is not possible.")
        del self.journals[tag]

    def new_journal_entry(self, journal_tag: str):
        journal = self.get_journal(journal_tag)
        return JournalEntry(journal)

    def add_journal_entry(self, new_journal_entry):
        journal = new_journal_entry.journal
        journal.journal_entries.insert_right(new_journal_entry)

    def get_journal_entry(self, journal_tag: str = None, *, sid: str = None, guid: str = None):
        if sid and guid:
            ValueError("Argument 'guid' is not allowed when 'sid' is present and vice-versa")
        if not sid and not guid:
            ValueError("At least one argument: 'sid' or 'guid' is required")
        if journal_tag:
            journal = self.get_journal(journal_tag)
            if sid:
                result = journal.get_by_sid(sid, not_rise_exception=True)
            if guid:
                result = journal.get_by_guid(guid, not_rise_exception=True)
        else:
            result = self.find_journal_entry(sid=sid, guid=guid)
        if result:
            return result
        raise ValueError(f'Journal entry not found ({journal_tag=}, {sid=}, {guid=})')

    def find_journal_entry(self, sid: str = None, guid: str = None):
        if sid:
            for journal in self.general_ledger.journals:
                result = journal.get_by_sid(sid, not_rise_exception=True)
                if result:
                    break
        elif guid:
            for journal in self.general_ledger.journals.values():
                result = journal.get_by_guid(guid, not_rise_exception=True)
                if result:
                    break
        return result
    
    def match_journal_entries_gen(self, date: str, desc: str, ref: str, journal_tag: str, sids: list, state: str, reading_order: str, limit: int = 1000):

        def match(je, date:str, desc:str, ref:str, sids):
            if sids:
                if str(je.sid) not in sids and SID.print_form(je.sid) not in sids:
                    return False
            if date and date not in je.date:
                return False
            if desc and desc not in je.description:
                return False
            if ref and ref not in je.reference:
                return False
            return True
            
        if state == 'ALL':
            posted = True
            unposted = True
        elif state == 'POSTED':
            posted = True
            unposted = False
        elif state == 'UNPOSTED':
            posted = False
            unposted = True
        else:
            raise ValueError()

        if reading_order == 'ASCENDING':
            reverse = False
        elif reading_order == 'DESCENDING':
            reverse = True
        else:
            raise ValueError()

        if date:
            pass # convert TODAY, YESTERDAY, TY, etc into date string

        counter = 0

        if journal_tag:
            journal = self.get_journal(journal_tag)
            for je in journal.entries_gen(posted=posted, unposted=unposted, reverse=reverse):
                if match(je, date, desc, ref, sids):
                    counter += 1
                    yield je
                    if counter == limit:
                        return
        else:
            for je in self.general_ledger.journal_entries_gen(posted=posted, unposted=unposted, reverse=reverse):
                if match(je, date, desc, ref, sids):
                    counter += 1
                    yield je
                    if counter == limit:
                        return

    def can_post_journal_entry(self, journal_entry):
        return journal_entry.can_post_journal_entry()

    def post_journal_entry(self, journal_entry):
        if journal_entry.can_post_this():
            journal_entry.post_this()
        else:
            raise ValueError('Posting error')
        
    def bulkpost_journal_entries(self, journal_tag: str, *, sids: list):
        journal = self.get_journal(journal_tag)
        journal_entries = []
        for je_sid in sids:
            je = journal.get_by_sid(je_sid)
            journal_entries.append(je)
        journal.post_these(journal_entries)

    def bulk_cancel_journal_entries(self, journal_tag: str, *, sids: list, method="STORNO") -> list:
        
        def cancel_account_record(account_record: AccountRecord, method: str):
            if method == "STORNO":
                # negate account amount
                return AccountRecord(
                                account=account_record.account,
                                raw_amount=-account_record.raw_amount,
                                side=account_record.side,
                                journal_entry=account_record.journal_entry,
                                post=None
                            )
            if method == "REVERSE":
                # reverse account side
                return AccountRecord(
                                account=account_record.account,
                                raw_amount=account_record.raw_amount,
                                side=account_record.side.opposite(),
                                journal_entry=account_record.journal_entry,
                                post=None
                            )
            raise ValueError()
            
        
        journal_entries = []
        for je_sid in sids:
            je = self.get_journal_entry(journal_tag, sid=je_sid)
            journal_entries.append(je)
            return []
        # check if entire list of j.entries can be processed
        if method == "REMOVE":
            wrong_state_entries = []
            for je_to_cancel in journal_entries:
                if je_to_cancel.post:
                    wrong_state_entries.append(SID.print_form(je_to_cancel.sid))
            if wrong_state_entries:
                raise ValueError(f'Cancel method "REMOVE" cannot be used for posted entry(-ies) {", ".join(wrong_state_entries)}')
        
        wrong_state_entries = []
        for je_to_cancel in journal_entries:
            if je_to_cancel.reference:
                if 'canceled' in je_to_cancel.reference.lower():
                    wrong_state_entries.append(SID.print_form(je_to_cancel.sid))
        if wrong_state_entries:
            raise ValueError(f'already canceled j/e {", ".join(wrong_state_entries)}')

        wrong_state_entries = []
        for je_to_cancel in journal_entries:
            if je_to_cancel.reference:
                if 'cancels' in je_to_cancel.reference.lower():
                    wrong_state_entries.append(SID.print_form(je_to_cancel.sid))
        if wrong_state_entries:
            # raise ValueError(f'j/e {", ".join(wrong_state_entries)} - "cancel entries" cannot be canceled')
            raise ValueError(f'j/e {", ".join(wrong_state_entries)} - cancellation of "storno/revese entry" is not allowed')

        result = []
        for je_to_cancel in journal_entries:
            if not je_to_cancel.post:
                je_to_cancel.journal.journal_entries.remove(je_to_cancel)
            else:
                cancel_entry = copy(je_to_cancel)
                old_je_ref = f'Canceled by j/e {SID.print_form(cancel_entry.sid)}'
                if je_to_cancel.reference:
                    old_je_ref += f' / {je_to_cancel.reference}'
                je_to_cancel.reference = old_je_ref
                cancel_entry.reference = f'Cancels j/e {SID.print_form(je_to_cancel.sid)}'
                cancel_entry.description = f'{method} entry -> {je_to_cancel.description}'
                for name, value in cancel_entry.fields.items():  
                    if isinstance(value, AccountRecord):
                        c = cancel_account_record(value, method)
                        cancel_entry.fields[name] = c
                    elif isinstance(value, list):
                        for index, record in enumerate(value):
                            c = cancel_account_record(record, method)
                            cancel_entry.fields[name][index] = c
                cancel_entry.post_this()
            result.append(cancel_entry.sid)

def setup_tiny_accounting_system() -> AccountingSystem:
    accsys = AccountingSystem()
    accsys.general_ledger = GeneralLedger()
    accsys.currencies = {
                "EUR": Currency('EUR', '978', 100, "Euro", '€', 'c'),
                "INR": Currency('INR', '356', 100, "Indian Rupee", '₹', 'p', separator_positions=(3,5,7,9,11,13,15,17), separator_predicate=None),
                "PLN": Currency('PLN', '985', 100, "Polish Złoty", 'zł', 'gr'),
                "USD": Currency('USD', '840', 100, "US Dollar", '$', 'c'),
    }
    accsys.accounts = {
            "1": Account('1', accsys.general_ledger, accsys.currencies["PLN"], "Assets"),
            "100": Account('100', accsys.general_ledger, accsys.currencies["PLN"], "Receivables"),
            "100-1": Account('100-1', accsys.general_ledger, accsys.currencies["PLN"], "Allegro (receivables)"),
            "110": Account('110', accsys.general_ledger, accsys.currencies["PLN"], "Cash"),
            "120": Account('120', accsys.general_ledger, accsys.currencies["PLN"], "Bank"),
            "130": Account('130', accsys.general_ledger, accsys.currencies["PLN"], "Stock"),
            "131": Account('131', accsys.general_ledger, accsys.currencies["PLN"], "Goods"),
            "132": Account('132', accsys.general_ledger, accsys.currencies["PLN"], "Materials"),
            "140": Account('140', accsys.general_ledger, accsys.currencies["PLN"], "Equipment"),
            "170": Account('170', accsys.general_ledger, accsys.currencies["PLN"], "Tax Receivables"),

            "2": Account('2', accsys.general_ledger, accsys.currencies["PLN"], "Liabilities"),
            "200": Account('200', accsys.general_ledger, accsys.currencies["PLN"], "Payables"),
            "200-1": Account('200-1', accsys.general_ledger, accsys.currencies["PLN"], "Allegro (payables)"),
            "270": Account('270', accsys.general_ledger, accsys.currencies["PLN"], "Tax Payables"),

            "3": Account('3', accsys.general_ledger, accsys.currencies["PLN"], "Equity"),
            "300": Account('300', accsys.general_ledger, accsys.currencies["PLN"], "Capital"),
            "310": Account('310', accsys.general_ledger, accsys.currencies["PLN"], "Retained earnings"),

            "4": Account('4', accsys.general_ledger, accsys.currencies["PLN"], "Revenues"),
            "400": Account('400', accsys.general_ledger, accsys.currencies["PLN"], "Sales"),
            "410": Account('410', accsys.general_ledger, accsys.currencies["PLN"], "Other Income"),

            "5": Account('5', accsys.general_ledger, accsys.currencies["PLN"], "Expenses"),
            "500": Account('500', accsys.general_ledger, accsys.currencies["PLN"], "Cost Of Goods Sold (COGS)"),
            "510": Account('510', accsys.general_ledger, accsys.currencies["PLN"], "Operating Expenses (OPEX)"),
            "511": Account('511', accsys.general_ledger, accsys.currencies["PLN"], "Packaging Cost"),
            "512": Account('512', accsys.general_ledger, accsys.currencies["PLN"], "External Services"),
            "513": Account('513', accsys.general_ledger, accsys.currencies["PLN"], "Office Supplies"),
            "514": Account('514', accsys.general_ledger, accsys.currencies["PLN"], "Utilities"),
        }

    class SaleJournal(Journal):

        def initialize_fields(self, journal_entry):
            return {
                'Cash': AccountRecord(accsys.accounts["110"], 0, AccountSide.Dr, journal_entry, None),
                'Sale': AccountRecord(accsys.accounts["400"], 0, AccountSide.Cr, journal_entry, None),
                'Tax': AccountRecord(accsys.accounts["270"], 0, AccountSide.Cr, journal_entry, None),
            }  
    sale_journal = SaleJournal("SJ", "Sale Journal", ledger=accsys.general_ledger)
    class PurchaseJournal(Journal):

        def initialize_fields(self, journal_entry):
            return {
                "Informaton": None,
                'Payables': AccountRecord(accsys.accounts["200"], 0, AccountSide.Dr, journal_entry, None),
                'Cash': AccountRecord(accsys.accounts["110"], 0, AccountSide.Cr, journal_entry, None),
            }
    purchase_journal = PurchaseJournal("PJ", "Purchase Journal", ledger=accsys.general_ledger)
    accsys.journals = {
            GeneralJournal().tag: GeneralJournal(),
            sale_journal.tag: sale_journal,
            purchase_journal.tag: purchase_journal,
        }
    root = AccountTree(None, None)
    assets = AccountTree(accsys.accounts["1"], root)
    receivables = AccountTree(accsys.accounts["100"], assets)
    AccountTree(accsys.accounts["100-1"], receivables)
    AccountTree(accsys.accounts["110"], assets)
    AccountTree(accsys.accounts["120"], assets)
    stock = AccountTree(accsys.accounts["130"], assets)
    AccountTree(accsys.accounts["131"], stock)
    AccountTree(accsys.accounts["132"], stock)
    AccountTree(accsys.accounts["140"], assets)
    AccountTree(accsys.accounts["170"], assets)

    liabilities = AccountTree(accsys.accounts["2"], root)
    payables = AccountTree(accsys.accounts["200"], liabilities)
    AccountTree(accsys.accounts["200-1"], payables)
    AccountTree(accsys.accounts["270"], liabilities)

    equity = AccountTree(accsys.accounts["3"], root)
    AccountTree(accsys.accounts["300"], equity)
    AccountTree(accsys.accounts["310"], equity)

    revenues = AccountTree(accsys.accounts["4"], root)
    AccountTree(accsys.accounts["400"], revenues)
    AccountTree(accsys.accounts["410"], revenues)

    expenses = AccountTree(accsys.accounts["5"], root)
    AccountTree(accsys.accounts["500"], expenses)
    opex = AccountTree(accsys.accounts["510"], expenses)
    AccountTree(accsys.accounts["511"], opex)
    AccountTree(accsys.accounts["512"], opex)
    AccountTree(accsys.accounts["513"], opex)
    AccountTree(accsys.accounts["514"], opex)
    accsys.coa = root # Chart of Accounts
    accsys.charts_of_accounts = {"main": root}
    accsys.selected = {
        "account": "110",
        "journal": "SJ",
        "currency": "PLN",
        "date": "today",
        "time": "now",
        "period": "2023-11",
        "chart-of-accounts": "main"
    }
    return accsys

def empty_accounting_system() -> AccountingSystem:
    accsys = AccountingSystem()
    accsys.general_ledger = GeneralLedger()
    accsys.currencies = {
                "EUR": Currency('EUR', '978', 100, "Euro", '€', 'c'),
                "PLN": Currency('PLN', '985', 100, "Polish Złoty", 'zł', 'gr'),
                "USD": Currency('USD', '840', 100, "US Dollar", '$', 'c'),
    }
    accsys.accounts = {
            # '100': Account('100', accsys.general_ledger, accsys.currencies["PLN"], "Receivables"),
    }

    # class SaleJournal(Journal):

    #     def initialize_fields(self, journal_entry):
    #         return {
    #             'Cash': AccountRecord(accsys.accounts["110"], 0, AccountSide.Dr, journal_entry, None),
    #             'Sale': AccountRecord(accsys.accounts["400"], 0, AccountSide.Cr, journal_entry, None),
    #             'Tax': AccountRecord(accsys.accounts["270"], 0, AccountSide.Cr, journal_entry, None),
    #         }  
    # sale_journal = SaleJournal("SJ", "Sale Journal", ledger=accsys.general_ledger)
    # class PurchaseJournal(Journal):

    #     def initialize_fields(self, journal_entry):
    #         return {
    #             "Informaton": None,
    #             'Payables': AccountRecord(accsys.accounts["200"], 0, AccountSide.Dr, journal_entry, None),
    #             'Cash': AccountRecord(accsys.accounts["110"], 0, AccountSide.Cr, journal_entry, None),
    #         }
    # purchase_journal = PurchaseJournal("PJ", "Purchase Journal", ledger=accsys.general_ledger)
    accsys.journals = {
            GeneralJournal().tag: GeneralJournal(),
            # sale_journal.tag: sale_journal,
            # purchase_journal.tag: purchase_journal,
        }
    # root = AccountTree(None, None)
    # assets = AccountTree(accsys.accounts["1"], root)
    # receivables = AccountTree(accsys.accounts["100"], assets)
    # AccountTree(accsys.accounts["100-1"], receivables)
    # AccountTree(accsys.accounts["110"], assets)
    # AccountTree(accsys.accounts["120"], assets)
    # stock = AccountTree(accsys.accounts["130"], assets)
    # AccountTree(accsys.accounts["131"], stock)
    # AccountTree(accsys.accounts["132"], stock)
    # AccountTree(accsys.accounts["140"], assets)
    # AccountTree(accsys.accounts["170"], assets)

    # liabilities = AccountTree(accsys.accounts["2"], root)
    # payables = AccountTree(accsys.accounts["200"], liabilities)
    # AccountTree(accsys.accounts["200-1"], payables)
    # AccountTree(accsys.accounts["270"], liabilities)

    # equity = AccountTree(accsys.accounts["3"], root)
    # AccountTree(accsys.accounts["300"], equity)
    # AccountTree(accsys.accounts["310"], equity)

    # revenues = AccountTree(accsys.accounts["4"], root)
    # AccountTree(accsys.accounts["400"], revenues)
    # AccountTree(accsys.accounts["410"], revenues)

    # expenses = AccountTree(accsys.accounts["5"], root)
    # AccountTree(accsys.accounts["500"], expenses)
    # opex = AccountTree(accsys.accounts["510"], expenses)
    # AccountTree(accsys.accounts["511"], opex)
    # AccountTree(accsys.accounts["512"], opex)
    # AccountTree(accsys.accounts["513"], opex)
    # AccountTree(accsys.accounts["514"], opex)
    # accsys.coa = root # Chart of Accounts
    # accsys.charts_of_accounts = {"main": root}
    # accsys.selected = {
    #     "account": "110",
    #     "journal": "SJ",
    #     "currency": "PLN",
    #     "date": "today",
    #     "time": "now",
    #     "period": "2023-11",
    #     "chart-of-accounts": "main"
    # }
    return accsys
