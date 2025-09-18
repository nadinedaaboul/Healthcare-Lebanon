# Healthcare.py — final, no sidebar controls, area locked to "Districts and Governorates"
import os
from PIL import Image
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- Page setup & styling ----------------
st.markdown("""
<style>
/* ---------- GLOBAL STYLING ---------- */
html, body, [class*="css"] {
    color: #2A2A2A;
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
}

/* ---------- PAGE PADDING ---------- */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ---------- HEADINGS ---------- */
h1, h2, h3 {
    font-weight: 700;
    text-align: center;
    color: #2A2A2A;
}

/* ---------- PLOTLY CHART MARGINS ---------- */
.stPlotlyChart {
    margin-top: 1rem;
    margin-bottom: 2rem;
}

/* ---------- MOBILE OPTIMIZATION ---------- */
@media screen and (max-width: 768px) {
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    h1 {
        font-size: 1.4rem !important;
    }

    h2 {
        font-size: 1.2rem !important;
    }

    h3 {
        font-size: 1.05rem !important;
    }

    .stPlotlyChart {
        margin-left: -10px;
        margin-right: -10px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- Load data ----------------
df = pd.read_csv("healthcareds.csv")

# Ensure the locked area column exists
AREA_COL = "Districts and Governorates"
if AREA_COL not in df.columns:
    if "refArea" in df.columns:
        df[AREA_COL] = df["refArea"].astype(str).str.split("/").str[-1].str.strip()
    else:
        st.error(f'Required column "{AREA_COL}" is missing and cannot be derived (no "refArea").')
        st.stop()

# Helper to convert existence columns to 0/1
def to_binary(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0)
    yes_vals = {"yes", "y", "true", "t", "1", "exist", "exists"}
    return series.astype(str).str.strip().str.lower().isin(yes_vals).astype(int)

# Build BOTH metric columns up-front
NEEDS_COL = "Existence of special needs care centers - exists"
AID_COL   = "Existence of a first aid center - exists"
if NEEDS_COL not in df.columns:
    st.error(f'Column "{NEEDS_COL}" not found in your CSV.'); st.stop()
if AID_COL not in df.columns:
    st.error(f'Column "{AID_COL}" not found in your CSV.'); st.stop()

df["_needs"] = to_binary(df[NEEDS_COL])
df["_aid"]   = to_binary(df[AID_COL])

# ============================
# PAGE OVERVIEW (under H1)
# ============================
st.markdown("### Overview")
st.markdown("""
> “The health sector in Lebanon operates under the leadership of the Ministry of Public Health (MoPH). Complementing this leadership from the UN and NGO sides, the sector is co-led by the World Health Organization (WHO), with coordination efforts facilitated by WHO and Amel Association.”
""")

st.divider()

# ============================
# SPECIAL NEEDS SECTION
# ============================
st.markdown("<h2 style='text-align:center;'>Areas with Special Needs Care Centers in Lebanon</h2>", unsafe_allow_html=True)

# Aggregate counts (build before using in slider)
df["_area_needs"] = df[AREA_COL].astype(str).str.strip()
counts_needs = (
    df.groupby("_area_needs", dropna=False)["_needs"]
      .sum(min_count=1).fillna(0).astype(int)
      .reset_index().rename(columns={"_area_needs": "Area", "_needs": "count"})
      .sort_values("count", ascending=False)
)

st.markdown("### Context")
st.markdown("""
According to a UN study done in 2023, approximately **10–15%** of the Lebanese population have disabilities—physical, sensory, cognitive, or mental. Additionally, in **2018**, **61.4%** of households locally were considered to have at least one member with a disability.  
The high prevalence of special needs cases demands accessibility to well-maintained care centers across the various regions in Lebanon.

The **bar chart** demonstrates the presence of special needs care centers per area across Lebanon by count, denoted by **“N.”**  
Use the **Top N** slider to view the most accessible areas.
""")

# ---- Interactivity (Top N + optional highlight) ----
c1, c2 = st.columns([2,2])
with c1:
    top_n_needs = st.slider("Top N Areas (Special Needs)", 1, min(len(counts_needs), 25), 10)
with c2:
    highlight_needs = st.multiselect("Highlight areas (Special Needs)", counts_needs["Area"], key="hi_needs")

counts_needs_f = counts_needs.head(top_n_needs).copy()
color_map = {True: "#4C6EF5", False: "#CBD5E1"}
counts_needs_f["__color"] = counts_needs_f["Area"].isin(highlight_needs)

fig_needs = px.bar(
    counts_needs_f.sort_values("count"),
    x="count", y="Area", orientation="h", text="count",
    color=counts_needs_f["__color"].map(color_map),
    color_discrete_sequence=px.colors.qualitative.Plotly)

fig_needs.update_traces(
    textposition="auto",
    cliponaxis=False
)


fig_needs.update_traces(textposition="outside", cliponaxis=False)
fig_needs.update_layout(
    title={"text":"Areas with Special Needs Care Centers in Lebanon","x":0.5,"xanchor":"center"},
    xaxis_title="Number of Special Needs Care Centers",
    yaxis_title="Governorate / District",
    showlegend=False,
    height=max(500, 28 * len(counts_needs_f)),
    paper_bgcolor="#EDF2F7", plot_bgcolor="#EDF2F7",
    margin=dict(l=10, r=20, t=60, b=20),
    xaxis=dict(gridcolor="rgba(0,0,0,0.08)", zeroline=False),
    yaxis=dict(showgrid=False, title_standoff=10),
)
st.plotly_chart(fig_needs, use_container_width=True)



st.markdown("### Interpretation")
st.markdown("""
- **Mount Lebanon Governorate** and **Matn** contain the highest number of special needs care centers, with **11** and **10** centers each.  
- **Akkar** and **Baabda** follow with **7** and **6** centers each.  
- Notably, **Zgharta, Bsharri, Hermel, Danniyeh, and Marjeyoun** are underserved, with only **1** center in each of these regions.
""")

st.markdown("### The Impact")
st.markdown("""
The uneven distribution of special needs care centers poses barriers to those with special needs, negatively impacting families.  
It contributes to **financial strain** (travel to other regions), increased **stress for caregivers**, and **limited opportunities** for children to receive the required support and intervention.
""")

st.divider()

# ============================
# FIRST AID SECTION (Ranked Bar)
# ============================
st.markdown("<h2 style='text-align:center;'>Distribution of First Aid Centers Across Lebanese Regions</h2>", unsafe_allow_html=True)

# Aggregate counts
df["_area_aid"] = df[AREA_COL].astype(str).str.strip()
counts_aid = (
    df.groupby("_area_aid", dropna=False)["_aid"]
      .sum(min_count=1).fillna(0).astype(int)
      .reset_index().rename(columns={"_area_aid": "Area", "_aid": "count"})
      .sort_values("count", ascending=False)
)

st.markdown("### Context")
st.markdown("""
The **Lebanese Red Cross** is considered the largest first aid assistance in Lebanon, operating via many centers and mobile medical units.  
In times of emergency, they can be reached at **01-366-888** or via the website: https://www.redcross.org.lb/.  
They provide **First Aid** training, **Basic Life Support (BLS)**, and **Advanced Cardiovascular Life Support (ACLS)** to medical professionals and the public.  
In addition to the Lebanese Red Cross, other organizations such as **UNICEF**, **Medair**, and the **International Committee of the Red Cross (ICRC)** provide similar support and intervention.

The visualization showcases the distribution of first aid centers across Lebanon.  
Use the **Top N** slider to see areas with the most first aid centers. The **red palette** echoes the Red Cross color.
""")

d1, d2 = st.columns([2,2])
with d1:
    top_n_aid = st.slider("Top N (First Aid)", 1, min(len(counts_aid), 25), 10)

with d2:
    highlight_aid = st.multiselect("Highlight areas (First Aid)", counts_aid["Area"], key="hi_aid")

counts_aid_f = counts_aid.head(top_n_aid).copy()
color_map_aid = {True: "#E53935", False: "#F9B5B3"}
counts_aid_f["__color"] = counts_aid_f["Area"].isin(highlight_aid)

# Plot
fig_aid = px.bar(
counts_aid_f.sort_values("count"),
x="count", y="Area", orientation="h", text="count",
color_discrete_sequence=["#E53935"] # Red
)

fig_aid.update_traces(
    textposition="auto",
    cliponaxis=False
)


fig_aid.update_traces(textposition="outside", cliponaxis=False)
fig_aid.update_layout(
title={"text":"First Aid Centers (Ranked by Area)","x":0.5},
xaxis_title="Number of First Aid Centers",
yaxis_title="Governorate / District",
height=max(500, 28 * len(counts_aid_f)),
paper_bgcolor="#EDF2F7", plot_bgcolor="#EDF2F7",
margin=dict(l=10, r=20, t=60, b=20),
xaxis=dict(gridcolor="rgba(0,0,0,0.08)", zeroline=False),
yaxis=dict(showgrid=False, title_standoff=10)
)
st.plotly_chart(fig_aid, use_container_width=True)


st.markdown("### Interpretation")
st.markdown("""
- **Akkar Governorate** has 48 first aid centers, clearly reflecting the highest number within Lebanon.  
- Following are **Matn** and **Mount Lebanon Governorate**, containing 28 and 27 centers each; meanwhile, **Sidon District**; and **Aley District** carry 27 and 25 centers, respectively.  
- Underserved communities are **Hermel** with 1 center, **Tripoli** at 2 centers. The number increases in **Byblos** with 8 centers, as well as **Batroun** and **Hasbaya** with **9** each.
""")

st.markdown("### The Impact")
st.markdown("""
Areas with limited access to first aid face **dire consequences** during illness or accidents.  
Conditions and injuries can worsen quickly, with higher risks of **death**, **long-term complications**, and **infection**.  
The lack of trained responders and necessary supplies puts patients at high risk, this calls for **immediate action** to expand first aid coverage.
""")
