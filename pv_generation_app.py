import pandas as pd
from pvlive_api import PVLive
from datetime import datetime
import streamlit as st
import time

# Streamlit setup
st.set_page_config(page_title="PV Generation Data", layout="wide")
st.title("Live PV Generation Data")
st.markdown("This app fetches and displays PV generation data in real-time.")

# Initialize PVLive API
actual_api = PVLive(ssl_verify=False)

# Sidebar configuration
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=10, max_value=600, value=60, step=10)

# Main function to fetch and return data
@st.cache_data(ttl=refresh_rate)
def fetch_data():
    start_time = pd.Timestamp.now('GMT').normalize()
    end_time = start_time + pd.Timedelta(days=1)
    actual_data = actual_api.between(start_time, end_time, period=5, dataframe=True)

    if 'generation_mw' in actual_data.columns:
        # Convert to Europe/Paris timezone
        actual_data['time'] = actual_data['datetime_gmt'].dt.tz_convert('Europe/Paris')
        return actual_data[['time', 'generation_mw']]

    return pd.DataFrame()  # Return an empty DataFrame if column is missing

# Display live chart
placeholder = st.empty()  # Placeholder for the chart
last_update_placeholder = st.sidebar.empty()  # Placeholder for last update time

while True:
    # Fetch new data
    data = fetch_data()

    # Check if data is available
    if not data.empty:
        with placeholder.container():
            st.line_chart(
                data=data.set_index('time')['generation_mw'], 
                use_container_width=True
            )
        last_update_placeholder.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    else:
        st.error("No generation data available. Please check the data source or time range.")

    # Wait before refreshing
    time.sleep(refresh_rate)
