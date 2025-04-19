import mysql.connector
from getpass import getpass

# Custom exception for clarity
class AccountNotFoundError(Exception):
    pass

# Database connection
def create_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="1q2w3e4r",
        database="online_banking"
    )

# Check if username already exists
def username_exists(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM accounts WHERE username = %s", (username,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

# Create a new account
def create_account():
    while True:
        username = input("Enter your username: ").strip()
        if username_exists(username):
            print("Username already exists. Please choose another.")
            continue

        name = input("Enter your full name: ").strip()
        pin = getpass("Enter a 4-digit PIN: ").strip()
        if len(pin) != 4 or not pin.isdigit():
            print("PIN must be exactly 4 digits.")
            continue

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO accounts (username, name, pin, balance) VALUES (%s, %s, %s, 0)",
                (username, name, pin)
            )
            conn.commit()
            print("Account created successfully!")
            break
        except mysql.connector.Error as err:
            print(f"Error creating account: {err}")
        finally:
            cursor.close()
            conn.close()

# Authenticate user
def authenticate(username, pin):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, name FROM accounts WHERE username = %s AND pin = %s",
        (username, pin)
    )
    account = cursor.fetchone()
    cursor.close()
    conn.close()
    return account  # None if not found

# Check balance (with None‐check)
def check_balance(username):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE username = %s", (username,))
        row = cursor.fetchone()
        if row is None:
            raise AccountNotFoundError(f"No account found for '{username}'.")
        return row[0]
    except mysql.connector.Error as err:
        print(f"Error fetching balance: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# Deposit money (handles non‐existent user)
def deposit(username, amount):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE username = %s",
            (amount, username)
        )
        if cursor.rowcount == 0:
            print(f"Account '{username}' not found.")
        else:
            conn.commit()
            new_bal = check_balance(username)
            if new_bal is not None:
                print(f"Deposited {amount}. New balance: {new_bal}")
    except mysql.connector.Error as err:
        print(f"Error during deposit: {err}")
    finally:
        cursor.close()
        conn.close()

# Withdraw money (with balance check and None‐check)
def withdraw(username, amount):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE username = %s", (username,))
        row = cursor.fetchone()
        if row is None:
            print(f"Account '{username}' not found.")
            return
        balance = row[0]

        if balance < amount:
            print("Insufficient funds!")
            return

        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE username = %s",
            (amount, username)
        )
        conn.commit()
        new_bal = check_balance(username)
        if new_bal is not None:
            print(f"Withdrew {amount}. New balance: {new_bal}")
    except mysql.connector.Error as err:
        print(f"Error during withdrawal: {err}")
    finally:
        cursor.close()
        conn.close()

# Modify account details function
def modify_account(username, new_name=None, new_pin=None):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        if new_name:
            cursor.execute("UPDATE accounts SET name = %s WHERE username = %s", (new_name, username))
        if new_pin:
            if len(new_pin) != 4 or not new_pin.isdigit():
                print("PIN must be exactly 4 digits. PIN not changed.")
            else:
                cursor.execute("UPDATE accounts SET pin = %s WHERE username = %s", (new_pin, username))
        conn.commit()
        print("Account details updated successfully!")
    except mysql.connector.Error as err:
        print(f"Error updating account: {err}")
    finally:
        cursor.close()
        conn.close()

# Close account function
def close_account(username):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM accounts WHERE username = %s", (username,))
        if cursor.rowcount == 0:
            print(f"Account '{username}' not found.")
        else:
            conn.commit()
            print("Account closed successfully!")
    except mysql.connector.Error as err:
        print(f"Error closing account: {err}")
    finally:
        cursor.close()
        conn.close()

# Handle logged‐in user menu with error handling
def handle_logged_in_user(account):
    username, name = account
    while True:
        print(f"\nWelcome, {name}!")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Modify Account")
        print("5. Close Account")
        print("6. Logout")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            bal = check_balance(username)
            if bal is not None:
                print(f"Your balance is: {bal}")

        elif choice == '2':
            try:
                amt = float(input("Enter amount to deposit: "))
                if amt > 0:
                    deposit(username, amt)
                else:
                    print("Amount must be positive.")
            except ValueError:
                print("Invalid amount. Please enter a number.")

        elif choice == '3':
            try:
                amt = float(input("Enter amount to withdraw: "))
                if amt > 0:
                    withdraw(username, amt)
                else:
                    print("Amount must be positive.")
            except ValueError:
                print("Invalid amount. Please enter a number.")

        elif choice == '4':
            new_name = input("Enter new name (leave blank to keep current): ").strip() or None
            new_pin  = getpass("Enter new PIN (leave blank to keep current): ").strip() or None
            modify_account(username, new_name, new_pin)

        elif choice == '5':
            if input("Are you sure you want to close your account? (yes/no): ").lower() == 'yes':
                close_account(username)
                return True

        elif choice == '6':
            print("Logging out...")
            return False

        else:
            print("Invalid option. Please try again.")

# Main CLI loop
def main():
    while True:
        print("\nWelcome to Online Banking")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            create_account()

        elif choice == '2':
            username = input("Enter your username: ").strip()
            pin      = getpass("Enter your PIN: ").strip()
            account = authenticate(username, pin)
            if account:
                closed = handle_logged_in_user(account)
                if closed:
                    continue
            else:
                print("Invalid username or PIN. Please try again.")

        elif choice == '3':
            print("Exiting the program. Thank you for using Online Banking!")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":  #Runs code
    main()