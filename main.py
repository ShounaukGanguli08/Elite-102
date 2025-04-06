import mysql.connector
from getpass import getpass

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
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

# Function to create a new account
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
            cursor.execute("INSERT INTO accounts (username, name, pin, balance) VALUES (%s, %s, %s, 0)", 
                         (username, name, pin))
            conn.commit()
            print("Account created successfully!")
            break
        except mysql.connector.Error as err:
            print(f"Error creating account: {err}")
        finally:
            cursor.close()
            conn.close()

# Function to authenticate user
def authenticate(username, pin):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE username = %s AND pin = %s", (username, pin))
    account = cursor.fetchone()
    cursor.close()
    conn.close()
    return account

# ... [keep all other functions the same, but change account_number parameters to username] ...

# Function to handle logged-in user operations
def handle_logged_in_user(account):
    username = account[0]  # Assuming username is first column
    name = account[1]      # Assuming name is second column
    
    while True:
        print(f"\nWelcome, {name}!")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Modify Account")
        print("5. Close Account")
        print("6. Logout")
        user_choice = input("Choose an option: ")

        if user_choice == '1':
            balance = check_balance(username)
            print(f"Your balance is: {balance}")

        elif user_choice == '2':
            amount = float(input("Enter amount to deposit: "))
            deposit(username, amount)

        elif user_choice == '3':
            amount = float(input("Enter amount to withdraw: "))
            withdraw(username, amount)

        elif user_choice == '4':
            new_name = input("Enter new name (leave blank to keep current): ").strip()
            new_pin = getpass("Enter new PIN (leave blank to keep current): ").strip()
            modify_account(username, new_name if new_name else None, new_pin if new_pin else None)

        elif user_choice == '5':
            confirm = input("Are you sure you want to close your account? (yes/no): ").lower()
            if confirm == 'yes':
                close_account(username)
                return True  # Account was closed

        elif user_choice == '6':
            print("Logging out...")
            return False  # Normal logout

        else:
            print("Invalid option. Please try again.")

# Main CLI loop
def main():
    while True:
        print("\nWelcome to Online Banking")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            create_account()

        elif choice == '2':
            username = input("Enter your username: ").strip()
            pin = getpass("Enter your PIN: ").strip()
            account = authenticate(username, pin)

            if account:
                account_closed = handle_logged_in_user(account)
                if account_closed:
                    continue  # Account was closed, return to main menu
            else:
                print("Invalid username or PIN. Please try again.")

        elif choice == '3':
            print("Exiting the program. Thank you for using Online Banking!")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()