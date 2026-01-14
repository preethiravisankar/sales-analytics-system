def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions

    Returns: float (total revenue)
    """

    total_revenue = 0.0

    for txn in transactions:
        try:
            total_revenue += txn["Quantity"] * txn["UnitPrice"]
        except KeyError:
            # Skip transactions with missing fields
            continue

    return total_revenue

def region_wise_sales(transactions):
    """
    Analyzes sales by region

    Returns: dictionary with region statistics
    """

    region_stats = {}
    grand_total = 0.0

    # ----------------------------
    # Aggregate sales and counts
    # ----------------------------
    for txn in transactions:
        try:
            region = txn["Region"]
            amount = txn["Quantity"] * txn["UnitPrice"]
        except KeyError:
            continue

        grand_total += amount

        if region not in region_stats:
            region_stats[region] = {
                "total_sales": 0.0,
                "transaction_count": 0
            }

        region_stats[region]["total_sales"] += amount
        region_stats[region]["transaction_count"] += 1

    # ----------------------------
    # Calculate percentages
    # ----------------------------
    for region in region_stats:
        if grand_total > 0:
            percentage = (region_stats[region]["total_sales"] / grand_total) * 100
        else:
            percentage = 0.0

        region_stats[region]["percentage"] = round(percentage, 2)

    # ----------------------------
    # Sort by total_sales desc
    # ----------------------------
    sorted_region_stats = dict(
        sorted(
            region_stats.items(),
            key=lambda item: item[1]["total_sales"],
            reverse=True
        )
    )

    return sorted_region_stats

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold

    Returns: list of tuples:
    (ProductName, TotalQuantity, TotalRevenue)
    """

    product_stats = {}

    # ----------------------------
    # Aggregate quantity & revenue
    # ----------------------------
    for txn in transactions:
        try:
            name = txn["ProductName"]
            quantity = txn["Quantity"]
            revenue = txn["Quantity"] * txn["UnitPrice"]
        except KeyError:
            continue

        if name not in product_stats:
            product_stats[name] = {
                "total_quantity": 0,
                "total_revenue": 0.0
            }

        product_stats[name]["total_quantity"] += quantity
        product_stats[name]["total_revenue"] += revenue

    # ----------------------------
    # Sort by total quantity desc
    # ----------------------------
    sorted_products = sorted(
        product_stats.items(),
        key=lambda item: item[1]["total_quantity"],
        reverse=True
    )

    # ----------------------------
    # Pick top n and format output
    # ----------------------------
    top_products = []

    for product, stats in sorted_products[:n]:
        top_products.append(
            (
                product,
                stats["total_quantity"],
                round(stats["total_revenue"], 2)
            )
        )

    return top_products

def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns

    Returns: dictionary of customer statistics
    """

    customer_stats = {}

    # ----------------------------
    # Aggregate per customer
    # ----------------------------
    for txn in transactions:
        try:
            customer_id = txn["CustomerID"]
            product = txn["ProductName"]
            amount = txn["Quantity"] * txn["UnitPrice"]
        except KeyError:
            continue

        if customer_id not in customer_stats:
            customer_stats[customer_id] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set()
            }

        customer_stats[customer_id]["total_spent"] += amount
        customer_stats[customer_id]["purchase_count"] += 1
        customer_stats[customer_id]["products_bought"].add(product)

    # ----------------------------
    # Calculate averages & format
    # ----------------------------
    for customer_id, stats in customer_stats.items():
        if stats["purchase_count"] > 0:
            avg_value = stats["total_spent"] / stats["purchase_count"]
        else:
            avg_value = 0.0

        stats["avg_order_value"] = round(avg_value, 2)
        stats["total_spent"] = round(stats["total_spent"], 2)
        stats["products_bought"] = sorted(stats["products_bought"])

    # ----------------------------
    # Sort by total_spent desc
    # ----------------------------
    sorted_customers = dict(
        sorted(
            customer_stats.items(),
            key=lambda item: item[1]["total_spent"],
            reverse=True
        )
    )

    return sorted_customers

from datetime import datetime

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date

    Returns: dictionary sorted by date
    """

    daily_stats = {}

    # ----------------------------
    # Aggregate per date
    # ----------------------------
    for txn in transactions:
        try:
            date_str = txn["Date"]
            customer_id = txn["CustomerID"]
            amount = txn["Quantity"] * txn["UnitPrice"]
        except KeyError:
            continue

        if date_str not in daily_stats:
            daily_stats[date_str] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "unique_customers": set()
            }

        daily_stats[date_str]["revenue"] += amount
        daily_stats[date_str]["transaction_count"] += 1
        daily_stats[date_str]["unique_customers"].add(customer_id)

    # ----------------------------
    # Final formatting
    # ----------------------------
    for date_str, stats in daily_stats.items():
        stats["revenue"] = round(stats["revenue"], 2)
        stats["unique_customers"] = len(stats["unique_customers"])

    # ----------------------------
    # Sort chronologically
    # ----------------------------
    sorted_daily_stats = dict(
        sorted(
            daily_stats.items(),
            key=lambda item: datetime.strptime(item[0], "%Y-%m-%d")
        )
    )

    return sorted_daily_stats

def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue

    Returns: tuple (date, revenue, transaction_count)
    """

    daily_sales = {}

    # ----------------------------
    # Aggregate revenue per day
    # ----------------------------
    for txn in transactions:
        try:
            date = txn["Date"]
            amount = txn["Quantity"] * txn["UnitPrice"]
        except KeyError:
            continue

        if date not in daily_sales:
            daily_sales[date] = {
                "revenue": 0.0,
                "transaction_count": 0
            }

        daily_sales[date]["revenue"] += amount
        daily_sales[date]["transaction_count"] += 1

    # ----------------------------
    # Find peak sales day
    # ----------------------------
    peak_date = None
    peak_revenue = 0.0
    peak_count = 0

    for date, stats in daily_sales.items():
        if stats["revenue"] > peak_revenue:
            peak_date = date
            peak_revenue = round(stats["revenue"], 2)
            peak_count = stats["transaction_count"]

    return peak_date, peak_revenue, peak_count

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales

    Returns: list of tuples:
    (ProductName, TotalQuantity, TotalRevenue)
    """

    product_stats = {}

    # ----------------------------
    # Aggregate quantity & revenue
    # ----------------------------
    for txn in transactions:
        try:
            name = txn["ProductName"]
            quantity = txn["Quantity"]
            revenue = txn["Quantity"] * txn["UnitPrice"]
        except KeyError:
            continue

        if name not in product_stats:
            product_stats[name] = {
                "total_quantity": 0,
                "total_revenue": 0.0
            }

        product_stats[name]["total_quantity"] += quantity
        product_stats[name]["total_revenue"] += revenue

    # ----------------------------
    # Filter low-performing products
    # ----------------------------
    low_products = []

    for name, stats in product_stats.items():
        if stats["total_quantity"] < threshold:
            low_products.append(
                (
                    name,
                    stats["total_quantity"],
                    round(stats["total_revenue"], 2)
                )
            )

    # ----------------------------
    # Sort by quantity ascending
    # ----------------------------
    low_products.sort(key=lambda x: x[1])

    return low_products





