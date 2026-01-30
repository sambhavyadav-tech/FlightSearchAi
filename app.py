import streamlit as st
import pandas as pd
from datetime import datetime

# App title
st.set_page_config(page_title="AI Flight Search MVP", page_icon="✈️")
st.title("AI Flight Search MVP ✈️")
st.write("Search flights by origin, destination, and date. Prices are simulated for now.")

# Input section
col1, col2, col3 = st.columns(3)
with col1:
    origin = st.text_input("From:", value="Delhi")
with col2:
    destination = st.text_input("To:", value="Mumbai")
with col3:
    date = st.date_input("Date:", min_value=datetime.today())

# Dummy flight data generator
def get_flights(origin, destination, date):
    # Normally here you'd call an API like Skyscanner
    flights = [
        {"Airline": "IndiGo", "Departure": "06:00", "Arrival": "08:00", "Price (INR)": 4500},
        {"Airline": "Air India", "Departure": "09:00", "Arrival": "11:30", "Price (INR)": 5200},
        {"Airline": "SpiceJet", "Departure": "12:00", "Arrival": "14:00", "Price (INR)": 4800},
        {"Airline": "Vistara", "Departure": "15:00", "Arrival": "17:30", "Price (INR)": 6000},
        {"Airline": "GoAir", "Departure": "18:00", "Arrival": "20:00", "Price (INR)": 4300},
    ]
    df = pd.DataFrame(flights)
    df["Origin"] = origin
    df["Destination"] = destination
    df["Date"] = date.strftime("%Y-%m-%d")
    return df

# Search button
if st.button("Search Flights"):
    results = get_flights(origin, destination, date)
    st.subheader(f"Flights from {origin} to {destination} on {date.strftime('%Y-%m-%d')}")
    st.table(results)
