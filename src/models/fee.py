from utils.utils import parse_numeric


class Fee:
    def __init__(self, row):
        self.currency = row.iloc[3]
        self.settle_date = row.iloc[4]
        self.description = row.iloc[5]
        self.amount = float(row.iloc[6])

# Fees,Header,Subtitle,Currency,Date,Description,Amount,,,,,,,,,,
# Fees,Data,Other Fees,USD,2024-12-03,E*******R3:CBOE ONE ADD-ON FOR NOV 2024,1,,,,,,,,,,
