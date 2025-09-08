import streamlit as st
import pandas as pd
import os

# CSV file
CSV_FILE = "agrilink_data.csv"

# Initialize CSV if not exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Name", "Role", "Crop/Need", "Quantity", "Address", "Contact", "Bank Details"])
    df.to_csv(CSV_FILE, index=False)

# Load data
df = pd.read_csv(CSV_FILE)

st.set_page_config(page_title="AgriLink", layout="wide")
st.title("🌱 AgriLink – Connecting Farmers, Volunteers & Buyers")

st.sidebar.header("Register / Offer Help")

with st.sidebar.form("user_form"):
    name = st.text_input("Name")
    role = st.selectbox("I am a", ["Farmer", "Volunteer", "Buyer"])
    crop_or_need = st.text_input("Crop (if Farmer) / Need (if Volunteer or Buyer)")
    quantity = st.text_input("Quantity / Support")
    address = st.text_area("Address (Village/District/State)")
    contact = st.text_input("Contact (Phone/Email)")
    
    bank_details = ""
    if role == "Farmer":
        bank_details = st.text_input("Bank Details (Optional)", placeholder="Account No, IFSC, Bank Name")
    
    submitted = st.form_submit_button("Submit")

    if submitted:
        if name and role and crop_or_need and address and contact:
            new_entry = {
                "Name": name,
                "Role": role,
                "Crop/Need": crop_or_need,
                "Quantity": quantity,
                "Address": address,
                "Contact": contact,
                "Bank Details": bank_details if role == "Farmer" else ""
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success("✅ Entry submitted successfully!")
        else:
            st.error("⚠️ Please fill all required fields.")

st.subheader("📋 Community Board")
st.write("Here you can see all farmers, volunteers, and buyers with their needs or offers:")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No entries yet. Be the first to register!")
