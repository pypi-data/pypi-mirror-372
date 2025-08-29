from decimal import Decimal

class JournalHelper:
    @staticmethod
    def normalize_account_name(account_name):
        if account_name is None or (isinstance(account_name, str) and not account_name.strip()):
            raise ValueError("Account name cannot be None or empty")
        if not isinstance(account_name, str):
            raise TypeError(f"Account name must be a string, got {type(account_name)}")
        return account_name.lower().replace(" ", "")

    @staticmethod
    def get_journal_amount(amount, entry_type):
        if (entry_type == "debit" and amount >= 0) or (entry_type == "credit" and amount < 0):
            return amount
        elif (entry_type == "credit" and amount >= 0) or (entry_type == "debit" and amount < 0):
            return -amount
        else:
            raise ValueError("Invalid type")

    @staticmethod
    def create_journal_item_collection(journal_items):
        return [item for item in journal_items if any(
            value != Decimal(0) for key, value in item.to_dict().items() 
            if key in ('debit', 'credit')
        )] 