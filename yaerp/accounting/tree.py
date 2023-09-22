from functools import reduce
from itertools import chain

from yaerp.accounting.account import Account


class AccountTree():

    def __init__(self, account, parent=None):
        # check arguments
        if account is not None:
            assert isinstance(account, Account)
        if parent is not None:
            assert isinstance(parent, AccountTree)
        if account is not None and parent is not None:
            if parent.get_root_node().get_node(tag=account.tag, guid=account.guid) is not None:
                raise ValueError('Error. Account {} already exist in parent tree. '.format(account))
        # make this instance as parent's child
        if parent is not None:
            parent.append_child(self)
            # if parent.children is None:
            #     parent.children = list()
            # parent.children.append(self)
        self.account = account
        self.parent = parent
        self.children = None

    def append_child(self, child):
        if self.children is None:
            self.children = list()
        self.children.append(child)

    def get_node(self, tag=None, name=None, guid=None):
        if self.account is not None:
            if self.account.tag == tag or self.account.name == name or self.account.guid == guid:
                return self
        if self.children is not None:
            for child in self.children:
                result = child.get_node(tag, name, guid)
                if result is not None:
                    return result
        return None

    def get_account(self, tag=None, name=None, guid=None):
        node = self.get_node(tag, name, guid)
        if node:
            return node.account
        raise RuntimeError('Account \'[tag={}] name={} (guid={})\' not found'.format(tag, name, guid))

    def find(self,  select_ledger_nodes=True, select_analytic_nodes=True, select_ledger_leafs=True, select_analytic_leafs=True):
        def match(node, select_ledger_nodes=True, select_analytic_nodes=True, select_ledger_leafs=True, select_analytic_leafs=True):
            result_ledger_nodes, result_ledger_leafs, result_analytic_nodes, result_analytic_leafs = True, True, True, True
            if not select_ledger_nodes:
                result_ledger_nodes = not node.has_ledger_node()
            if not select_analytic_nodes:
                result_analytic_nodes = not node.has_analytical_node()
            if not select_ledger_leafs:
                result_ledger_leafs = not node.has_ledger_leaf()
            if not select_analytic_leafs:
                result_analytic_leafs = not node.has_analytical_leaf()
            result = all([result_ledger_nodes, result_ledger_leafs, result_analytic_nodes, result_analytic_leafs])
            return result
        if self.account is not None:
            if match(self, select_ledger_nodes, select_analytic_nodes, select_ledger_leafs, select_analytic_leafs):
                yield self
        yield from filter(
            lambda node: match(node, select_ledger_nodes, select_analytic_nodes, select_ledger_leafs, select_analytic_leafs),
            self.get_internals_gen())

    def find_node_gen(self, tag_pattern=None, name_pattern=None, expected_marks_tuple=None, select_used=True, select_not_used=True,
                      select_ledger_nodes=True, select_analytic_nodes=True, select_ledger_leafs=True, select_analytic_leafs=True,
                      select_nodes=True, select_leafs=True,
                      currency=None):
        def match(node, tag_pattern=None, name_pattern=None, expected_marks=None, select_used=True, select_not_used=True,
                  select_ledger_nodes=True, select_analytic_nodes=True, select_ledger_leafs=True, select_analytic_leafs=True,
                  select_nodes=True, select_leafs=True,
                  currency=None):
            result_tag, result_name, result_marks, \
            result_used, result_not_used, \
            result_ledger_nodes, result_analytic_nodes, result_ledger_leafs, result_analytic_leafs, \
            result_nodes, result_leafs, \
            result_currency = \
                (True, True, True, True, True, True, True, True, True, True, True, True)
            account = node.account
            if tag_pattern:
                result_tag = tag_pattern.lower() in account.tag.lower()
            if name_pattern:
                result_name = name_pattern.lower() in account.name.lower()
            if expected_marks and account.marker.marks:
                result_marks = account.marker.has_all(*expected_marks)
            elif expected_marks and not account.marks:
                result_marks = False

            if not select_ledger_nodes:
                result_ledger_nodes = not node.has_ledger_node()
            if not select_analytic_nodes:
                result_analytic_nodes = not node.has_analytical_node()
            if not select_ledger_leafs:
                result_ledger_leafs = not node.has_ledger_leaf()
            if not select_analytic_leafs:
                result_analytic_leafs = not node.has_analytical_leaf()

            if select_used and select_not_used:
                pass
            elif not select_used and not select_not_used:
                result_used = False
                result_not_used = False
            else:
                if select_used:
                    result_used = len(account.posts) > 0
                if select_not_used:
                    result_not_used = len(account.posts) == 0

            if select_nodes and select_leafs:
                pass
            elif not select_nodes and not select_leafs:
                result_nodes = False
                result_leafs = False
            else:
                if select_nodes:
                    result_nodes = node.has_nodes()
                if select_leafs:
                    result_leafs = not node.has_nodes()

            if currency:
                result_currency = (account.currency == currency)
            result = result_tag and result_name and result_marks \
               and result_used and result_not_used \
               and result_ledger_nodes and result_analytic_nodes and result_ledger_leafs and result_analytic_leafs \
               and result_nodes and result_leafs and result_currency
            return result

        if self.account is not None:
            if match(self, tag_pattern, name_pattern, expected_marks_tuple, select_used, select_not_used,
                     select_ledger_nodes, select_analytic_nodes, select_ledger_leafs, select_analytic_leafs,
                     select_nodes, select_leafs,
                     currency):
                yield self
        yield from filter(
            lambda node: match(node, tag_pattern, name_pattern, expected_marks_tuple, select_used, select_not_used,
                               select_ledger_nodes, select_analytic_nodes, select_ledger_leafs, select_analytic_leafs,
                               select_nodes, select_leafs,
                               currency),
            self.get_internals_gen())

    def get_internals_gen(self):
        if self.children is not None:
            for child in self.children:
                yield child
                yield from child.get_internals_gen()

    def has_nodes(self):
        return self.children is not None and len(self.children) > 0

    def get_currencies(self):
        result = set()
        for node in self.get_internals_gen():
            result.add(node.account.currency)
        return result

    def internal_posts_iter(self):
        if self.has_nodes():
            posts = chain(self.account.posts)
            for internal in self.get_internals_gen():
                posts = chain(posts, internal.account.posts)
        else:
            posts = iter(self.account.posts)
        return posts

    def has_analytical_leaf(self):
        return self.account.analytical and not self.has_analytical_node()

    def has_ledger_leaf(self):
        return not self.account.analytical and not self.has_ledger_node()

    def has_analytical_node(self):
        if not self.account.analytical:
            return False
        if self.children is None or len(self.children) == 0:
            return False
        return reduce(lambda t, s: bool(t or s.has_analytical_leaf()), self.children, False)

    def has_ledger_node(self):
        if self.children is None or len(self.children) == 0:
            return False
        return reduce(lambda t, s: bool(t or s.has_ledger_leaf()), self.children, False)

    def is_group_of_ledger_accounts_node(self):
        # has any ledger accounts or group accounts as children
        if self.is_analytical_account_node():
            return False
        if self.children is None:
            return False
        return reduce(
            lambda prev, curr: prev and (curr.is_ledger_account_node() or curr.is_group_of_ledger_accounts_node()),
            self.children)

    def is_group_of_analytical_accounts_node(self):
        # has any analytical accounts or group accounts as children
        if self.children is None or len(self.children) == 0:
            return False
        return reduce(
            lambda prev, curr: prev and (curr.is_analytical_account_node() or curr.is_group_of_analytical_accounts_node()),
            self.children)

    def is_ledger_account_node(self):
        # all children (if they are exist) are analytical accounts
        if self.is_analytical_account_node():
            return False
        if self.children is None or len(self.children) == 0:
            return True
        return reduce(
            lambda prev, curr: prev and (curr.is_analytical_account_node() or curr.is_group_of_analytical_accounts_node()),
            self.children)

    def is_analytical_account_node(self):
        if self.account is None:
            return False
        # return self.account.marker.has(Marks.ANALYTICAL_ACCOUNT)
        return self.account.analytical

    def get_ledger_account_node(self):
        analytical = self.is_analytical_account_node()
        if analytical and self.parent is not None:
            return self.parent.get_ledger_account_node()
        elif analytical and self.parent is None:
            return None
        else:
            return self

    def get_root_node(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_root_node()

    def get_debit_sum(self, post_predicate=None):
        result = 0
        if self.account:
            result += self.account.get_debit(post_predicate)
        if self.children:
            for node in self.children:
                # if self.account and self.account.currency != node.account.currency and any(filter(predicate, node.account.posts)):
                #    raise ValueError('Adding different currency values is not allowed')
                result += node.get_debit_sum(post_predicate)
        return result

    def get_credit_sum(self, post_predicate=None):
        result = 0
        if self.account:
            result += self.account.get_credit(post_predicate)
        if self.children:
            for node in self.children:
                # if self.account and self.account.currency != node.account.currency and any(filter(predicate, node.account.posts)):
                #     raise ValueError('Adding different currency values is not allowed')
                result += node.get_credit_sum(post_predicate)
        return result

    def get_balance_sum(self, post_predicate=None):
        result = 0
        if self.account:
            result += self.account.get_balance(post_predicate)
        if self.children:
            for node in self.children:
                # if self.account and self.account.currency != node.account.currency and any(filter(predicate, node.account.posts)):
                #     raise ValueError('Adding different currency values is not allowed')
                result += node.get_balance_sum(post_predicate)
        return result

    def __str__(self):
        result = ''
        if self.account:
            result = '[{}] {}'.format(self.account.tag, self.account.name)
        else:
            result = 'root'
            return result
        if self.account.currency:
            result += ' (' + self.account.currency + ')'
        if self.is_group_of_ledger_accounts_node():
            result += ' (group account)'
        if self.is_ledger_account_node():
            result += ' (ledger account)'
        if self.is_analytical_account_node():
            result += ' (analytical account)'
        if (self.account and len(self.account.posts) > 0) or any(
                n for n in self.get_internals_gen() if len(n.account.posts) > 0):
            dr = self.account.get_debit()
            cr = self.account.get_credit()
            bl = self.account.get_balance()
            digits_count = max(len(str(dr)), len(str(cr)))
            formatter = '[{{:_^ {0}d}}|{{:_^ {0}d}}]  {{:+d}}'.format(digits_count + 4)
            report = formatter.format(dr, cr, bl)
            result += ',  {}'.format(report)
        return result

    def __repr__(self):
        return self.__str__()
