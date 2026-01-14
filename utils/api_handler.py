import requests

def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries
    """

    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises error for 4xx/5xx

        data = response.json()
        products = data.get("products", [])

        print(f"✓ Successfully fetched {len(products)} products")

        # Extract only required fields
        cleaned_products = []
        for p in products:
            cleaned_products.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand"),
                "price": p.get("price"),
                "rating": p.get("rating")
            })
        #print(cleaned_products)
        return cleaned_products

    except requests.exceptions.RequestException as e:
        print("✗ Failed to fetch products from API")
        print("Error:", e)
        return []

def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info

    Parameters: api_products from fetch_all_products()

    Returns: dictionary mapping product IDs to info
    """

    product_mapping = {}

    for product in api_products:
        try:
            product_id = product["id"]
        except KeyError:
            continue

        product_mapping[product_id] = {
            "title": product.get("title"),
            "category": product.get("category"),
            "brand": product.get("brand"),
            "rating": product.get("rating")
        }

    return product_mapping

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    """

    enriched_transactions = []

    for txn in transactions:
        enriched_txn = txn.copy()  # do not modify original

        # Default API fields
        enriched_txn["API_Category"] = None
        enriched_txn["API_Brand"] = None
        enriched_txn["API_Rating"] = None
        enriched_txn["API_Match"] = False

        try:
            # Extract numeric product ID (P101 -> 101)
            product_id_str = txn.get("ProductID", "").strip()

            if product_id_str.startswith("P"):
                numeric_id = int(product_id_str[1:])

                if numeric_id in product_mapping:
                    api_info = product_mapping[numeric_id]

                    enriched_txn["API_Category"] = api_info.get("category")
                    enriched_txn["API_Brand"] = api_info.get("brand")
                    enriched_txn["API_Rating"] = api_info.get("rating")
                    enriched_txn["API_Match"] = True

        except Exception:
            # Gracefully ignore any enrichment errors
            pass

        enriched_transactions.append(enriched_txn)

    # Save enriched data to file
    save_enriched_data(enriched_transactions)

    return enriched_transactions

def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions back to file
    """

    headers = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    try:
        with open(filename, "w", encoding="utf-8") as file:
            # Write header
            file.write("|".join(headers) + "\n")

            # Write records
            for txn in enriched_transactions:
                row = []
                for field in headers:
                    value = txn.get(field)

                    if value is None:
                        row.append("")
                    else:
                        row.append(str(value))

                file.write("|".join(row) + "\n")

        print("------------------------------------------------")
        print("[8/10] Saving enriched data...")

    except Exception as e:
        print("✗ Failed to save enriched data")
        print("Error:", e)

from datetime import datetime
from collections import defaultdict


def generate_sales_report(transactions, enriched_transactions, output_file="output/sales_report.txt"):
    """
    Generates a comprehensive formatted text report
    """

    if not transactions:
        print("✗ No transaction data available for report generation.")
        return

    # -----------------------------
    # Helper calculations
    # -----------------------------
    total_revenue = sum(t["Quantity"] * t["UnitPrice"] for t in transactions)
    total_transactions = len(transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions else 0

    dates = sorted(t["Date"] for t in transactions)
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"

    # -----------------------------
    # Region-wise performance
    # -----------------------------
    region_stats = defaultdict(lambda: {"revenue": 0.0, "count": 0})

    for t in transactions:
        amount = t["Quantity"] * t["UnitPrice"]
        region_stats[t["Region"]]["revenue"] += amount
        region_stats[t["Region"]]["count"] += 1

    region_summary = []
    for region, stats in region_stats.items():
        pct = (stats["revenue"] / total_revenue) * 100 if total_revenue else 0
        region_summary.append(
            (region, stats["revenue"], pct, stats["count"])
        )

    region_summary.sort(key=lambda x: x[1], reverse=True)

    # -----------------------------
    # Top products
    # -----------------------------
    product_stats = defaultdict(lambda: {"qty": 0, "revenue": 0.0})

    for t in transactions:
        product_stats[t["ProductName"]]["qty"] += t["Quantity"]
        product_stats[t["ProductName"]]["revenue"] += t["Quantity"] * t["UnitPrice"]

    top_products = sorted(
        product_stats.items(),
        key=lambda x: x[1]["qty"],
        reverse=True
    )[:5]

    # -----------------------------
    # Top customers
    # -----------------------------
    customer_stats = defaultdict(lambda: {"spent": 0.0, "count": 0})

    for t in transactions:
        customer_stats[t["CustomerID"]]["spent"] += t["Quantity"] * t["UnitPrice"]
        customer_stats[t["CustomerID"]]["count"] += 1

    top_customers = sorted(
        customer_stats.items(),
        key=lambda x: x[1]["spent"],
        reverse=True
    )[:5]

    # -----------------------------
    # Daily sales trend
    # -----------------------------
    daily_stats = defaultdict(lambda: {"revenue": 0.0, "count": 0, "customers": set()})

    for t in transactions:
        daily_stats[t["Date"]]["revenue"] += t["Quantity"] * t["UnitPrice"]
        daily_stats[t["Date"]]["count"] += 1
        daily_stats[t["Date"]]["customers"].add(t["CustomerID"])

    daily_summary = sorted(daily_stats.items())

    # -----------------------------
    # Peak sales day
    # -----------------------------
    peak_day = max(
        daily_summary,
        key=lambda x: x[1]["revenue"],
        default=(None, {})
    )

    # -----------------------------
    # Low performing products
    # -----------------------------
    low_products = [
        (name, stats["qty"], stats["revenue"])
        for name, stats in product_stats.items()
        if stats["qty"] < 10
    ]
    low_products.sort(key=lambda x: x[1])

    # -----------------------------
    # API enrichment summary
    # -----------------------------
    enriched_count = sum(1 for t in enriched_transactions if t.get("API_Match"))
    total_enriched = len(enriched_transactions)
    enrichment_rate = (enriched_count / total_enriched) * 100 if total_enriched else 0

    unenriched_products = sorted(
        {t["ProductName"] for t in enriched_transactions if not t.get("API_Match")}
    )

    # -----------------------------
    # Write report
    # -----------------------------
    with open(output_file, "w", encoding="utf-8") as file:

        # HEADER
        file.write("=" * 44 + "\n")
        file.write("       SALES ANALYTICS REPORT\n")
        file.write(f"     Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"     Records Processed: {total_transactions}\n")
        file.write("=" * 44 + "\n\n")

        # OVERALL SUMMARY
        file.write("OVERALL SUMMARY\n")
        file.write("-" * 44 + "\n")
        file.write(f"Total Revenue:        ₹{total_revenue:,.2f}\n")
        file.write(f"Total Transactions:   {total_transactions}\n")
        file.write(f"Average Order Value:  ₹{avg_order_value:,.2f}\n")
        file.write(f"Date Range:           {date_range}\n\n")

        # REGION-WISE PERFORMANCE
        file.write("REGION-WISE PERFORMANCE\n")
        file.write("-" * 44 + "\n")
        file.write(f"{'Region':10}{'Sales':15}{'% Total':12}{'Txn'}\n")
        for r, rev, pct, cnt in region_summary:
            file.write(f"{r:10}₹{rev:14,.0f}{pct:11.2f}%{cnt:6}\n")
        file.write("\n")

        # TOP PRODUCTS
        file.write("TOP 5 PRODUCTS\n")
        file.write("-" * 44 + "\n")
        file.write(f"{'Rank':5}{'Product':20}{'Qty':8}{'Revenue'}\n")
        for i, (name, stats) in enumerate(top_products, 1):
            file.write(f"{i:<5}{name:20}{stats['qty']:8}₹{stats['revenue']:,.0f}\n")
        file.write("\n")

        # TOP CUSTOMERS
        file.write("TOP 5 CUSTOMERS\n")
        file.write("-" * 44 + "\n")
        file.write(f"{'Rank':5}{'Customer':15}{'Spent':15}{'Orders'}\n")
        for i, (cid, stats) in enumerate(top_customers, 1):
            file.write(f"{i:<5}{cid:15}₹{stats['spent']:14,.0f}{stats['count']:8}\n")
        file.write("\n")

        # DAILY SALES TREND
        file.write("DAILY SALES TREND\n")
        file.write("-" * 44 + "\n")
        file.write(f"{'Date':12}{'Revenue':15}{'Txn':6}{'Customers'}\n")
        for date, stats in daily_summary:
            file.write(
                f"{date:12}₹{stats['revenue']:14,.0f}{stats['count']:6}{len(stats['customers']):10}\n"
            )
        file.write("\n")

        # PRODUCT PERFORMANCE
        file.write("PRODUCT PERFORMANCE ANALYSIS\n")
        file.write("-" * 44 + "\n")
        file.write(f"Best Selling Day: {peak_day[0]} (₹{peak_day[1]['revenue']:,.0f})\n")
        file.write("Low Performing Products:\n")
        for name, qty, rev in low_products:
            file.write(f"  - {name} (Qty: {qty}, Revenue: ₹{rev:,.0f})\n")
        file.write("\n")

        # API ENRICHMENT SUMMARY
        file.write("API ENRICHMENT SUMMARY\n")
        file.write("-" * 44 + "\n")
        file.write(f"Total Enriched Records: {enriched_count}/{total_enriched}\n")
        file.write(f"Success Rate: {enrichment_rate:.2f}%\n")
        file.write("Unmatched Products:\n")
        for p in unenriched_products:
            file.write(f"  - {p}\n")

    print(f"✓ Sales report generated and saved to: {output_file}")
