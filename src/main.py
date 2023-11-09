import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.ticker import MaxNLocator
from woocommerce import API
from datetime import datetime

# Utility function to ensure export directory exists
def setup_directory_structure():
    if not os.path.exists('../export/diagrams'):
        os.makedirs('../export/diagrams')

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

# Plots the number of orders and the number of units sold during the specified year
def plot_orders_number_and_units_sold_for_single_year_line_chart(year=2023,background_color='#333333',foreground_color='white'):
    title=f"Bestellungen {year}"
    year_after=year
    year_before=year+1
    date_after = f"{year_after}-01-01T00:00:00" # The first day of the year
    date_before = f"{year_before}-01-01T00:00:00" 
    # Get orders data from API
    load_dotenv() # Load environment variables from .env
    wcapi = API(
        url=os.getenv("WC_API_URL"), # store URL
        consumer_key=os.getenv("WC_API_CONSUMER_KEY"), # consumer key
        consumer_secret=os.getenv("WC_API_CONSUMER_SECRET"), # consumer secret
        wp_api=True, # Enable the WP REST API integration
        version=os.getenv("WC_API_VERSION") # WooCommerce API version
    )
    orders_data = []
    page = 1
    per_page = 100  # Adjust as needed, up to the maximum limit
    # Get all API result pages and combine
    while True:
        response = wcapi.get(f"orders?after={date_after}&before={date_before}&per_page={per_page}&page={page}").json()
        if not response:
            print("No orders data received from the API.")
            return
        orders_data.extend(response)
        if len(response) < per_page: # If the number of orders returned is less than 'per_page', it's the last page
            break
        page += 1 # Increment the page number to get the next set of results
    print(f"Retrieved {len(orders_data)} orders for year {year}.") # Debug log
    orders = pd.DataFrame(orders_data) # Convert to Pandas DataFrame
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
    plt.figure(figsize=(12, 6),facecolor=background_color) # Create plot canvas
    plt.rcParams.update({
        'text.color': foreground_color,
        'axes.labelcolor': foreground_color,
        'axes.edgecolor': foreground_color,
        'xtick.color': foreground_color,
        'ytick.color': foreground_color,
        'figure.facecolor': background_color, # Set the outer color
        'savefig.pad_inches': 0.1
    })
    ax = plt.gca() # Get the current Axes instance on the current figure matching the given keyword args, or create one.
    # Create plots
    orders_per_month.plot(ax=ax, kind='line', label='Number of Orders', linestyle='dashed', color='lightgreen') # Plotting the number of orders per month
    units_sold_per_month.plot(ax=ax, kind='line', label='Units Sold', color='green') # Plotting the number of units sold per month
    # Plot styling
    legend = plt.legend(loc='lower center', bbox_to_anchor=(0.75, -0.15), fancybox=False, facecolor=background_color)
    legend.get_frame().set_edgecolor(background_color)
    for text in legend.get_texts():
        text.set_color(foreground_color)
    plt.title(title, color=foreground_color)
    plt.xlabel('Month', color=foreground_color)
    plt.ylabel('Count', color=foreground_color)
    plt.setp(ax.get_xticklabels(), rotation=90, ha="right", color=foreground_color)
    ax.set_facecolor(background_color) # Set the background color of the plot area to black
    plt.grid(True, color='gray',linewidth=0.2)
    plt.autoscale(tight=True)
    plt.setp(ax.get_yticklabels(), color=foreground_color)
    plt.tight_layout()
    # Draw plots
    plt.savefig('orders_and_units_sold_per_month.png') # Save the plot as a diagram
    plt.show() # Display the plot

# Plots the number of orders and the number of units sold during the specified year
def plot_orders_number_and_units_sold_for_all_time_line_chart(background_color='#333333',foreground_color='white'):
    year = datetime.now().year
    year_after=2018
    title=f"Bestellungen {year_after} - {year}"
    date_after = f"{year_after}-01-01T00:00:00" # The first day of the year
    # Get orders data from API
    load_dotenv() # Load environment variables from .env
    wcapi = API(
        url=os.getenv("WC_API_URL"), # store URL
        consumer_key=os.getenv("WC_API_CONSUMER_KEY"), # consumer key
        consumer_secret=os.getenv("WC_API_CONSUMER_SECRET"), # consumer secret
        wp_api=True, # Enable the WP REST API integration
        version=os.getenv("WC_API_VERSION") # WooCommerce API version
    )
    orders_data = []
    page = 1
    per_page = 100  # Adjust as needed, up to the maximum limit
    # Get all API result pages and combine
    while True:
        response = wcapi.get(f"orders?after={date_after}&per_page={per_page}&page={page}").json()
        if not response:
            print("No orders data received from the API.")
            return
        orders_data.extend(response)
        if len(response) < per_page: # If the number of orders returned is less than 'per_page', it's the last page
            break
        page += 1 # Increment the page number to get the next set of results
    print(f"Retrieved {len(orders_data)} orders from {year_after} year {year}.") # Debug log
    orders = pd.DataFrame(orders_data) # Convert to Pandas DataFrame
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

    # To reindex, we need to create a range that covers all months from 'year_after' to the current year
    all_periods = pd.period_range(start=f'{year_after}-01', end=f'{year}-12', freq='M')

    # Use the complete range of periods for reindexing
    orders_per_month = orders_per_month.reindex(all_periods, fill_value=0)
    units_sold_per_month = units_sold_per_month.reindex(all_periods, fill_value=0)

    plt.figure(figsize=(12, 6),facecolor=background_color) # Create plot canvas
    plt.rcParams.update({
        'text.color': foreground_color,
        'axes.labelcolor': foreground_color,
        'axes.edgecolor': foreground_color,
        'xtick.color': foreground_color,
        'ytick.color': foreground_color,
        'figure.facecolor': background_color, # Set the outer color
        'savefig.pad_inches': 0.1
    })
    ax = plt.gca() # Get the current Axes instance on the current figure matching the given keyword args, or create one.
    # Create plots
    orders_per_month.plot(ax=ax, kind='line', label='Number of Orders', linestyle='dashed', color='lightgreen') # Plotting the number of orders per month
    units_sold_per_month.plot(ax=ax, kind='line', label='Units Sold', color='green') # Plotting the number of units sold per month
    # Plot styling
    legend = plt.legend(loc='lower center', bbox_to_anchor=(0.75, -0.15), fancybox=False, facecolor=background_color)
    legend.get_frame().set_edgecolor(background_color)
    for text in legend.get_texts():
        text.set_color(foreground_color)
    plt.title(title, color=foreground_color)
    plt.xlabel('Month', color=foreground_color)
    plt.ylabel('Count', color=foreground_color)
    plt.setp(ax.get_xticklabels(), rotation=90, ha="right", color=foreground_color)
    ax.set_facecolor(background_color) # Set the background color of the plot area to black
    plt.grid(True, color='gray',linewidth=0.2)
    plt.autoscale(tight=True)
    plt.setp(ax.get_yticklabels(), color=foreground_color)
    plt.tight_layout()
    # Draw plots
    plt.savefig('orders_and_units_sold_per_month.png') # Save the plot as a diagram
    plt.show() # Display the plot

# -- START Main program --
# Main program flow
def main():
    # setup_directory_structure()
    plot_orders_number_and_units_sold_for_single_year_line_chart()
    # plot_orders_number_and_units_sold_for_all_time_line_chart()

if __name__ == "__main__":
    main()
# -- END Main program --