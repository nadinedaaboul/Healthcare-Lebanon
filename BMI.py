import streamlit as st
st.set_page_config(page_title= "BMI Calculator", layout= "centered")
st.title("BMI Calculator")
st.caption("BMI= weight (kg)/[height (m)]²")

unit = st.radio("Units", ["Metric (kg, cm)", "Imperial (lb, ft/in)"], horizontal=True)

if unit.startswith("Metric"):
    col1, col2 = st.columns(2)
    with col1:
        weight_kg = st.number_input("Weight (kg)", min_value=0.0, value=70.0, step=0.1)
    with col2:
        height_cm = st.number_input("Height (cm)", min_value=0.0, value=175.0, step=0.1)
    height_m = height_cm / 100.0
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        weight_lb = st.number_input("Weight (lb)", min_value=0.0, value=154.0, step=0.1)
    with col2:
        height_ft = st.number_input("Height (ft)", min_value=0.0, value=5.0, step=1.0)
    with col3:
        height_in = st.number_input("Height (in)", min_value=0.0, value=9.0, step=0.1)
    # Convert to metric
    weight_kg = weight_lb * 0.45359237
    total_inches = height_ft * 12.0 + height_in
    height_m = total_inches * 0.0254

    # --- Compute BMI ---
def compute_bmi(w_kg: float, h_m: float) -> float:
    if h_m <= 0:
        return 0.0
    return w_kg / (h_m ** 2)

bmi = round(compute_bmi(weight_kg, height_m), 2)

# --- Categorize (WHO) ---
def bmi_category(b: float) -> str:
    if b == 0:
        return "Invalid height"
    if b < 18.5:
        return "Underweight"
    if b < 25:
        return "Normal weight"
    if b < 30:
        return "Overweight"
    return "Obesity"

category = bmi_category(bmi)

# --- Display ---
st.subheader("Results")
if bmi == 0:
    st.warning("Please enter a valid height greater than 0.")
else:
    st.metric(label="Your BMI", value=bmi)
    st.write(f"**Category:** {category}")

    # Simple progress visualization (scaled roughly to BMI 40)
    max_bmi = 40
    pct = min(bmi / max_bmi, 1.0)
    st.progress(pct)

    with st.expander("What your category means"):
        st.markdown(
            """
- **Underweight (< 18.5):** Consider a nutrient-dense diet and speak with a clinician if needed.  
- **Normal (18.5—24.9):** Great—maintain balanced nutrition and regular activity.  
- **Overweight (25—29.9):** Small, sustainable changes in diet and activity can help.  
- **Obesity (≥ 30):** Discuss comprehensive options with a healthcare professional.
            """
        )

# --- Footer note ---
st.caption("Note: BMI is a screening tool and does not directly assess body fat, distribution, or overall health.")

