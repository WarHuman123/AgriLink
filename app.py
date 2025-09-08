# import streamlit as st
# import pandas as pd
# import numpy as np

# # ----- Page Config -----
# st.set_page_config(
#     page_title="AgriLink",
#     page_icon="🌾",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ----- App Header -----
# st.title("🌾 AgriLink - Farmer, Buyer & Sponsor Portal")
# st.markdown("Connecting farmers, buyers, and sponsors efficiently.")

# # ----- Sidebar for Navigation -----
# st.sidebar.header("Choose your portal")
# user_type = st.sidebar.radio("I am a:", ("Farmer", "Buyer", "Sponsor"))

# # ----- Farmer Portal -----
# if user_type == "Farmer":
#     st.subheader("🚜 Farmer Portal")
#     st.write("Manage your crops, track market prices, and get sponsorships.")
    
#     # Sample input form
#     with st.form("farmer_form"):
#         crop_name = st.text_input("Enter crop name")
#         quantity = st.number_input("Quantity (in tons)", min_value=0.0, step=0.1)
#         submit_farmer = st.form_submit_button("Submit")
#     if submit_farmer:
#         st.success(f"✅ Submitted {quantity} tons of {crop_name}!")

# # ----- Buyer Portal -----
# elif user_type == "Buyer":
#     st.subheader("🛒 Buyer Portal")
#     st.write("Browse available crops, visualize data, and contact farmers directly.")

#     # Sample crop data
#     crop_data = pd.DataFrame({
#         "Crop": ["Wheat", "Rice", "Corn"],
#         "Available (tons)": [50, 120, 80],
#         "Price (₹ per ton)": [2000, 1800, 2200],
#         "Farmer Email": ["ramesh@mail.com", "sita@mail.com", "anil@mail.com"]
#     })

#     # Display table row by row with a contact button
#     for i, row in crop_data.iterrows():
#         st.write(f"**{row['Crop']}** - {row['Available (tons)']} tons - ₹{row['Price (₹ per ton)']}")
#         if st.button(f"Contact Farmer {i}"):
#             st.success(f"📧 Farmer Email: {row['Farmer Email']}")
#         st.markdown("---")

#     # Crop Availability Chart
#     st.subheader("📊 Crop Availability & Prices")
#     st.bar_chart(crop_data.set_index("Crop")["Available (tons)"])
#     st.line_chart(crop_data.set_index("Crop")["Price (₹ per ton)"])

# # ----- Sponsor / Volunteer Portal -----
# elif user_type == "Sponsor":
#     st.subheader("💰 Sponsor / Volunteer Portal")
#     st.write("Support farmers and contact them directly for sponsorships or assistance.")

#     # Sample farmer data with contact info
#     farmers = pd.DataFrame({
#         "Farmer": ["Ramesh", "Sita", "Anil"],
#         "Crop": ["Wheat", "Rice", "Corn"],
#         "Needs": ["Fertilizer", "Seeds", "Equipment"],
#         "Email": ["ramesh@mail.com", "sita@mail.com", "anil@mail.com"],
#         "lat": [22.57, 22.59, 22.60],
#         "lon": [88.36, 88.37, 88.35]
#     })

#     # Display each farmer with a contact button
#     for i, row in farmers.iterrows():
#         st.write(f"**{row['Farmer']}** - Crop: {row['Crop']} - Needs: {row['Needs']}")
#         if st.button(f"Contact {row['Farmer']}"):
#             st.success(f"📧 Email: {row['Email']}")
#         st.markdown("---")

#     # Map of farmer locations
#     st.subheader("🗺 Farmer Locations")
#     st.map(farmers[["lat", "lon"]])

# # ----- Footer -----
# st.markdown("---")
# st.markdown("© 2025 AgriLink - Connecting the Agri Community")

import streamlit as st
import sqlite3
import pandas as pd

# --- DATABASE SETUP ---
conn = sqlite3.connect("agrilink.db")
c = conn.cursor()

# Create tables if not exist, with new columns for contact information
c.execute("""CREATE TABLE IF NOT EXISTS farmers
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT, 
             crop TEXT, 
             quantity TEXT, 
             price TEXT, 
             location TEXT,
             phone_number TEXT,
             email TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS sponsors
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             sponsor_name TEXT, 
             help_type TEXT, 
             farmer_id INTEGER,
             sponsor_phone_number TEXT,
             sponsor_email TEXT)""")
conn.commit()

# --- APP UI ---
st.set_page_config(page_title="AgriLink", layout="wide")

# Add a header with an agriculture theme and a brief description
st.title("🌱 AgriLink - Connecting Our Fields")
st.markdown("A platform to connect local farmers with buyers and community supporters.")

menu = ["Farmer Portal", "Buyer Portal", "Sponsor/Volunteer", "Dashboard"]
choice = st.sidebar.selectbox("Choose a Portal", menu)

# --- Farmer Portal ---
if choice == "Farmer Portal":
    st.header("👨‍🌾 Add Your Produce")
    st.info("Fill out the form below to list your crops for potential buyers.")
    with st.form("farmer_form"):
        name = st.text_input("Farmer Name")
        crop = st.text_input("Crop")
        quantity = st.text_input("Quantity (e.g., 50kg)")
        price = st.text_input("Expected Price per unit")
        location = st.text_input("Location")
        
        # New fields for contact information
        phone_number = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        
        submitted = st.form_submit_button("Submit Produce")

        if submitted:
            # Insert the new data into the farmers table
            c.execute("INSERT INTO farmers (name, crop, quantity, price, location, phone_number, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (name, crop, quantity, price, location, phone_number, email))
            conn.commit()
            st.success("✅ Your produce has been listed successfully!")

# --- Buyer Portal ---
elif choice == "Buyer Portal":
    st.header("🛒 Available Produce")
    st.info("Browse the latest produce from local farmers. Contact them directly to make a purchase.")
    
    # Read all farmer data including the new contact info
    df = pd.read_sql("SELECT name, crop, quantity, price, location, phone_number, email FROM farmers", conn)
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No produce available at the moment. Check back soon!")

# --- Sponsor/Volunteer Portal ---
elif choice == "Sponsor/Volunteer":
    st.header("🤝 Support a Farmer")
    st.info("Show your support by helping a farmer in need.")
    
    # Get farmer names to display in the selectbox
    farmers = pd.read_sql("SELECT id, name, crop FROM farmers", conn)
    
    if not farmers.empty:
        # Create a dictionary for mapping ID to a user-friendly name
        farmer_options = {row['id']: f"{row['name']} ({row['crop']})" for index, row in farmers.iterrows()}
        selected_farmer_id = st.selectbox("Select a Farmer to Support", options=list(farmer_options.keys()), format_func=lambda x: farmer_options[x])

        with st.form("sponsor_form"):
            sponsor_name = st.text_input("Your Name")
            help_type = st.selectbox("Type of Help", ["Transport", "Funding", "Knowledge Sharing", "Other"])
            
            # New fields for sponsor contact information
            sponsor_phone_number = st.text_input("Your Phone Number")
            sponsor_email = st.text_input("Your Email Address")
            
            support_submitted = st.form_submit_button("Pledge Support")
            
            if support_submitted:
                # Insert sponsor data including new contact info
                c.execute("INSERT INTO sponsors (sponsor_name, help_type, farmer_id, sponsor_phone_number, sponsor_email) VALUES (?, ?, ?, ?, ?)",
                          (sponsor_name, help_type, int(selected_farmer_id), sponsor_phone_number, sponsor_email))
                conn.commit()
                st.success("🙏 Thank you for your support! Your pledge has been recorded.")
    else:
        st.warning("No farmers are currently listed for support.")

# --- Transparency Dashboard ---
elif choice == "Dashboard":
    st.header("📊 Transparency Dashboard")
    st.info("View a summary of all farmers and community support.")

    # Display Farmers
    st.write("### Farmers")
    farmer_data = pd.read_sql("SELECT name, crop, quantity, price, location, phone_number, email FROM farmers", conn)
    if not farmer_data.empty:
        st.dataframe(farmer_data)
    else:
        st.warning("No farmer data available.")
        
    st.write("---")

    # Display Sponsors and Volunteers
    st.write("### Sponsors & Volunteers")
    sponsor_data = pd.read_sql("""
        SELECT 
            s.sponsor_name, 
            s.help_type, 
            s.sponsor_phone_number, 
            s.sponsor_email,
            f.name as farmer_name
        FROM sponsors s
        JOIN farmers f ON s.farmer_id = f.id
    """, conn)
    
    if not sponsor_data.empty:
        st.dataframe(sponsor_data)
    else:
        st.warning("No sponsor data available.")