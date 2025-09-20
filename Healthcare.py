import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------- Page Setup -----------------------
st.set_page_config(page_title="Healthcare in Lebanon", page_icon="🏥", layout="wide")

# Sidebar toggles
with st.sidebar:
    st.markdown("## 🛠️ Display Settings")
    mobile_fix = st.checkbox("📱 Enable Mobile View", value=False)
    dark_mode = st.checkbox("🌙 Enable Dark Mode", value=False)

# Dynamic theming
background_color = "#1e1e1e" if dark_mode else "#EDF2F7"
text_color = "#FAFAFA" if dark_mode else "#2A2A2A"
bar_color_needs = "#82A0FF" if dark_mode else "#4C6EF5"
bar_color_aid = "#FF8A80" if dark_mode else "#E53935"

# ---------------------- Custom CSS -----------------------
st.markdown(f"""
<style>
html, body, [class*="css"] {{
    color: {text_color};
    background-color: {background_color};
}}
.stPlotlyChart {{
    margin-top: 1rem;
}}
.block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    padding-left: {"1rem" if mobile_fix else "4rem"};
    padding-right: {"1rem" if mobile_fix else "4rem"};
}}
h1, h2, h3 {{
    font-weight: 700;
    text-align: center;
    color: {text_color};
    font-size: {"1.5rem" if mobile_fix else "2rem"};
}}
</style>
""", unsafe_allow_html=True)

# ---------------------- Header -----------------------
st.markdown("<h1>Healthcare in Lebanon</h1>", unsafe_allow_html=True)

st.markdown("""## Overview""")

st.markdown(""" "The health sector in Lebanon operates under the leadership of the Ministry of Public Health (MoPH). Complementing this leadership from the UN and NGO sides, the sector is co-led by the World Health Organization (WHO), with coordination efforts facilitated by WHO and Amel Association." """)

# ---------------------- Load Data -----------------------
df = pd.read_csv("healthcareds.csv")
if "refArea" in df.columns and "Districts and Governorates" not in df.columns:
    df["Districts and Governorates"] = df["refArea"].astype(str).str.split("/").str[-1].str.strip()

# Process metrics
NEEDS_COL = "Existence of special needs care centers - exists"
AID_COL = "Existence of a first aid center - exists"
df["_needs"] = df[NEEDS_COL].astype(str).str.strip().str.lower().isin({"yes", "y", "true", "t", "1", "exist", "exists"}).astype(int)
df["_aid"] = df[AID_COL].astype(str).str.strip().str.lower().isin({"yes", "y", "true", "t", "1", "exist", "exists"}).astype(int)

# ---------------------- Special Needs Chart -----------------------
st.header("Areas with Special Needs Care Centers in Lebanon")

## Areas with Special Needs Care Centers in Lebanon
st.markdown('<h3 style="text-align:left;">Context</h3>', unsafe_allow_html=True)
st.markdown("""
According to UN study done in 2023, approximately 10-15% of the Lebanese population have disabilities, either in the form of physical, sensory, cognitive, or mental. Additionally, in 2018, 61.4% of households locally were considered to have at least one member with a disability. The high prevalence of special needs cases demands for accessibility to well-maintained care centers across the various regions in Lebanon.
The bar chart demonstrates the presence of special needs care centers per area across Lebanon by count, denoted by “N”. The slider is there to indicate which areas have the least to the most accessibility to special needs care centers. The Highlight Areas feature is there to compare selected areas together.""")

counts_needs = (
    df.groupby("Districts and Governorates")["_needs"]
    .sum(min_count=1)
    .fillna(0)
    .astype(int)
    .reset_index()
    .rename(columns={"_needs": "count"})
    .sort_values("count", ascending=False)
)

top_n_needs = st.slider("Top N (Special Needs)", 1, len(counts_needs), min(10, len(counts_needs)), key="top_n_needs")
# Slice top N and copy
counts_needs_f = counts_needs.head(top_n_needs).copy()

# Select areas to highlight
highlight_needs = st.multiselect("Highlight Areas (Special Needs)", counts_needs_f["Districts and Governorates"].tolist())

# Assign color based on highlight
highlight_set = set(highlight_needs)
counts_needs_f["highlight"] = counts_needs_f["Districts and Governorates"].apply(
    lambda x: "Highlighted" if x in highlight_set else "Normal"
)

# Color map
color_map_needs = {
    "Highlighted": "#1E40AF",  # Dark blue
    "Normal": "#60A5FA"        # Light blue
}


fig_needs = px.bar(
    counts_needs_f.sort_values("count"),
    x="count",
    y="Districts and Governorates",
    orientation="h",
    text="count",
    color="highlight",  # use the label
    color_discrete_map=color_map_needs
)
fig_needs.update_traces(textposition="auto", cliponaxis=False)
fig_needs.update_layout(
    title={"text": "Areas with Special Needs Care Centers in Lebanon", "x": 0.5, "xanchor": "center"},
    paper_bgcolor=background_color,
    plot_bgcolor=background_color,
    font_color=text_color,
    xaxis_title="Number of Special Needs Care Centers",
    yaxis_title="Governorate / District",
    height=max(500, 30 * len(counts_needs_f)),
)
fig_needs.update_layout(showlegend=False)
st.plotly_chart(fig_needs, use_container_width=True)


st.markdown('<h3 style="text-align:left;">Interpretation</h3>', unsafe_allow_html=True)
st.markdown("""
- Mount Lebanon Governorate and Matn contain the highest number or special needs care centers, with 11, and 10 centers each.

- Akkar and Baabda follow suit with 7 and 6 centers each.

- Notably, Zgharta, Bsharri, Hermel, Danniyeh, and Marjeyoun are underserved, with only 1 special needs care center in each of these regions.""")

st.markdown('<h3 style="text-align:left;">The Impact</h3>', unsafe_allow_html=True)
st.markdown("""
The uneven distribution in special needs care centers poses barriers those with special needs, marking a negative impact on families as this contributes to an increase in financial strain, since they must travel to other regions with access to these centers, in addition, this creates stress to caregivers supporting, and consequently leads to limited opportunities for children to receive the required support and intervention.""")

# ---------------------- First Aid Chart -----------------------
st.header("Distribution of First Aid Centers Across Lebanese Regions")

st.markdown('<h3 style="text-align:left;">Context</h3>', unsafe_allow_html=True)
st.markdown("""The Lebanese Red Cross is considered the largest first aid assistance in Lebanon, operating via many centers and mobile medical units. In times of emergency, they can be reached using the phone number: 01-366-888 or via the website: https://www.redcross.org.lb/. The Lebanese Red Cross provides First Aid trainings, Basic Life Support (BLS) and Advanced Cardiovascular Life Support (ACLS), to medical professionals and the public. In addition to the Lebanese Red Cross, other organizations such as UNICEF, Medair, and the International Committee of the Red Cross (ICRC) provide similar support and intervention.

The bar chart showcases the distribution of first aid centers across Lebanon.  It features multiple interactive tools such as the slider which can be used to manipulate the areas contains a certain number of first aid care centers in addition to the Highlight Areas feature which allows you to select certain areas and compare them in real time.""")

counts_aid = (
    df.groupby("Districts and Governorates")["_aid"]
    .sum(min_count=1)
    .fillna(0)
    .astype(int)
    .reset_index()
    .rename(columns={"_aid": "count"})
    .sort_values("count", ascending=False)
)

top_n_aid = st.slider("Top N (First Aid)", 1, len(counts_aid), min(10, len(counts_aid)), key="top_n_aid")
highlight_aid = st.multiselect("Highlight Areas (First Aid)", counts_aid["Districts and Governorates"], key="highlight_aid")
counts_aid_f = counts_aid.head(top_n_aid).copy()
counts_aid_f["__color"] = counts_aid_f["Districts and Governorates"].isin(highlight_aid)

counts_aid_f = counts_aid.head(top_n_aid).copy()
highlight_set = set(highlight_aid)

counts_aid_f["highlight"] = counts_aid_f["Districts and Governorates"].apply(
    lambda x: "Highlighted" if x in highlight_set else "Normal"
)
color_map = {"Highlighted": "#E53935", "Normal": "#FFCDD2"}  # red + light red


fig_aid = px.bar( 
    counts_aid_f.sort_values("count"),
    x="count",
    y="Districts and Governorates",
    orientation="h",
    text="count",
    color="highlight",
    color_discrete_map=color_map
    )

fig_aid.update_traces(textposition="auto", cliponaxis=False)
fig_aid.update_layout(
    title={"text": "First Aid Centers (Ranked by Area)", "x": 0.5, "xanchor": "center"},
    paper_bgcolor=background_color,
    plot_bgcolor=background_color,
    font_color=text_color,
    xaxis_title="Number of First Aid Centers",
    yaxis_title="Governorate / District",
    height=max(500, 30 * len(counts_aid_f)),
)
fig_aid.update_layout(showlegend=False)
st.plotly_chart(fig_aid, use_container_width=True)

st.markdown('<h3 style="text-align:left;">Interpretation</h3>', unsafe_allow_html=True)
st.markdown("""
- Akkar Governorate clearly reflects the highest number of first aid centers of 48 within Lebanon, with the maroon-red color.

- Following suit are Matn and Mount Governorate with 28 and 27 each, Sidon District contains 27, and Aley District at 25 first aid centers.

- Underserved communities include Hermel at 1, Tripoli at 2, Byblos at 8, as well as Batroun and Hasbaya containing 9 first aid centers each. This is also illustrated with the lightest red shade.""")

st.markdown('<h3 style="text-align:left;">The Impact</h3>', unsafe_allow_html=True)
st.markdown("""
Based on the above distribution, areas with limited access to first aid share dire consequences to those falling ill or facing accidents. Specifically, conditions and injuries can quickly worsen, with an increased chance of death, long term complications and higher chance of infection. The lack of presence of trained individuals with the necessary supplies puts patients at high risk. This calls for immediate action of increasing the number of first aid centers to cater to the public.""")
