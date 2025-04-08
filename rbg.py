import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="Nashik Bill Generator", layout="centered")

# Load and clean restaurant CSV
restaurant_df = pd.read_csv("restaurant.csv")
restaurant_df.columns = restaurant_df.columns.str.strip().str.lower()
restaurant_df.rename(columns={
    "restaurant name": "Restaurant Name",
    "tagline": "Tagline",
    "location": "Location"
}, inplace=True)

# Load and clean menu CSV
menu_df = pd.read_csv("menu.csv")
menu_df.columns = menu_df.columns.str.strip().str.lower()
menu_df.rename(columns={
    "dish name": "Dish Name",
    "rate": "Rate",
    "dish": "Dish Name",   # fallback
    "amount": "Rate"       # fallback
}, inplace=True)

# Step 1: Get available locations and ask user to pick one
locations = restaurant_df["Location"].dropna().unique().tolist()
locations.sort()

selected_location = st.selectbox("📍 Select Location", options=locations)

# Step 2: Filter restaurants by selected location
filtered_restaurants = restaurant_df[restaurant_df["Location"] == selected_location]

# Step 3: Pick a restaurant from that location
if filtered_restaurants.empty:
    st.error("❌ No restaurants found for this location.")
    st.stop()
else:
    restaurant = filtered_restaurants.sample(1).iloc[0]

# User input for desired total
desired_total = st.number_input("💰 Enter Desired Bill Amount (₹)", min_value=50, max_value=5000, value=300, step=10)

# Try dish combinations until total ≈ desired_total
found = False
max_attempts = 1000
for _ in range(max_attempts):
    sample_dishes = menu_df.sample(random.randint(3, 8)).copy()
    sample_dishes["Qty"] = 1
    sample_dishes["Amount"] = sample_dishes["Rate"]
    total = sample_dishes["Amount"].sum()
    if abs(total - desired_total) <= 10:
        dishes = sample_dishes
        total_amount = total
        found = True
        break

if not found:
    st.error("❌ Could not find dish combination close to desired amount. Try increasing range or reducing precision.")
    st.stop()

# Date selector (defaults to today)
selected_date = st.date_input("🗓️ Select Bill Date", value=datetime.now().date())

# Optional: Time is always current (or you can make it user-selectable too)
now = datetime.now()
date_str = selected_date.strftime("%d-%b-%Y")
time_str = now.strftime("%I:%M %p")  # Keep current time

# Thermal-style 32-char layout bill text
def generate_bill_text():
    lines = []
    lines.append(f"{restaurant['Restaurant Name']:^32}")
    lines.append(f"{restaurant['Tagline']:^32}")
    lines.append(f"{restaurant['Location']:^32}")
    lines.append(f"{date_str}  {time_str:^14}")
    lines.append("-" * 32)
    lines.append(f"{'Qty':<4} {'Item':<20} {'Amt':>6}")
    lines.append("-" * 32)

    for _, row in dishes.iterrows():
        name = str(row["Dish Name"])[:20]
        qty = row["Qty"]
        amt = row["Amount"]
        lines.append(f"{qty:<4} {name:<20} ₹{amt:>5.0f}")

    lines.append("-" * 32)
    lines.append(f"{'Total':>26} ₹{total_amount:>5.0f}")
    lines.append("-" * 32)
    lines.append(f"{'🙏 धन्यवाद! पुन्हा या! 🙏':^32}")
    return "\n".join(lines)

bill_text = generate_bill_text()

# Display on screen
st.markdown("### 🧾 Thermal Bill Preview")
st.markdown(
    f"<pre style='font-size:14px; font-family:monospace;' id='bill'>{bill_text}</pre>",
    unsafe_allow_html=True
)

# Print Button
st.components.v1.html("""
    <script>
        function printBill() {
            var billContent = document.getElementById('bill').innerText;
            var printWindow = window.open('', '', 'height=600,width=300');
            printWindow.document.write('<html><head><title>Print Bill</title>');
            printWindow.document.write('<style>body{font-family:monospace; font-size:13px; white-space:pre;}</style>');
            printWindow.document.write('</head><body><pre>');
            printWindow.document.write(billContent);
            printWindow.document.write('</pre></body></html>');
            printWindow.document.close();
            printWindow.print();
        }
    </script>
    <button onclick="printBill()" style="font-size:18px;padding:10px;margin-top:10px;">🖨️ Print Bill</button>
""", height=100)

# Regenerate Bill
if st.button("🔁 Generate Another Bill"):
    st.rerun()
