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

def main():
    print("Loading data...")
    df = pd.read_excel('Reconciliation_Report.xlsx')
    file_path = 'BDM project.xlsx'
    invoice_df = pd.read_excel(file_path, sheet_name='Courier company-Invoice')
    order_df = pd.read_excel(file_path, sheet_name='Order Report')
    sku_df = pd.read_excel(file_path, sheet_name='SKU Master')
    
    print("Merging Shipment Types...")
    if 'Type of Shipment' not in df.columns:
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
        plt.title('Figure 1: Proportion of Order Status', fontsize=13, fontweight='bold')
    
    # Plot 2: Overcharge Amount by Billed Zone
    plt.subplot(2, 2, 2)
    if not zone_overcharge.empty:
        zone_overcharge.plot(kind='bar', color='coral', edgecolor='black')
        plt.title('Figure 2: Overcharge Amount by Billed Zone', fontsize=13, fontweight='bold')
        plt.ylabel('Amount (Rs.)')
        plt.xticks(rotation=0)
    
    # Plot 3: Overcharge by Shipment Type
    plt.subplot(2, 2, 3)
    if not type_overcharge.empty:
        type_overcharge.plot(kind='pie', autopct='%1.1f%%', colors=['gold', 'lightgreen'])
        plt.title('Figure 3: Overcharge by Shipment Type', fontsize=13, fontweight='bold')
        plt.ylabel('')
    
    # Plot 4: Overcharge Amount by Weight Slab (Figure 4)
    plt.subplot(2, 2, 4)
    if not weight_overcharge.empty:
        weight_overcharge.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Figure 4: Overcharge Amount by Weight Slab (Small-Weight Dominance)', fontsize=13, fontweight='bold')
        plt.ylabel('Amount (Rs.)')
        plt.xticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig('BDM_Combined_Analysis.png', dpi=300)
    print("Combined charts saved to 'BDM_Combined_Analysis.png'.")
    
    # Descriptive Statistics
    print("\n" + "=" * 110)
    print("DESCRIPTIVE STATISTICS SUMMARY TABLE")
    print("=" * 110)
    if 'Weight Difference (kg)' not in df.columns:
        df['Weight Difference (kg)'] = df['Charged Weight'] - df['Total Weight (kg)']
        
    stats_list = [
        calculate_stats(order_df['Order Qty'], 'Order Quantity (Order Report)'),
        calculate_stats(sku_df['Weight (g)'], 'Item Weight (g) (SKU Master)'),
        calculate_stats(df['Total Weight (kg)'], 'Total Weight (kg) [Actual]'),
        calculate_stats(df['Expected Weight Slab (kg)'], 'Expected Weight Slab (kg)'),
        calculate_stats(df['Charged Weight'], 'Charged Weight (kg) [Courier]'),
        calculate_stats(df['Weight Difference (kg)'], 'Weight Difference (kg) [Charged - Actual]'),
        calculate_stats(df['Expected Charge (Rs.)'], 'Expected Charge (Rs.) [Contractual]'),
        calculate_stats(df['Billing Amount (Rs.)'], 'Billing Amount (Rs.) [Invoiced]'),
        calculate_stats(df['Difference (Rs.)'], 'Difference (Rs.) [Expected - Billed]'),
        calculate_stats(overcharged['Overcharge Amount'], 'Overcharge Amount (Rs.) [Overcharged Orders]')
    ]
    stats_df = pd.DataFrame(stats_list)
    print(stats_df.to_string(index=False))
    print("=" * 110)
    
    # Segment Summaries
    print("\n--- SEGMENT 1: OVERCHARGE BY BILLED ZONE ---")
    print(zone_overcharge.to_string())
    print("\n--- SEGMENT 2: OVERCHARGE BY SHIPMENT TYPE ---")
    print(type_overcharge.to_string())
    print("\n--- SEGMENT 3: OVERCHARGE BY WEIGHT SLAB (FIGURE 4) ---")
    print(weight_overcharge.to_string())
    print(f"\nSmall-Weight Items (<=1.0 kg) Overcharge: Rs. {weight_overcharge.get(0.5, 0) + weight_overcharge.get(1.0, 0):.2f} "
          f"({((weight_overcharge.get(0.5, 0) + weight_overcharge.get(1.0, 0)) / weight_overcharge.sum()) * 100:.2f}%)")
    
    print("\nAnalysis completed successfully!")

if __name__ == '__main__':
    main()
