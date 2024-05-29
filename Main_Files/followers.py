import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from folium.plugins import Fullscreen
from geopy.geocoders import ArcGIS
from streamlit_folium import folium_static
import time
from functions import load_data, plot_data, plot_data_for_industry, plot_new_followers
from constant import industry_grouping

def calculate_follower_counts_by_company_size(xls):
                    follower_counts_by_company_size = {}
                    if 'Company size' in xls.columns and 'Total followers' in xls.columns:
                        size_follower_counts = xls.groupby('Company size')['Total followers'].sum().to_dict()
                        for size, count in size_follower_counts.items():
                            follower_counts_by_company_size[size] = follower_counts_by_company_size.get(size, 0) + count
                    return follower_counts_by_company_size

# Function to calculate Followers counts by industry
def calculate_follower_counts_by_industry(df):
    grouped_followers = df.groupby('Industry Group')['Total followers'].sum()
    sorted_data = grouped_followers.sort_values(ascending=True).reset_index()
    return sorted_data

# Function to process data and add 'Industry Group' column based on the industry grouping dictionary
def process_data(df, industry_grouping):
    df['Industry Group'] = df['Industry'].apply(lambda x: next((key for key, value in industry_grouping.items() if x in value), 'Other Services'))

def calculate_follower_counts_by_job_function(xls):
                        follower_counts_by_job_function = {}

                        for sheet_name in xls.sheet_names:
                            df = pd.read_excel(xls, sheet_name, header=0)
                            if 'Job function' in df.columns and 'Total followers' in df.columns:
                                job_function_follower_counts = df.groupby('Job function')['Total followers'].sum().to_dict()
                                for job_function, count in job_function_follower_counts.items():
                                    follower_counts_by_job_function[job_function] = follower_counts_by_job_function.get(job_function, 0) + count

                        return follower_counts_by_job_function

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
        folium.Marker([row['Latitude'], row['Longitude']], popup=f"{row['Location']} - {row['Total followers']} followers").add_to(mymap)
    # Add fullscreen option
    Fullscreen().add_to(mymap)
    return mymap

# Define the function outside the process_followers_data function
def calculate_follower_counts_by_seniority(df):
    follower_counts_by_seniority = {}

    if 'Seniority' in df.columns and 'Total followers' in df.columns:
        seniority_follower_counts = df.groupby('Seniority')['Total followers'].sum().to_dict()
        for seniority, count in seniority_follower_counts.items():
            follower_counts_by_seniority[seniority] = follower_counts_by_seniority.get(seniority, 0) + count

    return follower_counts_by_seniority

        

def process_new_followers(df):
    if 'Date' in df.columns and ('Sponsored followers' in df.columns or 'Organic followers' in df.columns):
        df_selected = df[['Date', 'Sponsored followers', 'Organic followers']]
        df_melted = pd.melt(df_selected, id_vars=['Date'], var_name='Metric', value_name='Count')
        return df_melted
    else:
        st.warning("The 'Date' column and at least one of 'Sponsored followers' or 'Organic followers' columns are required.")
        return None


####//////main function\\\\\\########
def process_followers_data(uploaded_file):
    selected_option = st.radio("Select Option", ["Followers Company Size", "Followers Industry", "Followers Job Function", "Followers Location", "Followers Seniority", "New Followers"])
    if uploaded_file is not None:
 #first sub-section           
            if selected_option == "Followers Company Size":
                xls = load_data(uploaded_file , sheet_name="Company size")
                calculate_follower_counts_by_company_size(xls)
                xls_company_size = xls
                custom_order = ['1', '2-10', '11-50', '51-200', '201-500', '501-1000', '1001-5000', '5001-10000', '10001+']

                # Check if custom_order exists and has the first value from 'Company size' column
                if 'Company size' in xls_company_size.columns and custom_order[0] in xls_company_size['Company size'].values:
                    # Get the followers count for the first value in custom_order
                    first_value_followers = xls_company_size.loc[xls_company_size['Company size'] == custom_order[0], 'Total followers'].values[0]
                    # Create a custom_order_map with the first value as the first bar
                    custom_order_map = {custom_order[0]: first_value_followers}
                    # Iterate through the rest of the custom_order and assign followers accordingly
                    for size in sorted(xls_company_size['Company size'].unique(), key=lambda x: (custom_order.index(x), x)):
                        if size not in custom_order_map:
                            followers = xls_company_size.loc[xls_company_size['Company size'] == size, 'Total followers'].sum()
                            custom_order_map[size] = followers

                    # Convert 'Company size' to categorical with the custom order
                    xls_company_size['Company size'] = pd.Categorical(xls_company_size['Company size'], categories=custom_order, ordered=True)
                    follower_counts_by_company_size = calculate_follower_counts_by_company_size(xls_company_size)
                    sorted_data_company_size = sorted(custom_order_map.items(), key=lambda x: custom_order.index(x[0]))
                    # Ensure 'Total followers' is treated as numeric before plotting
                    xls_company_size['Total followers'] = pd.to_numeric(xls_company_size['Total followers'], errors='coerce')
                    plot_data(sorted_data_company_size,
                            x_label='Total Followers',
                            y_label='Company Size',
                            title='Total Follower Counts by Company Size')
#second sub-section     
            elif selected_option == "Followers Industry":

                df_followers = load_data(uploaded_file, sheet_name="Industry")
                process_data(df_followers, industry_grouping)
                sorted_data_industry = calculate_follower_counts_by_industry(df_followers)

                # Use the plot_data_for_industry function to plot the data
                plot_data_for_industry(
                    sorted_data_industry,
                    x_column='Total followers',  # Specify the correct column name
                    y_column='Industry Group',
                    title='Grouped Industries with Total Followers'
                )
                # Display industry grouping
                st.write("Industry Grouping:")
                for main_category, subcategories in industry_grouping.items():
                    st.write(f"{main_category}: {', '.join(subcategories)}")
#third sub-section     
            elif selected_option == "Followers Job Function":
                    xls = pd.ExcelFile(uploaded_file)
                    follower_counts_by_job_function = calculate_follower_counts_by_job_function(xls)
                    sorted_data_job_function = sorted(follower_counts_by_job_function.items(), key=lambda x: x[1], reverse=False)
                    plot_data(sorted_data_job_function, 
                            x_label='Total Followers',
                            y_label='Job function',
                            title='Total Follower Counts by Job Function')
#fourth sub-section                        
            elif selected_option == "Followers Location":
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


#fifth sub-section     
            elif selected_option == "Followers Seniority":
                xls_df = load_data(uploaded_file, sheet_name="Seniority")

                # Calculate follower counts by seniority
                follower_counts_by_seniority = calculate_follower_counts_by_seniority(xls_df)

                # Sort the data in decreasing order of follower counts
                sorted_data_seniority = sorted(follower_counts_by_seniority.items(), key=lambda x: x[1], reverse=False)

                # Plot follower counts by seniority
                plot_data(sorted_data_seniority,
                        x_label='Total Followers',
                        y_label='Seniority',
                        title='Total Follower Counts by Seniority')

#sixth sub-section                 
            elif selected_option == "New Followers":
                # Load the Excel file
                df_followers = load_data(uploaded_file, sheet_name="New followers")

                # Process and plot followers data
                df_melted_followers = process_new_followers(df_followers)
                plot_new_followers(df_melted_followers)