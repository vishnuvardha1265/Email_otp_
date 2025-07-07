# Required libraries
import streamlit as st
import smtplib
import random
import os
import time
import re
from dotenv import load_dotenv  # pip install python-dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()
EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")

# Constants
OTP_MIN = 1000
OTP_MAX = 9999
OTP_EXPIRY_SECONDS = 120  # 2 minutes


# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# Function to send OTP via email
def send_otp_email(to_email, otp):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg["Subject"] = "OTP for Verification"
    msg.attach(MIMEText(f"Your OTP for verification is: {otp}", "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send OTP: {e}")
        return False


# Streamlit app layout
st.title(" 📩 Email OTP Verification")

# Initialize session state variables
if "otp" not in st.session_state:
    st.session_state.otp = None
if "otp_time" not in st.session_state:
    st.session_state.otp_time = None
if "otp_attempts" not in st.session_state:
    st.session_state.otp_attempts = 0

# Form for email input and sending OTP
with st.form("otp_form"):
    user_email = st.text_input("Enter your email address:")
    send_clicked = st.form_submit_button("Send OTP")

    if send_clicked:
        if EMAIL is None or PASSWORD is None:
            st.error("❌ Email or Password missing in .env file")
        elif not is_valid_email(user_email):
            st.warning("⚠️ Please enter a valid email address")
        else:
            st.session_state.otp = random.randint(OTP_MIN, OTP_MAX)
            st.session_state.otp_time = time.time()
            st.session_state.otp_attempts = 0

            with st.spinner("Sending OTP..."):
                if send_otp_email(user_email, st.session_state.otp):
                    st.success(f"✅ OTP sent successfully to {user_email}")


# OTP input and verification
if st.session_state.otp:
    entered_otp = st.text_input("Enter the received OTP:", type="password")
    if st.button("Verify OTP"):
        # Check for expiry
        if time.time() - st.session_state.otp_time > OTP_EXPIRY_SECONDS:
            st.error("⏰ OTP expired. Please request a new one.")
            st.session_state.otp = None
        else:
            try:
                if int(entered_otp) == st.session_state.otp:
                    st.success("🎉 OTP verified successfully!")
                    st.session_state.otp = None
                else:
                    st.session_state.otp_attempts += 1
                    if st.session_state.otp_attempts >= 3:
                        st.error("🚫 Too many incorrect attempts. OTP locked.")
                        st.session_state.otp = None
                    else:
                        st.error("❌ Incorrect OTP. Please try again.")
            except ValueError:
                st.warning("⚠️ Please enter a 4-digit OTP only.")
