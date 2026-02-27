import streamlit as st
import sqlite3
import bcrypt
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TextMorph – Authentication",
    page_icon="🔐",
    layout="wide"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

.card {
    background-color: #0b1220;
    padding: 2.5rem;
    border-radius: 18px;
    box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    max-width: 460px;
    margin: auto;
}

.title {
    text-align: center;
    font-size: 38px;
    font-weight: 700;
    color: white;
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 30px;
}

.stButton button {
    width: 100%;
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    height: 46px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
}

.stButton button:hover {
    background: linear-gradient(90deg, #1e40af, #1e3a8a);
}

input {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute(
    "CREATE TABLE IF NOT EXISTS users ("
    "username TEXT, "
    "email TEXT UNIQUE, "
    "password BLOB, "
    "security_question TEXT, "
    "security_answer TEXT)"
)
conn.commit()

# ---------------- SESSION DEFAULT ----------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# ---------------- SECURITY ----------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# ---------------- SIGNUP ----------------
def signup():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Create Account")

    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password")

        question = st.selectbox(
            "Security Question",
            [
                "What is your pet name?",
                "What is your mother’s maiden name?",
                "Who is your favorite teacher?"
            ]
        )
        answer = st.text_input("Security Answer")
        submit = st.form_submit_button("Create Account")

    if submit:
        if not all([username, email, password, confirm, answer]):
            st.error("All fields are required")
        elif not re.match(r"[^@]+@[^@]+\.[a-zA-Z]{2,}", email):
            st.error("Invalid email format")
        elif not password.isalnum():
            st.error("Password must be alphanumeric")
        elif password != confirm:
            st.error("Passwords do not match")
        else:
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            if c.fetchone():
                st.error("Email already exists")
            else:
                c.execute(
                    "INSERT INTO users VALUES (?,?,?,?,?)",
                    (username, email, hash_password(password), question, answer)
                )
                conn.commit()
                st.success("Account created successfully! Please login.")
                st.session_state["page"] = "login"

    st.markdown("---")
    if st.button("← Back to Login"):
        st.session_state["page"] = "login"

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOGIN ----------------
def login():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Welcome Back")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        c.execute("SELECT username, password FROM users WHERE email=?", (email,))
        user = c.fetchone()
        if user and check_password(password, user[1]):
            st.session_state["user"] = user[0]
        else:
            st.error("Invalid email or password")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Create an account"):
            st.session_state["page"] = "signup"

    with col2:
        if st.button("Forgot password?"):
            st.session_state["page"] = "forgot"

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FORGOT PASSWORD ----------------
def forgot_password():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Reset Password")

    email = st.text_input("Email")

    if st.button("Get Security Question"):
        c.execute(
            "SELECT security_question, security_answer FROM users WHERE email=?",
            (email,)
        )
        data = c.fetchone()
        if data:
            st.session_state["fp_email"] = email
            st.session_state["fp_q"] = data[0]
            st.session_state["fp_a"] = data[1]
        else:
            st.error("Email not found")

    if "fp_q" in st.session_state:
        st.info(st.session_state["fp_q"])
        ans = st.text_input("Answer")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Reset Password"):
            if ans == st.session_state["fp_a"]:
                c.execute(
                    "UPDATE users SET password=? WHERE email=?",
                    (hash_password(new_pass), st.session_state["fp_email"])
                )
                conn.commit()
                st.success("Password updated successfully")
                st.session_state["page"] = "login"
            else:
                st.error("Incorrect answer")

    st.markdown("---")
    if st.button("← Back to Login"):
        st.session_state["page"] = "login"

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
def dashboard():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        f"<h2 style='text-align:center;color:#22c55e;'>Welcome {st.session_state['user']}</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center;color:#9ca3af;'>You are successfully logged in.</p>",
        unsafe_allow_html=True
    )
    if st.button("Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MAIN ----------------
st.markdown('<div class="title">TextMorph</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Secure User Authentication System</div>', unsafe_allow_html=True)

if "user" in st.session_state:
    dashboard()
else:
    if st.session_state["page"] == "login":
        login()
    elif st.session_state["page"] == "signup":
        signup()
    elif st.session_state["page"] == "forgot":
        forgot_password()
