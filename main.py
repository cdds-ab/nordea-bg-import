import datetime
import json
import sys
import os

# Field lengths of the format
MAX_BANK_ACCOUNT_LENGTH = 16
MAX_EMPLOYMENT_INFO_LENGTH = 10
MAX_PAYMENT_IDENTIFICATION_LENGTH = 12

class OpeningRecord:
    def __init__(self, creation_date, sender_customer_number, sender_bankgiro_number):
        self.transaction_code = "01"
        self.creation_date = self._validate_date(creation_date)
        self.product_code = "LÖN"
        self.currency_code = "   "  # Empty field for currency code, nordea is not supporting a "SEK" during import
        self.sender_customer_number = sender_customer_number.zfill(6)[:6]
        self.sender_bankgiro_number = sender_bankgiro_number.zfill(10)[:10]

    @staticmethod
    def _validate_date(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime('%y%m%d')
        except ValueError:
            raise ValueError("Invalid creation date format; expected YYYY-MM-DD.")

    def format(self):
        description = self.product_code.ljust(50)
        additional_info = f"{self.currency_code}{self.sender_customer_number}{self.sender_bankgiro_number}".ljust(20)
        return f"{self.transaction_code}{self.creation_date}  {description}{additional_info}".ljust(80)


class PaymentRecord:
    def __init__(self, payment_date, bank_account, amount, employment_info="", payment_identification=""):
        self.transaction_code = "35"
        self.payment_date = self._validate_date(payment_date)
        self.bank_account = bank_account.zfill(MAX_BANK_ACCOUNT_LENGTH)[:MAX_BANK_ACCOUNT_LENGTH]
        self.amount = self._validate_amount(amount)
        self.employment_info = employment_info.zfill(MAX_EMPLOYMENT_INFO_LENGTH)[:MAX_EMPLOYMENT_INFO_LENGTH]
        self.payment_identification = payment_identification.ljust(MAX_PAYMENT_IDENTIFICATION_LENGTH)[:MAX_PAYMENT_IDENTIFICATION_LENGTH]

    @staticmethod
    def _validate_date(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime('%y%m%d')
        except ValueError:
            raise ValueError("Invalid payment date format; expected YYYY-MM-DD.")

    @staticmethod
    def _validate_amount(amount):
        try:
            return str(int(round(float(amount) * 100))).zfill(12)  # Amount in "kronor and öre"
        except (ValueError, TypeError):
            raise ValueError("Invalid amount; must be a number.")

    def format(self):
        return f"{self.transaction_code}{self.payment_date}    {self.bank_account}{self.amount}                  {self.employment_info}{self.payment_identification}".ljust(80)


class FooterRecord:
    def __init__(self, creation_date, total_amount, record_count):
        self.transaction_code = "09"
        self.creation_date = self._validate_date(creation_date)
        self.total_amount = str(total_amount).zfill(12)
        self.record_count = str(record_count).zfill(6)

    @staticmethod
    def _validate_date(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime('%y%m%d')
        except ValueError:
            raise ValueError("Invalid date format; expected YYYY-MM-DD.")

    def format(self):
        return f"{self.transaction_code}{self.creation_date}{' ' * 20}{self.total_amount}{self.record_count}{'0' * 34}".ljust(80)


class SalaryFile:
    def __init__(self, creation_date, sender_customer_number, sender_bankgiro_number):
        self.creation_date = creation_date
        self.opening_record = OpeningRecord(creation_date, sender_customer_number, sender_bankgiro_number)
        self.payment_records = []
        self.footer_record = None

    def add_payment_record(self, payment_date, bank_account, amount, employment_info="", payment_identification=""):
        record = PaymentRecord(payment_date, bank_account, amount, employment_info, payment_identification)
        self.payment_records.append(record)

    def finalize(self):
        total_amount = sum(int(record.amount) for record in self.payment_records)
        record_count = len(self.payment_records)
        self.footer_record = FooterRecord(self.creation_date, total_amount, record_count)

    def format(self):
        if not self.footer_record:
            raise ValueError("Footer record has not been created. Call finalize() before formatting.")

        formatted_lines = [self.opening_record.format()]
        formatted_lines.extend(record.format() for record in self.payment_records)
        formatted_lines.append(self.footer_record.format())
        return "\n".join(formatted_lines)

    def save(self, filename):
        with open(filename, 'w', encoding='latin-1') as f:
            f.write(self.format() + "\n")

    @classmethod
    def from_json(cls, json_data):
        # Validate the JSON structure and create a SalaryFile instance
        try:
            creation_date = json_data['creation_date']
            sender_customer_number = json_data['sender_customer_number']
            sender_bankgiro_number = json_data['sender_bankgiro_number']
            salary_file = cls(creation_date, sender_customer_number, sender_bankgiro_number)

            # Add payment records
            for payment in json_data.get('payments', []):
                salary_file.add_payment_record(
                    payment_date=payment.get("payment_date"),
                    bank_account=payment.get("bank_account"),
                    amount=payment.get("amount"),
                    employment_info=payment.get("employment_info", ""),
                    payment_identification=payment.get("payment_identification", "")
                )

            salary_file.finalize()
            return salary_file
        except KeyError as e:
            raise ValueError(f"Missing required field in JSON: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scriptname.py inputfile.json")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)

    try:
        salary_file: SalaryFile = SalaryFile.from_json(json_data)
    except ValueError as e:
        print(f"Error in JSON data: {e}")
        sys.exit(1)

    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}.in.txt"

    try:
        salary_file.save(output_file)
        print(f"File '{output_file}' has been successfully created.")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)
