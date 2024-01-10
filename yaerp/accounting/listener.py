class AccountingBaseListener:

    # JOURNAL ENTRY (JE)

    def beginJournalEntry_create(self, ctx):
        pass

    def endJournalEntry_create(self, ctx):
        pass

    def beginJournalEntry_change(self, ctx):
        pass

    def endJournalEntry_change(self, ctx):
        pass

    def beginJournalEntry_change_field(self, ctx):
        pass

    def endJournalEntry_change_field(self, ctx):
        pass

    def beginJournalEntry_put_to_journal(self, ctx):
        pass

    def endJournalEntry_put_to_journal(self, ctx):
        pass

    def beginJournalEntry_del_from_journal(self, ctx):
        pass

    def endJournalEntry_del_from_journal(self, ctx):
        pass

    def beginJournalEntry_post(self, ctx):
        pass

    def endJournalEntry_post(self, ctx):
        pass

    def beginJournalEntry_cancel(self, ctx):
        pass

    def endJournalEntry_cancel(self, ctx):
        pass

    # ACCOUNT (ac)

    def beginAccount_create(self, ctx):
        pass

    def endAccount_create(self, ctx):
        pass

    def beginAccount_update(self, ctx):
        pass

    def endAccount_update(self, ctx):
        pass

    def beginAccount_read(self, ctx):
        pass

    def endAccount_read(self, ctx):
        pass

    # JOURNAL (j)

    def beginJournal_create(self, ctx):
        pass

    def endJournal_create(self, ctx):
        pass

    def beginJournal_update(self, ctx):
        pass

    def endJournal_update(self, ctx):
        pass

    def beginJournal_read(self, ctx):
        pass

    def endJournal_read(self, ctx):
        pass

    # GENERAL LEDGER (gl)

    def beginGeneralLedger_account_record_insert(self, ctx):
        pass

    def endGeneralLedger_account_record_insert(self, ctx):
        pass

    def beginGeneralLedger_account_record_remove(self, ctx):
        pass

    def endGeneralLedger_account_record_remove(self, ctx):
        pass

    def beginGeneralLedger_account_record_post(self, ctx):
        pass

    def endGeneralLedger_account_record_post(self, ctx):
        pass

    def beginGeneralLedger_register_account(self, ctx):
        pass

    def endGeneralLedger_register_account(self, ctx):
        pass

    def beginGeneralLedger_register_journal(self, ctx):
        pass

    def endGeneralLedger_register_journal(self, ctx):
        pass

    def beginGeneralLedger_register_post(self, ctx):
        pass

    def endGeneralLedger_register_post(self, ctx):
        pass

    # LEDGER (l)

    def beginLedger_account_record_insert(self, ctx):
        pass

    def endLedger_account_record_insert(self, ctx):
        pass

    def beginLedger_account_record_remove(self, ctx):
        pass

    def endLedger_account_record_remove(self, ctx):
        pass

    def beginLedger_account_record_change(self, ctx):
        pass

    def endLedger_account_record_change(self, ctx):
        pass

    def beginLedger_register_account(self, ctx):
        pass

    def endLedger_register_account(self, ctx):
        pass

    def beginLedger_register_journal(self, ctx):
        pass

    def endLedger_register_journal(self, ctx):
        pass

    def beginLedger_register_post(self, ctx):
        pass

    def endLedger_register_post(self, ctx):
        pass

    # ACCOUNT TREE (at)

    def beginAccountTree_create(self, ctx):
        pass

    def endAccountTree_create(self, ctx):
        pass

    def beginAccountTree_append_child(self, ctx):
        pass

    def endAccountTree_append_child(self, ctx):
        pass

    def beginAccountTree_add_marks(self, ctx):
        pass

    def endAccountTree_add_marks(self, ctx):
        pass