from fastapi import APIRouter, HTTPException, Body
from datetime import datetime
from app.models import get_connection, BOS_Balance, BOS_Counter, BOS_History
from time import sleep

router = APIRouter()
MAX_RERTY = 4
DELAY = 3

@router.get("/bank/histories")
def get_bank_history(account_id: int, start_date: str, end_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL SNAPSHOT")
    cursor.execute("COMMIT TRANSACTION")
    cursor.execute("BEGIN TRANSACTION")
    cursor.execute("""
        SELECT * FROM BOS_History 
        WHERE szAccountId = ? AND dtmTransaction BETWEEN ? AND ?
    """, (account_id, start_date, end_date))
    rows = cursor.fetchall()
    cursor.execute("COMMIT TRANSACTION")
    conn.close()
    if rows:
        return [dict(transaction_id=row[0], account_id=row[1], currency=row[2], transaction_date=row[3], amount=row[4], note=row[5]) for row in rows]
    else:
        raise HTTPException(status_code=404, detail="No history found for the given account and date range")

@router.put("/bank/deposits")
def deposit_amount(request_body: dict = Body(
        ...,
        example={
            "account_id": "0001010234134",
            "currency_id": "IDR",
            "amount": 1000000
        }
    )):
    account_id = request_body.get("account_id")
    currency_id = request_body.get("currency_id")
    amount = request_body.get("amount")

    NOTE_TYPE = 'SETOR'
    COUNTER_ID = '001-COU'

    conn = get_connection()
    for attempt in range(MAX_RERTY):
        try:
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SNAPSHOT")
            cursor.execute("COMMIT TRANSACTION")
            cursor.execute("BEGIN TRANSACTION")
            
            transaction_id = update_counter_and_get_transaction_id(cursor, COUNTER_ID)
            
            # Insert or update the BOS_Balance table
            cursor.execute("""
                IF EXISTS (SELECT * FROM BOS_Balance WHERE szAccountId = ? AND szCurrencyId = ?)
                BEGIN
                    UPDATE BOS_Balance SET decAmount = decAmount + ? WHERE szAccountId = ? AND szCurrencyId = ?
                END
                ELSE
                BEGIN
                    INSERT INTO BOS_Balance (szAccountId, szCurrencyId, decAmount) VALUES (?, ?, ?)
                END
            """, (account_id, currency_id, amount, account_id, currency_id, account_id, currency_id, amount))
            
            insert_history(cursor, transaction_id, account_id, currency_id, amount, NOTE_TYPE)
            
            # Commit the transaction
            cursor.execute("COMMIT TRANSACTION")
            conn.commit()

            return {
                "transaction_id": transaction_id,
                "account_id": account_id,
                "currency_id": currency_id,
                "amount": amount,
                "message": "Deposit successful"
            }
        except Exception as e:
            conn.rollback()
            if isinstance(e, ValueError):
                raise HTTPException(status_code=400, detail=str(e))
            if handle_transaction_exception(e, attempt):
                continue
    
    conn.close()

@router.put("/bank/withdrawals")
def withdraw_balance(request_body: dict = Body(
        ...,
        example={
            "account_id": "0001010234134",
            "currency_id": "IDR",
            "amount": 1000000
        }
    )):
    account_id = request_body.get("account_id")
    currency_id = request_body.get("currency_id")
    amount = request_body.get("amount")

    NOTE_TYPE = 'TARIK'
    COUNTER_ID = '001-COU'

    conn = get_connection()
    for attempt in range(MAX_RERTY):
        try:
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SNAPSHOT")
            cursor.execute("COMMIT TRANSACTION")
            cursor.execute("BEGIN TRANSACTION")

            transaction_id = update_counter_and_get_transaction_id(cursor, COUNTER_ID)
            
            check_balance(cursor, account_id, currency_id, amount)
            
            # Update the BOS_Balance table if the balance is enough
            cursor.execute("UPDATE BOS_Balance SET decAmount = decAmount - ? WHERE szAccountId = ? AND szCurrencyId = ?", (amount, account_id, currency_id))
            
            insert_history(cursor, transaction_id, account_id, currency_id, -amount, NOTE_TYPE)
            
            # Commit the transaction
            cursor.execute("COMMIT TRANSACTION")
            conn.commit()

            return {
                "transaction_id": transaction_id,
                "account_id": account_id,
                "currency_id": currency_id,
                "amount": amount,
                "message": "Withdraw successful"
            }
        except Exception as e:
            conn.rollback()
            if isinstance(e, ValueError):
                raise HTTPException(status_code=400, detail=str(e))
            if handle_transaction_exception(e, attempt):
                continue
    
    conn.close()

@router.put("/bank/transfers")
def transfer_amount(request_body: dict = Body(
        ...,
        example={
            "from_account_id": "0001010234134",
            "currency_id": "IDR",
            "to_accounts": [
                {
                    "account_id": "000108888888",
                    "amount": 10000
                },
                {
                    "account_id": "000108888889",
                    "amount": 10000
                }
            ]
        }
    )):
    from_account_id = request_body.get("from_account_id")
    to_accounts = request_body.get("to_accounts")  # Expecting a list of dictionaries with 'account_id' and 'amount'
    currency_id = request_body.get("currency_id")

    NOTE_TYPE = 'TRANSFER'
    COUNTER_ID = '001-COU'

    conn = get_connection()
    for attempt in range(MAX_RERTY):
        try:
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SNAPSHOT")
            cursor.execute("COMMIT TRANSACTION")
            cursor.execute("BEGIN TRANSACTION")

            transaction_id = update_counter_and_get_transaction_id(cursor, COUNTER_ID)

            # Calculate total amount to be transferred
            total_amount = sum(item['amount'] for item in to_accounts)
            check_balance(cursor, from_account_id, currency_id, total_amount)

            # Update the BOS_Balance table for the from_account
            cursor.execute("UPDATE BOS_Balance SET decAmount = decAmount - ? WHERE szAccountId = ? AND szCurrencyId = ?", (total_amount, from_account_id, currency_id))

            # Process each destination account
            for to_account in to_accounts:
                to_account_id = to_account['account_id']
                amount = to_account['amount']

                # Insert or update the BOS_Balance table for each to_account
                cursor.execute("""
                    IF EXISTS (SELECT * FROM BOS_Balance WHERE szAccountId = ? AND szCurrencyId = ?)
                    BEGIN
                        UPDATE BOS_Balance SET decAmount = decAmount + ? WHERE szAccountId = ? AND szCurrencyId = ?
                    END
                    ELSE
                    BEGIN
                        INSERT INTO BOS_Balance (szAccountId, szCurrencyId, decAmount) VALUES (?, ?, ?)
                    END
                """, (to_account_id, currency_id, amount, to_account_id, currency_id, to_account_id, currency_id, amount))

                insert_history(cursor, transaction_id, to_account_id, currency_id, amount, NOTE_TYPE) # history for receiver accounts

            insert_history(cursor, transaction_id, from_account_id, currency_id, -total_amount, NOTE_TYPE) # history for the sender

            # Commit the transaction
            cursor.execute("COMMIT TRANSACTION")
            conn.commit()

            return {
                "transaction_id": transaction_id,
                "from_account_id": from_account_id,
                "to_accounts": to_accounts,
                "currency_id": currency_id,
                "message": "Transfer successful"
            }
        except Exception as e:
            conn.rollback()
            if isinstance(e, ValueError):
                raise HTTPException(status_code=400, detail=str(e))
            if handle_transaction_exception(e, attempt):
                continue

    conn.close()


# =================================================================================================
# Helper Methods
# =================================================================================================
def handle_transaction_exception(e, attempt):
    should_retry = False
    if "deadlocked" in str(e):
        print(f"Transaction failed due to deadlock. Retrying... (Attempt {attempt + 1})")
        if attempt < MAX_RERTY - 1:
            sleep(attempt * DELAY)  # Wait before retrying, implement exponential backoff
            should_retry = True
        else:
            raise Exception("Transaction failed after maximum retries due to deadlock.") from e
    elif "Snapshot isolation transaction aborted" in str(e):
        print(f"Transaction failed due to snapshot isolation conflict. Retrying... (Attempt {attempt + 1})")
        if attempt < MAX_RERTY - 1:
            sleep(attempt * DELAY)  # Wait before retrying, implement exponential backoff
            should_retry = True
        else:
            raise Exception("Transaction failed after maximum retries due to snapshot isolation conflict.") from e
    else:
        raise Exception("An unexpected database error occurred.") from e
    
    return should_retry

def update_counter_and_get_transaction_id(cursor, counter_id):
    # Lock the BOS_Counter table for update
    cursor.execute("SELECT iLastNumber FROM BOS_Counter WITH (UPDLOCK) WHERE szCounterId = ?", (counter_id,))
    counter_row = cursor.fetchone()
    if not counter_row:
        raise ValueError("Counter not found")
    
    counter_number = f"{counter_row[0] + 1:010d}"
    counter_number = f"{counter_number[:5]}.{counter_number[5:]}"
    transaction_id = f"{datetime.now():%Y%m%d}-{counter_number}"
    
    # Update the BOS_Counter table
    cursor.execute(
        "UPDATE BOS_Counter SET iLastNumber = iLastNumber + 1 WHERE szCounterId = ?", 
        (counter_id,)
    )
    
    return transaction_id

def insert_history(cursor, transaction_id, account_id, currency_id, amount, type):
    # Insert the record into BOS_History table
    cursor.execute("""
        INSERT INTO BOS_History (szTransactionId, szAccountId, szCurrencyId, dtmTransaction, decAmount, szNote)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (transaction_id, account_id, currency_id, datetime.now(), amount, type))


def check_balance(cursor, account_id, currency_id, amount):
    # Check if BOS_Balance decAmount is enough to be transferred
    cursor.execute("SELECT decAmount FROM BOS_Balance WITH (UPDLOCK) WHERE szAccountId = ? AND szCurrencyId = ?", (account_id, currency_id))
    balance_row = cursor.fetchone()
    if not balance_row or balance_row[0] < amount:
        raise ValueError("Not enough balance")