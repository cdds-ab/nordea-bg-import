# Salary Payment File Format Documentation

This README outlines the format and structure of the salary payment file, compatible with Bankgirot's standards, as outlined in the official documentation. The file format includes three main sections: the opening record, payment records, and the footer record, with each line containing exactly 80 characters.

## Record Types

### 1. Opening Record (Type TK01)

| Position | Field                  | Value                   | Length | Notes                                                   |
|----------|-------------------------|-------------------------|--------|---------------------------------------------------------|
| 1-2      | Transaction Code        | `01`                   | 2      | Identifies the record as the opening record.            |
| 3-8      | Creation Date           | `YYMMDD`               | 6      | Date the file was created (year, month, day).           |
| 9-10     | Reserved                | Blank                  | 2      | Must be blank.                                          |
| 11-13    | Product Code            | `LÖN`                  | 3      | Specifies the product as "LÖN" (salary).                |
| 14-59    | Reserved                | Blank                  | 46     | Must be blank.                                          |
| 60-62    | Currency Code           | `SEK` or blank         | 3      | Must be `SEK` or left blank.                            |
| 63-68    | Sender's Customer Number| Right-aligned, zero-padded | 6  | Customer number without hyphens.                        |
| 69-78    | Sender's Bankgiro Number| Right-aligned, zero-padded | 10 | Bankgiro number without hyphens.                        |
| 79-80    | Reserved                | Blank                  | 2      | Must be blank.                                          |

### 2. Payment Record (Type TK35)

| Position | Field                     | Value                        | Length | Notes                                                  |
|----------|----------------------------|------------------------------|--------|--------------------------------------------------------|
| 1-2      | Transaction Code           | `35`                        | 2      | Identifies the record as a payment record.             |
| 3-8      | Payment Date               | `YYMMDD`                    | 6      | Salary payment date.                                   |
| 9-12     | Reserved                   | Blank                       | 4      | Must be blank.                                         |
| 13-28    | Recipient's Bank Account   | Right-aligned, zero-padded  | 16     | Includes clearing number in the first 4 positions.     |
| 29-40    | Amount                     | Right-aligned, zero-padded  | 12     | Amount in "kronor and öre", no commas or dots allowed. |
| 41-58    | Reserved                   | Blank                       | 18     | Must be blank.                                         |
| 59-68    | Employment Information     | Right-aligned, zero-padded  | 10     | Can include ID such as employee or social number.      |
| 69-80    | Payment Identification     | Alphanumeric                | 12     | Information for identifying the payment.               |

### 3. Footer Record (Type TK09)

| Position | Field                    | Value                        | Length | Notes                                                   |
|----------|---------------------------|------------------------------|--------|---------------------------------------------------------|
| 1-2      | Transaction Code          | `09`                        | 2      | Identifies the record as the footer record.             |
| 3-8      | Creation Date             | `YYMMDD`                    | 6      | Date the file was created (year, month, day).           |
| 9-28     | Reserved                  | Blank                       | 20     | Must be blank.                                          |
| 29-40    | Total Amount              | Right-aligned, zero-padded  | 12     | Total of all amounts in the payment records (TK35).     |
| 41-46    | Number of Payment Records | Right-aligned, zero-padded  | 6      | Total count of payment records (TK35).                  |
| 47-80    | Reserved                  | Zero-padded                 | 34     | Must be filled with zeros.                              |

## Example File Structure

```plaintext
01050407  LÖN                                              SEK1111110009912346  
35050413    3300003232323232000000512346                  0000000000VALFRI TEXT 
35050413    5841000001009955000001097107                  0000000000VALFRI TEXT 
35050413    3300001111111116000000744967                  0000000000VALFRI TEXT 
35050413    6561000123456789000000700492                  0000000000VALFRI TEXT 
35050413    8357001112223332000000711147                  0000000000VALFRI TEXT 
35050413    6001000334223113000000682071                  0000000000VALFRI TEXT 
09050407                    0000044481300000060000000000000000000000000000000000
```

# Notes

- The sender customer number can be anything, it will be filled by the import process at nordea.
- Nordea file import is not supporting SEK as currency code. We just provide 3 spaces.
- Nordea seems to ignore the employment information and the payment identification. After import, all of these values are empty.
