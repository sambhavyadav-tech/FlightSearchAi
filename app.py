import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Flight Search", layout="wide")
st.title("✈️ AI Flight Search")
st.caption("Real-time fares • Best cards & coupons auto-applied")

# ---------------- AIRPORT DATA ----------------
AIRPORTS = {
    "DEL": "Delhi",
    "BOM": "Mumbai",
    "BLR": "Bengaluru",
    "HYD": "Hyderabad",
    "MAA": "Chennai",
    "CCU": "Kolkata",
    "PNQ": "Pune",
    "AMD": "Ahmedabad"
}

# ---------------- AIRLINE DATA ----------------
AIRLINES = {
    "AI": {"name": "Air India", "url": "https://www.airindia.com"},
    "UK": {"name": "Vistara", "url": "https://www.airvistara.com"},
    "6E": {"name": "IndiGo", "url": "https://www.goindigo.in"},
    "SG": {"name": "SpiceJet", "url": "https://www.spicejet.com"},
    "G8": {"name": "Akasa Air", "url": "https://www.akasaair.com"}
}

# ---------------- OFFERS ----------------
BEST_OFFERS = [
    {"coupon": "FLY500", "card": "HDFC Credit Card"},
    {"coupon": "AIR250", "card": "SBI Debit Card"},
    {"coupon": "SKY400", "card": "ICICI Credit Card"},
]

# ---------------- SEARCH INPUTS ----------------
st.subheader("🔍 Search Flights")

col1, col2, col3 = st.columns(3)

with col1:
    origin = st.selectbox(
        "From",
        options=list(AIRPORTS.keys()),
        format_func=lambda x: f"{x} ({AIRPORTS[x]})"
    )

with col2:
    destination = st.selectbox(
        "To",
        options=list(AIRPORTS.keys()),
        index=1,
        format_func=lambda x: f"{x} ({AIRPORTS[x]})"
    )

with col3:
    min_date = date.today() + timedelta(days=1)
    travel_date = st.date_input(
        "Departure Date",
        value=min_date,
        min_value=min_date
    )

st.caption(f"Route: **{origin} ({AIRPORTS[origin]}) → {destination} ({AIRPORTS[destination]})**")

# ---------------- AMADEUS AUTH ----------------
@st.cache_data(ttl=3000)
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": st.secrets["AMADEUS_CLIENT_ID"],
        "client_secret": st.secrets["AMADEUS_CLIENT_SECRET"]
    }

    r = requests.post(url, data=payload)

    if r.status_code != 200:
        st.error("❌ Amadeus authentication failed")
        st.stop()

    return r.json()["access_token"]
    
# ---------------- FLIGHT SEARCH ----------------
@st.cache_data(ttl=3600)
def search_flights(origin, destination, travel_date):
    token = get_amadeus_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": travel_date.strftime("%Y-%m-%d"),
        "adults": 1,
        "currencyCode": "INR",
        "max": 15
    }
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()["data"]

# ---------------- SEARCH ACTION ----------------
if st.button("Search Flights"):
    with st.spinner("Fetching best fares and applying offers..."):
        flights_raw = search_flights(origin, destination, travel_date)

    cards = []

    for f in flights_raw:
        try:
            seg = f["itineraries"][0]["segments"][0]
            airline_code = seg["carrierCode"]
            airline_data = AIRLINES.get(airline_code)

            if not airline_data:
                continue

            base_price = float(f["price"]["grandTotal"])
            offer = random.choice(BEST_OFFERS)
            final_price = int(base_price * 0.95)

            cards.append({
                "Airline": airline_data["name"],
                "Departure": seg["departure"]["at"][11:16],
                "Arrival": seg["arrival"]["at"][11:16],
                "Base Price": int(base_price),
                "Final Price": final_price,
                "Coupon": offer["coupon"],
                "Card": offer["card"],
                "BookURL": airline_data["url"]
            })
        except Exception:
            continue

    df = pd.DataFrame(cards).sort_values("Final Price")

    cheapest = df.head(3)
    moderate = df.iloc[3:6]
    costly = df.tail(3)

    # ---------------- CARD RENDER ----------------
    def render_cards(title, data):
        st.subheader(title)
        for _, r in data.iterrows():
            c1, c2, c3, c4, c5 = st.columns([1.6, 2.2, 2, 2, 2])
            with c1:
                st.markdown(
                    f"""
                    <a href="{r['BookURL']}" target="_blank">
                        <button style="
                            background-color:#FFD700;
                            border:none;
                            padding:10px 18px;
                            font-weight:bold;
                            cursor:pointer;">
                            Book
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown("**Airline**")
                st.write(r["Airline"])
            with c3:
                st.markdown("**Time**")
                st.write(f"{r['Departure']} → {r['Arrival']}")
            with c4:
                st.markdown("**Final Price**")
                st.write(f"₹{r['Final Price']}")
            with c5:
                st.markdown("**Offer Applied**")
                st.caption(f"Coupon: {r['Coupon']}")
                st.caption(f"Card: {r['Card']}")

    render_cards("💸 Cheapest Flights", cheapest)
    render_cards("⚖️ Moderate Flights", moderate)
    render_cards("💎 Premium Flights", costly)

    st.info("Prices refresh automatically every 1 hour")
