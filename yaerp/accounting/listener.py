class Listener:

    # ACCOUNT

    def account_create_beg(self, ctx):
        pass

    def account_create_end(self, ctx):
        pass

    def account_update_beg(self, ctx):
        pass

    def account_update_end(self, ctx):
        pass

    def account_delete_beg(self, ctx):
        pass

    def account_delete_end(self, ctx):
        pass

    # ACCOUNT TREE (Chart of Accounts)

    def atree_create_beg(self, ctx):
        pass

    def atree_create_end(self, ctx):
        pass

    def atree_add_beg(self, ctx):
        pass

    def atree_add_end(self, ctx):
        pass

    def atree_update_beg(self, ctx):
        pass

    def atree_update_end(self, ctx):
        pass

    def atree_delete_beg(self, ctx):
        pass

    def atree_delete_end(self, ctx):
        pass

    # JOURNAL

    def journal_create_beg(self, ctx):
        pass

    def journal_create_end(self, ctx):
        pass

    def journal_update_beg(self, ctx):
        pass

    def journal_update_end(self, ctx):
        pass

    def journal_delete_beg(self, ctx):
        pass

    def journal_delete_end(self, ctx):
        pass

    def journal_bulk_post_beg(self, ctx):
        pass

    def journal_bulk_post_end(self, ctx):
        pass
    # JOURNAL ENTRY

    def jentry_create_beg(self, ctx):
        pass

    def jentry_create_end(self, ctx):
        pass

    def jentry_add_date_field_beg(self, ctx):
        pass

    def jentry_add_date_field_end(self, ctx):
        pass

    def jentry_add_desc_field_beg(self, ctx):
        pass

    def jentry_add_desc_field_end(self, ctx):
        pass

    def jentry_add_ref_field_end(self, ctx):
        pass

    def jentry_add_ref_field_beg(self, ctx):
        pass

    def jentry_add_ref_field_end(self, ctx):
        pass

    def jentry_add_info_field_beg(self, ctx):         # filling Info field 
        pass

    def jentry_add_info_field_end(self, ctx):
        pass

    def jentry_add_record_field_beg(self, ctx):      # filling Debit or Credit field
        pass

    def jentry_add_record_field_end(self, ctx):
        pass

    def jentry_put_beg(self, ctx):              # storing entry into the journal
        pass

    def jentry_put_end(self, ctx):
        pass

    def jentry_del_beg(self, ctx):
        pass

    def jentry_del_end(self, ctx):
        pass

    def jentry_single_post_beg(self, ctx):
        pass

    def jentry_single_post_end(self, ctx):
        pass

    def jentry_copy_beg(self, ctx):
        pass

    def jentry_copy_end(self, ctx):
        pass


    # LEDGER

    def ledger_create_beg(self, ctx):
        pass

    def ledger_create_end(self, ctx):
        pass

    def ledger_register_account_beg(self, ctx):
        pass

    def ledger_register_account_end(self, ctx):
        pass

    def ledger_unregister_account_beg(self, ctx):
        pass

    def ledger_unregister_account_end(self, ctx):
        pass

    def ledger_register_journal_beg(self, ctx):
        pass

    def ledger_register_journal_end(self, ctx):
        pass

    def ledger_unregister_journal_beg(self, ctx):
        pass

    def ledger_unregister_journal_end(self, ctx):
        pass

    def ledger_post_jentry_beg(self, ctx):
        pass

    def ledger_post_jentry_end(self, ctx):
        pass
