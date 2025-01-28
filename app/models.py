import pyodbc
from app.config import DATABASE_URL

# Create a connection to the SQL Server database
def get_connection():
    return pyodbc.connect(DATABASE_URL, autocommit=False)

class BOS_Counter:
    def __init__(self, szCounterId: str, iLastNumber: int):
        self.szCounterId = szCounterId
        self.iLastNumber = iLastNumber

class BOS_Balance:
    def __init__(self, szAccountId: str, szCurrencyId: str, decAmount: float):
        self.szAccountId = szAccountId
        self.szCurrencyId = szCurrencyId
        self.decAmount = decAmount

class BOS_History:
    def __init__(self, szTransactionId: str, szAccountId: str, szCurrencyId: str, dtmTransaction: str, decAmount: float, szNote: str):
        self.szTransactionId = szTransactionId
        self.szAccountId = szAccountId
        self.szCurrencyId = szCurrencyId
        self.dtmTransaction = dtmTransaction
        self.decAmount = decAmount
        self.szNote = szNote
