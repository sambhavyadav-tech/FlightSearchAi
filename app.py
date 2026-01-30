import streamlit as st
import requests
from datetime import datetime,date, timedelta
import pandas as pd
import random

st.set_page_config(page_title="AI Flight Search", layout="wide")
st.title("✈️ AI Flight Search (Prototype)")
st.caption("Real-time fares • Best coupons • Smart booking")

# ------------------ FAIL-SAFE TOKEN ------------------
@st.cache_data(ttl=1700)
def get_amadeus_token():
    try:
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": st.secrets["AMADEUS_CLIENT_ID"],
            "client_secret": st.secrets["AMADEUS_CLIENT_SECRET"],
        }
        r = requests.post(url, data=data)
        r.raise_for_status()
        token = r.json()["access_token"]
        return token
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to get Amadeus token: {e}")
        st.stop()

token = get_amadeus_token()

# ------------------ AIRPORT SEARCH ------------------
@st.cache_data(ttl=86400)
def search_airports(keyword, token):
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "subType": "AIRPORT,CITY",
        "keyword": keyword,
        "page[limit]": 10,
        "view": "LIGHT",
    }
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()["data"]

# ------------------ FLIGHT SEARCH ------------------
def search_flights(token, origin, destination, dep_date, adults, children, travel_class):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": dep_date,
        "adults": adults,
        "travelClass": travel_class.upper(),
        "currencyCode": "INR",
        "max": 20,
    }
    if children > 0:
        params["children"] = children

    try:
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 401:
            get_amadeus_token.clear()
            token = get_amadeus_token()
            headers["Authorization"] = f"Bearer {token}"
            r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Flight search failed: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.stop()

# ------------------ SEARCH UI ------------------
st.subheader("🔍 Search Flights")

col1, col2 = st.columns(2)
with col1:
    from_query = st.text_input("From (City / Airport)")
    origin_code = None
    if len(from_query) >= 3:
        from_results = search_airports(from_query, token)
        from_options = {
            f"{x['iataCode']} ({x['address']['cityName']}, {x['address']['countryName']})": x["iataCode"]
            for x in from_results if "iataCode" in x
        }
        if from_options:
            from_label = st.selectbox("Select Origin", from_options.keys())
            origin_code = from_options[from_label]

with col2:
    to_query = st.text_input("To (City / Airport)")
    dest_code = None
    if len(to_query) >= 3:
        to_results = search_airports(to_query, token)
        to_options = {
            f"{x['iataCode']} ({x['address']['cityName']}, {x['address']['countryName']})": x["iataCode"]
            for x in to_results if "iataCode" in x
        }
        if to_options:
            to_label = st.selectbox("Select Destination", to_options.keys())
            dest_code = to_options[to_label]

c1, c2, c3, c4 = st.columns(4)
with c1:
    dep_date = st.date_input("Departure Date", min_value=date.today() + timedelta(days=1))
with c2:
    adults = st.number_input("Adults", 1, 9, 1)
with c3:
    children = st.number_input("Children", 0, 9, 0)
with c4:
    travel_class = st.selectbox("Class", ["Economy", "Business"])

search = st.button("🔎 Search Flights")

# ------------------ SEARCH RESULTS ------------------
if search and origin_code and dest_code:
    data = search_flights(token, origin_code, dest_code, dep_date.isoformat(), adults, children, travel_class)

    BEST_OFFERS = [
        {"coupon": "FLY500", "card": "HDFC Credit Card"},
        {"coupon": "AIR250", "card": "SBI Debit Card"},
        {"coupon": "SKY400", "card": "ICICI Credit Card"}
    ]

    flights = []
    for f in data["data"]:
        segment = f["itineraries"][0]["segments"][0]
        dep_time = datetime.fromisoformat(segment["departure"]["at"])
        arr_time = datetime.fromisoformat(segment["arrival"]["at"])
        duration = arr_time - dep_time
        duration_str = str(duration).split(".")[0]  # HH:MM:SS

        base_price = float(f["price"]["base"])
        total_price = float(f["price"]["total"])
        offer = random.choice(BEST_OFFERS)
        final_price = int(total_price * 0.95)  # simulate offer

        flights.append({
            "Airline": data["dictionaries"]["carriers"][segment["carrierCode"]],
            "Departure": dep_time.strftime("%a, %b %d, %Y • %H:%M"),
            "Arrival": arr_time.strftime("%a, %b %d, %Y • %H:%M"),
            "Duration": duration_str,
            "BaseFare": int(base_price),
            "FareBeforeOffer": int(total_price),
            "FinalFare": final_price,
            "Coupon": offer["coupon"],
            "Card": offer["card"],
            "Book": f"https://www.google.com/flights?hl=en#flt={origin_code}.{dest_code}.{dep_date}"
        })

    df = pd.DataFrame(flights).sort_values("Departure")

    cheapest, moderate, premium = st.tabs(
        ["💸 Cheapest", "⚖️ Moderate", "💎 Premium"]
    )

    def render_tab(tab, data):
        with tab:
            for _, r in data.iterrows():
                with st.container():
                    c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 1.5, 2, 1])
                    c1.markdown(f"### {r['Airline']}")
                    c2.markdown(f"<span style='background-color:#FFD700;padding:3px;border-radius:4px;'>🕒 {r['Departure']} → {r['Arrival']}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span style='background-color:#FFD700;padding:3px;border-radius:4px;'>⏱ Duration: {r['Duration']}</span>\n"
                                f"<span style='background-color:#FFD700;padding:3px;border-radius:4px;'>💰 Base: ₹{r['BaseFare']}\nFare: ₹{r['FareBeforeOffer']}\nAfter Offer: ₹{r['FinalFare']}</span>", unsafe_allow_html=True)
                    c4.markdown(f"🏷 Coupon: {r['Coupon']}")
                    c5.markdown(f"💳 Card: {r['Card']}")
                    c6.markdown(
                        f"""
                        <a href="{r['Book']}" target="_blank">
                        <button style="
                            background-color:#FFD700;
                            padding:10px;
                            border:none;
                            border-radius:6px;
                            font-weight:bold;">
                            BOOK
                        </button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )

    render_tab(cheapest, df.nsmallest(5, "FinalFare"))
    render_tab(moderate, df.iloc[5:10])
    render_tab(premium, df.nlargest(5, "FinalFare"))

    st.info("Prices refresh automatically every 1 hour")
