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
        parsed = phonenumbers.parse(number, "IN")
        if phonenumbers.is_valid_number(parsed):
            clean_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            link = f"https://wa.me/{clean_number.replace('+', '')}?text={message.replace(' ', '%20')}"
            return link
        else:
            return None
    except:
        return None

# Load or create CSV
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Role", "Crop/Need", "Quantity", "Address",
                               "Contact", "Bank Details", "Edit Code"])
    df.to_csv(CSV_FILE, index=False)

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "future" not in st.session_state:
    st.session_state.future = []
if "wa_confirmed" not in st.session_state:
    st.session_state.wa_confirmed = False

# App title
st.title("🌱 AgriLink – Connect Farmers, Buyers, and Volunteers")

# Sidebar – Undo/Redo
st.sidebar.header("⚙️ Options")
if st.sidebar.button("↩️ Undo"):
    if st.session_state.history:
        last_state = st.session_state.history.pop()
        st.session_state.future.append(df.copy())
        df = last_state
        df.to_csv(CSV_FILE, index=False)
        st.sidebar.success("Undid last change")
if st.sidebar.button("↪️ Redo"):
    if st.session_state.future:
        next_state = st.session_state.future.pop()
        st.session_state.history.append(df.copy())
        df = next_state
        df.to_csv(CSV_FILE, index=False)
        st.sidebar.success("Redid last change")

# Role selection with instant update
role = st.selectbox("You are a:", ["Farmer", "Buyer", "Volunteer"])

# Form
with st.form("entry_form"):
    name = st.text_input("Your Name")
    # Show field dynamically
    if role == "Farmer":
        role_field_label = "Crop"
        bank_details = st.text_input("Bank Details (optional, for Farmers only)")
    elif role == "Buyer":
        role_field_label = "Requirement"
        bank_details = ""
    else:
        role_field_label = "Support"
        bank_details = ""
    
    crop_or_need = st.text_input(role_field_label)
    quantity = st.text_input("Quantity (optional)")
    address = st.text_area("Address / Location")
    contact = st.text_input("Contact Number")
    
    submitted = st.form_submit_button("Submit")

if submitted:
    if not (name and crop_or_need and address and contact):
        st.error("❌ Please fill in all required fields.")
    else:
        message = f"Hello {name}, thanks for registering as {role} on AgriLink!"
        wa_link = get_whatsapp_link(contact, message)
        
        if wa_link:
            st.info("✅ WhatsApp confirmation is required. Click the button below to open WhatsApp and send the message.")
            if st.button("Open WhatsApp"):
                st.markdown(f"[Click here if WhatsApp did not open automatically]({wa_link})")
                st.session_state.wa_confirmed = True
        else:
            st.error("⚠️ Phone number invalid. Must be a valid WhatsApp number.")

# Only save after WhatsApp confirmed
if st.session_state.wa_confirmed:
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
    st.session_state.history.append(df.copy())
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success(f"✅ Registration complete! Your edit code is: **{edit_code}**. Save this code to edit/delete later.")
    st.session_state.wa_confirmed = False  # reset for next entry

# Tabs to show entries
tab1, tab2, tab3 = st.tabs(["🌾 Farmers", "🛒 Buyers", "🤝 Volunteers"])

with tab1:
    st.write("👨‍🌾 Farmers and their crops:")
    farmers = df[df["Role"] == "Farmer"]
    if not farmers.empty:
        st.dataframe(farmers.drop(columns=["Edit Code"]), use_container_width=True)
    else:
        st.info("No farmers yet.")

with tab2:
    st.write("🛒 Buyers and their requirements:")
    buyers = df[df["Role"] == "Buyer"]
    if not buyers.empty:
        st.dataframe(buyers.drop(columns=["Edit Code", "Bank Details"]), use_container_width=True)
    else:
        st.info("No buyers yet.")

with tab3:
    st.write("🤝 Volunteers and their offers:")
    volunteers = df[df["Role"] == "Volunteer"]
    if not volunteers.empty:
        st.dataframe(volunteers.drop(columns=["Edit Code", "Bank Details"]), use_container_width=True)
    else:
        st.info("No volunteers yet.")
