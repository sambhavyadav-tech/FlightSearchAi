import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ------------------ Page setup ------------------
st.set_page_config(page_title="AI Flight Search MVP", page_icon="✈️", layout="wide")
st.title("AI Flight Search MVP ✈️")
st.write("Search flights and see the final price with discounts and offers (simulated).")

# ------------------ Input Section ------------------
with st.expander("Search Flights", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        origin = st.text_input("From:", value="Delhi")
    with col2:
        destination = st.text_input("To:", value="Mumbai")
    with col3:
        date = st.date_input("Date:", min_value=datetime.today())

    st.markdown("---")
    
    # Optional: Coupon / Credit Card selection
    col4, col5 = st.columns(2)
    with col4:
        coupon = st.selectbox("Select Coupon", ["None", "FLY50", "SAVE10", "DISCOUNT5"])
    with col5:
        card = st.selectbox("Payment Method", ["None", "Credit Card - 5% off", "Debit Card - 3% off", "UPI - 2% off"])

# ------------------ Flight Data Simulation ------------------
def get_flights(origin, destination, date):
    airlines = ["IndiGo", "Air India", "SpiceJet", "Vistara", "GoAir"]
    departure_times = ["06:00", "09:00", "12:00", "15:00", "18:00"]
    arrival_times = ["08:00", "11:30", "14:00", "17:30", "20:00"]
    base_prices = [4500, 5200, 4800, 6000, 4300]
    
    flights = []
    for i in range(len(airlines)):
        price = base_prices[i]
        
        # Apply coupon discounts
        if coupon == "FLY50":
            price -= 50
        elif coupon == "SAVE10":
            price *= 0.9
        elif coupon == "DISCOUNT5":
            price *= 0.95
        
        # Apply card discounts
        if card == "Credit Card - 5% off":
            price *= 0.95
        elif card == "Debit Card - 3% off":
            price *= 0.97
        elif card == "UPI - 2% off":
            price *= 0.98

        flights.append({
            "Airline": airlines[i],
            "Departure": departure_times[i],
            "Arrival": arrival_times[i],
            "Base Price (INR)": base_prices[i],
            "Final Price (INR)": round(price, 2),
            "Origin": origin,
            "Destination": destination,
            "Date": date.strftime("%Y-%m-%d")
        })
    
    df = pd.DataFrame(flights)
    return df

# ------------------ Search Button ------------------
if st.button("Search Flights"):
    results = get_flights(origin, destination, date)
    st.subheader(f"Flights from {origin} to {destination} on {date.strftime('%Y-%m-%d')}")
    
    # Highlight the lowest price
    def highlight_lowest(s):
        is_min = s == s.min()
        return ['background-color: lightgreen' if v else '' for v in is_min]
    
    st.dataframe(results.style.apply(highlight_lowest, subset=['Final Price (INR)']))
