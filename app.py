import streamlit as st
import pandas as pd
import urllib.parse
import os

st.set_page_config(page_title="AgriLink", layout="wide")

CSV_FILE = "registrations.csv"

# ---------- CSV Setup ----------
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "Role", "Name", "Phone", "Crop/Requirement/Service", "Bank Details"
    ])
    df_init.to_csv(CSV_FILE, index=False)


def load_data():
    df = pd.read_csv(CSV_FILE)
    # Reset index for clean serials
    df.reset_index(drop=True, inplace=True)
    df.index += 1
    return df


def save_data(entry):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)


# ---------- Sidebar ----------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Register", "View Data"])

# ---------- Register Page ----------
if page == "Register":
    st.title("🌾 AgriLink Registration")

    with st.form("registration_form", clear_on_submit=True):
        role = st.selectbox("You are a:", ["Farmer", "Buyer", "Volunteer"])

        name = st.text_input("Full Name")
        phone = st.text_input("WhatsApp Number (with country code, e.g. +91)")

        # Role-specific field
        if role == "Farmer":
            specific = st.text_input("Crop")
        elif role == "Buyer":
            specific = st.text_input("Requirement")
        else:
            specific = st.text_input("Service you can support with")

        # Optional bank details (only visible for Farmer)
        bank_details = ""
        if role == "Farmer":
            bank_details = st.text_input("Bank Details (Optional)")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name or not phone or not specific:
                st.error("⚠️ Please fill all required fields.")
            else:
                # WhatsApp confirmation message
                msg = f"Hello, I am registering as a {role}.\n\n"
                msg += f"👤 Name: {name}\n📞 Phone: {phone}\n"

                if role == "Farmer":
                    msg += f"🌱 Crop: {specific}\n"
                elif role == "Buyer":
                    msg += f"🛒 Requirement: {specific}\n"
                else:
                    msg += f"🤝 Service: {specific}\n"

                if role == "Farmer" and bank_details:
                    msg += f"🏦 Bank Details: {bank_details}\n"

                encoded_msg = urllib.parse.quote(msg)
                wa_url = f"https://wa.me/{phone}?text={encoded_msg}"

                st.markdown(
                    f"### ✅ WhatsApp confirmation is mandatory\n"
                    f"[👉 Click here to confirm on WhatsApp]({wa_url})"
                )

                # Save to CSV
                entry = {
                    "Role": role,
                    "Name": name,
                    "Phone": phone,
                    "Crop/Requirement/Service": specific,
                    "Bank Details": bank_details
                }
                save_data(entry)

                st.success("✅ Registration saved successfully!")

                # Rerun so table updates instantly
                st.experimental_rerun()

# ---------- View Data Page ----------
elif page == "View Data":
    st.title("📊 Registered Users")
    df = load_data()

    if df.empty:
        st.info("No registrations yet.")
    else:
        st.dataframe(df, use_container_width=True)
