class BankAccount:
    next_number = 100 #Incrementor for every new account created

    # Constructor to initialize account details
    def __init__(self, account_holder, balance = 0.0, phone = 0):
        self.account_holder = account_holder
        self.balance = float(balance)
        self.account_holder_phone = phone
        self.account_number = f"2025-{BankAccount.next_number}"
        BankAccount.next_number += 1
        print(f"\nAccount created for {self.account_holder} with account number {self.account_number}")


    # Deposit method
    def deposit(self, amount):
        if amount <= 10:
            print("\nDeposit amount must be a minimum of $10.00 ")
            return
        self.balance += amount
        print(f"\nDeposited ${amount:.2f}. Your New balance is ${self.balance:.2f}")

    # Withdraw method
    def withdraw(self, amount):
        if amount <= 0:
            print("\nInvalid withdrawal amount")
            return
        if amount > self.balance:
            print("\nInsufficient funds!")
            return
        self.balance -= amount
        print(f"\nWithdrawn ${amount:.2f}. Your New balance is ${self.balance:.2f}")

    # Display balance info
    def show_balance(self):
        print(f"\nCurrent balance in {self.account_number}: ${self.balance:.2f}")

# ----------------------------------------
# Main Menu for Bank Operations
# ----------------------------------------

def bank_menu():
    accounts = {} #Using dictionary to store accounts

    while True:
        print("\n === BANK ACCOUNT MENU ===")
        print("1  Create a new account")
        print("2  Search for an account")
        print("3  Close an Existing account")
        print("0  Exit")

        choice = int(input("\nEnter your choice: ").strip())

        if choice == 0:
            print("Please Visit Again. Thank You!")
            break

        elif choice == 1:
            print("Inorder to create we need some basic information. Please answer the following\n")
            name = input("Name of the account holder: ").strip()
            try:
                initial_balance = float(input("Enter valid amount to deposit: "))
                if initial_balance <= 99 :
                    print("Minimum Deposit Amount to Create an Account is $100.00")
                    print("Please deposit $100.00 or more. Try Again. Thank you!")
                    continue
            except ValueError:
                print("Invalid Entry!")
                continue
            phone_number = int(input("Please enter account holder phone number: ").strip())
            new_acc = BankAccount(name, initial_balance, phone_number)
            accounts[new_acc.account_number] = new_acc
        
        elif choice == 3:
            print("\nInorder to close an account please make sure you have at least one these following details ready with you.\n")
            print("a) Account Number or b) Account Holder Entire Name or c) Account Holder Phone Number\n")
            close_choice = input("Please choose one of the available options that you posses: ").strip().lower()
            while True:
                if close_choice == 'a':
                    acc_no = input("\nEnter account number to delete: ")
                    if acc_no in accounts:
                        del accounts[acc_no]
                        print(f"\nAccount number {acc_no} was deleted successfully.")
                        break
                    else:
                        print("\nAccount not found/not exists.")
                        break
                elif close_choice == 'b':
                    acc_name = input("Enter account holder full name in order to delete: ")
                    for key, obj in accounts.items():
                        if obj.account_holder == acc_name:
                            del accounts[key]
                            print(f"\nAccount with name {acc_name} was deleted successfully.")
                            break
                        break
                    else:
                        print("\nAccount not found/not exists.")
                        break
                elif close_choice == 'c':
                    try:
                        acc_phone = int(input("Enter account holder phone number to delete: "))
                    except ValueError:
                        print("\nInvalid phone number. Try again.")
                        continue
                    for key, obj in accounts.items():
                        if obj.account_holder_phone == acc_phone:
                            del accounts[key]
                            print(f"\nAccount with phone number {acc_phone} was deleted successfully.")
                            break
                        break
                    else:
                        print("\nNo Account is found with this phone number.")
                        break
                else:
                    print("\nInvalid choice. Please try again.")

        elif choice == 2:
            acc_no = input("Enter account number to search: ")
            if acc_no in accounts:
                selected_account = accounts[acc_no]
                print("\nAccount Found! Your Account are as follows")
                account_submenu(selected_account)
            else:
                print("\nAccount not found. Try again Thank You!")

        else:
            print("\nInvalid Choice. Try again.\n")

# ----------------------------------------
# Submenu for a specific account
# ----------------------------------------
def account_submenu(account):
    while True:
        print(f"Account: {account.account_holder} | Account Number: {account.account_number} | Phone Number: {account.account_holder_phone}")
        print("1 Deposit Money")
        print("2 Withdraw Money")
        print("3 Check Balance")
        print("0 Back to Main menu\n")

        option = int(input("Choose an option: ").strip())

        if option == 1:
            try:
                amount = float(input("\nEnter the amount to deposit: "))
                if amount < 10:
                    print("\nMinimum of $10.00 deposite is requried. Please try again. Thank You.")
                    amount = float(input("\nEnter a valid amount: "))
            except ValueError:
                print("\nInvalid Entry.")
                continue
            account.deposit(amount)

        elif option == 2:
            try:
                amount = float(input("\nEnter amount to withdraw: "))
                if 1 < amount >= 1000:
                    print("\nUnable to withdraw mentioned amount. You can only withdraw $1000.00 at a time and no less than $1.00\n Thank you for understanding.")
                    amount = float(input("\nEnter valid amount: "))
            except ValueError:
                print("\nInvalid Entry.")
                continue
            account.withdraw(amount)

        elif option == 3:
            account.show_balance()

        elif option == 0:
            break

        else:
            print("Invalid option choosen.")

if __name__ == "__main__":
    bank_menu()