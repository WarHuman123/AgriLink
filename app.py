import streamlit as st
import pandas as pd
import numpy as np

# ----- Page Config -----
st.set_page_config(
    page_title="AgriLink",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- App Header -----
st.title("🌾 AgriLink - Farmer, Buyer & Sponsor Portal")
st.markdown("Connecting farmers, buyers, and sponsors efficiently.")

# ----- Sidebar for Navigation -----
st.sidebar.header("Choose your portal")
user_type = st.sidebar.radio("I am a:", ("Farmer", "Buyer", "Sponsor"))

# ----- Farmer Portal -----
if user_type == "Farmer":
    st.subheader("🚜 Farmer Portal")
    st.write("Manage your crops, track market prices, and get sponsorships.")
    
    # Sample input form
    with st.form("farmer_form"):
        crop_name = st.text_input("Enter crop name")
        quantity = st.number_input("Quantity (in tons)", min_value=0.0, step=0.1)
        submit_farmer = st.form_submit_button("Submit")
    if submit_farmer:
        st.success(f"✅ Submitted {quantity} tons of {crop_name}!")

# ----- Buyer Portal -----
elif user_type == "Buyer":
    st.subheader("🛒 Buyer Portal")
    st.write("Browse available crops, visualize data, and contact farmers directly.")

    # Sample crop data
    crop_data = pd.DataFrame({
        "Crop": ["Wheat", "Rice", "Corn"],
        "Available (tons)": [50, 120, 80],
        "Price (₹ per ton)": [2000, 1800, 2200],
        "Farmer Email": ["ramesh@mail.com", "sita@mail.com", "anil@mail.com"]
    })

    # Display table row by row with a contact button
    for i, row in crop_data.iterrows():
        st.write(f"**{row['Crop']}** - {row['Available (tons)']} tons - ₹{row['Price (₹ per ton)']}")
        if st.button(f"Contact Farmer {i}"):
            st.success(f"📧 Farmer Email: {row['Farmer Email']}")
        st.markdown("---")

    # Crop Availability Chart
    st.subheader("📊 Crop Availability & Prices")
    st.bar_chart(crop_data.set_index("Crop")["Available (tons)"])
    st.line_chart(crop_data.set_index("Crop")["Price (₹ per ton)"])

# ----- Sponsor / Volunteer Portal -----
elif user_type == "Sponsor":
    st.subheader("💰 Sponsor / Volunteer Portal")
    st.write("Support farmers and contact them directly for sponsorships or assistance.")

    # Sample farmer data with contact info
    farmers = pd.DataFrame({
        "Farmer": ["Ramesh", "Sita", "Anil"],
        "Crop": ["Wheat", "Rice", "Corn"],
        "Needs": ["Fertilizer", "Seeds", "Equipment"],
        "Email": ["ramesh@mail.com", "sita@mail.com", "anil@mail.com"],
        "lat": [22.57, 22.59, 22.60],
        "lon": [88.36, 88.37, 88.35]
    })

    # Display each farmer with a contact button
    for i, row in farmers.iterrows():
        st.write(f"**{row['Farmer']}** - Crop: {row['Crop']} - Needs: {row['Needs']}")
        if st.button(f"Contact {row['Farmer']}"):
            st.success(f"📧 Email: {row['Email']}")
        st.markdown("---")

    # Map of farmer locations
    st.subheader("🗺 Farmer Locations")
    st.map(farmers[["lat", "lon"]])

# ----- Footer -----
st.markdown("---")
st.markdown("© 2025 AgriLink - Connecting the Agri Community")
