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
    df = pd.DataFrame(columns=["Name", "Role", "Detail", "Quantity", "Address",
                               "Contact", "Bank Details", "Edit Code"])
    df.to_csv(CSV_FILE, index=False)

# Session state for undo/redo
if "history" not in st.session_state:
    st.session_state.history = []
if "future" not in st.session_state:
    st.session_state.future = []

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

# Form
with st.form("entry_form"):
    name = st.text_input("Your Name")
    role = st.selectbox("You are a:", ["Farmer", "Buyer", "Volunteer"])
    
    # Dynamic label based on role
    if role == "Farmer":
        detail_label = "Crop Name / Type"
    elif role == "Buyer":
        detail_label = "Requirement / Product Needed"
    else:
        detail_label = "Support / Help Offered"
        
    detail = st.text_input(detail_label)
    quantity = st.text_input("Quantity (optional)")
    address = st.text_area("Address / Location")
    contact = st.text_input("Contact Number")
    bank_details = st.text_input("Bank Details (optional, for Farmers only)") if role == "Farmer" else ""
    submitted = st.form_submit_button("Submit")

if submitted:
    if name and role and detail and address and contact:
        edit_code = generate_code()
        new_entry = {
            "Name": name,
            "Role": role,
            "Detail": detail,
            "Quantity": quantity,
            "Address": address,
            "Contact": contact,
            "Bank Details": bank_details if role == "Farmer" else "",
            "Edit Code": edit_code
        }
        st.session_state.history.append(df.copy())  # save state for undo
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        st.success(f"✅ Entry submitted successfully! Your edit code is: **{edit_code}**. Save this code to edit/delete later.")

        # Role-specific WhatsApp messages
        if role == "Farmer":
            message = f"Hello {name}, 👨‍🌾 thanks for registering as a Farmer on AgriLink! Your crop details are saved. Your edit code is {edit_code}."
        elif role == "Buyer":
            message = f"Hello {name}, 🛒 thanks for registering as a Buyer on AgriLink! Your requirement has been noted. Your edit code is {edit_code}."
        else:
            message = f"Hello {name}, 🤝 thanks for registering as a Volunteer on AgriLink! Your support offer is recorded. Your edit code is {edit_code}."

        wa_link = get_whatsapp_link(contact, message)
        if wa_link:
            st.markdown(f"👉 [Click here to send WhatsApp confirmation]({wa_link})")
        else:
            st.warning("⚠️ Phone number invalid. Could not generate WhatsApp link.")
    else:
        st.error("❌ Please fill in all required fields.")

# Edit/Delete section
st.subheader("✏️ Edit or Delete Your Entry")
edit_code_input = st.text_input("Enter your edit code")
if st.button("Find Entry"):
    entry = df[df["Edit Code"] == edit_code_input]
    if not entry.empty:
        st.write("Your current entry:", entry)

        action = st.radio("Choose action:", ["Edit", "Delete"])
        if action == "Edit":
            new_name = st.text_input("Name", entry.iloc[0]["Name"])
            new_detail = st.text_input(detail_label, entry.iloc[0]["Detail"])
            new_quantity = st.text_input("Quantity", entry.iloc[0]["Quantity"])
            new_address = st.text_area("Address", entry.iloc[0]["Address"])
            new_contact = st.text_input("Contact", entry.iloc[0]["Contact"])
            new_bank = st.text_input("Bank Details", entry.iloc[0].get("Bank Details", ""))

            if st.button("Save Changes"):
                st.session_state.history.append(df.copy())
                df.loc[df["Edit Code"] == edit_code_input, ["Name", "Detail", "Quantity", "Address", "Contact", "Bank Details"]] = [
                    new_name, new_detail, new_quantity, new_address, new_contact, new_bank
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

# Tabs
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
