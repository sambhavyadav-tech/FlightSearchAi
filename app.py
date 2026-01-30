import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------ Page Setup ------------------
st.set_page_config(page_title="AI Flight Search MVP", page_icon="✈️", layout="wide")
st.title("AI Flight Search MVP ✈️")
st.write("Flights categorized into Cheapest, Moderate, Costly. Shows best coupons and payment options (simulated).")

# ------------------ Input Section ------------------
with st.expander("Search Flights", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        origin = st.text_input("From:", value="Delhi")
    with col2:
        destination = st.text_input("To:", value="Mumbai")
    with col3:
        date = st.date_input("Date:", min_value=datetime.today())

# ------------------ Flight Data Simulation ------------------
def generate_flights(origin, destination, date):
    # Flight details
    airlines = ["IndiGo", "Air India", "SpiceJet", "Vistara", "GoAir"]
    departure_times = ["06:00", "09:00", "12:00", "15:00", "18:00"]
    arrival_times = ["08:00", "11:30", "14:00", "17:30", "20:00"]
    base_prices = [4500, 5200, 4800, 6000, 4300]

    # Websites & best offers
    websites = ["MakeMyTrip", "Cleartrip", "Goibibo"]
    coupons = ["FLY50", "SAVE10", "DISCOUNT5"]
    cards = ["Credit Card - 5% off", "Debit Card - 3% off", "UPI - 2% off"]

    flights = []
    for i in range(len(airlines)):
        price = base_prices[i]
        # Pre-select best coupon for each price category
        if price <= 4500:
            best_coupon = "FLY50"
            best_card = "Credit Card - 5% off"
        elif price <= 5200:
            best_coupon = "SAVE10"
            best_card = "Debit Card - 3% off"
        else:
            best_coupon = "DISCOUNT5"
            best_card = "UPI - 2% off"

        for site in websites:
            flights.append({
                "Airline": airlines[i],
                "Departure": departure_times[i],
                "Arrival": arrival_times[i],
                "Website": site,
                "Base Price (INR)": price,
                "Coupon": best_coupon,
                "Payment Option": best_card,
                "Origin": origin,
                "Destination": destination,
                "Date": date.strftime("%Y-%m-%d")
            })

    df = pd.DataFrame(flights)
    # Categorize flights by price
    df["Category"] = pd.cut(df["Base Price (INR)"], bins=[0, 4500, 5200, 10000], labels=["Cheapest", "Moderate", "Costly"])
    return df

# ------------------ Display Tables ------------------
if st.button("Search Flights"):
    df = generate_flights(origin, destination, date)

    categories = ["Cheapest", "Moderate", "Costly"]
    for cat in categories:
        st.subheader(f"{cat} Flights")
        cat_df = df[df["Category"] == cat].sort_values(by="Departure")
        st.dataframe(cat_df.reset_index(drop=True))
