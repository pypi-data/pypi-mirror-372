class NetsuiteJournalItem:
    def __init__(
        self,
        account_id,
        amount,
        department,
        class_id,
        location,
        memo,
        entity=None,
        custcol=None,
        netsuite_helper=None
    ):
        self.account_id = account_id
        self.amount = abs(float(amount))
        self.department = department
        self.class_id = class_id
        self.location = location
        self.memo = memo
        self.is_debit = float(amount) >= 0
        self.custcol4 = 2 if "CGST" in memo or "SGST" in memo or "IGST" in memo else 1
        self.custcol_porter_direct_indirect_tax = 3 if "TDS" in memo else 1
        self.custcol_in_hsn_code = netsuite_helper.get_hsn_code(memo) if netsuite_helper else None
        self.custcol3 = custcol
        self.entity = entity
        if "TDS 1" in memo:
            self.custcol_in_scode_tds = 264
        elif "TDS 2" in memo:
            self.custcol_in_scode_tds = 68
        else:
            self.custcol_in_scode_tds = None

    def to_dict(self):
        entry_type = "debit" if self.is_debit else "credit"
        result = {
            "account": {"id": str(self.account_id)},
            entry_type: self.amount,
            "department": self.department,
            "class": self.class_id,
            "location": self.location,
            "memo": self.memo,
            "custcol4": self.custcol4,
            "custcol_porter_direct_indirect_tax": self.custcol_porter_direct_indirect_tax,
            "custcol_in_scode_tds": self.custcol_in_scode_tds,
            "custcol_in_hsn_code": self.custcol_in_hsn_code,
        }

        if self.entity is not None:
            result["entity"] = {"id": self.entity}
        
        if self.custcol3 is not None:
            result["custcol3"] = self.custcol3

        return result
