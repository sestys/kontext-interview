import streamlit as st
import pandas as pd

analytics_hourly = pd.read_csv('analytics_hourly.csv')
analytics_hourly = analytics_hourly[analytics_hourly['country_tier'] == 'US']

platform_agg = pd.read_csv('per_platform_aggregate.csv')
content_agg = pd.read_csv('per_content_aggregate.csv')


# --- Streamlit Layout ---
st.set_page_config(page_title="Ready or Not - Kontext.so performance", layout="wide")
st.markdown("<h1 style='text-align: center; width: 100%;'>Ready or Not - Kontext.so performance</h1>", unsafe_allow_html=True)
with open("logo.svg", "r") as f:
    svg = f.read()

st.markdown(
    f"""
    <div style="position: absolute; top: 10px; left: 10px; z-index: 9999;filter: brightness(10)">
        {svg}
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# --- KPI Metrics ---
total_views = int(analytics_hourly['views'].sum())
total_clicks = int(analytics_hourly['clicks'].sum())
overall_ctr = total_clicks / total_views

col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 2, 2])
col0.metric("Ad Views promised", "350,000")
col1.metric("Ad Views", f"{total_views:,}")
col2.metric("Ad Clicks", f"{total_clicks:,}")
col3.metric("CTR", f"{overall_ctr:.2%}")
col4.metric("CTR promised", "1.25%")


st.markdown("---")

# --- KPI Metrics Unique ---
unique_views = int(platform_agg['total_unique_views'].sum())
unique_clicks = int(platform_agg['total_unique_clicks'].sum())
unique_ctr = unique_clicks / unique_views


left_spacer1, col11, col21, col31, right_spacer1 = st.columns([2, 2, 2, 2, 2])
col11.metric("Unique Ad Views", f"{unique_views:,}")
col21.metric("Unique Ad Clicks", f"{unique_clicks:,}")
col31.metric("Uniqeu Ad CTR", f"{unique_ctr:.2%}")

st.markdown("---")


views_per_platform, views_per_publisher = st.columns(2)
# --- View split per Platform ---
platform_agg['views_dist'] = platform_agg['total_views'] / platform_agg['total_views'].sum() * 100

with views_per_platform:
    st.subheader("Views distribution (%) per Platform")
    st.bar_chart(platform_agg[['platform','views_dist']].set_index('platform'))


# --- View split per Publisher ---
publisher_agg = (analytics_hourly.assign(publisher=analytics_hourly['publisher_token'].str.split('-').str[0])
           .groupby('publisher')['views']
           .sum()
           .reset_index())
publisher_agg['views_dist'] = publisher_agg['views'] / publisher_agg['views'].sum() * 100

with views_per_publisher:
    st.subheader("Views distribution (%) per Publisher")
    st.bar_chart(publisher_agg[['publisher','views_dist']].set_index('publisher'))


# --- Top 10 Performing Ad Copy ---
st.subheader("Top 10 Viewed Ad Copy")
top_ads = content_agg[['cleaned_content', 'total_views']]
top_ads.rename(columns={'cleaned_content': 'Ad Copy', 'total_views': 'Views'}, inplace=True)
top_ads = top_ads.sort_values(by='Views', ascending=False).head(10).reset_index()
st.dataframe(top_ads[['Ad Copy', 'Views']])

