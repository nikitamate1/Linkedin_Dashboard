import streamlit as st
import pandas as pd
from functions import calculate_rates, process_and_display_data, truncate_text  
from constant import metric_info

def process_content_data(uploaded_file):
    st.write("Inside process_content_data")  # Debugging print
    # If the user has uploaded a file, process the data for the "All Posts" option
    if uploaded_file is not None:
        # Load the Excel file for All Posts
        df_all_posts = pd.read_excel(uploaded_file, sheet_name="All posts", header=1)

        # Replace null values in "Post title" with a custom name like "nan"
        df_all_posts['Post title'].fillna('nan', inplace=True)

        # Calculate Engagement Rate (ER) and Click Through Rate (CTR)
        df_all_posts = calculate_rates(df_all_posts)

        # Get unique post titles
        unique_post_titles = df_all_posts['Post title'].unique()

        # Create a selector for choosing the option
        selected_option = st.radio("Select Option", ["Post Analysis", "Comparison of All Posts"])

        if selected_option == "Post Analysis":
            # Create a multiselect to choose posts for comparison
            selected_posts_all_posts = st.multiselect("Select Posts for Comparison (All Posts)",
                                                      unique_post_titles,
                                                      default=unique_post_titles[:2].tolist(), key="comparison_all_posts")

            # Set to keep track of processed post titles
            processed_post_titles = set()

            # Display the graphs for each selected post in "All Posts"
            for post_title in selected_posts_all_posts:
                # Check if the post title has already been processed
                if post_title not in processed_post_titles:
                    # Find the rows corresponding to the selected post
                    selected_rows_all_posts = df_all_posts[df_all_posts['Post title'] == post_title]

                    # Call the function to process and display data
                    process_and_display_data(selected_rows_all_posts, metric_info, f"{post_title} - Reactions of Post")

                    # Add the processed post title to the set
                    processed_post_titles.add(post_title)

        elif selected_option == "Comparison of All Posts":

            # Truncate titles to a maximum of 5 words using truncate_text function
            df_all_posts['Truncated Title'] = df_all_posts['Post title'].apply(lambda x: truncate_text(x, max_words=5))

            # Call the function to process and display data for all posts
            process_and_display_data(df_all_posts, metric_info, "All Posts - Reactions Summary")