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
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Role", "Crop/Need", "Quantity", "Address",
                               "Contact", "Bank Details", "Edit Code"])
    df.to_csv(CSV_FILE, index=False)

# Session state for undo/redo
if "history" not in st.session_state:
    st.session_state.history = []
if "future" not in st.session_state:
    st.session_state.future = []

# Session state for role-specific fields
if "role" not in st.session_state:
    st.session_state.role = "Farmer"

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

# --- Form ---
with st.form("entry_form"):
    name = st.text_input("Your Name")
    
    # Role selection
    role = st.selectbox("You are a:", ["Farmer", "Buyer", "Volunteer"], index=["Farmer","Buyer","Volunteer"].index(st.session_state.role))
    st.session_state.role = role  # update session
    
    # Dynamic field label based on role
    if role == "Farmer":
        main_label = "Crop"
        bank_details = st.text_input("Bank Details (optional, for Farmers only)")
    elif role == "Buyer":
        main_label = "Requirement"
        bank_details = ""
    else:
        main_label = "Support"
        bank_details = ""
    
    crop_or_need = st.text_input(main_label)
    quantity = st.text_input("Quantity (optional)")
    address = st.text_area("Address / Location")
    contact = st.text_input("Contact Number")
    
    submitted = st.form_submit_button("Submit")

if submitted:
    if not (name and role and crop_or_need and address and contact):
        st.error("❌ Please fill in all required fields.")
    else:
        # WhatsApp confirmation mandatory
        wa_message = f"Hello {name}, thanks for registering as {role} on AgriLink!"
        wa_link = get_whatsapp_link(contact, wa_message)
        
        if wa_link:
            st.info("✅ WhatsApp confirmation is required. Click the link below to open WhatsApp and send the message.")
            st.markdown(f"[Open WhatsApp and send message]({wa_link})", unsafe_allow_html=True)
            
            if st.button("✅ I sent the WhatsApp message"):
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
        else:
            st.error("⚠️ Phone number invalid. Must be a valid WhatsApp number.")

# --- Edit/Delete section ---
st.subheader("✏️ Edit or Delete Your Entry")
edit_code_input = st.text_input("Enter your edit code")
if st.button("Find Entry"):
    entry = df[df["Edit Code"] == edit_code_input]
    if not entry.empty:
        st.write("Your current entry:", entry)
        action = st.radio("Choose action:", ["Edit", "Delete"])
        
        if action == "Edit":
            new_name = st.text_input("Name", entry.iloc[0]["Name"])
            new_crop_or_need = st.text_input(main_label, entry.iloc[0]["Crop/Need"])
            new_quantity = st.text_input("Quantity", entry.iloc[0]["Quantity"])
            new_address = st.text_area("Address", entry.iloc[0]["Address"])
            new_contact = st.text_input("Contact", entry.iloc[0]["Contact"])
            new_bank = st.text_input("Bank Details", entry.iloc[0].get("Bank Details", ""))
            
            if st.button("Save Changes"):
                st.session_state.history.append(df.copy())
                df.loc[df["Edit Code"] == edit_code_input, ["Name", "Crop/Need", "Quantity", "Address", "Contact", "Bank Details"]] = [
                    new_name, new_crop_or_need, new_quantity, new_address, new_contact, new_bank
                ]
                df.to_csv(CSV_FILE, index=False)
                st.success("✅ Entry updated successfully!")
        
        elif action == "Delete":
            if st.button("Confirm Delete"):
                st.session_state.history.append(df.copy())
                df = df[df["Edit Code"] != edit_code_input]
                df.to_csv(CSV_FILE, index=False)
                st.success("🗑️ Entry deleted successfully!")
    else:
        st.error("❌ No entry found with that edit code.")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🌾 Farmers", "🛒 Buyers", "🤝 Volunteers"])

with tab1:
    st.write("👨‍🌾 Farmers and their crops:")
    farmers = df[df["Role"] == "Farmer"].drop(columns=[c for c in ["Edit Code"] if c in df.columns])
    if not farmers.empty:
        st.dataframe(farmers, use_container_width=True)
    else:
        st.info("No farmers yet.")

with tab2:
    st.write("🛒 Buyers and their requirements:")
    buyers = df[df["Role"] == "Buyer"].drop(columns=[c for c in ["Edit Code", "Bank Details"] if c in df.columns])
    if not buyers.empty:
        st.dataframe(buyers, use_container_width=True)
    else:
        st.info("No buyers yet.")

with tab3:
    st.write("🤝 Volunteers and their offers:")
    volunteers = df[df["Role"] == "Volunteer"].drop(columns=[c for c in ["Edit Code", "Bank Details"] if c in df.columns])
    if not volunteers.empty:
        st.dataframe(volunteers, use_container_width=True)
    else:
        st.info("No volunteers yet.")
