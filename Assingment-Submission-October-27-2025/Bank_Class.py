from __future__ import annotations

import csv
import os
from datetime import datetime

LOG_FILE = "transactions_log.csv"


def log_event(action: str,
              status: str,
              *,
              account_no: str = "",
              holder: str = "",
              loan_id: str = "",
              loan_type: str = "",
              amount: float | str = "",
              balance_before: float | str = "",
              balance_after: float | str = "",
              due_before: float | str = "",
              due_after: float | str = "",
              message: str = "") -> None:
    """Append a row to transactions_log.csv."""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "action", "status",
                "account_no", "holder",
                "loan_id", "loan_type",
                "amount",
                "balance_before", "balance_after",
                "due_before", "due_after",
                "message"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action, status,
            account_no, holder,
            loan_id, loan_type,
            amount,
            balance_before, balance_after,
            due_before, due_after,
            message
        ])


def pause(message: str = "\nPress Enter to continue........ :)"):
    input(message)


# =========================
# BANK ACCOUNT SYSTEM
# =========================
class BankAccount:
    next_number = 100  # Incrementor for every new account created

    def __init__(self, account_holder: str, balance: float = 0.0, phone: int = 0):
        self.account_holder = account_holder
        self.balance = float(balance)
        self.account_holder_phone = int(phone)
        self.account_number = f"2025-{BankAccount.next_number}"
        BankAccount.next_number += 1

        print(f"\nAccount created for {self.account_holder} with account number {self.account_number}")
        log_event(
            action="ACCOUNT_CREATE",
            status="SUCCESS",
            account_no=self.account_number,
            holder=self.account_holder,
            amount=self.balance,
            balance_before="",
            balance_after=self.balance,
            message="New bank account created"
        )

    def deposit(self, amount: float):
        amount = float(amount)
        before = self.balance

        if amount < 10:
            print("\nDeposit amount must be a minimum of $10.00")
            log_event(
                action="DEPOSIT",
                status="FAILED",
                account_no=self.account_number,
                holder=self.account_holder,
                amount=amount,
                balance_before=before,
                balance_after=before,
                message="Deposit below minimum"
            )
            pause()
            return False

        self.balance += amount
        after = self.balance

        print(f"\nDeposited ${amount:.2f}. Your new balance is ${after:.2f}")
        log_event(
            action="DEPOSIT",
            status="SUCCESS",
            account_no=self.account_number,
            holder=self.account_holder,
            amount=amount,
            balance_before=before,
            balance_after=after,
            message="Deposit completed"
        )
        pause()
        return True

    def withdraw(self, amount: float):
        amount = float(amount)
        before = self.balance

        if amount <= 0:
            print("\nInvalid withdrawal amount")
            log_event(
                action="WITHDRAW",
                status="FAILED",
                account_no=self.account_number,
                holder=self.account_holder,
                amount=amount,
                balance_before=before,
                balance_after=before,
                message="Invalid withdraw amount"
            )
            pause()
            return False

        if amount > 1000:
            print("\nYou can only withdraw up to $1000.00 at a time.")
            log_event(
                action="WITHDRAW",
                status="FAILED",
                account_no=self.account_number,
                holder=self.account_holder,
                amount=amount,
                balance_before=before,
                balance_after=before,
                message="Withdraw exceeds per-transaction limit"
            )
            pause()
            return False

        if amount > self.balance:
            print("\nInsufficient funds!")
            log_event(
                action="WITHDRAW",
                status="FAILED",
                account_no=self.account_number,
                holder=self.account_holder,
                amount=amount,
                balance_before=before,
                balance_after=before,
                message="Insufficient funds"
            )
            pause()
            return False

        self.balance -= amount
        after = self.balance

        print(f"\nWithdrawn ${amount:.2f}. Your new balance is ${after:.2f}")
        log_event(
            action="WITHDRAW",
            status="SUCCESS",
            account_no=self.account_number,
            holder=self.account_holder,
            amount=amount,
            balance_before=before,
            balance_after=after,
            message="Withdraw completed"
        )
        pause()
        return True

    def cash_out(self) -> float:
        """Withdraw all remaining balance (closure payout)."""
        before = self.balance
        payout = self.balance
        self.balance = 0.0
        after = self.balance

        print(f"\nCashed out ${payout:.2f}. Account balance is now $0.00")
        log_event(
            action="ACCOUNT_CASHOUT",
            status="SUCCESS",
            account_no=self.account_number,
            holder=self.account_holder,
            amount=payout,
            balance_before=before,
            balance_after=after,
            message="Full balance cashed out for account closure"
        )
        pause()
        return payout

    def show_balance(self):
        print(f"\nCurrent balance in {self.account_number}: ${self.balance:.2f}")
        pause()


# =========================
# LOAN ACCOUNT SYSTEM
# =========================
class LoanAccount:
    def __init__(self, loan_type: str, holder_name: str, bank_account_number: str,
                 allocated_amount: float, interest_rate: float):
        self.issue_date = datetime.now()
        self.holder_name = holder_name
        self.loan_type = loan_type

        self.loan_id = self._generate_loan_id(bank_account_number)

        self.bank_account_number = bank_account_number
        self.allocated_amount = float(allocated_amount)
        self.disbursed_amount = 0.0
        self.balance_due = 0.0
        self.interest_rate = float(interest_rate)
        self.primary_deposit_holder = None
        self.last_interest_date = self.issue_date

        print(
            f"\nLoan account created for {self.holder_name}."
            f"\nLoan ID: {self.loan_id}"
            f"\nApproved amount: ${self.allocated_amount:.2f}"
        )
        log_event(
            action="LOAN_CREATE",
            status="SUCCESS",
            account_no=self.bank_account_number,
            holder=self.holder_name,
            loan_id=self.loan_id,
            loan_type=self.loan_type,
            amount=self.allocated_amount,
            due_before=0,
            due_after=self.balance_due,
            message="Loan created (not yet disbursed)"
        )

    def _generate_loan_id(self, bank_account_number: str) -> str:
        month_code = self.issue_date.strftime("%b").upper()[:2]  # MA
        name_code = self.holder_name.strip().upper()[:2]         # SA
        return f"{month_code}-{bank_account_number}-{name_code}"

    def disburse_amount(self, amount: float):
        amount = float(amount)
        due_before = self.balance_due

        if amount <= 0:
            print("\nInvalid disbursement amount.")
            log_event(
                action="LOAN_DISBURSE",
                status="FAILED",
                account_no=self.bank_account_number,
                holder=self.holder_name,
                loan_id=self.loan_id,
                loan_type=self.loan_type,
                amount=amount,
                due_before=due_before,
                due_after=due_before,
                message="Invalid disbursement amount"
            )
            pause()
            return False

        if self.disbursed_amount + amount > self.allocated_amount:
            print("\nAmount exceeds allocated limit.")
            log_event(
                action="LOAN_DISBURSE",
                status="FAILED",
                account_no=self.bank_account_number,
                holder=self.holder_name,
                loan_id=self.loan_id,
                loan_type=self.loan_type,
                amount=amount,
                due_before=due_before,
                due_after=due_before,
                message="Exceeds allocated limit"
            )
            pause()
            return False

        self.disbursed_amount += amount
        self.balance_due += amount
        due_after = self.balance_due

        print(f"\nDisbursed ${amount:.2f}. Total disbursed: ${self.disbursed_amount:.2f}")
        log_event(
            action="LOAN_DISBURSE",
            status="SUCCESS",
            account_no=self.bank_account_number,
            holder=self.holder_name,
            loan_id=self.loan_id,
            loan_type=self.loan_type,
            amount=amount,
            due_before=due_before,
            due_after=due_after,
            message="Disbursement successful"
        )
        pause()
        return True

    def set_primary_deposit_holder(self, name: str):
        self.primary_deposit_holder = name
        print(f"\nPrimary deposit holder set to: {self.primary_deposit_holder}")
        pause()

    def accumulate_interest(self):
        now = datetime.now()
        days_passed = (now - self.last_interest_date).days
        due_before = self.balance_due

        if days_passed <= 0:
            print("\nNo days passed since last interest calculation.")
            log_event(
                action="LOAN_INTEREST",
                status="SKIPPED",
                account_no=self.bank_account_number,
                holder=self.holder_name,
                loan_id=self.loan_id,
                loan_type=self.loan_type,
                amount=0,
                due_before=due_before,
                due_after=due_before,
                message="No days passed"
            )
            pause()
            return 0.0

        interest = (self.disbursed_amount * (self.interest_rate / 100) * days_passed / 365)
        self.balance_due += interest
        self.last_interest_date = now
        due_after = self.balance_due

        print(f"\nInterest of ${interest:.2f} accumulated for {days_passed} days. Total due: ${self.balance_due:.2f}")
        log_event(
            action="LOAN_INTEREST",
            status="SUCCESS",
            account_no=self.bank_account_number,
            holder=self.holder_name,
            loan_id=self.loan_id,
            loan_type=self.loan_type,
            amount=round(interest, 2),
            due_before=round(due_before, 2),
            due_after=round(due_after, 2),
            message=f"Interest added for {days_passed} days"
        )
        pause()
        return interest

    def display_account_summary(self):
        print("\n---- Loan Account Summary ----")
        print(f"Loan ID:               {self.loan_id}")
        print(f"Loan Type:             {self.loan_type}")
        print(f"Holder Name:           {self.holder_name}")
        print(f"Linked Bank Account:   {self.bank_account_number}")
        print(f"Primary Deposit Holder:{self.primary_deposit_holder or 'Not assigned'}")
        print(f"Allocated Amount:      ${self.allocated_amount:.2f}")
        print(f"Disbursed Amount:      ${self.disbursed_amount:.2f}")
        print(f"Interest Rate:         {self.interest_rate:.2f}% per annum")
        print(f"Total Balance Due:     ${self.balance_due:.2f}")
        print(f"Account Created On:    {self.issue_date.strftime('%Y-%m-%d')}")
        print(f"Last Interest Calc:    {self.last_interest_date.strftime('%Y-%m-%d')}")
        print("--------------------------------\n")

    def repay(self, amount: float) -> float:
        amount = float(amount)
        due_before = self.balance_due

        if amount <= 0:
            print("\nInvalid repayment amount.")
            log_event(
                action="LOAN_REPAY",
                status="FAILED",
                account_no=self.bank_account_number,
                holder=self.holder_name,
                loan_id=self.loan_id,
                loan_type=self.loan_type,
                amount=amount,
                due_before=due_before,
                due_after=due_before,
                message="Invalid repayment amount"
            )
            pause()
            return 0.0

        if self.balance_due <= 0:
            print("\nNothing due on this loan.")
            log_event(
                action="LOAN_REPAY",
                status="SKIPPED",
                account_no=self.bank_account_number,
                holder=self.holder_name,
                loan_id=self.loan_id,
                loan_type=self.loan_type,
                amount=0,
                due_before=due_before,
                due_after=due_before,
                message="No due amount"
            )
            pause()
            return 0.0

        paid = min(amount, self.balance_due)
        self.balance_due -= paid
        due_after = self.balance_due

        print(f"\nPayment applied: ${paid:.2f}. Remaining due: ${self.balance_due:.2f}")
        log_event(
            action="LOAN_REPAY",
            status="SUCCESS",
            account_no=self.bank_account_number,
            holder=self.holder_name,
            loan_id=self.loan_id,
            loan_type=self.loan_type,
            amount=round(paid, 2),
            due_before=round(due_before, 2),
            due_after=round(due_after, 2),
            message="Repayment applied"
        )
        pause()
        return paid


# =========================
# SHARED INPUT HELPERS
# =========================
def get_linked_loans(loans_by_id: dict[str, LoanAccount], account_number: str) -> list[LoanAccount]:
    return [ln for ln in loans_by_id.values()
            if getattr(ln, "bank_account_number", "") == account_number]


def ask_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("\nInvalid Entry!! Please enter a whole number.")
            pause()


def ask_float(prompt: str, *, min_value: float | None = None, max_value: float | None = None) -> float:
    while True:
        try:
            val = float(input(prompt).strip())
        except ValueError:
            print("\nInvalid Entry!! Numericals are allowed.")
            pause()
            continue

        if min_value is not None and val < min_value:
            print(f"\nInvalid Entry!! Minimum allowed is {min_value:.2f}")
            pause()
            continue
        if max_value is not None and val > max_value:
            print(f"\nInvalid Entry!! Maximum allowed is {max_value:.2f}")
            pause()
            continue
        return val


def ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("yes", "y"):
            return True
        if ans in ("no", "n"):
            return False
        print("\nInvalid selection. Please type Yes or No.")
        pause()


# =========================
# MENUS
# =========================
def loan_selection_menu() -> str:
    while True:
        print("\nWhat type of loan are you looking for?")
        print("A) Personal Loan")
        print("B) Mortgage/Home Loan")
        print("C) Home Equity Loan")
        print("D) Auto Loan")
        print("E) Education Loan")
        print("F) Debt Consolidation Loan")
        print("G) Payday Loan")
        print("Z) Back")

        option = input("\nEnter your choice: ").strip().lower()
        mapping = {
            "a": "Personal Loan",
            "b": "Mortgage/Home Loan",
            "c": "Home Equity Loan",
            "d": "Auto Loan",
            "e": "Education Loan",
            "f": "Debt Consolidation Loan",
            "g": "Payday Loan",
        }
        if option == "z":
            return ""
        if option in mapping:
            return mapping[option]
        print("\nInvalid Option!! Please choose from the menu.")
        pause()


def default_interest_rate_for(loan_type: str) -> float:
    rates = {
        "Personal Loan": 12.0,
        "Mortgage/Home Loan": 7.5,
        "Home Equity Loan": 9.0,
        "Auto Loan": 8.0,
        "Education Loan": 6.5,
        "Debt Consolidation Loan": 15.0,
        "Payday Loan": 35.0,
    }
    return rates.get(loan_type, 10.0)


def account_submenu(account: BankAccount):
    while True:
        print(f"\nAccount: {account.account_holder} | Account Number: {account.account_number} | Phone: {account.account_holder_phone}")
        print("1 Deposit Money")
        print("2 Withdraw Money")
        print("3 Check Balance")
        print("0 Back")

        option = ask_int("Choose an option: ")

        if option == 1:
            amount = ask_float("\nEnter the amount to deposit: ", min_value=10.0)
            account.deposit(amount)

        elif option == 2:
            amount = ask_float("\nEnter amount to withdraw (max $1000): ", min_value=1.0, max_value=1000.0)
            account.withdraw(amount)

        elif option == 3:
            account.show_balance()

        elif option == 0:
            break
        else:
            print("\nInvalid option chosen.")
            pause()


def bank_menu(accounts_by_number: dict[str, BankAccount], loans_by_id: dict[str, LoanAccount]):
    while True:
        print("\n=== BANK ACCOUNT MENU ===")
        print("1 Create a new account")
        print("2 Search for an account")
        print("3 Close an existing account")
        print("0 Back")

        choice = ask_int("\nEnter your choice: ")

        if choice == 0:
            return

        if choice == 1:
            print("\nTo create an account, please provide the following.")
            name = input("Name of the account holder: ").strip()
            initial_balance = ask_float("Enter amount to deposit (min $100): ", min_value=100.0)
            phone_number = ask_int("Please enter phone number: ")

            new_acc = BankAccount(name, initial_balance, phone_number)
            accounts_by_number[new_acc.account_number] = new_acc
            pause()

        elif choice == 2:
            print("\nTo search for your account details please enter any one of the following options!")
            print("a) Account Number")
            print("b) Account Holder Name")
            print("c) Account Holder Phone Number")
            search_choice = input("Choose a, b, or c: ").strip().lower()

            if search_choice == 'a':
                acc_no = input("Enter account number: ").strip()
                if acc_no in accounts_by_number:
                    print("\nAccount Found!")
                    pause()
                    account_submenu(accounts_by_number[acc_no])
                else:
                    print("\nAccount not found. Try again.")
                    pause()

            elif search_choice == 'b':
                acc_name = input("Enter account holder name: ").strip().lower()
                to_search = None
                for k, obj in accounts_by_number.items():
                    if obj.account_holder.strip().lower() == acc_name:
                        to_search = k
                        break
                if to_search:
                    print("\nAccount Found!")
                    pause()
                    account_submenu(accounts_by_number[to_search])
                else:
                    print("\nAccount not Found. Try again.")
                    pause()

            elif search_choice == 'c':
                acc_phone = ask_int("Enter account holder phone number: ")
                to_search = None
                for k, obj in accounts_by_number.items():
                    if obj.account_holder_phone == acc_phone:
                        to_search = k
                        break
                if to_search:
                    print("\nAccount Found!")
                    pause()
                    account_submenu(accounts_by_number[to_search])
                else:
                    print("\nAccount not found. Try again.")
                    pause()

            else:
                print("\nInvalid Choice.")
                pause()

        elif choice == 3:
            print("\nClose account using:")
            print("a) Account Number")
            print("b) Account Holder Name")
            print("c) Account Holder Phone")
            close_choice = input("Choose a, b, or c: ").strip().lower()

            # Resolve account to delete
            key_to_delete = None
            if close_choice == "a":
                acc_no = input("Enter account number to delete: ").strip()
                key_to_delete = acc_no if acc_no in accounts_by_number else None
            elif close_choice == "b":
                acc_name = input("Enter account holder full name to delete: ").strip().lower()
                for k, obj in accounts_by_number.items():
                    if obj.account_holder.strip().lower() == acc_name:
                        key_to_delete = k
                        break
            elif close_choice == "c":
                acc_phone = ask_int("Enter account holder phone number to delete: ")
                for k, obj in accounts_by_number.items():
                    if obj.account_holder_phone == acc_phone:
                        key_to_delete = k
                        break
            else:
                print("\nInvalid choice.")
                pause()
                continue

            if not key_to_delete:
                print("\nAccount not found.")
                log_event(action="ACCOUNT_CLOSE", status="FAILED", message="Account not found for closure")
                pause()
                continue

            acc = accounts_by_number[key_to_delete]

            # 1) Block closure if any linked loan has dues
            linked_loans = get_linked_loans(loans_by_id, acc.account_number)
            unpaid = [ln for ln in linked_loans if getattr(ln, "balance_due", 0) > 0]

            if unpaid:
                print("\nAccount closure blocked.")
                print("This account has unpaid loan dues linked to it:")
                for ln in unpaid:
                    print(f"  - Loan ID: {ln.loan_id} | Due: ${ln.balance_due:.2f} | Type: {ln.loan_type}")
                log_event(
                    action="ACCOUNT_CLOSE",
                    status="FAILED",
                    account_no=acc.account_number,
                    holder=acc.account_holder,
                    balance_before=acc.balance,
                    message="Blocked: unpaid linked loan dues"
                )
                pause()
                continue

            # 2) Cash out remaining balance
            if acc.balance > 0:
                acc.cash_out()

            # 3) Delete account
            balance_at_close = acc.balance  # should be 0.0 now
            del accounts_by_number[key_to_delete]
            print(f"\nAccount {key_to_delete} closed successfully.")
            log_event(
                action="ACCOUNT_CLOSE",
                status="SUCCESS",
                account_no=acc.account_number,
                holder=acc.account_holder,
                balance_before=balance_at_close,
                balance_after="",
                message="Account closed/deleted"
            )
            pause()

        else:
            print("\nInvalid choice. Try again.")
            pause()


def loan_menu(accounts_by_number: dict[str, BankAccount], loans_by_id: dict[str, LoanAccount]):
    while True:
        print("\n=== LOAN ACCOUNT MENU ===")
        print("1 Apply for a new loan")
        print("2 Check loan details")
        print("3 Repay a loan")
        print("4 Accumulate interest")
        print("0 Back")

        choice = ask_int("\nEnter your choice: ")

        if choice == 0:
            return

        if choice == 1:
            acc_no = input("\nEnter your BANK account number: ").strip()
            acc = accounts_by_number.get(acc_no)
            if not acc:
                print("\nNo bank account found with that number. Create an account first.")
                pause()
                continue

            print(f"\nHello {acc.account_holder}!")
            loan_type = loan_selection_menu()
            if not loan_type:
                continue

            max_quote = 100000.0 if loan_type == "Personal Loan" else 1000000.0
            amount = ask_float(
                f"\nEnter intended loan amount (min $1000, max ${max_quote:,.2f}): ",
                min_value=1000.0, max_value=max_quote
            )
            rate = default_interest_rate_for(loan_type)

            # Create loan, but avoid collisions
            temp = LoanAccount(loan_type, acc.account_holder, acc.account_number, allocated_amount=amount, interest_rate=rate)
            if temp.loan_id in loans_by_id:
                print("\nLoan ID already exists (same month/account/name). Try again later or change rules.")
                log_event(
                    action="LOAN_CREATE",
                    status="FAILED",
                    account_no=acc.account_number,
                    holder=acc.account_holder,
                    loan_id=temp.loan_id,
                    loan_type=loan_type,
                    amount=amount,
                    message="Loan ID collision"
                )
                pause()
                continue

            temp.set_primary_deposit_holder(acc.account_holder)

            # Optional disbursement
            if ask_yes_no("\nDo you want to disburse some amount now? Yes/No: "):
                disb_amt = ask_float("\nEnter disbursement amount: ", min_value=1.0, max_value=amount)
                if temp.disburse_amount(disb_amt):
                    acc.deposit(disb_amt)

            loans_by_id[temp.loan_id] = temp
            print("\nLoan created successfully.")
            pause()
            continue

        if choice == 2:
            loan_id = input("\nEnter your Loan ID: ").strip().upper()
            loan = loans_by_id.get(loan_id)
            if not loan:
                print("\nLoan not found.")
                pause()
                continue
            loan.display_account_summary()
            pause()
            continue

        if choice == 3:
            loan_id = input("\nEnter your Loan ID: ").strip().upper()
            loan = loans_by_id.get(loan_id)
            if not loan:
                print("\nLoan not found.")
                pause()
                continue

            acc_no = input("\nEnter your BANK account number to pay from: ").strip()
            acc = accounts_by_number.get(acc_no)
            if not acc:
                print("\nBank account not found.")
                pause()
                continue

            if ask_yes_no("\nAccumulate interest before paying? Yes/No: "):
                loan.accumulate_interest()

            pay_amt = ask_float("\nEnter repayment amount: ", min_value=1.0)
            if not acc.withdraw(pay_amt):
                print("\nPayment failed from bank account.")
                pause()
                continue

            applied = loan.repay(pay_amt)
            overpay = pay_amt - applied
            if overpay > 0:
                acc.deposit(overpay)
                print(f"\nOverpayment of ${overpay:.2f} refunded to your bank account.")
                pause()
            continue

        if choice == 4:
            loan_id = input("\nEnter your Loan ID: ").strip().upper()
            loan = loans_by_id.get(loan_id)
            if not loan:
                print("\nLoan not found.")
                pause()
                continue
            loan.accumulate_interest()
            pause()
            continue

        print("\nInvalid choice.")
        pause()


def main():
    accounts_by_number: dict[str, BankAccount] = {}
    loans_by_id: dict[str, LoanAccount] = {}

    while True:
        print("\n========== MAIN MENU ==========")
        print("1 Saving/Checkings Account System")
        print("2 Loan Account System")
        print("0 Exit")

        choice = ask_int("\nEnter your choice: ")

        if choice == 0:
            print("\nThank you! Visit again.")
            break
        elif choice == 1:
            bank_menu(accounts_by_number, loans_by_id)
        elif choice == 2:
            loan_menu(accounts_by_number, loans_by_id)
        else:
            print("\nInvalid choice.")
            pause()
            


if __name__ == "__main__":
    main()
