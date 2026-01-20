def main():
    # Welcome message
    width = 33
    print("=" * width)
    print("SALES ANALYTICS SYSTEM".center(width))
    print("=" * width)

    # step 1: Reading sales data
    from pathlib import Path
    from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
    from utils.data_processor import calculate_total_revenue, region_wise_sales, top_selling_products, customer_analysis, daily_sales_trend
    from utils.data_processor import find_peak_sales_day, low_performing_products
    from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data, generate_sales_report

    try:
        print("[1/10] Reading sales data...")

        base_dir = Path(__file__).parent
        data_file = base_dir / "data" / "sales_data.txt"
        sales_data = read_sales_data(data_file)
        count = len(sales_data)
        print(f"    ✓ Successfully read {count} transactions")

        # step 2: Parsing and cleaning data
        print("------------------------------------------------")
        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(sales_data)
        print(f"    ✓ Successfully parsed {len(transactions)} transactions")

        # step 3: filtering data
        print("------------------------------------------------")
        print("[3/10] Available filter options")
        regions = set()
        amounts = []

        for txn in transactions:
            try:
                amount = txn["Quantity"] * txn["UnitPrice"]
                regions.add(txn["Region"])
                amounts.append(amount)
            except Exception:
                continue

        if regions:
            print("     Available regions:", ", ".join(sorted(regions)))
        else:
            print("     Available regions: None")

        if amounts:
            print(f"    Transaction amount range: {min(amounts):.2f} to {max(amounts):.2f}")
        else:
            print("     Transaction amount range: N/A")
        # Ask user if filtering is required
        choice = input("Do you want to apply filters? (y/n): ").strip().lower()
        region = None
        min_amount = None
        max_amount = None

        if choice == "y":
            region = input("Enter region (leave blank for no region filter): ").strip()
            if region:
                region = region.lower()
            else:
                region = None

            # Minimum amount input
            while True:
                min_val = input("Enter minimum transaction amount (leave blank for none): ").strip()

                if min_val == "":
                    min_amount = None
                    break

                try:
                    min_amount = float(min_val)
                    break
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")

            # Maximum amount input
            while True:
                max_val = input("Enter maximum transaction amount (leave blank for none): ").strip()

                if max_val == "":
                    max_amount = None
                    break

                try:
                    max_amount = float(max_val)
                    break
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
        
        #step4: validate and filtering
        print("------------------------------------------------")
        print("[4/10] Validating transactions...")

        filtered_txns, invalid_count, summary = validate_and_filter(
            transactions,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount
        )
        print(f"✓ Valid: {summary['final_count']} | Invalid: {summary['invalid']}")
        
        print(f"Total input records      : {summary['total_input']}")
        print(f"Invalid records removed  : {summary['invalid']}")
        print(f"Filtered out by region       : {summary['filtered_by_region']}")
        print(f"Filtered out by amount       : {summary['filtered_by_amount']}")
        print(f"Final valid records      : {summary['final_count']}")
        
        #step5: analysing data
        print("------------------------------------------------")
        print("[5/10] Analysing sales data...")
        total_revenue = calculate_total_revenue(filtered_txns)
        print(f"\n → Total Revenue: {total_revenue:.2f}")
        print("\n → Region-wise sales analysis...")
        region_stats = region_wise_sales(filtered_txns)
        for region, stats in region_stats.items():
            print(
                f"  {region}: "
                f"  Total Sales = {stats['total_sales']:.2f}, "
                f"  Transactions = {stats['transaction_count']}, "
                f"  Percentage = {stats['percentage']}%"
            )   
        print("\n → Top selling products...")
        top_products = top_selling_products(filtered_txns, n=5)
        for name, qty, revenue in top_products:
            print(f"  {name}: Quantity Sold = {qty}, Revenue = {revenue:.2f}")
        print("\n → Customer analysis...")
        customer_stats = customer_analysis(filtered_txns)

        for cust_id, stats in customer_stats.items():
            print(
                f"  {cust_id}: "
                f"  Total Spent = {stats['total_spent']:.2f}, "
                f"  Orders = {stats['purchase_count']}, "
                f"  Avg Order = {stats['avg_order_value']:.2f}, "
                f"  Products = {', '.join(stats['products_bought'])}"
            )

        print("\n →  Daily sales trend...")
        daily_trends = daily_sales_trend(filtered_txns)
        for date, stats in daily_trends.items():
            print(
                f"  {date}: "
                f"  Revenue = {stats['revenue']:.2f}, "
                f"  Transactions = {stats['transaction_count']}, "
                f"  Unique Customers = {stats['unique_customers']}"
            )
        print("\n →  Peak sales day analysis...")
        date, revenue, count = find_peak_sales_day(filtered_txns)
        print(f"  Peak Sales Day: {date}")
        print(f"  Revenue: {revenue:.2f}")
        print(f"  Transactions: {count}")
        print("\n →  Low performing products analysis...")
        low_products = low_performing_products(filtered_txns, threshold=10)
        for name, qty, revenue in low_products:
            print(f"  {name}: Quantity Sold = {qty}, Revenue = {revenue:.2f}")
        print(f"✓ Analysis complete")
        
        print("------------------------------------------------")
        print("[6/10] Fetching product data from API...")
        products = fetch_all_products()

        if not products:
            print("✗ No products fetched. Cannot proceed to next step.")
            return  # or sys.exit(1)

        
        print("------------------------------------------------")
        print("[7/10] Enriching sales data...")
        # create product mapping if there are any products
        if products:
            product_map = create_product_mapping(products)
            print("  → Product mapping created")
        
        enriched_transactions = enrich_sales_data(
            filtered_txns,   # cleaned transaction list
            product_map
        )

        print(f"✓ Enriched {len(enriched_transactions)} of {len(filtered_txns)} transactions")

        print("------------------------------------------------")
        print("[9/10] Generating report...")
        generate_sales_report(
            transactions=filtered_txns,     
            enriched_transactions=enriched_transactions,
            output_file="output/sales_report.txt"
        )
        print("------------------------------------------------")
        print("[10/10] ✓ Process complete")

    except FileNotFoundError as e:
        print("    ✗ Unable to read sales data.")
        print(f"      Data file not found.{e.filename}")

    except Exception as e:
        print("    ✗ An unexpected error occurred.")
        print(f"      Details: {e}")
     
    
    
if __name__ == "__main__":
    main()
