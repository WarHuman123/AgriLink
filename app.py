import streamlit as st
import pandas as pd
import random
import string
import phonenumbers
import os

# ---------- Config ----------
CSV_FILE = "agrilink_data.csv"

# ---------- Helpers ----------
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def format_whatsapp_number(number, default_region="IN"):
    """
    Validate & format number to E.164 using phonenumbers.
    Returns string without '+' (for wa.me) or None if invalid.
    """
    try:
        parsed = phonenumbers.parse(number, default_region)
        if phonenumbers.is_valid_number(parsed):
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            return e164.replace('+', '')
        else:
            return None
    except:
        return None

def get_whatsapp_link(formatted_number, message):
    # formatted_number must be e.g. '919876543210'
    return f"https://wa.me/{formatted_number}?text={message.replace(' ', '%20')}"

# ---------- Load / Init data (use session_state for live updates) ----------
if "data" not in st.session_state:
    if os.path.exists(CSV_FILE):
        st.session_state["data"] = pd.read_csv(CSV_FILE)
    else:
        st.session_state["data"] = pd.DataFrame(columns=[
            "Name", "Role", "Detail", "Quantity", "Address", "Contact", "Bank Details", "Edit Code"
        ])
        st.session_state["data"].to_csv(CSV_FILE, index=False)

# Undo/Redo stacks
if "history" not in st.session_state:
    st.session_state.history = []
if "future" not in st.session_state:
    st.session_state.future = []

# Small util to push history before change
def push_history():
    st.session_state.history.append(st.session_state["data"].copy())
    # clear future on new action
    st.session_state.future.clear()

# ---------- UI ----------
st.set_page_config(page_title="AgriLink", layout="wide")
st.title("🌱 AgriLink — Farmers · Buyers · Volunteers")

# Sidebar: undo/redo and quick reset
st.sidebar.header("Control")
if st.sidebar.button("↩️ Undo"):
    if st.session_state.history:
        st.session_state.future.append(st.session_state["data"].copy())
        st.session_state["data"] = st.session_state.history.pop()
        st.session_state["data"].to_csv(CSV_FILE, index=False)
        st.sidebar.success("Undid last change")
    else:
        st.sidebar.info("Nothing to undo")

if st.sidebar.button("↪️ Redo"):
    if st.session_state.future:
        st.session_state.history.append(st.session_state["data"].copy())
        st.session_state["data"] = st.session_state.future.pop()
        st.session_state["data"].to_csv(CSV_FILE, index=False)
        st.sidebar.success("Redid last change")
    else:
        st.sidebar.info("Nothing to redo")

if st.sidebar.button("⚠️ Reset all data (dev)"):
    st.session_state["data"] = pd.DataFrame(columns=[
        "Name", "Role", "Detail", "Quantity", "Address", "Contact", "Bank Details", "Edit Code"
    ])
    st.session_state["data"].to_csv(CSV_FILE, index=False)
    st.success("Data reset (CSV overwritten)")

# Role selector outside form so label updates immediately
role = st.selectbox("You are a:", ["Farmer", "Buyer", "Volunteer"])

# Dynamic label
if role == "Farmer":
    detail_label = "Crop"
elif role == "Buyer":
    detail_label = "Requirement"
else:
    detail_label = "Support / Service"

st.markdown("---")
st.subheader("Register / Offer — fill details and confirm via WhatsApp")

# Form for registration (clear_on_submit = False so we can control flows)
with st.form("register_form", clear_on_submit=False):
    name = st.text_input("Name", key="name_input")
    detail = st.text_input(detail_label, key="detail_input")
    quantity = st.text_input("Quantity (optional)", key="qty_input")
    address = st.text_area("Address / Location", key="addr_input")
    contact = st.text_input("Contact Number (WhatsApp required)", key="contact_input",
                           help="Include country code if possible (e.g., +91xxxxxxxxxx or 919xxxx...)")
    bank_details = st.text_input("Bank Details (optional, for Farmers only)", key="bank_input") if role == "Farmer" else ""
    submit_clicked = st.form_submit_button("Submit")

# Variables to hold the last generated edit_code (so we include it in message)
if "last_edit_code" not in st.session_state:
    st.session_state["last_edit_code"] = None

# After submit: validate, prepare WhatsApp message, require manual "I sent it" confirmation
if submit_clicked:
    # basic required field check
    if not (name and detail and address and contact):
        st.error("❌ Please fill Name, the role-specific field, Address, and Contact.")
    else:
        # format & validate whatsapp number
        formatted = format_whatsapp_number(contact)
        if not formatted:
            st.error("❌ Phone number invalid. Use a real WhatsApp-capable number.")
        else:
            # generate edit code now (so message contains it)
            edit_code = generate_code()
            st.session_state["last_edit_code"] = edit_code

            wa_message = f"Hello {name}, thanks for registering as {role} on AgriLink! Your edit code is {edit_code}."
            wa_link = get_whatsapp_link(formatted, wa_message)

            st.info("✅ WhatsApp confirmation required. Click the link below (opens WhatsApp web/app) and **send** the message. Then click 'I sent it' to complete registration.")
            st.markdown(f"[📲 Open WhatsApp with pre-filled message]({wa_link})", unsafe_allow_html=True)

            if st.button("✅ I sent the WhatsApp message (complete registration)"):
                # save entry
                push_history()
                new_row = {
                    "Name": name,
                    "Role": role,
                    "Detail": detail,
                    "Quantity": quantity,
                    "Address": address,
                    "Contact": formatted,
                    "Bank Details": bank_details if role == "Farmer" else "",
                    "Edit Code": edit_code
                }
                st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_row])], ignore_index=True)
                st.session_state["data"].to_csv(CSV_FILE, index=False)

                st.success(f"✅ Saved. Your edit code is **{edit_code}** — keep it to edit/delete your entry later.")
                # clear inputs by resetting keys
                for k in ["name_input", "detail_input", "qty_input", "addr_input", "contact_input", "bank_input"]:
                    if k in st.session_state:
                        try:
                            del st.session_state[k]
                        except:
                            pass

# ---------- Edit / Delete ----------
st.markdown("---")
st.subheader("Edit / Delete your entry (use your Edit Code)")

col1, col2 = st.columns([2, 1])
with col1:
    edit_code_query = st.text_input("Enter your edit code", key="edit_code_query")
with col2:
    if st.button("Find"):
        pass  # trigger rerun so below block runs

if edit_code_query:
    entry = st.session_state["data"][st.session_state["data"]["Edit Code"] == edit_code_query]
    if entry.empty:
        st.info("No entry found with that code.")
    else:
        entry = entry.iloc[0]
        st.write("Current entry:")
        st.table(pd.DataFrame([entry.drop(labels=["Edit Code"])]))

        action = st.radio("Action", ["Edit", "Delete"], key="action_choice")
        if action == "Edit":
            st.markdown("### Edit your data (you must re-confirm via WhatsApp to save edits)")
            new_name = st.text_input("Name", value=entry["Name"], key="edit_name")
            new_role = st.selectbox("Role", ["Farmer", "Buyer", "Volunteer"], index=["Farmer","Buyer","Volunteer"].index(entry["Role"]), key="edit_role")
            # dynamic label for edit
            if new_role == "Farmer":
                new_detail_label = "Crop"
            elif new_role == "Buyer":
                new_detail_label = "Requirement"
            else:
                new_detail_label = "Support / Service"

            new_detail = st.text_input(new_detail_label, value=entry["Detail"], key="edit_detail")
            new_quantity = st.text_input("Quantity", value=entry["Quantity"], key="edit_qty")
            new_address = st.text_area("Address", value=entry["Address"], key="edit_addr")
            new_contact = st.text_input("Contact Number (WhatsApp required)", value=entry["Contact"], key="edit_contact")
            new_bank = st.text_input("Bank Details (optional)", value=entry.get("Bank Details", ""), key="edit_bank")

            if st.button("Prepare Edit — validate WhatsApp and show message"):
                formatted_edit = format_whatsapp_number(new_contact)
                if not formatted_edit:
                    st.error("❌ New contact number is invalid for WhatsApp.")
                else:
                    # keep same edit code (entry identifier)
                    wa_message_edit = f"Hello {new_name}, your AgriLink entry was updated. Edit code: {edit_code_query}."
                    wa_link_edit = get_whatsapp_link(formatted_edit, wa_message_edit)
                    st.markdown(f"[📲 Open WhatsApp to confirm edit]({wa_link_edit})", unsafe_allow_html=True)
                    if st.button("✅ I sent the WhatsApp message for edit"):
                        push_history()
                        mask = st.session_state["data"]["Edit Code"] == edit_code_query
                        st.session_state["data"].loc[mask, ["Name", "Role", "Detail", "Quantity", "Address", "Contact", "Bank Details"]] = [
                            new_name, new_role, new_detail, new_quantity, new_address, formatted_edit, new_bank
                        ]
                        st.session_state["data"].to_csv(CSV_FILE, index=False)
                        st.success("✅ Entry updated and saved.")

        else:  # Delete
            st.warning("This will permanently delete the entry.")
            if st.button("Confirm Delete"):
                push_history()
                st.session_state["data"] = st.session_state["data"][st.session_state["data"]["Edit Code"] != edit_code_query].reset_index(drop=True)
                st.session_state["data"].to_csv(CSV_FILE, index=False)
                st.success("🗑️ Entry deleted.")

# ---------- Tabs: display per-role ----------
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["🌾 Farmers", "🛒 Buyers", "🤝 Volunteers"])

with tab1:
    st.write("👨‍🌾 Farmers")
    farmers = st.session_state["data"][st.session_state["data"]["Role"] == "Farmer"].drop(columns=[c for c in ["Edit Code"] if c in st.session_state["data"].columns])
    if not farmers.empty:
        st.dataframe(farmers, use_container_width=True)
    else:
        st.info("No farmers yet.")

with tab2:
    st.write("🛒 Buyers")
    buyers = st.session_state["data"][st.session_state["data"]["Role"] == "Buyer"].drop(columns=[c for c in ["Edit Code", "Bank Details"] if c in st.session_state["data"].columns])
    if not buyers.empty:
        st.dataframe(buyers, use_container_width=True)
    else:
        st.info("No buyers yet.")

with tab3:
    st.write("🤝 Volunteers")
    volunteers = st.session_state["data"][st.session_state["data"]["Role"] == "Volunteer"].drop(columns=[c for c in ["Edit Code", "Bank Details"] if c in st.session_state["data"].columns])
    if not volunteers.empty:
        st.dataframe(volunteers, use_container_width=True)
    else:
        st.info("No volunteers yet.")
