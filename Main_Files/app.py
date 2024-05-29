import streamlit as st
from content import process_content_data  
from followers import process_followers_data
from visitors import process_views_data
import warnings

# Filter out warnings
warnings.filterwarnings("ignore")


class SessionState:
    def __init__(self):
        self.selected_file = None
        self.selected_option = None

# Create an instance of the SessionState class
session_state = SessionState()

def clear_session_state():
    session_state.selected_file = None
    session_state.selected_option = None

def main():
    # Filter out warnings
    warnings.filterwarnings("ignore")

    st.sidebar.title("LinkedIn Data Insights")
    selected_function = st.sidebar.radio("Select Function", ["Content", "Followers", "Visitors"])

    st.title(f"LinkedIn {selected_function} Dashboard")
    st.write(f"Explore and visualize your LinkedIn {selected_function.lower()} with meaningful insights!")

    # Create a file uploader widget to allow the user to upload their data
    uploaded_file = st.file_uploader(f"Upload an Excel file", type=["xls", "xlsx"], key=f"file_uploader_{selected_function}")

    # Clear selected file when switching functions
    if session_state.selected_option != selected_function:
        clear_session_state()

    try:
        # If the user has uploaded a file, process the data based on the selected function
        if uploaded_file is not None:
            session_state.selected_option = selected_function

            # Clear uploaded file when switching functions
            if session_state.selected_option != selected_function:
                uploaded_file = None
                clear_session_state()

            # Save the selected file to session state
            session_state.selected_file = uploaded_file

            if selected_function == "Content":
                process_content_data(uploaded_file)  # Call the content processing function

            elif selected_function == "Followers":
                process_followers_data(uploaded_file)  # Call the followers processing function

            elif selected_function == "Visitors":
                process_views_data(uploaded_file)  # Call the Visitors processing function

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()








