import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import random

# ----------------------
# Streamlit page setup
# ----------------------
st.set_page_config(
    page_title="AI Flight Search",
    layout="wide"
)
st.title("✈️ AI Flight Search (Amadeus Hybrid Prototype)")
st.caption("Powered by Amadeus API • Hourly refresh • Safe public offers")

# ----------------------
# User Input
# ----------------------
with st.expander("Search Flights", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        origin = st.text_input("From (IATA Code)", value="DEL")
    with col2:
        destination = st.text_input("To (IATA Code)", value="BOM")
    with col3:
        date = st.date_input("Departure Date", value=datetime.today())

# ----------------------
# Amadeus API Authentication
# ----------------------
@st.cache_data(ttl=3500)
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": st.secrets["AMADEUS_CLIENT_ID"],
        "client_secret": st.secrets["AMADEUS_CLIENT_SECRET"]
    }
    r = requests.post(url, data=payload)
    r.raise_for_status()
    return r.json()["access_token"]

# ----------------------
# Flight Search Function
# ----------------------
@st.cache_data(ttl=3600)
def search_flights(origin, destination, date):
    token = get_amadeus_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date.strftime("%Y-%m-%d"),
        "adults": 1,
        "max": 20,
        "currencyCode": "INR"
    }
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json().get("data", [])

# ----------------------
# Search Flights Action
# ----------------------
if st.button("🔍 Search Flights"):
    with st.spinner("Fetching real-time flights from Amadeus..."):
        flights_raw = search_flights(origin, destination, date)

    # Normalize results for display
    flights = []
    for f in flights_raw:
        try:
            seg = f["itineraries"][0]["segments"][0]
            price = float(f["price"]["grandTotal"])
            # Simulate slight volatility for demo
            price *= random.uniform(0.97, 1.05)
            flights.append({
                "Airline": seg["carrierCode"],
                "Departure": seg["departure"]["at"][11:16],
                "Arrival": seg["arrival"]["at"][11:16],
                "Base Price (₹)": int(price),
                "Final Price (₹)": int(price * 0.97),  # apply demo "best deal"
                "Best Offer": "HDFC/UPI/FLY50",
                "Booking URL": f"https://www.google.com/search?q={seg['carrierCode']}+flight+booking"
            })
        except Exception:
            continue

    df = pd.DataFrame(flights)

    # ----------------------
    # Bucket by Price
    # ----------------------
    cheapest = df.nsmallest(3, "Final Price (₹)").sort_values("Departure")
    moderate = df.iloc[3:6].sort_values("Departure")
    costly = df.nlargest(3, "Final Price (₹)").sort_values("Departure")

    # ----------------------
    # Table rendering with Book buttons
    # ----------------------
    def render_table(title, data):
        st.subheader(title)
        for _, row in data.iterrows():
            c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2, 2, 1.5])
            with c1:
                st.markdown(
                    f'<a href="{row["Booking URL"]}" target="_blank">'
                    f'<button style="padding:6px 12px">Book</button></a>',
                    unsafe_allow_html=True
                )
            with c2:
                st.write(row["Airline"])
                st.caption(f"{row['Departure']} → {row['Arrival']}")
            with c3:
                st.write(f"₹{row['Base Price (₹)']}")
                st.caption("Base")
            with c4:
                st.write(f"₹{row['Final Price (₹)']}")
                st.caption(row["Best Offer"])
            with c5:
                st.success("Best Deal")

    render_table("💸 Cheapest Flights", cheapest)
    render_table("⚖️ Moderate Flights", moderate)
    render_table("💎 Costly Flights", costly)
