import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection details from environment variables
SQL_SERVER = os.getenv('SQL_SERVER')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_DRIVER = os.getenv('SQL_DRIVER')

# Establish the connection using pyodbc
connection = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SQL_SERVER};'
    f'DATABASE={SQL_DATABASE};'
    f'UID={SQL_USER};'
    f'PWD={SQL_PASSWORD}'
)

cursor = connection.cursor()

# Create BOS_Counter table
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BOS_Counter' AND xtype='U')
    CREATE TABLE BOS_Counter
    (
        szCounterId NVARCHAR(50) NOT NULL,
        iLastNumber BIGINT NOT NULL,
        CONSTRAINT PK_BOS_Counter PRIMARY KEY CLUSTERED
        (
            szCounterId ASC
        )
    )
''')

# Create BOS_Balance table
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BOS_Balance' AND xtype='U')
    CREATE TABLE BOS_Balance
    (
        szAccountId NVARCHAR(50) NOT NULL,
        szCurrencyId NVARCHAR(50) NOT NULL,
        decAmount DECIMAL (30, 8) NOT NULL,
        CONSTRAINT PK_BOS_Balance PRIMARY KEY CLUSTERED
        (
            szAccountId ASC, szCurrencyId ASC
        )
    )
''')

# Create BOS_History table
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BOS_History' AND xtype='U')
    CREATE TABLE BOS_History
    (
        szTransactionId NVARCHAR(50) NOT NULL,
        szAccountId NVARCHAR(50) NOT NULL,
        szCurrencyId NVARCHAR(50) NOT NULL,
        dtmTransaction DATETIME NOT NULL,
        decAmount DECIMAL (30, 8) NOT NULL,
        szNote NVARCHAR(255) NOT NULL,
        CONSTRAINT PK_BOS_History PRIMARY KEY CLUSTERED
        (
            szTransactionId ASC, szAccountId ASC, szCurrencyId ASC
        )
    )
''')

# Insert data into BOS_Counter table
cursor.execute("INSERT INTO BOS_Counter VALUES ('001-COU', 4)")

# Insert data into BOS_Balance table
cursor.execute("INSERT INTO BOS_Balance VALUES ('000108757484', 'IDR', 34500000.00)")
cursor.execute("INSERT INTO BOS_Balance VALUES ('000108757484', 'USD', 125.8750)")
cursor.execute("INSERT INTO BOS_Balance VALUES ('000109999999', 'IDR', 1250.00)")
cursor.execute("INSERT INTO BOS_Balance VALUES ('000109999999', 'SGD', 2.25)")
cursor.execute("INSERT INTO BOS_Balance VALUES ('000108888888', 'SGD', 125.75)")

# Insert data into BOS_History table
cursor.execute("INSERT INTO BOS_History VALUES ('20201231-00000.00001', '000108757484', 'IDR', GETDATE(), 34500000.00, 'SETOR')")
cursor.execute("INSERT INTO BOS_History VALUES ('20201231-00000.00001', '000108757484', 'SGD', GETDATE(), 125.8750, 'SETOR')")
cursor.execute("INSERT INTO BOS_History VALUES ('20201231-00000.00002', '000109999999', 'IDR', GETDATE(), 1250.00, 'SETOR')")
cursor.execute("INSERT INTO BOS_History VALUES ('20201231-00000.00003', '000109999999', 'SGD', GETDATE(), 128.00, 'SETOR')")
cursor.execute("INSERT INTO BOS_History VALUES ('20201231-00000.00004', '000109999999', 'SGD', GETDATE(), -125.75, 'TRANSFER')")
cursor.execute("INSERT INTO BOS_History VALUES ('20201231-00000.00004', '000108888888', 'SGD', GETDATE(), 125.75, 'TRANSFER')")

connection.commit()
print("Database seeded successfully!")

cursor.close()
connection.close()
