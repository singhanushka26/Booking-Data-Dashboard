import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Ensure Streamlit runs in headless mode
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

# Set Streamlit page config
st.set_page_config(page_title="Booking Data Dashboard", layout="wide")
st.title("📊 Booking Data Dashboard")

# Load Cleaned Data
file_path = "Cleaned_Booking_Data.csv"  # Ensure this file exists in the correct directory
if not os.path.exists(file_path):
    st.error("⚠️ File not found. Please check the file path.")
    st.stop()

df = pd.read_csv(file_path)

# Convert Booking Date to datetime
df["Booking Date"] = pd.to_datetime(df["Booking Date"], errors='coerce')

# Extract month names
df["month"] = df["Booking Date"].dt.strftime("%B")

# Aggregate bookings per month
df_monthly = df.groupby("month").size().reset_index(name="bookings")

# Sort months correctly
month_order = ["January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]
df_monthly["month"] = pd.Categorical(df_monthly["month"], categories=month_order, ordered=True)
df_monthly = df_monthly.sort_values("month")

# Layout Organization
col1, col2 = st.columns(2)

with col1:
    # Month selection
    selected_month = st.selectbox("Select a Month:", df_monthly["month"].unique())
    
    # Filter data based on selected month
    filtered_df = df[df["month"] == selected_month]
    
    # Display filtered data in an expander
    with st.expander("📋 View Filtered Data"):
        st.dataframe(filtered_df)

with col2:
    # Display missing values summary in an expander
    with st.expander("🚨 Missing Values Summary"):
        st.write(df.isnull().sum())
    
    # Handle missing values
df.fillna(0, inplace=True)

# Booking Trends Over Time
st.subheader("📅 Booking Trends Over Time")
booking_trends = df.resample('W', on='Booking Date').size().reset_index(name='Booking Count')
fig1 = px.line(booking_trends, x='Booking Date', y='Booking Count', 
               title='Bookings Over Time', color_discrete_sequence=["#FF5733"])
st.plotly_chart(fig1, use_container_width=True)

# Booking Type Distribution
st.subheader("📌 Booking Type Distribution")
fig2 = px.pie(df, names="Booking Type", title="Distribution of Booking Types", color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(fig2)

# Revenue Insights
st.subheader("💰 Revenue Insights")
if 'Price' in df.columns:
    total_revenue = df['Price'].sum()
    avg_revenue = df['Price'].mean()
    
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col4:
        st.metric("Avg Revenue per Booking", f"${avg_revenue:,.2f}")
else:
    st.warning("⚠️ 'Price' column not found in the dataset.")

# Top 10 Customers by Spending
if 'Customer ID' in df.columns and 'Price' in df.columns:
    st.subheader("🏅 Top 10 Customers by Spending")
    top_customers = df.groupby("Customer ID")['Price'].sum().reset_index().nlargest(10, 'Price')
    st.dataframe(top_customers)
else:
    st.warning("⚠️ Missing 'Customer ID' or 'Price' column.")

# Facility Utilization
st.subheader("🏢 Facility Utilization")
if 'Facility' in df.columns:
    df_facility = df['Facility'].value_counts().reset_index()
    df_facility.columns = ['Facility', 'Count']
    fig3 = px.bar(df_facility, x='Facility', y='Count', 
                  title="Most Used Facilities", color_discrete_sequence=["#00CC96"])
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("⚠️ 'Facility' column not found.")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Booking Type Filter
if 'Booking Type' in df.columns:
    selected_type = st.sidebar.multiselect("Select Booking Type", df['Booking Type'].unique(), default=df['Booking Type'].unique())
    filtered_df = df[df['Booking Type'].isin(selected_type)]
else:
    selected_type = []
    st.warning("⚠️ 'Booking Type' column not found.")

# Booking Status Filter
if "Status" in df.columns:
    selected_status = st.sidebar.selectbox("Select Booking Status:", df["Status"].unique())
    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
else:
    st.warning("⚠️ 'Status' column not found.")

# Display Filtered Data in Expander
with st.expander("📋 View Filtered Data"):
    st.dataframe(filtered_df)

# Bookings Per Month Visualization
st.subheader("📆 Bookings Per Month")
fig4 = px.bar(df_monthly, x="month", y="bookings", 
              title="Bookings Per Month", color_discrete_sequence=["#636EFA"])
st.plotly_chart(fig4)