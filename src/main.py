import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.ticker import MaxNLocator
from woocommerce import API
from datetime import datetime
import json

# Global Variables
g_current_year = datetime.now().year
g_background_color='#333333'
g_foreground_color='white'
g_data_start_year=2018
g_export_dir='../export/diagrams'

# Utility function to ensure export directory exists
def setup_directory_structure():
    if not os.path.exists(g_export_dir):
        os.makedirs(g_export_dir)

# Establishes a connection to the WooCommerce API
# For API reference see: https://woocommerce.github.io/woocommerce-rest-api-docs/#orders
def get_wc_api():
    load_dotenv()  # Load environment variables from .env

    wcapi = API(
        url=os.getenv("WC_API_URL"),  # store URL
        consumer_key=os.getenv("WC_API_CONSUMER_KEY"),  # consumer key
        consumer_secret=os.getenv("WC_API_CONSUMER_SECRET"),  # consumer secret
        wp_api=True,  # Enable the WP REST API integration
        version=os.getenv("WC_API_VERSION")  # WooCommerce API version
    )
    return wcapi

# Returns a wc_api table in a timeframe as a pandas DataFrame object
def get_dataframe(wc_api_object, wc_api_table_name="orders", iso8601_start_date=f"{g_current_year-1}-01-01T00:00:00", iso8601_end_date=f"{g_current_year+1}-01-01T00:00:00"):
    data = []
    page = 1
    per_page = 100
    # add all pages to data
    while True:
        response = wc_api_object.get(
            f"{wc_api_table_name}?after={iso8601_start_date}&before={iso8601_end_date}&per_page={per_page}&page={page}"
        ).json()
        # Check if data was loaded 
        if not response:
            print(f"No {wc_api_table_name} data received from the API.")
            return
        # Add result page to data
        data.extend(response)
        # If page is last page, exit loop
        if len(response) < per_page:
            break
        # Go to the next page
        page += 1
    # print(f"Retrieved {len(data)} {wc_api_table_name} from {iso8601_start_date} to {iso8601_end_date}.")
    return pd.DataFrame(data)

# Plots line charts for the input data
def plot_line_chart(data, x_data, x_label, y_label, title, legend_labels=None, colors=None, background_color='#333333', foreground_color='white', save_file=None, annotate=False):
    plt.figure(figsize=(12, 6), facecolor=background_color)
    plt.rcParams.update({
        'text.color': foreground_color,
        'axes.labelcolor': foreground_color,
        'axes.edgecolor': foreground_color,
        'xtick.color': foreground_color,
        'ytick.color': foreground_color,
        'figure.facecolor': background_color,
        'savefig.pad_inches': 0.1
    })
    ax = plt.gca()
    # Setting x-axis as a date axis
    ax.xaxis_date()  # interpret the x-axis data as dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # format the dates as 'Jan', 'Feb', etc.
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # locate ticks at the start of every month

    # If x_data is not a datetime index, convert it
    if not isinstance(x_data, pd.DatetimeIndex):
        x_data = pd.to_datetime(x_data)

    for i, y_data in enumerate(data):
        if colors and i < len(colors):  # Check if colors list is provided and has enough colors.
            color = colors[i]
        else:
            color = None
        # Check if legend_labels list is provided and has enough labels.
        if legend_labels and i < len(legend_labels): 
            label = legend_labels[i]
        else:
            label = None
        # Plotting the line chart
        plt.plot(x_data, y_data, label=label, color=color)

        if annotate:
            # Annotate each data point with its value
            for x, y in zip(x_data, y_data):
                ax.annotate(f'{y:.2f}', xy=(mdates.date2num(x), y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, color=foreground_color)

    # legend = plt.legend(loc='lower center', bbox_to_anchor=(0.75, -0.15), fancybox=False, facecolor=background_color)
    legend = plt.legend(loc='upper right', fancybox=False, facecolor=background_color)
    legend.get_frame().set_edgecolor(background_color)
    for text in legend.get_texts():
        text.set_color(foreground_color)

    plt.title(title, color=foreground_color)
    plt.xlabel(x_label, color=foreground_color)
    plt.ylabel(y_label, color=foreground_color)
    plt.setp(ax.get_xticklabels(), rotation=90, ha="right", color=foreground_color)
    ax.set_facecolor(background_color)
    plt.grid(True, color='gray', linewidth=0.2)
    plt.autoscale(tight=True)
    plt.setp(ax.get_yticklabels(), color=foreground_color)
    plt.tight_layout()

    if save_file:
        plt.savefig(save_file)
    plt.show()

#  Plots pie charts for the input data
def plot_pie_chart(data, title, category_labels, colors=None, background_color=g_background_color, foreground_color=g_foreground_color, save_file=None):
    plt.figure(figsize=(12, 6), facecolor=background_color)
    plt.rcParams.update({
        'text.color': foreground_color,
        'axes.facecolor': background_color,
        'savefig.facecolor': background_color,
        'savefig.edgecolor': background_color,
        'savefig.pad_inches': 0.1
    })

    # Generate a pie chart with the given data
    wedges, texts, autotexts = plt.pie(data, labels=category_labels, colors=colors, autopct='%1.1f%%', startangle=140)

    # Set the color of the pie chart texts
    for text in texts:
        text.set_color(foreground_color)
    for autotext in autotexts:
        autotext.set_color(background_color)  # Adjust this to foreground_color if it suits the visual better

    plt.title(title, color=foreground_color)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    if save_file:
        plt.savefig(save_file, facecolor=background_color)  # Save the figure with the specified background color
    plt.show()

# Plots bar charts for the input data
def plot_bar_chart(x_data, y_data, title, x_label, y_label, colors=None, background_color=g_background_color, foreground_color=g_foreground_color, save_file=None):
    plt.figure(figsize=(12, 6), facecolor=background_color)
    plt.rcParams.update({
        'text.color': foreground_color,
        'axes.labelcolor': foreground_color,
        'axes.edgecolor': foreground_color,
        'xtick.color': foreground_color,
        'ytick.color': foreground_color,
        'figure.facecolor': background_color,
        'savefig.pad_inches': 0.1
    })

    bars = plt.bar(x_data, y_data, color=colors if colors else 'lightgreen')

    # Get the current axes for setting their background color
    ax = plt.gca()
    ax.set_facecolor(background_color)  # Set the axes' background color

    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center', color=foreground_color)

    plt.title(title, color=foreground_color)
    plt.xlabel(x_label, color=foreground_color)
    plt.ylabel(y_label, color=foreground_color)
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability

    # Adjust layout to prevent labels from being cut off
    plt.tight_layout(pad=3.0)

    if save_file:
        plt.savefig(save_file)  # Save the figure with the specified background color
    plt.show()

# Plots the number of orders and the number of units sold during the specified year
def plot_orders_number_and_units_sold_for_single_year_line_chart(annotate=False, year=g_current_year,background_color=g_background_color,foreground_color=g_foreground_color, export_dir=g_export_dir):
    title=f"Bestellungen {year}"
    iso8601_date_start = f"{year}-01-01T00:00:00"
    iso8601_date_end = f"{year+1}-01-01T00:00:00"
    orders = get_dataframe(get_wc_api(),"orders",iso8601_date_start,iso8601_date_end)
    #  Convert 'date_created' to datetime 
    if not pd.api.types.is_datetime64_any_dtype(orders['date_created']):
        orders['date_created'] = pd.to_datetime(orders['date_created']) 
    # Extract the month and create a new 'month' column
    orders['month'] = orders['date_created'].dt.to_period('M')
    # Ensure we have the 'line_items' as a column containing list of dicts with 'quantity'
    if 'line_items' not in orders.columns:
        print("ERROR 'line_items' column missing")
        return
    # Extract the total items sold per order into a new column
    orders['total_items_sold'] = orders['line_items'].apply(lambda x: sum(item.get('quantity', 0) for item in x if isinstance(item, dict)))
    # Group by 'month' to get the number of orders and total units sold per month
    orders_per_month = orders.groupby('month').size()
    units_sold_per_month = orders.groupby('month')['total_items_sold'].sum()
    # Fill empty years by re-indexing
    all_months = pd.period_range(start=f'{year}-01', end=f'{year}-12', freq='M') # complete range of monthly periods for the year
    orders_per_month = orders_per_month.reindex(all_months, fill_value=0)
    units_sold_per_month = units_sold_per_month.reindex(all_months, fill_value=0)
    # Plot
    x_data = all_months.to_timestamp()

    # Plot
    plot_line_chart(
        x_data=x_data,  # Pass the correct x_data
        data=[orders_per_month, units_sold_per_month],
        x_label='Month',
        y_label='Count',
        title=title,
        legend_labels=['Number of Orders', 'Units Sold'],
        colors=['lightgreen', 'green'],
        background_color=background_color,
        foreground_color=foreground_color,
        save_file=f'{export_dir}/plot_orders_number_and_units_sold_for_single_year_line_chart_{year}.png',
        annotate=annotate
    )

# Plots the number of orders and the number of units sold during the specified year
def plot_orders_number_and_units_sold_for_all_time_line_chart(annotate=False, background_color=g_background_color,foreground_color=g_foreground_color, export_dir=g_export_dir):
    year = g_current_year
    title=f"Bestellungen {g_data_start_year} - {year}"
    iso8601_date_start = f"{g_data_start_year}-01-01T00:00:00"
    orders = get_dataframe(get_wc_api(),"orders",iso8601_date_start)
    #  Convert 'date_created' to datetime 
    if not pd.api.types.is_datetime64_any_dtype(orders['date_created']):
        orders['date_created'] = pd.to_datetime(orders['date_created']) 
    # Extract the month and create a new 'month' column
    orders['month'] = orders['date_created'].dt.to_period('M')
    # Create a new column that combines year and month for proper grouping
    orders['year_month'] = orders['date_created'].dt.to_period('M')
    # Ensure we have the 'line_items' as a column containing list of dicts with 'quantity'
    if 'line_items' not in orders.columns:
        print("ERROR 'line_items' column missing")
        return
    # Extract the total items sold per order into a new column
    orders['total_items_sold'] = orders['line_items'].apply(lambda x: sum(item.get('quantity', 0) for item in x if isinstance(item, dict)))
    orders_per_month = orders.groupby('year_month').size()
    units_sold_per_month = orders.groupby('year_month')['total_items_sold'].sum()
    # To reindex, we need to create a range that covers all months from 'iso8601_date_start' to the current year
    all_periods = pd.period_range(start=f'{iso8601_date_start}-01', end=f'{year}-12', freq='M')
    # Use the complete range of periods for reindexing
    orders_per_month = orders_per_month.reindex(all_periods, fill_value=0)
    units_sold_per_month = units_sold_per_month.reindex(all_periods, fill_value=0)
    x_data = all_periods.to_timestamp()
    
    # Plot
    plot_line_chart(
        x_data=x_data,
        data=[orders_per_month, units_sold_per_month],
        x_label='Month',
        y_label='Count',
        title=title,
        legend_labels=['Number of Orders', 'Units Sold'],
        colors=['lightgreen', 'green'],
        background_color=g_background_color,
        foreground_color=g_foreground_color,
        save_file=f'{g_export_dir}/plot_orders_number_and_units_sold_for_all_time_line_chart.png',
        annotate=annotate
    )

def clean_numeric_column(data_series):
    # Remove any unwanted characters that cannot be converted to float, for example:
    data_series = data_series.str.replace('$', '')  # Remove dollar signs
    data_series = data_series.str.replace(',', '')  # Remove commas
    # Add any other replacements needed based on your data's format

    # After cleaning, convert the series to numeric, coercing any errors into NaN (which will then be filled with zero)
    return pd.to_numeric(data_series, errors='coerce').fillna(0)

# TODO fix taxes
def plot_compare_revenue_to_previous_year_line_chart(annotate=False, year=g_current_year, background_color=g_background_color, foreground_color=g_foreground_color):
    # Fetch and process data for current year...
    current_year_orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year}-12-31T23:59:59")
    current_year_orders['date_created'] = pd.to_datetime(current_year_orders['date_created'])
    # Fetch and process data for previous year...
    previous_year_orders = get_dataframe(get_wc_api(), "orders", f"{year-1}-01-01T00:00:00", f"{year-1}-12-31T23:59:59")
    previous_year_orders['date_created'] = pd.to_datetime(previous_year_orders['date_created'])
    
    # Clean data for both years
    current_year_orders['total'] = clean_numeric_column(current_year_orders['total'])
    previous_year_orders['total'] = clean_numeric_column(previous_year_orders['total'])
    
    # Group data for both years
    current_year_gross_revenue = current_year_orders.groupby(current_year_orders['date_created'].dt.to_period('M'))['total'].sum().astype(float)    
    previous_year_gross_revenue = previous_year_orders.groupby(previous_year_orders['date_created'].dt.to_period('M'))['total'].sum().astype(float)
    
    # Create a list of all months for both years for indexing.
    all_months = pd.period_range(start=f'{year-1}-01', end=f'{year}-12', freq='M')

    # Create a DataFrame to capture the monthly data for each year
    comparison_df = pd.DataFrame(index=pd.period_range(start=f'{year-1}-01', end=f'{year}-12', freq='M'))

    # Assign revenue data to DataFrame using reindexing to ensure all months are present
    comparison_df[f'Gross Revenue {year}'] = current_year_gross_revenue.reindex(comparison_df.index, fill_value=0)
    comparison_df[f'Gross Revenue {year-1}'] = previous_year_gross_revenue.reindex(comparison_df.index, fill_value=0)

    # Prepare data for plotting
    comparison_df.index = comparison_df.index.to_timestamp()  # Convert to Timestamp for plotting

    # Extract only the common months for plotting (i.e., ignore the year)
    common_months_index = comparison_df.index[comparison_df.index.year == year]

    # Call the custom plot function with updated parameters
    plot_line_chart(
        x_data=common_months_index, 
        data=[
            comparison_df.loc[comparison_df.index.year == year-1, f'Gross Revenue {year-1}'].values,
            comparison_df.loc[comparison_df.index.year == year, f'Gross Revenue {year}'].values,
        ],
        x_label='Month',
        y_label='Revenue',
        title=f'Revenue Comparison: {year-1} vs. {year}',
        legend_labels=[f'Gross Revenue {year-1}', f'Gross Revenue {year}'],
        colors=['green', 'lightgreen'],
        background_color=g_background_color,
        foreground_color=g_foreground_color,
        save_file=f'{g_export_dir}/plot_revenue_comparison_{year}.png',
        annotate=annotate
    )

def fetch_product_categories(product_id, category_cache):
    wc_api = get_wc_api()
    # If we have already fetched this category, return it
    if product_id in category_cache:
        return category_cache[product_id]
    
    # Fetch the product details from the API to get the category
    product_details = wc_api.get(f"products/{product_id}").json()
    # This assumes 'categories' is a list of category details in the product details response
    categories = product_details.get('categories', [])
    # We'll store the list of category names in the cache
    category_names = [category.get('name') for category in categories]
    category_cache[product_id] = category_names
    return category_names

def plot_sales_by_category_pie_chart(year=g_current_year, save_file=None):
    # Initialize a cache for product categories to avoid repeated API calls
    category_cache = {}

    # Fetch order data for the year
    orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year+1}-01-01T00:00:00")
    
    # Check if line_items column is present
    if 'line_items' not in orders.columns:
        print("ERROR 'line_items' column missing")
        return

    # Extract categories and calculate the total sales per category
    category_sales = []

    # Loop through each order's line_items
    for index, row in orders.iterrows():
        for item in row['line_items']:
            # Fetch the categories for the given product_id
            categories = fetch_product_categories(item['product_id'], category_cache)
            for category_name in categories:
                # Append the category and sales to the list
                category_sales.append((category_name, float(item['price']) * item['quantity']))

    # Convert to DataFrame
    category_df = pd.DataFrame(category_sales, columns=['Category', 'Sales'])
    # Group by 'Category' and sum 'Sales'
    category_sales_summary = category_df.groupby('Category')['Sales'].sum()
    # Plot
    plot_pie_chart(
        data=category_sales_summary.values,
        title=f'Sales by Category for {year}',
        category_labels=category_sales_summary.index.tolist(),
        colors=['gold', 'yellowgreen', 'lightcoral'],
        save_file=f'{g_export_dir}/plot_sales_by_category_pie_chart_{year}.png'
    )

def plot_customer_type_pie_chart(year=g_current_year, background_color=g_background_color, foreground_color=g_foreground_color):
    # Fetch order data for the specified year
    current_year_orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year+1}-01-01T00:00:00")

    # Determine unique customer IDs for the year
    current_year_customers = set(current_year_orders['customer_id'].unique())

    # Fetch order data prior to the specified year to determine returning customers
    previous_orders = get_dataframe(get_wc_api(), "orders", "2018-01-01T00:00:00", f"{year}-01-01T00:00:00")
    previous_customers = set(previous_orders['customer_id'].unique())

    # Classify customers as new or returning
    new_customers = current_year_customers - previous_customers
    returning_customers = current_year_customers & previous_customers

    # Count the number of new and returning customers
    num_new = len(new_customers)
    num_returning = len(returning_customers)

    # Data for pie chart
    sizes = [num_returning, num_new]
    # Update labels with customer counts
    labels = [f'Returning Customers ({num_returning})', f'New Customers ({num_new})']
    colors = ['lightblue', 'lightgreen']  # Choose colors that fit the chart's color scheme

    # Use the plot_pie_chart function
    plot_pie_chart(
        data=sizes,
        title=f"New VS Returning Customers in {year}",
        category_labels=labels,
        colors=colors,
        background_color=background_color,
        foreground_color=foreground_color,
        save_file=f'{g_export_dir}/plot_customer_types_{year}.png'  # Pass the path to save the file or None to just show the chart
    )

def plot_top_products_bar_chart(year=g_current_year, background_color=g_background_color, foreground_color=g_foreground_color):
    # Fetch order data for the year 2023
    orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year+1}-01-01T00:00:00")

    # Aggregate data to get the total quantity sold per product
    # This assumes you have a 'line_items' column which is a list of items, where each item is a dict that contains 'product_id' and 'quantity'
    product_sales = {}
    for index, row in orders.iterrows():
        for item in row['line_items']:
            # Here 'name' is used as a unique identifier for each product; replace with 'product_id' if using IDs
            product_name = item['name']  
            quantity = item['quantity']
            
            if product_name in product_sales:
                product_sales[product_name] += quantity
            else:
                product_sales[product_name] = quantity

    # Sort the products by the total quantity sold and get the top 5
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]

    # Prepare data for plotting
    product_names = [product[0] for product in top_products]
    quantities_sold = [product[1] for product in top_products]
    # Plot
    plot_bar_chart(
        x_data=product_names,
        y_data=quantities_sold,
        title="Top 5 Bestselling Products of 2023",
        x_label="Product Name",
        y_label="Units Sold",
        colors=['lightgreen', 'green', 'green', 'green', 'green'],
        background_color=background_color,
        foreground_color=foreground_color,
        save_file=f'{g_export_dir}/plot_top_5_products_{year}.png'  # Replace with your actual save file path
    )

# TODO Fix formula
def plot_financials_line_chart(year=g_current_year, background_color=g_background_color, foreground_color=g_foreground_color):
    # Fetch order data for the year 2023
    orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year+1}-01-01T00:00:00")
    
    # Calculate Revenue, Market Revenue, and Margin
    # This is a placeholder example where 'total' is revenue and 'cost' needs to be provided
    # You may need to adjust this to reflect your actual data and financial calculations
    orders['total'] = pd.to_numeric(orders['total'], errors='coerce').fillna(0)
    # TODO calculate cost & margin
    # orders['cost']= ...
    # orders['margin'] = orders['total'] - orders['cost'] # Add a 'margin' column
    orders['margin'] = orders['total'] # Margin Placeholder

    # Summarize data by month
    orders['date_created'] = pd.to_datetime(orders['date_created'])
    orders['month'] = orders['date_created'].dt.to_period('M')
    monthly_financials = orders.groupby('month').agg({
        'total': 'sum',
        'margin': 'sum'
    }).rename(columns={'total': 'Revenue', 'margin': 'Margin'})

    # Plot the financial data
    x_data = monthly_financials.index.to_timestamp()  # Convert PeriodIndex to Timestamp for plotting
    plot_line_chart(
        x_data=x_data,
        data=[monthly_financials['Revenue'], monthly_financials['Margin']],  # Add Market Revenue if available
        x_label='Month',
        y_label='Amount',
        title=f"Financial Overview (Calculate Revenue, Market Revenue, and Margin) for {year}",
        legend_labels=['Revenue', 'Margin'],  # Add 'Market Revenue' label if you have this data
        colors=['green', 'red'],  # Choose appropriate colors
        background_color=background_color,
        foreground_color=foreground_color,
        save_file=f'{g_export_dir}/plot_financial_overview_{year}.png'
    )

def plot_product_revenue_bar_chart(year=g_current_year, background_color=g_background_color, foreground_color=g_foreground_color, export_dir=g_export_dir):
    # Fetch order data for the specified year
    orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year+1}-01-01T00:00:00")

    # Aggregate the total revenue per product
    product_revenue = {}
    for index, order in orders.iterrows():
        for item in order['line_items']:
            product_name = item['name']  # Assuming each item dict has 'name' and 'total' keys
            product_total = float(item['total'])  # Convert the total to float

            if product_name in product_revenue:
                product_revenue[product_name] += product_total
            else:
                product_revenue[product_name] = product_total

    # Sort products by total revenue and prepare data for plotting
    sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)  # Sort by revenue in descending order
    product_names, revenues = zip(*sorted_products)  # Unzip into two separate lists for plotting

    # Plot the bar chart using a custom function
    plot_bar_chart(
        x_data=product_names,
        y_data=revenues,
        title="Product Revenue Comparison 2023",
        x_label="Product",
        y_label="Revenue",
        background_color=background_color,
        foreground_color=foreground_color,
        save_file=f"{export_dir}/plot_product_revenue_comparison_{year}.png"
    )

def plot_product_revenue_line_chart(year=g_current_year, background_color=g_background_color, foreground_color=g_foreground_color, export_dir=g_export_dir):
    # Fetch order data for the specified year
    orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year+1}-01-01T00:00:00")

    # Ensure 'date_created' is a datetime type
    orders['date_created'] = pd.to_datetime(orders['date_created'])

    # Initialize list to store monthly revenue data
    monthly_revenue_list = []

    # Collect revenue data
    for index, order in orders.iterrows():
        for item in order['line_items']:
            monthly_revenue_list.append({
                'date': order['date_created'].to_period('M').start_time, # Use start_time to convert to timestamp
                'product_name': item['name'],  # or item['product_id'] if you prefer to use product IDs
                'revenue': float(item['total'])  # Convert the total to float
            })

    # Convert list to DataFrame
    monthly_revenue = pd.DataFrame(monthly_revenue_list)

    # Group by product and date and sum revenue
    monthly_revenue_grouped = monthly_revenue.groupby(['date', 'product_name'])['revenue'].sum().reset_index()

    # Pivot the grouped DataFrame to have one column per product
    monthly_revenue_pivoted = monthly_revenue_grouped.pivot(index='date', columns='product_name', values='revenue').fillna(0)

    # Plotting each product's revenue over time using the custom plot function
    # Generate a list of data for each product
    product_data = [monthly_revenue_pivoted[product].values for product in monthly_revenue_pivoted.columns]

    # Generate a list of product names for the legend
    product_names = monthly_revenue_pivoted.columns.tolist()

    # Plot using the plot_line_chart function
    plot_line_chart(
        x_data=monthly_revenue_pivoted.index,
        data=product_data,
        x_label='Month',
        y_label='Revenue',
        title=f"Monthly Revenue per Product in {year}",
        legend_labels=product_names,
        colors=None,  # You can specify colors or leave it to use default colors
        background_color=background_color,
        foreground_color=foreground_color,
        save_file=f"{export_dir}/plot_product_revenue_line_chart_{year}.png",
        # annotate=True  # Set to True to annotate data points
    )

def plot_payment_method_usage(year=g_current_year, background_color=g_background_color, foreground_color=g_foreground_color, export_dir=g_export_dir):
    # Fetch order data for the specified year, including payment method
    orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year+1}-01-01T00:00:00")
    # Ensure 'date_created' and 'payment_method_title' are available
    orders['date_created'] = pd.to_datetime(orders['date_created'])
    orders['month'] = orders['date_created'].dt.to_period('M')
    # Group by month and payment method
    payment_method_data = orders.groupby(['month', 'payment_method_title']).size().unstack(fill_value=0)
    # Convert PeriodIndex to Timestamp for plotting
    x_data = payment_method_data.index.to_timestamp()
    # Plot each payment method's usage over time using the custom plot function
    # Generate a list of data for each payment method
    payment_method_series = [payment_method_data[method] for method in payment_method_data.columns]
    # Generate a list of payment method names for the legend
    payment_methods = payment_method_data.columns.tolist()
    # Call the custom plot_line_chart function
    plot_line_chart(
        x_data=x_data,
        data=payment_method_series,
        x_label='Month',
        y_label='Number of Uses',
        title=f"Payment Method Usage in {year}",
        legend_labels=payment_methods,
        background_color=background_color,
        foreground_color=foreground_color,
        save_file=f"{export_dir}/plot_payment_method_usage_{year}.png"
    )

def plot_payment_method_ranking(year=g_current_year, background_color=g_background_color, foreground_color=g_foreground_color, export_dir=g_export_dir):
    # Fetch order data for the specified year, including payment method
    orders = get_dataframe(get_wc_api(), "orders", f"{year}-01-01T00:00:00", f"{year+1}-01-01T00:00:00")
    # Assuming 'payment_method_title' is the column with payment method information
    payment_method_counts = orders['payment_method_title'].value_counts()
    # Sort the payment methods by count in descending order
    payment_method_counts_sorted = payment_method_counts.sort_values(ascending=False)
    # Prepare data for the bar chart
    payment_methods = payment_method_counts_sorted.index
    counts = payment_method_counts_sorted.values
    # Plot the bar chart using a custom function
    plot_bar_chart(
        x_data=payment_methods,
        y_data=counts,
        title="Payment Method Ranking 2023",
        x_label="Payment Method",
        y_label="Total Uses",
        background_color=background_color,
        foreground_color=foreground_color,
        save_file=f"{export_dir}/plot_payment_method_ranking_{year}.png"
    )

# -- START Main program --
# Main program flow
def main():
    setup_directory_structure()
    # plot_orders_number_and_units_sold_for_all_time_line_chart()
    # plot_orders_number_and_units_sold_for_single_year_line_chart(True)
    # plot_compare_revenue_to_previous_year_line_chart(True)
    # plot_sales_by_category_pie_chart()
    # plot_customer_type_pie_chart()
    # plot_top_products_bar_chart()

    # plot_financials_line_chart() #TODO Fix formula
    
    # plot_product_revenue_bar_chart()
    # plot_product_revenue_line_chart()
    # plot_payment_method_usage()
    plot_payment_method_ranking()

if __name__ == "__main__":
    main()
# -- END Main program --