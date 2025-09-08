import streamlit as st
import pandas as pd
import random
import string
import phonenumbers
import os

# CSV file path
CSV_FILE = "agrilink_data.csv"

# Generate unique edit code
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# WhatsApp link generator
def get_whatsapp_link(number, message):
    try:
        parsed = phonenumbers.parse(number, "IN")  # Default India
        if phonenumbers.is_valid_number(parsed):
            clean_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            link = f"https://wa.me/{clean_number.replace('+', '')}?text={message.replace(' ', '%20')}"
            return link
        else:
            return None
    except:
        return None

# Load or create CSV
if "data" not in st.session_state:
    if os.path.exists(CSV_FILE):
        st.session_state["data"] = pd.read_csv(CSV_FILE)
    else:
        st.session_state["data"] = pd.DataFrame(columns=["Name", "Role", "Crop/Need", "Quantity", "Address",
                                                        "Contact", "Bank Details", "Edit Code"])
        st.session_state["data"].to_csv(CSV_FILE, index=False)

df = st.session_state["data"]

# App title
st.title("🌱 AgriLink – Connect Farmers, Buyers, and Volunteers")

# Form
with st.form("entry_form"):
    name = st.text_input("Your Name")
    role = st.selectbox("You are a:", ["Farmer", "Buyer", "Volunteer"], key="role_select")
    
    # Show field dynamically based on role
    if role == "Farmer":
        crop_or_need = st.text_input("Crop")
        bank_details = st.text_input("Bank Details (optional)")
    elif role == "Buyer":
        crop_or_need = st.text_input("Requirement")
        bank_details = ""
    else:  # Volunteer
        crop_or_need = st.text_input("Support Offer")
        bank_details = ""

    quantity = st.text_input("Quantity (optional)")
    address = st.text_area("Address / Location")
    contact = st.text_input("Contact Number")

    submitted = st.form_submit_button("Submit")

if submitted:
    if not (name and role and crop_or_need and address and contact):
        st.error("❌ Please fill in all required fields.")
    else:
        edit_code = generate_code()
        message = f"Hello {name}, thanks for registering as {role} on AgriLink! Your edit code is {edit_code}."
        wa_link = get_whatsapp_link(contact, message)

        if wa_link:
            st.info("✅ WhatsApp confirmation is required. Click the link below to open WhatsApp and send the message.")
            st.markdown(f"[Open WhatsApp and send message]({wa_link})", unsafe_allow_html=True)

            if st.button("✅ I sent the WhatsApp message"):
                # Save entry in session state
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
                st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_entry])], ignore_index=True)
                st.session_state["data"].to_csv(CSV_FILE, index=False)
                st.success(f"✅ Registration complete! Your edit code is: **{edit_code}**. Save this code to edit/delete later.")
        else:
            st.error("⚠️ Phone number invalid or not a WhatsApp number. Registration cannot continue.")

# Edit/Delete section
st.subheader("✏️ Edit or Delete Your Entry")
edit_code_input = st.text_input("Enter your edit code to edit/delete entry")
if st.button("Find Entry"):
    entry = st.session_state["data"][st.session_state["data"]["Edit Code"] == edit_code_input]
    if not entry.empty:
        st.write("Your current entry:", entry)

        action = st.radio("Choose action:", ["Edit", "Delete"])
        if action == "Edit":
            new_name = st.text_input("Name", entry.iloc[0]["Name"])
            new_crop_or_need = st.text_input("Crop/Need", entry.iloc[0]["Crop/Need"])
            new_quantity = st.text_input("Quantity", entry.iloc[0]["Quantity"])
            new_address = st.text_area("Address", entry.iloc[0]["Address"])
            new_contact = st.text_input("Contact", entry.iloc[0]["Contact"])
            new_bank = st.text_input("Bank Details", entry.iloc[0].get("Bank Details", ""))

            if st.button("Save Changes"):
                st.session_state["data"].loc[st.session_state["data"]["Edit Code"] == edit_code_input,
                                             ["Name", "Crop/Need", "Quantity", "Address", "Contact", "Bank Details"]] = [
                                                 new_name, new_crop_or_need, new_quantity, new_address, new_contact, new_bank
                                             ]
                st.session_state["data"].to_csv(CSV_FILE, index=False)
                st.success("✅ Entry updated successfully!")

        elif action == "Delete":
            if st.button("Confirm Delete"):
                st.session_state["data"] = st.session_state["data"][st.session_state["data"]["Edit Code"] != edit_code_input]
                st.session_state["data"].to_csv(CSV_FILE, index=False)
                st.success("🗑️ Entry deleted successfully!")
    else:
        st.error("❌ No entry found with that edit code.")

# Tabs
tab1, tab2, tab3 = st.tabs(["🌾 Farmers", "🛒 Buyers", "🤝 Volunteers"])

with tab1:
    st.write("👨‍🌾 Farmers and their crops:")
    farmers = st.session_state["data"][st.session_state["data"]["Role"] == "Farmer"].drop(
        columns=[c for c in ["Edit Code"] if c in st.session_state["data"].columns]
    )
    if not farmers.empty:
        st.dataframe(farmers, use_container_width=True)
    else:
        st.info("No farmers yet.")

with tab2:
    st.write("🛒 Buyers and their requirements:")
    buyers = st.session_state["data"][st.session_state["data"]["Role"] == "Buyer"].drop(
        columns=[c for c in ["Edit Code", "Bank Details"] if c in st.session_state["data"].columns]
    )
    if not buyers.empty:
        st.dataframe(buyers, use_container_width=True)
    else:
        st.info("No buyers yet.")

with tab3:
    st.write("🤝 Volunteers and their offers:")
    volunteers = st.session_state["data"][st.session_state["data"]["Role"] == "Volunteer"].drop(
        columns=[c for c in ["Edit Code", "Bank Details"] if c in st.session_state["data"].columns]
    )
    if not volunteers.empty:
        st.dataframe(volunteers, use_container_width=True)
    else:
        st.info("No volunteers yet.")
