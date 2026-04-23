import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from io import BytesIO

# --- CONFIGURATION & SOR DATA (Nashik 1419) ---
SOR_RATES = {
    "EARTH_FILL": 344.00,      # INR per M3
    "RET_WALL": 4540.71,       # INR per RM (Composite rate from your template)
    "PAVERS": 646.44,         # INR per M2
    "CULVERT": 4201.40,        # INR per RM (0.6M Hume pipe)
    "B0_BLDG": 1403674.00      # INR LS (Sales Building B0 Type)
}

BUILDING_DIM = {"L": 9.23, "B": 5.0}
PESO_CLEARANCE = 4.0

def generate_bpcl_automation(frontage, depth, road_setback, wall_setback, entry_w, exit_w, fill_depth):
    """
    Main function to generate both the Excel Estimate and the Layout Drawing.
    """
    
    # --- 1. CALCULATE QUANTITIES ---
    culvert_qty = entry_w + exit_w
    # Wall calculation: Side1 + Side2 + Back + (Frontage - Openings)
    wall_qty = (2 * depth) + frontage + (frontage - culvert_qty)
    
    total_area = frontage * depth
    bldg_area = BUILDING_DIM["L"] * BUILDING_DIM["B"]
    # Estimate driveway area (Total - Building - Green Belt/Buffer approx 15%)
    driveway_qty = total_area - bldg_area - (total_area * 0.15)
    fill_qty = total_area * fill_depth

    # --- 2. CREATE EXCEL ESTIMATE ---
    boq_data = [
        {"Service": "7006847", "Description": "Earth Filling", "Qty": fill_qty, "Unit": "M3", "Rate": SOR_RATES["EARTH_FILL"]},
        {"Service": "CIVIL-02", "Description": "Boundary/Retention Wall", "Qty": wall_qty, "Unit": "RM", "Rate": SOR_RATES["RET_WALL"]},
        {"Service": "7006843", "Description": "Driveway Paver Blocks", "Qty": driveway_qty, "Unit": "M2", "Rate": SOR_RATES["PAVERS"]},
        {"Service": "7006154", "Description": "Culvert (Entry/Exit)", "Qty": culvert_qty, "Unit": "RM", "Rate": SOR_RATES["CULVERT"]},
        {"Service": "BLDG-B0", "Description": "Sales Building (B0 Standard)", "Qty": 1, "Unit": "LS", "Rate": SOR_RATES["B0_BLDG"]}
    ]
    
    df = pd.DataFrame(boq_data)
    df['Total Amount'] = df['Qty'] * df['Rate']
    df.to_excel("BPCL_Project_Estimate.xlsx", index=False)
    
    # --- 3. CREATE PDF DRAWING ---
    fig, ax = plt.subplots(figsize=(8, 10))
    
    # Plot Boundary
    ax.add_patch(Rectangle((0, 0), frontage, depth, fill=False, edgecolor='black', lw=2, label="Plot Boundary"))
    
    # Sales Building placement (Anchored at road and wall setback)
    bldg_x, bldg_y = wall_setback, depth - road_setback - BUILDING_DIM["B"]
    ax.add_patch(Rectangle((bldg_x, bldg_y), BUILDING_DIM["L"], BUILDING_DIM["B"], color='blue', alpha=0.3, label="Sales Bldg (B0)"))
    
    # PESO Clearance Line (Offset from walls)
    ax.add_patch(Rectangle((wall_setback, wall_setback), frontage-(2*wall_setback), depth-(2*wall_setback), 
                           fill=False, edgecolor='red', ls='--', lw=1, label="PESO Clearance Line (4m)"))

    # Entry/Exit indicators
    ax.add_patch(Rectangle((0, -2), entry_w, 2, color='green', alpha=0.5))
    ax.add_patch(Rectangle((frontage - exit_w, -2), exit_w, 2, color='green', alpha=0.5))
    
    # Formatting
    ax.set_xlim(-10, frontage + 10)
    ax.set_ylim(-10, depth + 10)
    ax.set_aspect('equal')
    ax.set_title(f"Automated Layout: {frontage}m x {depth}m\n(Nashik Territory)", fontsize=12)
    ax.legend(loc='lower right', fontsize='small')
    
    plt.savefig("BPCL_Site_Layout.pdf", bbox_inches='tight')
    print("Success: 'BPCL_Project_Estimate.xlsx' and 'BPCL_Site_Layout.pdf' generated.")

# --- EXECUTION ---
# Change these values to test different site scenarios
generate_bpcl_automation(
    frontage=60.0, 
    depth=70.0, 
    road_setback=15.0, 
    wall_setback=4.0, 
    entry_w=15.0, 
    exit_w=15.0, 
    fill_depth=1.2
)