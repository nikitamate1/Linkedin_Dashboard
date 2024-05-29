import pandas as pd
import plotly.express as px
import streamlit as st



# functions that are used in content section
def calculate_rates(df):
    df['Engagement rate'] = (df['Comments'] + df['Clicks'] + df['Reposts'] + df['Likes']) / df['Impressions']
    df['Click through rate (CTR)'] = (df['Clicks'] / df['Impressions'])
    return df

def process_and_display_data(selected_rows, metric_info, title):
    st.markdown(f"## {title}")

    # Create a row layout for the charts
    col1, col2 = st.columns(2)

    # Create a new column 'Truncated Title'
    selected_rows['Post Title'] = selected_rows['Post title'].apply(lambda x: truncate_text(x, max_words=5))

    # Create the first graph (Clicks, Likes, Comments, Reposts)
    with col1:
        metrics_columns_first_graph = ['Clicks', 'Likes', 'Comments', 'Reposts']
        fig1 = px.bar(selected_rows, x='Post Title', y=metrics_columns_first_graph,
                    labels={'value': 'Values', 'index': 'Metrics'},
                    title='Reactions of Post', barmode='group', height=400, width=700)  # Group bars for better visibility

        for i, metric in enumerate(metrics_columns_first_graph):
            fig1.data[i].marker.color = metric_info[metric]['color']

        # Add text labels above the bars
        fig1.update_traces(textposition='outside', texttemplate='%{y}')
        st.plotly_chart(fig1)

    # Create the second graph (CTR and Engagement Rate)
    with col2:
        metrics_columns_second_graph = ['Click through rate (CTR)', 'Engagement rate']
        fig2 = px.bar(selected_rows, x='Post Title', y=metrics_columns_second_graph,
                    labels={'value': 'Values', 'index': 'Metrics'},
                    title='Click Through Rate and Engagement Rate', barmode='group', height=400, width=700)  # Group bars for better visibility

        for i, metric in enumerate(metrics_columns_second_graph):
            fig2.data[i].marker.color = metric_info[metric]['color']

        # Add text labels above the bars
        fig2.update_traces(textposition='outside', texttemplate='%{y}')
        st.plotly_chart(fig2)

    # Create a list to store clickable links
    links = []
    # Iterate through rows to display data
    for _, row in selected_rows.iterrows():
        truncated_title = truncate_text(row['Post title'], max_words=5)
        link = f"[{truncated_title}]({row['Post link']})"
        links.append(link)

    # Display clickable links
    st.markdown("Original Post Link:")
    for link in links:
        st.markdown(link)

def truncate_text(text, max_words=5):
    if pd.isna(text):
        return 'NaN...    '
    words = text.split()[:max_words]
    truncated_title = ' '.join(words)
    if len(words) < len(text.split()):
        truncated_title += '...'
    return truncated_title



# functions that are used in followers and visitors data
def load_data(file_uploader, sheet_name):
    xls = pd.ExcelFile(file_uploader)
    return pd.read_excel(xls, sheet_name=sheet_name)

def plot_data(sorted_data, x_label, y_label, title):
    fig = px.bar(
        x=[item[1] for item in sorted_data],
        y=[item[0] for item in sorted_data],
        orientation='h',
        labels={'x': x_label, 'y': y_label},
        title=title,
        width=800,
        height=500,
        color_discrete_sequence=['dodgerblue'] * len(sorted_data),
    )
    fig.update_traces(
        text=[f"{item[1]}" for item in sorted_data],  # Set the text to the values
        textposition='outside',  # Place the text outside the bars
    )
    st.plotly_chart(fig)
    

def plot_data_for_industry(sorted_data, x_column, y_column, title):
    fig = px.bar(
        x=sorted_data[x_column],
        y=sorted_data[y_column],
        orientation='h',
        labels={'x': x_column, 'y': y_column},
        title=title,
        width=800,
        height=500,
        color_discrete_sequence=['dodgerblue'] * len(sorted_data),
    )
     # Customize the layout
    fig.update_traces(
        textposition='outside',  # Place the text outside the bars
        text=sorted_data[x_column].astype(str)  # Convert the column to string for text labels
    )
    st.plotly_chart(fig)


def plot_new_followers(df_melted):
    if df_melted is not None:
        fig = px.line(
            df_melted,
            x='Date',
            y='Count',
            color='Metric',
            labels={'Count': 'Total Followers'},
            title='Total Followers Over Time (Sponsored vs. Organic)',
            markers=True,
        )

        fig.update_layout(xaxis_title='Date', yaxis_title='Total Followers', legend_title_text='Metrics')
        fig.update_xaxes(tickangle=90)

        # Use the add_annotations function
        add_annotations(fig, df_melted, x_column='Date', y_columns=['Count'])

        st.plotly_chart(fig)

def plot_visitors_metrics(df, x_column, y_columns, title):
                # Create a line chart using Plotly Express
                fig = px.line(df, x=x_column, y=y_columns, markers=True, labels={'value': 'Counts', 'variable': 'Categories'},
                            title=title, width=800, height=500)
                # Customize the layout
                fig.update_layout(xaxis=dict(tickangle=90))
                # Add annotations
                add_annotations(fig, df, x_column, y_columns)
                # Display the chart
                st.plotly_chart(fig)

def add_annotations(fig, df, x_column, y_columns):
    # Add text annotations to display only values on top of each data point
    for metric in df[y_columns].columns:
        for i, row in df.iterrows():
            fig.add_annotation(
                x=row[x_column],
                y=row[metric],
                text=f"{row[metric]}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-20
            )