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
            link = f"https://wa.me/{clean_number.replace('+','')}?text={message.replace(' ', '%20')}"
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

# Role selection
role = st.selectbox("You are a:", ["Farmer", "Buyer", "Volunteer"])

# Determine the label dynamically
crop_label = {"Farmer": "Crop", "Buyer": "Requirement", "Volunteer": "Support"}[role]

# Entry form
with st.form("entry_form"):
    name = st.text_input("Your Name")
    crop_or_need = st.text_input(crop_label)
    quantity = st.text_input("Quantity (optional)")
    address = st.text_area("Address / Location")
    contact = st.text_input("Contact Number")
    bank_details = st.text_input("Bank Details (optional, for Farmers only)") if role=="Farmer" else ""
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
            "Bank Details": bank_details if role=="Farmer" else "",
            "Edit Code": edit_code
        }
        st.session_state.history.append(df.copy())
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success(f"✅ Entry submitted successfully! Your edit code is: **{edit_code}**. Save this code to edit/delete later.")

        # Role-specific WhatsApp messages
        message_map = {
            "Farmer": f"Hello {name}, 👨‍🌾 thanks for registering as a Farmer on AgriLink! Your crop details are saved. Your edit code is {edit_code}.",
            "Buyer": f"Hello {name}, 🛒 thanks for registering as a Buyer on AgriLink! Your requirement has been noted. Your edit code is {edit_code}.",
            "Volunteer": f"Hello {name}, 🤝 thanks for registering as a Volunteer on AgriLink! Your support offer is recorded. Your edit code is {edit_code}."
        }
        wa_link = get_whatsapp_link(contact, message_map[role])
        if wa_link:
            st.markdown(f"👉 [Click here to send WhatsApp confirmation]({wa_link})")
        else:
            st.warning("⚠️ Phone number invalid or WhatsApp not available. Registration cannot proceed.")
    else:
        st.error("❌ Please fill in all required fields.")

# Edit/Delete section
st.subheader("✏️ Edit or Delete Your Entry")
edit_code_input = st.text_input("Enter your edit code")
find_pressed = st.button("Find Entry")

if find_pressed or st.session_state.get("editing_entry"):
    entry = df[df["Edit Code"] == edit_code_input]
    if not entry.empty:
        st.session_state["editing_entry"] = True
        st.write("Your current entry:", entry)
        
        action = st.radio("Choose action:", ["Edit", "Delete"], key="action_radio")
        
        if action == "Edit":
            with st.form("edit_form"):
                new_name = st.text_input("Name", entry.iloc[0]["Name"])
                new_crop_or_need = st.text_input("Crop/Need", entry.iloc[0]["Crop/Need"])
                new_quantity = st.text_input("Quantity", entry.iloc[0]["Quantity"])
                new_address = st.text_area("Address", entry.iloc[0]["Address"])
                new_contact = st.text_input("Contact", entry.iloc[0]["Contact"])
                new_bank = st.text_input("Bank Details", entry.iloc[0].get("Bank Details", ""))
                save_changes = st.form_submit_button("Save Changes")
                if save_changes:
                    st.session_state.history.append(df.copy())
                    df.loc[df["Edit Code"] == edit_code_input, ["Name","Crop/Need","Quantity","Address","Contact","Bank Details"]] = [
                        new_name, new_crop_or_need, new_quantity, new_address, new_contact, new_bank
                    ]
                    df.to_csv(CSV_FILE, index=False)
                    st.success("✅ Entry updated successfully!")
                    st.session_state.pop("editing_entry")
        else:  # Delete
            delete_confirm = st.button("Confirm Delete")
            if delete_confirm:
                st.session_state.history.append(df.copy())
                df = df[df["Edit Code"] != edit_code_input]
                df.to_csv(CSV_FILE, index=False)
                st.success("🗑️ Entry deleted successfully!")
                st.session_state.pop("editing_entry")
    else:
        st.error("❌ No entry found with that edit code.")

# Tabs for display
tab1, tab2, tab3 = st.tabs(["🌾 Farmers", "🛒 Buyers", "🤝 Volunteers"])

with tab1:
    st.write("👨‍🌾 Farmers and their crops:")
    farmers = df[df["Role"]=="Farmer"].drop(columns=["Edit Code"])
    st.dataframe(farmers.reset_index(drop=True), use_container_width=True) if not farmers.empty else st.info("No farmers yet.")

with tab2:
    st.write("🛒 Buyers and their requirements:")
    buyers = df[df["Role"]=="Buyer"].drop(columns=["Edit Code","Bank Details"])
    st.dataframe(buyers.reset_index(drop=True), use_container_width=True) if not buyers.empty else st.info("No buyers yet.")

with tab3:
    st.write("🤝 Volunteers and their offers:")
    volunteers = df[df["Role"]=="Volunteer"].drop(columns=["Edit Code","Bank Details"])
    st.dataframe(volunteers.reset_index(drop=True), use_container_width=True) if not volunteers.empty else st.info("No volunteers yet.")
