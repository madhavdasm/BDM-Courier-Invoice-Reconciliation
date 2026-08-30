import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    print("Loading data...")
    df = pd.read_excel('Reconciliation_Report.xlsx')
    invoice_df = pd.read_excel('BDM project.xlsx', sheet_name='Courier company-Invoice')
    
    print("Merging Shipment Types...")
    df = df.merge(invoice_df[['Order ID', 'Type of Shipment']], on='Order ID', how='left')
    
    print("Analyzing overcharges...")
    
    # 1. Proportion of Order Status
    summary_counts = df['Charge Status'].value_counts()
    
    # Analyze only overcharged for the rest
    overcharged = df[df['Charge Status'] == 'Overcharged'].copy()
    overcharged['Overcharge Amount'] = abs(overcharged['Difference (Rs.)'])
    
    # 2. Zone-wise overcharging
    zone_overcharge = overcharged.groupby('Billed Zone')['Overcharge Amount'].sum().sort_values(ascending=False)
    
    # 3. Weight-slab-wise overcharging
    weight_overcharge = overcharged.groupby('Expected Weight Slab (kg)')['Overcharge Amount'].sum().sort_values(ascending=False)
    
    # 4. Shipment-type-wise overcharging
    type_overcharge = overcharged.groupby('Type of Shipment')['Overcharge Amount'].sum().sort_values(ascending=False)
    
    print("Generating BDM Overcharge Analysis Plots...")
    plt.figure(figsize=(16, 12))
    
    # Plot 1: Proportion of Order Status
    plt.subplot(2, 2, 1)
    if not summary_counts.empty:
        plt.pie(summary_counts, labels=summary_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
        plt.title('Proportion of Order Status')
    
    # Plot 2: Overcharge Amount by Billed Zone
    plt.subplot(2, 2, 2)
    if not zone_overcharge.empty:
        zone_overcharge.plot(kind='bar', color='coral')
        plt.title('Overcharge Amount by Billed Zone')
        plt.ylabel('Rs.')
        plt.xticks(rotation=0)
    
    # Plot 3: Overcharge Amount by Weight Slab
    plt.subplot(2, 2, 3)
    if not weight_overcharge.empty:
        weight_overcharge.plot(kind='bar', color='skyblue')
        plt.title('Overcharge Amount by Weight Slab')
        plt.ylabel('Rs.')
        plt.xticks(rotation=0)
    
    # Plot 4: Overcharge by Shipment Type
    plt.subplot(2, 2, 4)
    if not type_overcharge.empty:
        type_overcharge.plot(kind='pie', autopct='%1.1f%%', colors=['gold', 'lightgreen'])
        plt.title('Overcharge by Shipment Type')
        plt.ylabel('')
    
    plt.tight_layout()
    plt.savefig('BDM_Combined_Analysis.png')
    
    print("Generating BDM Summary Report text...")
    # ... existing report logic here (omitted for brevity since we already have the metrics)
    print("Done! Charts saved to BDM_Combined_Analysis.png")

if __name__ == '__main__':
    main()
