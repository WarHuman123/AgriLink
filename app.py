import streamlit as st
import pandas as pd
import os
import random
import string

# CSV file
CSV_FILE = "agrilink_data.csv"

# Initialize CSV if not exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Name", "Role", "Crop/Need", "Quantity", "Address", "Contact", "Bank Details", "Edit Code"])
    df.to_csv(CSV_FILE, index=False)

# Load data
df = pd.read_csv(CSV_FILE)

st.set_page_config(page_title="AgriLink", layout="wide")
st.title("🌱 AgriLink – Connecting Farmers, Volunteers & Buyers")

st.sidebar.header("Register / Offer Help")

# Generate random edit code
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ----------------------------
# FORM FOR NEW ENTRY
# ----------------------------
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
            edit_code = generate_code()
            new_entry = {
                "Name": name,
                "Role": role,
                "Crop/Need": crop_or_need,
                "Quantity": quantity,
                "Address": address,
                "Contact": contact,
                "Bank Details": bank_details if role == "Farmer" else "",
                "Edit Code": edit_code
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success(f"✅ Entry submitted successfully! Your edit code is: **{edit_code}**. Save this code to edit/delete later.")
        else:
            st.error("⚠️ Please fill all required fields.")

# ----------------------------
# EDIT / DELETE ENTRY
# ----------------------------
st.sidebar.header("Edit / Delete My Entry")
with st.sidebar.form("edit_form"):
    user_code = st.text_input("Enter your Edit Code")
    action = st.radio("Action", ["Edit", "Delete"])
    confirm = st.form_submit_button("Proceed")

    if confirm:
        if user_code in df["Edit Code"].values:
            row_index = df.index[df["Edit Code"] == user_code][0]
            if action == "Delete":
                df = df.drop(row_index)
                df.to_csv(CSV_FILE, index=False)
                st.sidebar.success("🗑️ Entry deleted successfully!")
            elif action == "Edit":
                st.sidebar.info("✏️ Update your details below:")

                with st.sidebar.form("update_form"):
                    upd_name = st.text_input("Name", df.loc[row_index, "Name"])
                    upd_crop = st.text_input("Crop/Need", df.loc[row_index, "Crop/Need"])
                    upd_quantity = st.text_input("Quantity", df.loc[row_index, "Quantity"])
                    upd_address = st.text_area("Address", df.loc[row_index, "Address"])
                    upd_contact = st.text_input("Contact", df.loc[row_index, "Contact"])
                    upd_bank = st.text_input("Bank Details", df.loc[row_index, "Bank Details"])
                    save_changes = st.form_submit_button("Save Changes")

                    if save_changes:
                        df.loc[row_index, "Name"] = upd_name
                        df.loc[row_index, "Crop/Need"] = upd_crop
                        df.loc[row_index, "Quantity"] = upd_quantity
                        df.loc[row_index, "Address"] = upd_address
                        df.loc[row_index, "Contact"] = upd_contact
                        df.loc[row_index, "Bank Details"] = upd_bank
                        df.to_csv(CSV_FILE, index=False)
                        st.sidebar.success("✅ Entry updated successfully!")
        else:
            st.sidebar.error("❌ Invalid Edit Code!")

# ----------------------------
# DISPLAY COMMUNITY BOARDS
# ----------------------------
st.subheader("📋 Community Board")

tab1, tab2, tab3 = st.tabs(["🌾 Farmers", "🛒 Buyers", "🤝 Volunteers"])

with tab1:
    st.write("👨‍🌾 Farmers and their crops:")
    farmers = df[df["Role"] == "Farmer"]
    farmers = farmers.drop(columns=[c for c in ["Edit Code"] if c in farmers.columns])
    if not farmers.empty:
        st.dataframe(farmers, use_container_width=True)
    else:
        st.info("No farmers yet.")

with tab2:
    st.write("🛒 Buyers and their requirements:")
    buyers = df[df["Role"] == "Buyer"]
    buyers = buyers.drop(columns=[c for c in ["Edit Code", "Bank Details"] if c in buyers.columns])
    if not buyers.empty:
        st.dataframe(buyers, use_container_width=True)
    else:
        st.info("No buyers yet.")

with tab3:
    st.write("🤝 Volunteers and their offers:")
    volunteers = df[df["Role"] == "Volunteer"]
    volunteers = volunteers.drop(columns=[c for c in ["Edit Code", "Bank Details"] if c in volunteers.columns])
    if not volunteers.empty:
        st.dataframe(volunteers, use_container_width=True)
    else:
        st.info("No volunteers yet.")
