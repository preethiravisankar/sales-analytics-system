import os
from pprint import pprint
# *********************************************
# Read sales data with encoding handling
# *********************************************
def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues

    Returns: list of raw lines (strings)
    """

    file_path = os.path.join("data", filename)
    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                lines = file.readlines()
            #return lines
            # Skip header and remove empty lines
            cleaned_lines = []
            for line in lines[1:]:  # skip header
                line = line.strip()
                if line:
                    cleaned_lines.append(line)

            return cleaned_lines

        except UnicodeDecodeError:
            # Try next encoding
            continue

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return []

    print("Error: Unable to read file using supported encodings.")
    return []
    
sales_lines = read_sales_data("sales_data.txt")
#print(len(sales_lines))
#print(sales_lines[:2])



# *********************************************
# Read sales data with encoding handling
# *********************************************
def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    Applies validation and cleaning rules
    """

    transactions = []

    for line in raw_lines:
        # Split by pipe delimiter
        fields = line.split("|")

        # INVALID: incorrect number of fields
        if len(fields) != 8:
            continue

        (
            transaction_id,
            date,
            product_id,
            product_name,
            quantity,
            unit_price,
            customer_id,
            region
        ) = fields

        # Strip whitespace early
        transaction_id = transaction_id.strip()
        product_id = product_id.strip()
        customer_id = customer_id.strip()
        region = region.strip()
        date = date.strip()

        # INVALID: ID format checks
        #if not transaction_id.startswith("T"):
           # continue
        #if not product_id.startswith("P"):
          #  continue
        #if not customer_id.startswith("C"):
           # continue

        # INVALID: missing mandatory fields
        if not customer_id or not region:
            continue

        # DIRTY: clean product name
        product_name = product_name.replace(",", " ").strip()

        try:
            # DIRTY: clean numeric fields
            quantity = int(quantity.replace(",", "").strip())
            unit_price = float(unit_price.replace(",", "").strip())
        except ValueError:
            # INVALID: non-numeric quantity or price
            continue

        # INVALID: non-positive values
        if quantity <= 0 or unit_price <= 0:
            continue

        # VALID record
        transaction = {
            "TransactionID": transaction_id,
            "Date": date,
            "ProductID": product_id,
            "ProductName": product_name,
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": customer_id,
            "Region": region
        }

        transactions.append(transaction)

    return transactions

#transactions = parse_transactions(sales_lines)
#print(transactions[:3])

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters.
    Returns filtered transactions, invalid count, and summary.
    """

    required_fields = [
        'TransactionID', 'Date', 'ProductID', 'ProductName',
        'Quantity', 'UnitPrice', 'CustomerID', 'Region'
    ]

    valid_transactions = []
    invalid_count = 0

    # -----------------------
    # Validation step
    # -----------------------
    for txn in transactions:

        # Required fields check
        if not all(field in txn for field in required_fields):
            invalid_count += 1
            continue

        # ID format checks
        if not (
            txn['TransactionID'].startswith('T') and
            txn['ProductID'].startswith('P') and
            txn['CustomerID'].startswith('C')
        ):
            invalid_count += 1
            continue

        # Quantity & UnitPrice checks
        if txn['Quantity'] <= 0 or txn['UnitPrice'] <= 0:
            invalid_count += 1
            continue

        valid_transactions.append(txn)

    # -----------------------
    # Filtering step
    # -----------------------
    filtered_by_region = 0
    filtered_by_amount = 0

    filtered_transactions = valid_transactions

    # Region filter
    if region is not None:
        before = len(filtered_transactions)
        filtered_transactions = [
            t for t in filtered_transactions if t['Region'].lower() == region
        ]
        filtered_by_region = before - len(filtered_transactions)

    # Amount filter
    if min_amount is not None or max_amount is not None:
        before = len(filtered_transactions)
        temp = []

        for t in filtered_transactions:
            amount = t['Quantity'] * t['UnitPrice']

            if min_amount is not None and amount < min_amount:
                continue
            if max_amount is not None and amount > max_amount:
                continue

            temp.append(t)

        filtered_transactions = temp
        filtered_by_amount = before - len(filtered_transactions)

    # -----------------------
    # Summary
    # -----------------------
    filter_summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(filtered_transactions)
    }

    return filtered_transactions, invalid_count, filter_summary