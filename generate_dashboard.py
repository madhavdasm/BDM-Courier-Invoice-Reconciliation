import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def calculate_stats(series, name):
    clean = series.dropna()
    q1 = clean.quantile(0.25)
    med = clean.median()
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    return {
        'Variable': name,
        'Count': int(clean.count()),
        'Mean': round(float(clean.mean()), 4),
        'Std Dev': round(float(clean.std()), 4),
        'Min': round(float(clean.min()), 4),
        'Q1 (25%)': round(float(q1), 4),
        'Median (50%)': round(float(med), 4),
        'Q3 (75%)': round(float(q3), 4),
        'IQR': round(float(iqr), 4),
        'Max': round(float(clean.max()), 4)
    }

def save_charts(df, overcharged):
    # 1. Order Charge Status
    plt.figure(figsize=(6, 4))
    summary_counts = df['Charge Status'].value_counts()
    plt.pie(summary_counts, labels=summary_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
    plt.title('ORDER CHARGE STATUS (FIGURE 1)')
    plt.tight_layout()
    plt.savefig('pie_status.png', dpi=200)
    plt.close()

    # 2. Overcharge by Zone
    plt.figure(figsize=(6, 4))
    zone_overcharge = overcharged.groupby('Billed Zone')['Overcharge Amount'].sum().sort_values(ascending=False)
    zone_overcharge.plot(kind='bar', color='coral', edgecolor='black')
    plt.title('OVERCHARGE BY ZONE (FIGURE 2)')
    plt.ylabel('Amount (₹)')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('bar_zone.png', dpi=200)
    plt.close()

    # 3. Overcharge by Weight Slab
    plt.figure(figsize=(6, 4))
    weight_overcharge = overcharged.groupby('Expected Weight Slab (kg)')['Overcharge Amount'].sum().sort_values(ascending=False)
    weight_overcharge.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('OVERCHARGE BY WEIGHT SLAB (FIGURE 4)')
    plt.ylabel('Amount (₹)')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('bar_weight.png', dpi=200)
    plt.close()

    # 4. Overcharge by Shipment Type
    plt.figure(figsize=(6, 4))
    type_overcharge = overcharged.groupby('Type of Shipment')['Overcharge Amount'].sum().sort_values(ascending=False)
    plt.pie(type_overcharge, labels=type_overcharge.index, autopct='%1.1f%%', colors=['gold', 'lightgreen'])
    plt.title('OVERCHARGE BY SHIPMENT TYPE (FIGURE 3)')
    plt.tight_layout()
    plt.savefig('pie_shipment.png', dpi=200)
    plt.close()

def main():
    print("Loading data...")
    recon_df = pd.read_excel('Reconciliation_Report.xlsx')
    file_path = 'BDM project.xlsx'
    invoice_df = pd.read_excel(file_path, sheet_name='Courier company-Invoice')
    order_df = pd.read_excel(file_path, sheet_name='Order Report')
    sku_df = pd.read_excel(file_path, sheet_name='SKU Master')
    
    # Ensure Type of Shipment is in recon_df
    if 'Type of Shipment' not in recon_df.columns:
        recon_df = recon_df.merge(invoice_df[['Order ID', 'Type of Shipment']], on='Order ID', how='left')
    
    overcharged = recon_df[recon_df['Charge Status'] == 'Overcharged'].copy()
    overcharged['Overcharge Amount'] = abs(overcharged['Difference (Rs.)'])
    
    # Calculate KPIs
    total_billed = recon_df['Billing Amount (Rs.)'].sum()
    total_overcharge = overcharged['Overcharge Amount'].sum()
    pct_affected = (total_overcharge / total_billed)
    pct_orders_overcharged = len(overcharged) / len(recon_df)
    
    top_5 = overcharged.sort_values(by='Overcharge Amount', ascending=False).head(5)
    
    # Generate Charts
    print("Generating charts...")
    save_charts(recon_df, overcharged)
    
    # Generate Descriptive Statistics
    print("Calculating descriptive statistics...")
    if 'Weight Difference (kg)' not in recon_df.columns:
        recon_df['Weight Difference (kg)'] = recon_df['Charged Weight'] - recon_df['Total Weight (kg)']
        
    stats_list = [
        calculate_stats(order_df['Order Qty'], 'Order Quantity (Order Report)'),
        calculate_stats(sku_df['Weight (g)'], 'Item Weight (g) (SKU Master)'),
        calculate_stats(recon_df['Total Weight (kg)'], 'Total Weight (kg) [Actual]'),
        calculate_stats(recon_df['Expected Weight Slab (kg)'], 'Expected Weight Slab (kg)'),
        calculate_stats(recon_df['Charged Weight'], 'Charged Weight (kg) [Courier]'),
        calculate_stats(recon_df['Weight Difference (kg)'], 'Weight Difference (kg) [Charged - Actual]'),
        calculate_stats(recon_df['Expected Charge (Rs.)'], 'Expected Charge (Rs.) [Contractual]'),
        calculate_stats(recon_df['Billing Amount (Rs.)'], 'Billing Amount (Rs.) [Invoiced]'),
        calculate_stats(recon_df['Difference (Rs.)'], 'Difference (Rs.) [Expected - Billed]'),
        calculate_stats(overcharged['Overcharge Amount'], 'Overcharge Amount (Rs.) [Overcharged Orders]')
    ]
    stats_df = pd.DataFrame(stats_list)
    
    # Create Excel Writer
    print("Writing to Excel Dashboard...")
    output_file = 'Final_Reconciliation_Dashboard.xlsx'
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    workbook = writer.book
    
    # Formats
    title_format = workbook.add_format({'bold': True, 'font_size': 18, 'align': 'center', 'valign': 'vcenter', 'font_color': '#ffffff', 'bg_color': '#1f4e78'})
    subtitle_format = workbook.add_format({'italic': True, 'font_size': 12, 'align': 'center', 'valign': 'vcenter'})
    
    kpi_value_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '₹#,##0.00'})
    kpi_pct_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '0.00%'})
    kpi_title_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#d9d9d9', 'bold': True})
    
    section_header = workbook.add_format({'bold': True, 'font_size': 13, 'bg_color': '#d9e1f2', 'border': 1})
    findings_format = workbook.add_format({'font_size': 11, 'text_wrap': True, 'valign': 'top'})

    # --- SHEET 1: Dashboard ---
    ws_dash = workbook.add_worksheet('Dashboard')
    ws_dash.hide_gridlines(2)
    
    # Adjust column widths
    ws_dash.set_column('A:A', 4)
    ws_dash.set_column('B:E', 24)
    ws_dash.set_column('F:I', 24)
    
    # Header
    ws_dash.merge_range('B2:I3', 'BDM COURIER INVOICE RECONCILIATION DASHBOARD', title_format)
    ws_dash.merge_range('B4:I4', 'Automated 3-Way Audit Pipeline | Pre-Payment Governance | IIT Madras BDM', subtitle_format)
    
    # KPIs Row
    ws_dash.merge_range('B6:C6', 'Total Invoice Value', kpi_title_format)
    ws_dash.merge_range('B7:C8', total_billed, kpi_value_format)
    
    ws_dash.merge_range('D6:E6', 'Total Overcharge Amount', kpi_title_format)
    ws_dash.merge_range('D7:E8', total_overcharge, kpi_value_format)
    
    ws_dash.merge_range('F6:G6', '% Invoiced Spend Affected', kpi_title_format)
    ws_dash.merge_range('F7:G8', pct_affected, kpi_pct_format)
    
    ws_dash.merge_range('H6:I6', '% Orders Overcharged', kpi_title_format)
    ws_dash.merge_range('H7:I8', pct_orders_overcharged, kpi_pct_format)
    
    # Charts
    ws_dash.insert_image('B11', 'pie_status.png', {'x_scale': 0.88, 'y_scale': 0.88})
    ws_dash.insert_image('F11', 'bar_zone.png', {'x_scale': 0.88, 'y_scale': 0.88})
    ws_dash.insert_image('B32', 'bar_weight.png', {'x_scale': 0.88, 'y_scale': 0.88})
    ws_dash.insert_image('F32', 'pie_shipment.png', {'x_scale': 0.88, 'y_scale': 0.88})
    
    # Key Business Findings
    ws_dash.merge_range('B54:I54', 'Key Business Findings & Root-Cause Explanations', section_header)
    findings_text = (
        "1. TOTAL FINANCIAL LEAKAGE: ₹4,426.60 in overcharges across 79 out of 124 orders (63.71%), affecting 32.43% of total billed spend.\n\n"
        "2. ZONE D OVERCHARGING (₹3,997.40 / 90.31%): 60 orders contractually destined for Zone B were erroneously billed under Zone D. "
        "Zone D applies a +37.6% higher base rate (₹45.40 vs ₹33.00) and +58.3% higher slab rate (₹44.80 vs ₹28.30), creating severe cost compounding.\n\n"
        "3. SMALL-WEIGHT ITEMS OVERCHARGED (FIGURE 4: ₹4,101.20 / 92.65%): Shipments in 0.5 kg (₹2,485.70) and 1.0 kg (₹1,615.50) slabs represent "
        "almost all leakage. Root causes: (a) Volumetric weight arbitrage (L x W x H / 5000) on lightweight products packed in standard boxes; "
        "(b) Step-function slab boundary penalties where crossing 0.5 kg doubles freight cost; (c) High volume concentration in small parcels.\n\n"
        "4. PRE-PAYMENT AUDITING & PREDICTIVE ML: Transition to pre-payment 3-way matching in ERP with automated payment holds and debit notes. "
        "Deploy Machine Learning models (GBDT / Random Forest) for pre-billing freight forecasting and overcharge anomaly classification."
    )
    ws_dash.merge_range('B55:I65', findings_text, findings_format)
    
    # --- SHEET 2: Descriptive Statistics ---
    stats_df.to_excel(writer, sheet_name='Descriptive Statistics', index=False, startrow=2)
    ws_stats = writer.sheets['Descriptive Statistics']
    ws_stats.write('A1', 'Descriptive Statistics Summary (Parametric & Non-Parametric)', workbook.add_format({'bold': True, 'font_size': 14}))
    ws_stats.set_column('A:A', 35)
    ws_stats.set_column('B:K', 14)
    
    # --- SHEET 3: Detailed Analysis ---
    top_5.to_excel(writer, sheet_name='Detailed Analysis', index=False, startrow=2)
    ws_details = writer.sheets['Detailed Analysis']
    ws_details.write('A1', 'Top 5 Most Overcharged Orders', workbook.add_format({'bold': True, 'font_size': 14}))
    
    recon_df.to_excel(writer, sheet_name='Detailed Analysis', index=False, startrow=10)
    ws_details.write('A9', 'Full Order Reconciliation Data', workbook.add_format({'bold': True, 'font_size': 14}))
    
    # --- SHEET 4: Reconciliation ---
    recon_df.to_excel(writer, sheet_name='Reconciliation', index=False)
    
    # --- SHEET 5: Raw Invoiced Data ---
    invoice_df.to_excel(writer, sheet_name='Raw Invoiced Data', index=False)
    
    writer.close()
    print("Done! Dashboard generated successfully at 'Final_Reconciliation_Dashboard.xlsx'.")

if __name__ == '__main__':
    main()
