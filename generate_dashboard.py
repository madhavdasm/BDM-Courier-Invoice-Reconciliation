import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def save_charts(df, overcharged):
    # 1. Order Charge Status
    plt.figure(figsize=(6, 4))
    summary_counts = df['Charge Status'].value_counts()
    plt.pie(summary_counts, labels=summary_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
    plt.title('ORDER CHARGE STATUS')
    plt.tight_layout()
    plt.savefig('pie_status.png')
    plt.close()

    # 2. Overcharge by Zone
    plt.figure(figsize=(6, 4))
    zone_overcharge = overcharged.groupby('Billed Zone')['Overcharge Amount'].sum().sort_values(ascending=False)
    zone_overcharge.plot(kind='bar', color='coral')
    plt.title('OVERCHARGE BY ZONE')
    plt.ylabel('Amount (₹)')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('bar_zone.png')
    plt.close()

    # 3. Overcharge by Weight Slab
    plt.figure(figsize=(6, 4))
    weight_overcharge = overcharged.groupby('Expected Weight Slab (kg)')['Overcharge Amount'].sum().sort_values(ascending=False)
    weight_overcharge.plot(kind='bar', color='skyblue')
    plt.title('OVERCHARGE BY WEIGHT SLAB')
    plt.ylabel('Amount (₹)')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('bar_weight.png')
    plt.close()

    # 4. Overcharge by Shipment Type
    plt.figure(figsize=(6, 4))
    type_overcharge = overcharged.groupby('Type of Shipment')['Overcharge Amount'].sum().sort_values(ascending=False)
    plt.pie(type_overcharge, labels=type_overcharge.index, autopct='%1.1f%%', colors=['gold', 'lightgreen'])
    plt.title('OVERCHARGE BY SHIPMENT TYPE')
    plt.tight_layout()
    plt.savefig('pie_shipment.png')
    plt.close()

def main():
    print("Loading data...")
    recon_df = pd.read_excel('Reconciliation_Report.xlsx')
    invoice_df = pd.read_excel('BDM project.xlsx', sheet_name='Courier company-Invoice')
    order_df = pd.read_excel('BDM project.xlsx', sheet_name='Order Report')
    
    # Ensure Type of Shipment is in recon_df
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
    
    # Create Excel Writer
    print("Writing to Excel Dashboard...")
    output_file = 'Final_Reconciliation_Dashboard.xlsx'
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    workbook = writer.book
    
    # Formats
    title_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter', 'font_color': '#ffffff', 'bg_color': '#4f81bd'})
    subtitle_format = workbook.add_format({'italic': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
    
    kpi_value_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '₹#,##0.00'})
    kpi_pct_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '0.00%'})
    kpi_title_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#d9d9d9', 'bold': True})
    
    findings_title_format = workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#d9d9d9'})
    findings_format = workbook.add_format({'font_size': 12, 'text_wrap': True})

    # --- SHEET 4: Dashboard ---
    ws_dash = workbook.add_worksheet('Dashboard')
    ws_dash.hide_gridlines(2)
    
    # Adjust column widths
    ws_dash.set_column('A:A', 5)
    ws_dash.set_column('B:E', 25)
    ws_dash.set_column('F:I', 25)
    
    # Header
    ws_dash.merge_range('B2:I3', 'BDM COURIER INVOICE RECONCILIATION DASHBOARD', title_format)
    ws_dash.merge_range('B4:I4', 'Courier Billing Analysis | Order-level Reconciliation', subtitle_format)
    
    # KPIs Row
    # Box 1
    ws_dash.merge_range('B6:C6', 'Total Invoice Value', kpi_title_format)
    ws_dash.merge_range('B7:C8', total_billed, kpi_value_format)
    # Box 2
    ws_dash.merge_range('D6:E6', 'Total Overcharge', kpi_title_format)
    ws_dash.merge_range('D7:E8', total_overcharge, kpi_value_format)
    # Box 3
    ws_dash.merge_range('F6:G6', 'Invoice Affected', kpi_title_format)
    ws_dash.merge_range('F7:G8', pct_affected, kpi_pct_format)
    # Box 4
    ws_dash.merge_range('H6:I6', '% Orders Overcharged', kpi_title_format)
    ws_dash.merge_range('H7:I8', pct_orders_overcharged, kpi_pct_format)
    
    # Charts
    ws_dash.insert_image('B11', 'pie_status.png', {'x_scale': 0.9, 'y_scale': 0.9})
    ws_dash.insert_image('F11', 'bar_zone.png', {'x_scale': 0.9, 'y_scale': 0.9})
    ws_dash.insert_image('B32', 'bar_weight.png', {'x_scale': 0.9, 'y_scale': 0.9})
    ws_dash.insert_image('F32', 'pie_shipment.png', {'x_scale': 0.9, 'y_scale': 0.9})
    
    # Key Business Findings
    ws_dash.merge_range('B54:I54', 'Key Business Findings', findings_title_format)
    ws_dash.merge_range('B55:I60', 
        "• ₹4,426.60 in courier overcharges were identified.\n"
        "• 32.43% of the total invoiced value is affected.\n"
        "• Zone D is the largest contributor to overcharges.\n"
        "• 0.5 kg and 1.0 kg shipments account for the majority of overcharge value.\n"
        "• Forward charges account for 98.5% of the identified overcharge.", 
        findings_format)
    
    # --- SHEET 3: Detailed Analysis ---
    top_5.to_excel(writer, sheet_name='Detailed Analysis', index=False, startrow=2)
    ws_details = writer.sheets['Detailed Analysis']
    ws_details.write('A1', 'Top 5 Most Overcharged Orders', workbook.add_format({'bold': True, 'font_size': 14}))
    
    recon_df.to_excel(writer, sheet_name='Detailed Analysis', index=False, startrow=10)
    ws_details.write('A9', 'Full Reconciliation Data', workbook.add_format({'bold': True, 'font_size': 14}))
    
    # --- SHEET 2: Reconciliation ---
    recon_df.to_excel(writer, sheet_name='Reconciliation', index=False)
    
    # --- SHEET 1: Raw Data ---
    invoice_df.to_excel(writer, sheet_name='Raw Data', index=False)
    
    writer.close()
    print("Done! Dashboard generated successfully.")

if __name__ == '__main__':
    main()
