# model_calculations.py

# --- Constants (can be overridden by UI) ---
FARM_SIZE_ACRES = 50

# Default AgriLife Budget Figures (per acre unless specified)
AGRILIFE_DEFAULTS = {
    "main_crop": {
        "seed": 46.75,
        "fertilizer_materials": 192.29,
        "custom_fertilizer_application": 21.47,
        "herbicides_materials": 51.36,
        "insecticides_materials": 13.64,
        "fungicides_materials": 31.78,
        "other_chemicals_surfactants": 4.46,
        "custom_aerial_application": 37.21, # for 4.5 treated acres/crop acre
        "water_cost_volume_based": 43.45, # for 2.75 AcFt
        "base_water_charge_fixed": 70.30,
        "irrigation_labor": 27.48,
        "machinery_labor_pre_harvest": 15.32,
        "diesel_fuel_pre_harvest": 18.64,
        "repairs_maintenance_machinery_pre_harvest": 40.18,
        "other_field_supplies": 10.07, # (Butt Up Field, Plastic, Pipe)
        "interest_on_operating_capital": 44.05,
        # Per CWT costs
        "hauling_per_cwt": 0.48,
        "drying_per_cwt": 1.33,
        "storage_per_cwt": 0.34,
        "commission_per_cwt": 0.08,
        "check_off_per_cwt": 0.08,
    },
    "ratoon_crop": {
        "fertilizer": 40.62,
        "custom_top_dress": 9.54,
        "insecticide_stinkbug": 4.56,
        "water_cost_irrigation_labor": 48.32, # (35.89 + 12.43)
        "machinery_labor_fuel_rm": 14.73, # (3.44 + 3.54 + 7.75)
        "interest_on_operating_capital": 1.55,
        # Per CWT costs (same as main crop)
        "hauling_per_cwt": 0.48,
        "drying_per_cwt": 1.33,
        "storage_per_cwt": 0.34,
        "commission_per_cwt": 0.08,
        "check_off_per_cwt": 0.08,
    },
    "fixed_costs_per_acre": { # Per acre
        "crop_insurance": 11.00,
        "g_a_overhead": 11.13,
        "pickup_mileage_charge": 19.61,
        "machinery_depreciation": 44.28, # if owned
        "equipment_investment_interest": 28.46, # if owned
        "management_fee_main_crop": 56.00,
        "management_fee_ratoon_crop": 10.00,
    }
}

def calculate_revenue(params):
    farm_size = params["farm_size_acres"]
    main_crop_yield = params["main_crop_yield_active"]
    active_price = params["price_active"]
    ratoon_cultivation = params["ratoon_crop_cultivation"]
    ratoon_yield = params["ratoon_crop_yield"] if ratoon_cultivation == "Yes" else 0
    gov_payments = params["government_program_payments"]

    main_crop_revenue = main_crop_yield * active_price * farm_size
    ratoon_crop_revenue = ratoon_yield * active_price * farm_size if ratoon_cultivation == "Yes" else 0
    total_gross_annual_revenue = main_crop_revenue + ratoon_crop_revenue + gov_payments

    return {
        "main_crop_revenue": main_crop_revenue,
        "ratoon_crop_revenue": ratoon_crop_revenue,
        "government_program_payments": gov_payments,
        "total_gross_annual_revenue": total_gross_annual_revenue
    }

def calculate_establishment_costs(params):
    costs = {}
    total_establishment_costs = 0

    if params["land_tenure"] == "Owned" and params["land_purchase_cost"] > 0:
        costs["land_purchase_cost"] = params["land_purchase_cost"]
        total_establishment_costs += params["land_purchase_cost"]
    elif params["land_tenure"] == "Rented" and params["first_year_land_rental_cost"] > 0:
        # Typically first year rent is an operational cost, but if specific setup, include here.
        # For this model, we'll assume land rent is annual operational.
        # If it's a pre-payment for long lease setup, it might be here.
        # For simplicity, let's follow the idea that annual rent is operational.
        pass


    costs["land_clearing"] = params["land_clearing_cost"]
    total_establishment_costs += params["land_clearing_cost"]

    costs["laser_land_leveling"] = params["laser_land_leveling_cost_total"] # Already total
    total_establishment_costs += params["laser_land_leveling_cost_total"]

    costs["levee_surveying_construction"] = params["levee_surveying_construction_cost_total"] # Already total
    total_establishment_costs += params["levee_surveying_construction_cost_total"]

    costs["well_drilling_pump_system"] = params["well_drilling_pump_system_cost"]
    total_establishment_costs += params["well_drilling_pump_system_cost"]

    costs["on_farm_irrigation_system_installation"] = params["on_farm_irrigation_system_installation_cost_total"] # Already total
    total_establishment_costs += params["on_farm_irrigation_system_installation_cost_total"]
    
    costs["major_equipment_purchase_cost"] = params["major_equipment_purchase_cost"]
    total_establishment_costs += params["major_equipment_purchase_cost"]

    costs["total_establishment_costs"] = total_establishment_costs
    return costs

def calculate_annual_operational_expenditures(params, revenue_details):
    farm_size = params["farm_size_acres"]
    main_crop_yield = params["main_crop_yield_active"]
    ratoon_cultivation = params["ratoon_crop_cultivation"]
    ratoon_yield = params["ratoon_crop_yield"] if ratoon_cultivation == "Yes" else 0

    # A. Variable Costs (Main Crop)
    vc_main = AGRILIFE_DEFAULTS["main_crop"]
    total_vc_main_per_acre = (
        vc_main["seed"] +
        vc_main["fertilizer_materials"] +
        vc_main["custom_fertilizer_application"] +
        vc_main["herbicides_materials"] +
        vc_main["insecticides_materials"] +
        vc_main["fungicides_materials"] +
        vc_main["other_chemicals_surfactants"] +
        vc_main["custom_aerial_application"] +
        vc_main["water_cost_volume_based"] +
        vc_main["base_water_charge_fixed"] +
        vc_main["irrigation_labor"] +
        vc_main["machinery_labor_pre_harvest"] +
        vc_main["diesel_fuel_pre_harvest"] +
        vc_main["repairs_maintenance_machinery_pre_harvest"] +
        vc_main["other_field_supplies"] +
        vc_main["interest_on_operating_capital"]
    )
    # Yield-dependent costs for main crop
    total_vc_main_per_acre += main_crop_yield * (
        vc_main["hauling_per_cwt"] +
        vc_main["drying_per_cwt"] +
        vc_main["storage_per_cwt"] +
        vc_main["commission_per_cwt"] +
        vc_main["check_off_per_cwt"]
    )
    total_main_crop_variable_costs = total_vc_main_per_acre * farm_size

    # B. Variable Costs (Ratoon Crop)
    total_ratoon_crop_variable_costs = 0
    if ratoon_cultivation == "Yes":
        vc_ratoon = AGRILIFE_DEFAULTS["ratoon_crop"]
        total_vc_ratoon_per_acre = (
            vc_ratoon["fertilizer"] +
            vc_ratoon["custom_top_dress"] +
            vc_ratoon["insecticide_stinkbug"] +
            vc_ratoon["water_cost_irrigation_labor"] +
            vc_ratoon["machinery_labor_fuel_rm"] +
            vc_ratoon["interest_on_operating_capital"]
        )
        # Yield-dependent costs for ratoon crop
        total_vc_ratoon_per_acre += ratoon_yield * (
            vc_ratoon["hauling_per_cwt"] +
            vc_ratoon["drying_per_cwt"] +
            vc_ratoon["storage_per_cwt"] +
            vc_ratoon["commission_per_cwt"] +
            vc_ratoon["check_off_per_cwt"]
        )
        total_ratoon_crop_variable_costs = total_vc_ratoon_per_acre * farm_size

    # C. Annual Fixed Costs
    fc = AGRILIFE_DEFAULTS["fixed_costs_per_acre"]
    total_annual_fixed_costs = 0
    fixed_costs_details = {}

    if params["land_tenure"] == "Owned":
        # Simplified: User inputs total property tax for the 50 acres
        property_taxes = params["property_taxes_owned_total"]
        fixed_costs_details["property_taxes"] = property_taxes
        total_annual_fixed_costs += property_taxes
    else: # Rented
        annual_land_rent = params["annual_land_rent_per_acre"] * farm_size
        fixed_costs_details["annual_land_rent"] = annual_land_rent
        total_annual_fixed_costs += annual_land_rent

    crop_insurance_total = fc["crop_insurance"] * farm_size
    fixed_costs_details["crop_insurance"] = crop_insurance_total
    total_annual_fixed_costs += crop_insurance_total

    ga_overhead_total = fc["g_a_overhead"] * farm_size
    fixed_costs_details["g_a_overhead"] = ga_overhead_total
    total_annual_fixed_costs += ga_overhead_total
    
    pickup_mileage_total = fc["pickup_mileage_charge"] * farm_size
    fixed_costs_details["pickup_mileage_charge"] = pickup_mileage_total
    total_annual_fixed_costs += pickup_mileage_total

    # Assuming major equipment purchase is establishment, then depreciation/interest applies if owned
    # If not purchasing major equip (custom hire), these might be lower or zero.
    # The model outline implies these are separate from establishment if *not* custom hiring all.
    machinery_depreciation_total = fc["machinery_depreciation"] * farm_size
    fixed_costs_details["machinery_depreciation"] = machinery_depreciation_total
    total_annual_fixed_costs += machinery_depreciation_total
    
    equipment_investment_interest_total = fc["equipment_investment_interest"] * farm_size
    fixed_costs_details["equipment_investment_interest"] = equipment_investment_interest_total
    total_annual_fixed_costs += equipment_investment_interest_total

    management_fee = fc["management_fee_main_crop"]
    if ratoon_cultivation == "Yes":
        management_fee += fc["management_fee_ratoon_crop"]
    management_fee_total = management_fee * farm_size
    fixed_costs_details["management_fee_owner_labor"] = management_fee_total
    total_annual_fixed_costs += management_fee_total
    
    fixed_costs_details["total_annual_fixed_costs"] = total_annual_fixed_costs

    total_annual_operational_costs = (
        total_main_crop_variable_costs +
        total_ratoon_crop_variable_costs +
        total_annual_fixed_costs
    )

    return {
        "total_main_crop_variable_costs": total_main_crop_variable_costs,
        "total_ratoon_crop_variable_costs": total_ratoon_crop_variable_costs,
        "fixed_costs_details": fixed_costs_details,
        "total_annual_fixed_costs": total_annual_fixed_costs,
        "total_annual_operational_costs": total_annual_operational_costs
    }

def calculate_profitability(revenue_details, operational_expenditures):
    total_revenue = revenue_details["total_gross_annual_revenue"]
    total_vc = (operational_expenditures["total_main_crop_variable_costs"] +
                operational_expenditures["total_ratoon_crop_variable_costs"])
    total_op_costs = operational_expenditures["total_annual_operational_costs"]

    gross_profit = total_revenue - total_vc
    net_profit_before_tax = total_revenue - total_op_costs
    
    # Placeholder for tax calculation
    # tax_rate = params["income_tax_rate"] / 100
    # net_profit_after_tax = net_profit_before_tax * (1 - tax_rate)

    return {
        "gross_profit_revenue_less_vc": gross_profit,
        "net_profit_before_tax": net_profit_before_tax,
        # "net_profit_after_tax": net_profit_after_tax # If tax is implemented
    }

def calculate_roi(profitability_details, operational_expenditures, establishment_costs):
    npbt = profitability_details["net_profit_before_tax"]
    total_op_costs = operational_expenditures["total_annual_operational_costs"]
    total_est_costs = establishment_costs["total_establishment_costs"]

    annual_operational_roi = (npbt / total_op_costs) * 100 if total_op_costs > 0 else 0
    roi_on_initial_establishment = (npbt / total_est_costs) * 100 if total_est_costs > 0 else 0
    
    return {
        "annual_operational_roi_percent": annual_operational_roi,
        "roi_on_initial_establishment_percent": roi_on_initial_establishment
    }

def run_full_model(params):
    """
    Runs all calculations based on the input parameters.
    """
    # Resolve active yield and price from scenarios
    params["main_crop_yield_active"] = params["main_crop_yield_scenarios"][params["active_yield_scenario"]]
    params["price_active"] = params["price_scenarios"][params["active_price_scenario"]]

    revenue = calculate_revenue(params)
    establishment_costs = calculate_establishment_costs(params)
    operational_expenditures = calculate_annual_operational_expenditures(params, revenue)
    profitability = calculate_profitability(revenue, operational_expenditures)
    roi = calculate_roi(profitability, operational_expenditures, establishment_costs)

    results = {
        "inputs_summary": {
            "Farm Size (Acres)": params["farm_size_acres"],
            "Land Tenure": params["land_tenure"],
            "Ratoon Crop": params["ratoon_crop_cultivation"],
            "Active Main Crop Yield (cwt/acre)": params["main_crop_yield_active"],
            "Active Ratoon Crop Yield (cwt/acre)": params["ratoon_crop_yield"] if params["ratoon_crop_cultivation"] == "Yes" else "N/A",
            "Active Rice Price ($/cwt)": params["price_active"],
        },
        "revenue": revenue,
        "establishment_costs": establishment_costs,
        "operational_expenditures": operational_expenditures,
        "profitability": profitability,
        "roi": roi
    }
    # Add advanced analysis params for display if needed
    # results["financial_parameters"] = {
    # "Discount Rate (%)": params["discount_rate"],
    # "Project Time Horizon (Years)": params["project_time_horizon"]
    # }
    return results