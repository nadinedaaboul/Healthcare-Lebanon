import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Healthcare in Lebanon", page_icon="🏥", layout="wide")
st.markdown("<h1 style='text-align: center;'>Healthcare in Lebanon</h1>", unsafe_allow_html=True)


# --- Upload CSV ---
df = pd.read_csv("healthcareds.csv")

import os
from PIL import Image  # Pillow comes with Streamlit

# ==== STATIC PHOTO ROTATOR ====
IMAGE_DIR = "images"
image_files = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)
               if f.lower().endswith((".jpg", ".jpeg", ".png"))]

if "carousel_idx" not in st.session_state:
    st.session_state.carousel_idx = 0

if image_files:
    idx = st.session_state.carousel_idx
    img = Image.open(image_files[idx])

    # Counter + dots
    count_text = f"{idx+1} / {len(image_files)}"
    dots = " • ".join(["●" if i == idx else "○" for i in range(len(image_files))])
    st.markdown(
        f"<p style='text-align:center; margin:0; font-size:14px; color:#666;'>{count_text}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align:center; margin:0 0 6px 0; font-size:14px; color:#666;'>{dots}</p>",
        unsafe_allow_html=True,
    )

    # Display current image
    st.image(img, use_container_width=True, caption=os.path.basename(image_files[idx]))

    # Navigation buttons
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("◀︎ Previous"):
            st.session_state.carousel_idx = (idx - 1) % len(image_files)
    with c3:
        if st.button("Next ▶︎"):
            st.session_state.carousel_idx = (idx + 1) % len(image_files)
else:
    st.caption("No images found in the 'images/' folder.")
# ==== END STATIC PHOTO ROTATOR ====




# --- Create helper column from refArea ---
if "refArea" in df.columns and "Districts and Governorates" not in df.columns:
    df["Districts and Governorates"] = (
        df["refArea"].astype(str).str.split("/").str[-1].str.strip()
    )

    
    st.markdown('### Overview')
    st.markdown("""“The health sector in Lebanon operates under the leadership of the Ministry of Public Health (MoPH). Complementing this leadership from the UN and NGO sides, the sector is co-led by the World Health Organization (WHO), with coordination efforts facilitated by WHO and Amel Association.”""")

st.subheader("Areas with Special Needs Care Centers in Lebanon")
st.markdown('### Context')
st.markdown("""According to UN study done in 2023, approximately 10-15 percent of the Lebanese population have disabilities, either in the form of physical, sensory, cognitive, or mental. Additionally, in 2018, 61.4 percent of households locally were considered to have at least one member with a disability. The high prevalence of special needs cases demands for accessibility to well-maintained care centers across the various regions in Lebanon. 
The bar chart demonstrates the presence of special needs care centers per area across Lebanon by count, denoted by “N”. The slider is there to indicate which areas have the least to the most accessibility to special needs care centers."""
)
    # Ensure metric column exists
NEEDS_COL = "Existence of special needs care centers - exists"
if NEEDS_COL not in df.columns:
        st.error(f'Column "{NEEDS_COL}" not found in your CSV.')
        st.stop()

    # Convert to numeric (handles Yes/No)
if pd.api.types.is_numeric_dtype(df[NEEDS_COL]):
        df["_needs_metric"] = df[NEEDS_COL].fillna(0)
else:
        yes_vals = {"yes", "y", "true", "t", "1", "exist", "exists"}
        df["_needs_metric"] = (
            df[NEEDS_COL].astype(str).str.strip().str.lower().isin(yes_vals)
        ).astype(int)

    # Pick area column
area_col1 = st.selectbox(
        "Area column for chart",
        options=list(df.columns),
        index=(df.columns.get_loc("Districts and Governorates")
               if "Districts and Governorates" in df.columns else 0)
    )

counts = (
        df.groupby(area_col1)["_needs_metric"]
          .sum(min_count=1).fillna(0).astype(int)
          .reset_index().rename(columns={area_col1: "Area", "_needs_metric": "count"})
          .sort_values("count", ascending=False)
    )

if counts.empty:
        st.warning("No data to display.")
        st.stop()

    # Slider for threshold
max_count = int(counts["count"].max())
min_needed = st.slider(
        "Show areas with at least N centers",
        min_value=0, max_value=max_count, value=0, step=1
    )
counts_f = counts[counts["count"] >= min_needed]

    # Plot bar chart
fig1 = px.bar(
        counts_f.sort_values("count"),
        x="count", y="Area",
        orientation="h",
        text="count",
        color_discrete_sequence=["#4C6EF5"],
    )
fig1.update_traces(textposition="outside", cliponaxis=False)
fig1.update_layout(
        title={"text": "Areas with Special Needs Care Centers in Lebanon",
               "x": 0.5, "xanchor": "center"},
        title_font=dict(size=22),
        xaxis_title="Number of Special Needs Care Centers",
        yaxis_title="Governorate / District",
        showlegend=False,
        height=max(500, 28 * len(counts_f)),
        paper_bgcolor="#EDF2F7",
        plot_bgcolor="#EDF2F7",
    )
st.plotly_chart(fig1, use_container_width=True)

st.markdown("### Interpretation")
st.markdown("""
    - Mount Lebanon Governorate and Matn contain the highest number or special needs care centers, with 11, and 10 centers each.
    - Akkar and Baabda follow suit with 7 and 6 centers each. 
    - Notably, Zgharta, Bsharri, Hermel, Danniyeh, and Marjeyoun are underserved, with only 1 special needs care center in each of these regions.
""")

st.markdown("#### The Impact")
st.markdown("""The uneven distribution in special needs care centers poses barriers those with special needs, marking a negative impact on families as this contributes to an increase in financial strain, since they must travel to other regions with access to these centers, in addition, this creates stress to caregivers supporting, and consequently leads to limited opportunities for children to receive the required support and intervention.""")

st.subheader("Distribution of First Aid Centers Across Lebanese Regions")
st.markdown('### Context')
st.markdown("""The Lebanese Red Cross is considered the largest first aid assistance in Lebanon, operating via many centers and mobile medical units. In times of emergency, they can be reached using the phone number: 01-366-888 or via the website: https://www.redcross.org.lb/. The Lebanese Red Cross provides First Aid trainings, Basic Life Support (BLS) and Advanced Cardiovascular Life Support (ACLS), to medical professionals and the public. In addition to the Lebanese Red Cross, other organizations such as UNICEF, Medair, and the International Committee of the Red Cross (ICRC) provide similar support and intervention.
The heatmap is developed in a multilayered way to showcase the distribution of first aid centers across Lebanon.  It features multiple interactive tools such as the slider which can be used to manipulate the areas contains a certain number of first aid care centers. The red gradient used reflects the red cross color, and in addition to the box size, it shows which areas contain the highest to least presence. The color palette and font size can also be manipulated based on preference.
""")

AID_COL = "Existence of a first aid center - exists"
if AID_COL not in df.columns:
        st.error(f'Column "{AID_COL}" not found in your CSV.')
        st.stop()

    # Convert metric to numeric (handles Yes/No/True/False/1/0)
if pd.api.types.is_numeric_dtype(df[AID_COL]):
        df["_aid_metric"] = df[AID_COL].fillna(0)
else:
        yes_set = {"yes", "y", "true", "t", "1", "exist", "exists"}
        df["_aid_metric"] = (
            df[AID_COL].astype(str).str.strip().str.lower().isin(yes_set).astype(int)
        )

    # Choose area column (Governorate / District)
area_cols = [c for c in df.columns if any(k in c.lower() for k in
                  ["governorate","district","caza","mouhafaza","city","region","area"])]
if "Districts and Governorates" in df.columns and "Districts and Governorates" not in area_cols:
        area_cols.insert(0, "Districts and Governorates")

area_col = st.selectbox(
        "Area column for treemap",
        options=list(df.columns),
        index=(df.columns.get_loc(area_cols[0]) if area_cols else 0)
    )

    # Clean labels
df["_area"] = df[area_col].astype(str).str.strip()

    # Aggregate counts
counts2 = (
        df.groupby("_area")["_aid_metric"]
          .sum(min_count=1).fillna(0).astype(int)
          .reset_index().rename(columns={"_area":"Area","_aid_metric":"count"})
          .sort_values("count", ascending=False)
    )

    # Threshold slider
max_count = int(counts2["count"].max()) if not counts2.empty else 0
min_needed = st.slider("Show areas with at least N centers",
                           min_value=0, max_value=max_count, value=0, step=1)
counts2 = counts2[counts2["count"] >= min_needed]

if counts2.empty:
        st.warning("No areas to display. Try lowering the threshold.")
        st.stop()

    # --- User controls for style ---
col1, col2 = st.columns([1, 1])
with col1:
        colorscale = st.selectbox(
            "Color scale",
            ["Reds", "Blues", "Greens", "Oranges", "Purples", "Viridis", "Cividis"],
            index=0
        )
with col2:
        label_size = st.slider("Label text size", 10, 30, 14)

    # Treemap (flat, single level)
fig2 = px.treemap(
        counts2,
        path=["Area"],
        values="count",
        color="count",
        color_continuous_scale=colorscale
    )

fig2.update_layout(
        title={
            "text": "Distribution of First Aid Centers Across Lebanese Regions",
            "x": 0.5, "xanchor": "center"
        },
        title_font=dict(size=24),
        margin=dict(l=40, r=40, t=70, b=20),
        paper_bgcolor="#EDF2F7",
        plot_bgcolor="#EDF2F7",
    )

fig2.update_traces(
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
        texttemplate="%{label}<br>%{value}",
        textfont_size=label_size
    )

st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Interpretation")
st.markdown("""
    - Akkar Governorate clearly reflects the highest number of first aid centers of 48 within Lebanon, with the maroon-red color.
    - Following suit are Matn and Mount Governorate with 28 and 27 each, Sidon District contains 27, and Aley District at 25 first aid centers.
    - Underserved communities include Hermel at 1, Tripoli at 2, Byblos at 8, as well as Batroun and Hasbaya containing 9 first aid centers each. This is also illustrated with the lightest red shade.""")

st.markdown("#### The Impact")
st.markdown("""Based on the above distribution, areas with limited access to first aid share dire consequences to those falling ill or facing accidents. Specifically, conditions and injuries can quickly worsen, with an increased chance of feath, long term complications and higher change of infection. The lack of presence of trained individuals with the necessary supplies puts patients at high risk. This calls for immediate action of increasing the number of first aid centers to cater to the public.""")