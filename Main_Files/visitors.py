import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from folium.plugins import Fullscreen
from geopy.geocoders import ArcGIS
from streamlit_folium import folium_static
import time
from functions import load_data, plot_data, plot_data_for_industry, plot_visitors_metrics, add_annotations
from constant import industry_grouping

# Function to calculate view counts by company size
def calculate_view_counts_by_company_size(xls):
    view_counts_by_company_size = {}
    # Check if 'Company size' and 'Total views' columns exist in the data
    if 'Company size' in xls.columns and 'Total views' in xls.columns:
        # Group by 'Company size' and sum the 'Total views' for each size
        size_view_counts = xls.groupby('Company size')['Total views'].sum().to_dict()
        for size, count in size_view_counts.items():
            view_counts_by_company_size[size] = view_counts_by_company_size.get(size, 0) + count
            return view_counts_by_company_size
        

# Function to calculate view counts by industry
def calculate_view_counts_by_industry(df):
    grouped_views = df.groupby('Industry Group')['Total views'].sum()
    sorted_data = grouped_views.sort_values(ascending=True).reset_index()
    return sorted_data
            
# Function to process data and add 'Industry Group' column based on the industry grouping dictionary
def process_data(df, industry_grouping):
    df['Industry Group'] = df['Industry'].apply(lambda x: next((key for key, value in industry_grouping.items() if x in value), 'Other Services'))

# Function to calculate view counts by job function
def calculate_view_counts_by_job_function(xls):
    # Dictionary to store view counts for each job function
    view_counts_by_job_function = {}
    # Iterate through each sheet in the Excel file
    for sheet_name in xls.sheet_names:
        # Read the sheet into a DataFrame
        df = pd.read_excel(xls, sheet_name, header=0)
        # Check if 'Job function' and 'Total views' columns are present in the DataFrame
        if 'Job function' in df.columns and 'Total views' in df.columns:
            # Group the DataFrame by 'Job function' and sum the 'Total views' for each group
            job_function_view_counts = df.groupby('Job function')['Total views'].sum().to_dict()
            # Update the overall dictionary with view counts for each job function
            for job_function, count in job_function_view_counts.items():
                view_counts_by_job_function[job_function] = view_counts_by_job_function.get(job_function, 0) + count
    return view_counts_by_job_function

# Function to get latitude and longitude for a location
def get_lat_long(location, geolocator):
    try:
        location_info = geolocator.geocode(location)
        if location_info:
            lat, lon = location_info.latitude, location_info.longitude
            return lat, lon
        else:
            return None, None
    except Exception as e:
            print(f"Error geocoding {location}: {e}")
            return None, None

# Function to create folium map
def create_folium_map(df, map_center):
                # Create a folium map
                mymap = folium.Map(location=map_center, zoom_start=12)

                # Add markers to the map based on the data in the DataFrame
                for index, row in df.iterrows():
                    folium.Marker([row['Latitude'], row['Longitude']], popup=f"{row['Location']} - {row['Total views']} views").add_to(mymap)

                # Add fullscreen option
                Fullscreen().add_to(mymap)

                return mymap

# Function to calculate view counts by seniority
def calculate_view_counts_by_seniority(df):
    # Dictionary to store view counts for each seniority level
    view_counts_by_seniority = {}

    # Check if 'Seniority' and 'Total views' columns are present in the DataFrame
    if 'Seniority' in df.columns and 'Total views' in df.columns:
        # Group the DataFrame by 'Seniority' and sum the 'Total views' for each group
        seniority_view_counts = df.groupby('Seniority')['Total views'].sum().to_dict()

        # Update the overall dictionary with view counts for each seniority level
        for seniority, count in seniority_view_counts.items():
            view_counts_by_seniority[seniority] = view_counts_by_seniority.get(seniority, 0) + count

        return view_counts_by_seniority




def process_views_data(uploaded_file):

    # File upload system for Followers Data
    #uploaded_file = st.file_uploader(f"Upload an Excel file", type=["xls", "xlsx"])
    selected_option = st.radio("Select Option", ["Visitors Company Size", "Visitors Industry", "Visitors Job Function", "Visitors Location", "Visitors Seniority", "New Visitors"])

    if uploaded_file is not None:
            
        if selected_option == "Visitors Company Size":
            # Load data for company size from the uploaded file
            xls_company_size = load_data(uploaded_file, sheet_name="Company size")
            # Define a custom order for company sizes
            custom_order = ['1', '2-10', '11-50', '51-200', '201-500', '501-1000', '1001-5000', '5001-10000', '10001+']

            # Check if 'Company size' column exists and has the first value from custom_order
            if 'Company size' in xls_company_size.columns and custom_order[0] in xls_company_size['Company size'].values:
                # Get the view count for the first value in custom_order
                first_value_views = xls_company_size.loc[xls_company_size['Company size'] == custom_order[0], 'Total views'].values[0]
                # Create a custom_order_map with the first value as the first bar
                custom_order_map = {custom_order[0]: first_value_views}

                # Iterate through the rest of the custom_order and assign views accordingly
                for size in sorted(xls_company_size['Company size'].unique(), key=lambda x: (custom_order.index(x), x)):
                    if size not in custom_order_map:
                        views = xls_company_size.loc[xls_company_size['Company size'] == size, 'Total views'].sum()
                        custom_order_map[size] = views

                # Convert 'Company size' to categorical with the custom order
                xls_company_size['Company size'] = pd.Categorical(xls_company_size['Company size'], categories=custom_order, ordered=True)

                # Calculate view counts by company size and get sorted data for plotting
                view_counts_by_company_size = calculate_view_counts_by_company_size(xls_company_size)
                sorted_data_company_size = sorted(custom_order_map.items(), key=lambda x: custom_order.index(x[0]))

                # Ensure 'Total views' is treated as numeric before plotting
                xls_company_size['Total views'] = pd.to_numeric(xls_company_size['Total views'], errors='coerce')
                
                # Plot total view counts by company size
                plot_data(sorted_data_company_size,
                        x_label='Total Views',
                        y_label='Company Size',
                        title='Total View Counts by Company Size')


        elif selected_option == "Visitors Industry":
            df_visitors = load_data(uploaded_file, sheet_name="Industry")
            process_data(df_visitors, industry_grouping)
            sorted_data_industry = calculate_view_counts_by_industry(df_visitors)
            plot_data_for_industry(sorted_data_industry,
                                    x_column='Total views',
                                    y_column='Industry Group',
                                    title='Grouped Industries with Total Views')
            # Display industry grouping
            st.write("Industry Grouping:")
            for main_category, subcategories in industry_grouping.items():
                st.write(f"{main_category}: {', '.join(subcategories)}")




        elif selected_option == "Visitors Job Function":
            # Load the Excel file for visitors
            xls_visitors = pd.ExcelFile(uploaded_file)
            # Calculate view counts by job function
            view_counts_by_job_function = calculate_view_counts_by_job_function(xls_visitors)
            # Sort the data in decreasing order of view counts
            sorted_data_job_function = sorted(view_counts_by_job_function.items(), key=lambda x: x[1], reverse=False)

            # Plot total view counts by job function
            plot_data(sorted_data_job_function, 
                    x_label='Total Views',
                    y_label='Job function',
                    title='Total View Counts by Job Function')


                                  
        elif selected_option == "Visitors Location":
            # Add a spinner at the beginning
            with st.spinner('Loading.....It may take up to 2 minutes to finish'):
                time.sleep(1)  # Add a small delay to display the initial spinner

                # Load data from the uploaded file with the correct sheet name
                df = load_data(uploaded_file, sheet_name="Location")

                # Create a geocoder using ArcGIS
                geolocator = ArcGIS()

                # Add latitude and longitude columns to the DataFrame
                df['Latitude'], df['Longitude'] = zip(*df['Location'].apply(lambda x: get_lat_long(x, geolocator)))

                # Filter out rows with missing Latitude or Longitude values
                df = df.dropna(subset=['Latitude', 'Longitude'])

                # Create a folium map centered at a specific location
                map_center = [df['Latitude'].mean(), df['Longitude'].mean()]

                # Add a spinner while the map is loading
                with st.spinner('Loading Map...'):
                # Create folium map using the function
                    mymap = create_folium_map(df, map_center)

                    # Display the map using Streamlit
                    folium_static(mymap)

                    # Stop the outer spinner when the map is ready
                    st.success('Map Loaded!')


        elif selected_option == "Visitors Seniority":
            # Load the Excel file for visitors
            xls_visitors = load_data(uploaded_file, sheet_name="Seniority")

            # Calculate view counts by seniority
            view_counts_by_seniority = calculate_view_counts_by_seniority(xls_visitors)

            # Sort the data in decreasing order of view counts
            sorted_data_seniority = sorted(view_counts_by_seniority.items(), key=lambda x: x[1], reverse=False)

            # Plot total view counts by seniority
            plot_data(sorted_data_seniority,
                        x_label='Total Views',
                        y_label='Seniority',
                        title='Total View Counts by Seniority')

            
        elif selected_option == "New Visitors":
            def load_and_plot_visitors_data(file_uploader, sheet_name):

                # Load the Excel file
                xls = pd.ExcelFile(uploaded_file)

                # Read the data from the Excel file
                df = pd.read_excel(xls, sheet_name=sheet_name, header=0)

                # Use the 'Date' column as the x-axis
                dates = df['Date']

                # Page Views
                page_views_columns = ['Overview page views (total)', 'Total page views (total)', 'Jobs page views (total)', 'Life page views (total)']
                plot_visitors_metrics(df, 'Date', page_views_columns, 'Total Data of Page Views by Date')

                # Unique Visitors
                unique_visitors_columns = ['Overview unique visitors (total)', 'Total unique visitors (total)', 'Jobs unique visitors (total)', 'Life unique visitors (total)']
                plot_visitors_metrics(df, 'Date', unique_visitors_columns, 'Total Data of Unique Visitors by Date')

            # Example usage
            load_and_plot_visitors_data("Upload a Visitors Excel file", sheet_name="Visitor metrics")


