import streamlit as st
import sqlite3
import pandas as pd

# --- DATABASE SETUP ---
conn = sqlite3.connect("agrilink.db")
c = conn.cursor()

# Create tables if not exist
c.execute("""CREATE TABLE IF NOT EXISTS farmers
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT, crop TEXT, quantity TEXT, price TEXT, location TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS sponsors
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              sponsor_name TEXT, help_type TEXT, farmer_id INTEGER)""")
conn.commit()

# --- APP UI ---
st.set_page_config(page_title="AgriLink", layout="wide")

st.title("🌱 AgriLink - Farmers Meet Buyers & Supporters")

menu = ["Farmer Portal", "Buyer Portal", "Sponsor/Volunteer", "Dashboard"]
choice = st.sidebar.selectbox("Choose a Portal", menu)

# Farmer Portal
if choice == "Farmer Portal":
    st.subheader("👨‍🌾 Add Your Produce")
    with st.form("farmer_form"):
        name = st.text_input("Farmer Name")
        crop = st.text_input("Crop")
        quantity = st.text_input("Quantity (e.g., 50kg)")
        price = st.text_input("Expected Price per unit")
        location = st.text_input("Location")
        submitted = st.form_submit_button("Submit")

        if submitted:
            c.execute("INSERT INTO farmers (name, crop, quantity, price, location) VALUES (?, ?, ?, ?, ?)",
                      (name, crop, quantity, price, location))
            conn.commit()
            st.success("✅ Produce added successfully!")

# Buyer Portal
elif choice == "Buyer Portal":
    st.subheader("🛒 Available Produce")
    df = pd.read_sql("SELECT * FROM farmers", conn)
    st.dataframe(df)

# Sponsor/Volunteer Portal
elif choice == "Sponsor/Volunteer":
    st.subheader("🤝 Support a Farmer")
    farmers = pd.read_sql("SELECT id, name, crop FROM farmers", conn)
    farmer_id = st.selectbox("Select Farmer", farmers["id"])
    sponsor_name = st.text_input("Your Name")
    help_type = st.selectbox("Type of Help", ["Transport", "Funding", "Knowledge Sharing", "Other"])
    if st.button("Pledge Support"):
        c.execute("INSERT INTO sponsors (sponsor_name, help_type, farmer_id) VALUES (?, ?, ?)",
                  (sponsor_name, help_type, int(farmer_id)))
        conn.commit()
        st.success("🙏 Thank you for supporting!")

# Transparency Dashboard
elif choice == "Dashboard":
    st.subheader("📊 Transparency Dashboard")
    farmer_data = pd.read_sql("SELECT * FROM farmers", conn)
    sponsor_data = pd.read_sql("""SELECT s.sponsor_name, s.help_type, f.name as farmer_name
                                  FROM sponsors s
                                  JOIN farmers f ON s.farmer_id = f.id""", conn)

    st.write("### Farmers")
    st.dataframe(farmer_data)

    st.write("### Sponsors & Volunteers")
    st.dataframe(sponsor_data)
