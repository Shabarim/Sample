import mysql.connector

# -------------------- Database Connection --------------------
con = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="mysql@123",
    database="bank"
)
cur = con.cursor()

# -------------------- Functions --------------------
def create_account():
    name = input("Enter name: ")
    if not name.isalpha():
        print("Invalid name. Only alphabets are allowed.")
        return
    pin = input("Set 4-digit PIN: ")
    if len(pin) != 4 or not pin.isdigit():
        print("Invalid PIN. Must be 4 digits.")
        return
    cur.execute("INSERT INTO accounts (name, pin) VALUES (%s, %s)", (name, pin))
    con.commit()
    cur.execute("SELECT account_id, name, pin, balance FROM accounts WHERE name = %s ORDER BY account_id DESC LIMIT 1", (name,))
    account = cur.fetchone()
    print("\nAccount created successfully!")
    print(f"Account ID: {account[0]}")
    print(f"Name: {account[1]}")
    print(f"PIN: {account[2]}")
    print(f"Balance: {account[3]:.2f}\n")

def check_pin(account_id, pin):
    cur.execute("SELECT pin FROM accounts WHERE account_id = %s", (account_id,))
    result = cur.fetchone()
    return result and result[0] == pin

def view_accounts():
    code = input("Enter your Account ID: ")
    if code == "s1":
        while True:
            print("\n--- Admin Access ---")
            print("1. View all accounts")
            print("2. View all transactions")
            print("3. Delete ALL accounts and transactions")
            print("4. Delete specific account")
            print("5. Delete specific transaction")
            print("6. Exit admin panel")

            admin_choice = input("Select an option: ")

            if admin_choice == "1":
                cur.execute("SELECT account_id, name, pin, balance FROM accounts")
                accounts = cur.fetchall()
                print("\n--- All Accounts ---")
                for acc in accounts:
                    print(f"ID: {acc[0]} | Name: {acc[1]} | PIN: {acc[2]} | Balance: {acc[3]:.2f}")
            
            elif admin_choice == "2":
                cur.execute("SELECT txn_id, account_id, type, amount, timestamp FROM transactions")
                transactions = cur.fetchall()
                if transactions:
                    print("\n--- All Transactions ---")
                    for txn in transactions:
                        print(f"Txn ID: {txn[0]} | Account ID: {txn[1]} | Type: {txn[2]} | Amount: {txn[3]} | Time: {txn[4]}")
                else:
                    print("No transactions found.")

            elif admin_choice == "3":
                confirm = input("Are you sure? Type DELETE to confirm: ")
                if confirm == "DELETE":
                    cur.execute("DELETE FROM transactions")
                    cur.execute("DELETE FROM accounts")
                    con.commit()
                    print("All accounts and transactions deleted.")                    
            
            elif admin_choice == "4":
                acc_id = input("Enter account ID to delete: ")
    
                # Check if account exists before trying to delete
                cur.execute("SELECT * FROM accounts WHERE account_id = %s", (acc_id,))
                if not cur.fetchone():
                    print(f"Account {acc_id} does not exist.")
                else:
                    cur.execute("DELETE FROM transactions WHERE account_id = %s", (acc_id,))
                    cur.execute("DELETE FROM accounts WHERE account_id = %s", (acc_id,))
                    con.commit()
                    print(f"Account {acc_id} and its transactions deleted.")

            
            elif admin_choice == "5":
                txn_id = input("Enter transaction ID to delete: ")
    
                # Check if transaction exists
                cur.execute("SELECT * FROM transactions WHERE txn_id = %s", (txn_id,))
                if not cur.fetchone():
                    print(f"Transaction {txn_id} does not exist.")
                else:
                    cur.execute("DELETE FROM transactions WHERE txn_id = %s", (txn_id,))
                    con.commit()
                    print(f"Transaction {txn_id} deleted.")

            
            elif admin_choice == "6":
                break
            else:
                print("Invalid option")
        return

    if code.isdigit():
        cur.execute("SELECT account_id, name, balance FROM accounts WHERE account_id = %s", (code,))
        account = cur.fetchone()
        if account:
            print("\n--- Account Details ---")
            print(f"Account ID: {account[0]} | Name: {account[1]} | Balance: {account[2]:.2f}")
        else:
            print("No account found with that ID.")
    else:
        print("Invalid input. Enter a valid account ID.")

def deposit():
    acc_id = input("Enter account ID: ")
    
    # Check if account exists
    cur.execute("SELECT * FROM accounts WHERE account_id = %s", (acc_id,))
    account = cur.fetchone()
    if not account:
        print("Account does not exist.")
        return
   
    pin = input("Enter PIN: ")
    if not check_pin(acc_id, pin):
        print("Incorrect PIN.")
        return
    
    amount = float(input("Enter amount to deposit: "))
    cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, acc_id))
    cur.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'deposit', %s)", (acc_id, amount))
    con.commit()
    print("Deposit successful!")

def withdraw():
    acc_id = input("Enter account ID: ")

        # Check if account exists
    cur.execute("SELECT * FROM accounts WHERE account_id = %s", (acc_id,))
    account = cur.fetchone()
    if not account:
        print("Account does not exist.")
        return

    pin = input("Enter PIN: ")
    if not check_pin(acc_id, pin):
        print("Incorrect PIN.")
        return
    amount = float(input("Enter amount to withdraw: "))
    cur.execute("SELECT balance FROM accounts WHERE account_id = %s", (acc_id,))
    balance = cur.fetchone()
    if balance and balance[0] >= amount:
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, acc_id))
        cur.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'withdraw', %s)", (acc_id, amount))
        con.commit()
        print("Withdrawal successful!")
    else:
        print("Insufficient balance.")

def transfer():
    sender = input("Enter sender account ID: ")

    # Check if sender account exists
    cur.execute("SELECT account_id FROM accounts WHERE account_id = %s", (sender,))
    sender_exists = cur.fetchone()
    if not sender_exists:
        print("Sender account does not exist.")
        return

    pin = input("Enter sender's PIN: ")
    if not check_pin(sender, pin):
        print("Incorrect PIN.")
        return

    receiver = input("Enter receiver account ID: ")
    
    # Check if receiver account exists
    cur.execute("SELECT account_id FROM accounts WHERE account_id = %s", (receiver,))
    receiver_exists = cur.fetchone()
    if not receiver_exists:
        print("Receiver account does not exist.")
        return

    amount = float(input("Enter amount to transfer: "))
    cur.execute("SELECT balance FROM accounts WHERE account_id = %s", (sender,))
    sender_balance = cur.fetchone()

    if sender_balance and sender_balance[0] >= amount:
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, sender))
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, receiver))
        cur.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'transfer_out', %s)", (sender, amount))
        cur.execute("INSERT INTO transactions (account_id, type, amount) VALUES (%s, 'transfer_in', %s)", (receiver, amount))
        con.commit()
        print("Transfer successful!")
    else:
        print("Insufficient balance.")

def transaction_history():
    acc_id = input("Enter account ID: ")

    # First check if the account exists
    cur.execute("SELECT * FROM accounts WHERE account_id = %s", (acc_id,))
    account_exists = cur.fetchone()
    if not account_exists:
        print("No account found.")
        return

    # If account exists, check for transactions
    cur.execute("SELECT txn_id, type, amount, timestamp FROM transactions WHERE account_id = %s", (acc_id,))
    transactions = cur.fetchall()
    if transactions:
        print("\n--- Transaction History ---")
        for txn in transactions:
            print(f"ID: {txn[0]} | {txn[3]} | {txn[1].capitalize()} | Amount: {txn[2]}")
    else:
        print("No transactions found.")

# -------------------- Menu --------------------

def main():
    while True:
        print("\nBank Menu:")
        print("1. Create Account")
        print("2. View Account")
        print("3. Deposit")
        print("4. Withdraw")
        print("5. Transfer")
        print("6. Transaction History")
        print("7. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            create_account()
        elif choice == '2':
            view_accounts()
        elif choice == '3':
            deposit()
        elif choice == '4':
            withdraw()
        elif choice == '5':
            transfer()
        elif choice == '6':
            transaction_history()
        elif choice == '7':
            break
        else:
            print("Invalid choice")

main()
cur.close()
con.close()
