import streamlit as st
import pandas as pd
import random
from datetime import datetime
import textwrap

st.set_page_config(page_title="🗳️ Bill Generator", layout="centered")

# Load data
menu_df = pd.read_csv("menu.csv", encoding="utf-8")
restaurant_df = pd.read_csv("restaurant.csv", encoding="utf-8")

# Clean column names
menu_df.columns = menu_df.columns.str.strip()
restaurant_df.columns = restaurant_df.columns.str.strip()

# Rename columns
menu_df.rename(columns={"Category": "Category", "Dish Name": "Dish", "Rate": "Rate"}, inplace=True)
restaurant_df.rename(columns={"Restaurant Name": "Restaurant Name", "Tagline": "Tagline", "Location": "Location"}, inplace=True)

# App Title
st.title("🍽️ Bill Generator")

# Select location
locations = sorted(restaurant_df["Location"].dropna().unique().tolist())
selected_location = st.selectbox("📍 Select Location", locations)

# Filter restaurants
filtered_restaurants = restaurant_df[restaurant_df["Location"] == selected_location]
if filtered_restaurants.empty:
    st.error("❌ No restaurants found for this location.")
    st.stop()

# Random restaurant from selected location
restaurant = filtered_restaurants.sample(1).iloc[0]

# User inputs
total_amount = st.number_input("💰 Enter Total Bill Amount", min_value=50, step=50)
selected_date = st.date_input("🗓️ Select Bill Date", value=datetime.now().date())
now = datetime.now()
date_str = selected_date.strftime("%d-%b-%Y")
time_str = now.strftime("%I:%M %p")

# Artistic font options
font_options = [
    "Impact", "Cursive", "Georgia", "Courier New", "Monospace",
    "Brush Script MT", "Lucida Handwriting", "Papyrus", "Comic Sans MS", "Copperplate"
]
selected_font = st.selectbox("🎨 Choose Hotel Name Font Style", font_options)

# Thank-you message options
thank_you_messages = [
    "धन्यवाद! Visit Again 🙏",
    "आपली सेवा करण्यास आनंद झाला!",
    "Thank you! Come Again 😊",
    "पुन्हा भेटूया! धन्यवाद 🙏",
    "Thanks for visiting! 🙌",
    "आमच्या हॉटेलला भेट दिल्याबद्दल धन्यवाद!",
    "आपके आने के लिए धन्यवाद! फिर आइए!",
    "Thank you for your visit, come back soon!"
]

custom_message = st.text_input("✍️ Custom Thank-You Message (optional)")
random_thanks = st.checkbox("🎲 Use Random Thank-You Message", value=True)

# Generate button
if st.button("🔀 Generate Bill"):
    # Dish selection
    possible_dishes = menu_df[menu_df["Rate"] <= total_amount].copy()
    selected_dishes = []
    total = 0

    while not possible_dishes.empty and total < total_amount:
        dish = possible_dishes.sample(1).iloc[0]
        if total + dish["Rate"] <= total_amount:
            selected_dishes.append(dish)
            total += dish["Rate"]
        possible_dishes = possible_dishes[possible_dishes["Dish"] != dish["Dish"]]

    # Final thank-you line
    thank_you = custom_message if custom_message else random.choice(thank_you_messages) if random_thanks else thank_you_messages[0]

    # Generate random table and bill number
    table_no = random.randint(1, 20)
    bill_no = random.randint(1, 5000)

    # Styling for print-only content
    bill_style = """
    <style>
    @media print {
        body * {
            visibility: hidden;
        }
        #bill, #bill * {
            visibility: visible;
        }
        #bill {
            position: absolute;
            left: 0;
            top: 0;
            width: 58mm;
            font-family: 'Noto Sans Devanagari', 'Mangal', monospace;
            font-size: 12px;
        }
    }
    </style>
    """

    # Build bill HTML
    bill_html = textwrap.dedent(f"""
        <div id='bill' style='width:58mm; font-family: "Noto Sans Devanagari", "Mangal", monospace;'>
            <h3 style="
                text-align:center;
                font-family: '{selected_font}', 'Courier New', monospace;
                letter-spacing: 1px;
                font-size: 18px;
                text-shadow: 1px 1px 0 #ccc;
                margin-bottom: 4px;">
                {restaurant['Restaurant Name'].upper()}
            </h3>
            <p style='text-align:center;'>{restaurant['Tagline']}</p>
            <hr>
            <p>Bill No: {bill_no} | Table No: {table_no}</p>
            <p>{date_str} {time_str}</p>
            <hr>
            <table style='width:100%; font-size: 12px; border-collapse: collapse;'>
    """)

    for item in selected_dishes:
        bill_html += f"<tr><td>{item['Dish']}</td><td style='text-align:right;'>{item['Rate']:.0f}</td></tr>\n"

    bill_html += f"<tr><td><b>Total</b></td><td style='text-align:right;'><b>{total:.0f}</b></td></tr>"
    bill_html += f"</table><hr><p style='text-align:center;'>{thank_you}</p></div>"

    # Display the bill content with print styles
    st.markdown(bill_style + bill_html, unsafe_allow_html=True)

    # Print instruction
    st.markdown("<p style='text-align:center;'>🖨️ Use Ctrl+P or right-click to print this bill</p>", unsafe_allow_html=True)
