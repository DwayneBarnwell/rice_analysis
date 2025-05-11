import streamlit as st
import pandas as pd
from model_calculations import run_full_model, FARM_SIZE_ACRES, AGRILIFE_DEFAULTS

st.set_page_config(layout="wide")

st.title("🌾 Rice Farming Financial Scenario Modeler")

# --- I. Model Setup and Key Input Variables ---
st.sidebar.header("I. Model Setup & Inputs")

# A. Farm & Operational Basics
st.sidebar.subheader("A. Farm & Operational Basics")
params = {}
params["farm_size_acres"] = st.sidebar.number_input("Farm Size (Acres)", value=FARM_SIZE_ACRES, min_value=1, step=1)
params["land_tenure"] = st.sidebar.selectbox("Land Tenure", ("Owned", "Rented"))
params["primary_crop"] = "Long-Grain Rice" # Fixed for this model
st.sidebar.caption(f"Primary Crop: {params['primary_crop']}")
params["ratoon_crop_cultivation"] = st.sidebar.radio("Ratoon Crop Cultivation?", ("Yes", "No"))

# B. Yield Scenarios
st.sidebar.subheader("B. Yield Scenarios (per acre)")
default_yields = {
    "Low": 65.0,
    "Average": 75.0,
    "High": 85.0
}
params["main_crop_yield_scenarios"] = {
    "Low": st.sidebar.number_input("Main Crop Yield - Low (cwt/acre)", value=default_yields["Low"], format="%.2f"),
    "Average": st.sidebar.number_input("Main Crop Yield - Average (cwt/acre)", value=default_yields["Average"], format="%.2f"),
    "High": st.sidebar.number_input("Main Crop Yield - High (cwt/acre)", value=default_yields["High"], format="%.2f")
}
params["active_yield_scenario"] = st.sidebar.selectbox("Active Main Crop Yield Scenario", list(default_yields.keys()), index=1)

if params["ratoon_crop_cultivation"] == "Yes":
    params["ratoon_crop_yield"] = st.sidebar.number_input("Ratoon Crop Yield (cwt/acre)", value=16.0, format="%.2f")
else:
    params["ratoon_crop_yield"] = 0.0

# C. Price Scenarios
st.sidebar.subheader("C. Price Scenarios (per cwt)")
default_prices = {
    "Baseline ($16.00)": 16.00,
    "Alternative 1 ($14.20)": 14.20,
    "Alternative 2 (User-defined)": 15.00 # Placeholder for user-defined
}
params["price_scenarios"] = {
    "Baseline ($16.00)": default_prices["Baseline ($16.00)"], # Fixed based on name
    "Alternative 1 ($14.20)": default_prices["Alternative 1 ($14.20)"], # Fixed
    "Alternative 2 (User-defined)": st.sidebar.number_input("Long-Grain Rice Price - Alternative 2 ($/cwt)", value=default_prices["Alternative 2 (User-defined)"], format="%.2f")
}
params["active_price_scenario"] = st.sidebar.selectbox("Active Price Scenario", list(default_prices.keys()), index=0)

# D. Financial Parameters (for future advanced analysis)
st.sidebar.subheader("D. Financial Parameters (for NPV/IRR)")
params["discount_rate"] = st.sidebar.slider("Discount Rate (%)", 0.0, 20.0, 7.0, 0.5)
params["project_time_horizon"] = st.sidebar.slider("Project Time Horizon (Years)", 1, 30, 10, 1)
# Financing details can be complex; for now, let's assume these are handled within establishment or operational costs if interest is paid.

# Placeholder for Government Payments (from Revenue section)
params["government_program_payments"] = st.sidebar.number_input("Government Program Payments (Total $)", value=0.0, format="%.2f")


# --- III. Establishment Costs ---
with st.sidebar.expander("III. Establishment Costs (One-Time/Infrequent)", expanded=False):
    if params["land_tenure"] == "Owned":
        params["land_purchase_cost"] = st.number_input("Land Purchase Cost (Total $)", value=0.0, format="%.2f", help="Total cost for 50 acres if purchasing.")
        params["first_year_land_rental_cost"] = 0.0
    else: # Rented
        params["land_purchase_cost"] = 0.0
        params["first_year_land_rental_cost"] = st.number_input("First Year Land Rental Cost (Total $)", value=0.0, format="%.2f", help="If any specific first-year setup rent.")

    params["land_clearing_cost"] = st.number_input("Land Clearing Cost (Total $ for 50 acres)", value=0.0, format="%.2f")
    params["laser_land_leveling_cost_total"] = st.number_input("Laser Land Leveling (Total $)", value=150.0 * params["farm_size_acres"], format="%.2f", help="e.g., $150-$500/acre")
    params["levee_surveying_construction_cost_total"] = st.number_input("Levee Surveying & Construction (Total $)", value=7.0 * params["farm_size_acres"] + (200 * params["farm_size_acres"]) , format="%.2f", help="Survey ~$6-$7/acre + Construction") # Example construction
    params["well_drilling_pump_system_cost"] = st.number_input("Well Drilling & Pump System Cost (Total $)", value=0.0, format="%.2f")
    params["on_farm_irrigation_system_installation_cost_total"] = st.number_input("On-Farm Irrigation System Installation (Total $)", value=210.0 * params["farm_size_acres"], format="%.2f", help="e.g., ~$210/acre for basic furrow/flood")
    params["major_equipment_purchase_cost"] = st.number_input("Major Equipment Purchase Cost (Total $)", value=0.0, format="%.2f")

# --- IV. Annual Operational Expenditures (Overrides for AgriLife Defaults if needed) ---
# For simplicity, we'll use AgriLife defaults in calculations.
# UI could be added here to override specific line items from AGRILIFE_DEFAULTS if desired.
# Example: params["seed_cost_override"] = st.sidebar.number_input(...)

# Specific inputs for fixed costs that depend on tenure or are totals
with st.sidebar.expander("IV.C. Annual Fixed Costs (Specific Inputs)", expanded=False):
    if params["land_tenure"] == "Owned":
        params["property_taxes_owned_total"] = st.number_input("Property Taxes (Total Annual $)", value=500.0, format="%.2f", help="Total for 50 acres")
        params["annual_land_rent_per_acre"] = 0.0
    else: # Rented
        params["property_taxes_owned_total"] = 0.0
        params["annual_land_rent_per_acre"] = st.number_input("Annual Land Rent ($/acre)", value=75.0, format="%.2f", help="e.g., $55-$130/acre")

# --- Optional: Income Tax Rate ---
# params["income_tax_rate"] = st.sidebar.slider("Applicable Income Tax Rate (%)", 0.0, 50.0, 0.0, 0.5) # if NPAT is needed


# --- Main Panel for Results ---
st.header("Financial Model Results")

if st.sidebar.button("Calculate Scenario"):
    results = run_full_model(params)

    st.subheader("Selected Scenario Inputs Summary")
    st.json(results["inputs_summary"])

    # --- II. Revenue Calculations ---
    st.subheader("II. Revenue Calculations")
    rev = results["revenue"]
    st.metric("Main Crop Revenue", f"${rev['main_crop_revenue']:,.2f}")
    if params["ratoon_crop_cultivation"] == "Yes":
        st.metric("Ratoon Crop Revenue", f"${rev['ratoon_crop_revenue']:,.2f}")
    st.metric("Government Program Payments", f"${rev['government_program_payments']:,.2f}")
    st.metric("Total Gross Annual Revenue", f"${rev['total_gross_annual_revenue']:,.2f}")

    # --- III. Establishment Costs (Summary) ---
    st.subheader("III. Establishment Costs (One-Time or Infrequent)")
    est_costs = results["establishment_costs"]
    # Create a DataFrame for better display of establishment costs
    est_df_data = {k:v for k,v in est_costs.items() if k != "total_establishment_costs"}
    est_df = pd.DataFrame(list(est_df_data.items()), columns=['Cost Item', 'Amount ($)'])
    st.dataframe(est_df.style.format({'Amount ($)': '${:,.2f}'}))
    st.metric("Total Establishment Costs", f"${est_costs['total_establishment_costs']:,.2f}")

    # --- IV. Annual Operational Expenditures ---
    st.subheader("IV. Annual Operational Expenditures")
    op_exp = results["operational_expenditures"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Main Crop Variable Costs", f"${op_exp['total_main_crop_variable_costs']:,.2f}")
    if params["ratoon_crop_cultivation"] == "Yes":
        col2.metric("Total Ratoon Crop Variable Costs", f"${op_exp['total_ratoon_crop_variable_costs']:,.2f}")
    else:
        col2.metric("Total Ratoon Crop Variable Costs", "$0.00")
    
    st.write("**Fixed Costs Details:**")
    fixed_df_data = {k:v for k,v in op_exp['fixed_costs_details'].items() if k != "total_annual_fixed_costs"}
    fixed_df = pd.DataFrame(list(fixed_df_data.items()), columns=['Cost Item', 'Amount ($)'])
    st.dataframe(fixed_df.style.format({'Amount ($)': '${:,.2f}'}))
    col3.metric("Total Annual Fixed Costs", f"${op_exp['total_annual_fixed_costs']:,.2f}")
    
    st.metric("TOTAL ANNUAL OPERATIONAL COSTS", f"${op_exp['total_annual_operational_costs']:,.2f}", delta_color="inverse")


    # --- V. Profitability Analysis ---
    st.subheader("V. Profitability Analysis")
    profit = results["profitability"]
    col1_prof, col2_prof = st.columns(2)
    col1_prof.metric("Gross Profit (Revenue - Variable Costs)", f"${profit['gross_profit_revenue_less_vc']:,.2f}")
    col2_prof.metric("Net Profit Before Tax (NPBT)", f"${profit['net_profit_before_tax']:,.2f}")
    # if "net_profit_after_tax" in profit:
    # st.metric("Net Profit After Tax", f"${profit['net_profit_after_tax']:,.2f}")

    # --- VI. Return on Investment (ROI) Calculations ---
    st.subheader("VI. Return on Investment (ROI) Calculations")
    roi_res = results["roi"]
    col1_roi, col2_roi = st.columns(2)
    col1_roi.metric("Annual Operational ROI", f"{roi_res['annual_operational_roi_percent']:.2f}%")
    if est_costs['total_establishment_costs'] > 0:
        col2_roi.metric("ROI on Initial Establishment (Simplified Annual)", f"{roi_res['roi_on_initial_establishment_percent']:.2f}%")
    else:
        col2_roi.metric("ROI on Initial Establishment (Simplified Annual)", "N/A (No Est. Costs)")

    st.info("Note: AgriLife budget figures are used as defaults for many per-acre operational costs. Advanced users can modify `model_calculations.py` or extend UI to override these.")

else:
    st.info("Adjust parameters in the sidebar and click 'Calculate Scenario' to see results.")

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit & Python.")