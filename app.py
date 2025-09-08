import streamlit as st
import pandas as pd
import random
import string

# File to save data
CSV_FILE = "registrations.csv"

# Load or initialize dataframe
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Name", "Role", "Crop/Need/Service", "Quantity", "Address", "Contact", "Bank Details", "Edit Code"])

# Generate unique edit code
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Create WhatsApp link
def get_whatsapp_link(phone, message):
    return f"https://wa.me/{phone}?text={message.replace(' ', '%20')}"

st.title("🌾 AgriLink Registration")

with st.form("registration_form", clear_on_submit=True):
    name = st.text_input("Name")
    role = st.selectbox("You are a:", ["Farmer", "Buyer", "Volunteer"])

    # Dynamic fields
    if role == "Farmer":
        crop = st.text_input("Crop")
        quantity = st.text_input("Quantity")
        bank_details = st.text_area("Bank Details")
        special_field = crop
    elif role == "Buyer":
        need = st.text_input("What do you need?")
        quantity = st.text_input("Quantity")
        special_field = need
        bank_details = ""
    else:  # Volunteer
        service = st.text_input("Service you want to provide")
        quantity = ""
        special_field = service
        bank_details = ""

    address = st.text_area("Address")
    contact = st.text_input("WhatsApp Number (with country code, e.g. 91xxxxxxxxxx)")

    submitted = st.form_submit_button("Submit")

if submitted:
    if not contact.startswith("91") or not contact.isdigit():
        st.error("❌ Enter a valid WhatsApp number with country code (e.g. 91xxxxxxxxxx).")
    else:
        edit_code = generate_code()
        wa_message = f"Hello {name}, thanks for registering as {role} on AgriLink! Your edit code is {edit_code}."
        wa_link = get_whatsapp_link(contact, wa_message)

        st.info("✅ WhatsApp confirmation is required. Click below to open WhatsApp and send the message.")
        st.markdown(f"[📲 Open WhatsApp and send message]({wa_link})", unsafe_allow_html=True)

        if st.button("✅ I sent the WhatsApp message"):
            new_entry = {
                "Name": name,
                "Role": role,
                "Crop/Need/Service": special_field,
                "Quantity": quantity,
                "Address": address,
                "Contact": contact,
                "Bank Details": bank_details,
                "Edit Code": edit_code
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success(f"✅ Registration complete! Your edit code is: **{edit_code}**. Save it for later updates.")

            st.subheader("📋 Current Registrations")
            st.dataframe(df)
