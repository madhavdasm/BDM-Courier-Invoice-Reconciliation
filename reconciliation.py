import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_weight_slab(weight):
    return np.ceil(weight / 0.5) * 0.5

def main():
    file_path = 'BDM project.xlsx'
    
    # 1. Load Data
    print("Loading data...")
    pincode_df = pd.read_excel(file_path, sheet_name='pincode')
    sku_df = pd.read_excel(file_path, sheet_name='SKU Master')
    order_df = pd.read_excel(file_path, sheet_name='Order Report')
    invoice_df = pd.read_excel(file_path, sheet_name='Courier company-Invoice')
    rates_df = pd.read_excel(file_path, sheet_name='Courier company - Rates')
    
    # 2. Preprocess & Clean
    print("Preprocessing data...")
    order_df.rename(columns={'ExternOrderNo': 'Order ID'}, inplace=True)
    pincode_df.drop_duplicates(subset=['Customer Pincode'], inplace=True) 
    
    # 3. Calculate Weight per Order
    order_sku_df = pd.merge(order_df, sku_df, on='SKU', how='left')
    order_sku_df['Total Weight (g)'] = order_sku_df['Order Qty'] * order_sku_df['Weight (g)']
    
    order_weight_df = order_sku_df.groupby('Order ID')['Total Weight (g)'].sum().reset_index()
    order_weight_df['Total Weight (kg)'] = order_weight_df['Total Weight (g)'] / 1000.0
    order_weight_df['Expected Weight Slab (kg)'] = order_weight_df['Total Weight (kg)'].apply(calculate_weight_slab)
    
    # 4. Merge with Invoice
    reconciliation_df = pd.merge(invoice_df, order_weight_df, on='Order ID', how='left')
    
    # 5. Merge with Pincode to get expected Zone
    reconciliation_df = pd.merge(reconciliation_df, pincode_df[['Customer Pincode', 'Zone']], 
                                 on='Customer Pincode', how='left')
    
    reconciliation_df.rename(columns={'Zone_x': 'Billed Zone', 'Zone_y': 'Expected Delivery Zone'}, inplace=True)
    
    if 'Zone' in reconciliation_df.columns:
        reconciliation_df.rename(columns={'Zone': 'Expected Delivery Zone'}, inplace=True)
    
    # 6. Calculate Expected Charges
    print("Calculating expected charges...")
    rates = rates_df.iloc[0]
    
    def calculate_expected_charge(row):
        zone = row['Expected Delivery Zone']
        if pd.isna(zone):
            return 0
        zone = str(zone).lower()
        
        weight_slab = row['Expected Weight Slab (kg)']
        shipment_type = str(row['Type of Shipment']).strip().lower()
        
        fwd_fixed = rates.get(f'fwd_{zone}_fixed', 0)
        fwd_add = rates.get(f'fwd_{zone}_additional', 0)
        rto_fixed = rates.get(f'rto_{zone}_fixed', 0)
        rto_add = rates.get(f'rto_{zone}_additional', 0)
        
        charge = 0
        
        additional_weight = max(0, weight_slab - 0.5)
        additional_slabs = additional_weight / 0.5
        
        if shipment_type == 'forward charges':
            charge = fwd_fixed + (additional_slabs * fwd_add)
        
        elif shipment_type == 'forward and rto charges':
            charge = (
                fwd_fixed
                + (additional_slabs * fwd_add)
                + rto_fixed
                + (additional_slabs * rto_add)
            )
        
        return charge
        
    reconciliation_df['Expected Charge (Rs.)'] = reconciliation_df.apply(calculate_expected_charge, axis=1)
    
    # 7. Reconciliation Differences
    reconciliation_df['Difference (Rs.)'] = reconciliation_df['Expected Charge (Rs.)'] - reconciliation_df['Billing Amount (Rs.)']
    
    def determine_status(diff):
        if abs(diff) < 0.1: 
            return 'Correctly Charged'
        elif diff < 0:
            return 'Overcharged'
        else:
            return 'Undercharged'
            
    reconciliation_df['Charge Status'] = reconciliation_df['Difference (Rs.)'].apply(determine_status)
    
    # 8. Save final report
    print("Saving reconciliation report...")
    final_cols = [
        'Order ID', 'AWB Code', 'Total Weight (kg)', 'Expected Weight Slab (kg)', 
        'Charged Weight', 'Expected Delivery Zone', 'Billed Zone', 
        'Expected Charge (Rs.)', 'Billing Amount (Rs.)', 'Difference (Rs.)', 'Charge Status'
    ]
    try:
        final_df = reconciliation_df[final_cols]
    except KeyError as e:
        print(f"Warning: Column missing from final output: {e}")
        final_df = reconciliation_df
    
    final_df.to_excel('Reconciliation_Report.xlsx', index=False)
    
    # 9. Visualizations
    print("Generating visualizations...")
    summary_counts = final_df['Charge Status'].value_counts()
    
    overcharged_amt = final_df[final_df['Charge Status'] == 'Overcharged']['Difference (Rs.)'].sum()
    undercharged_amt = final_df[final_df['Charge Status'] == 'Undercharged']['Difference (Rs.)'].sum()
    correctly_charged_amt = final_df[final_df['Charge Status'] == 'Correctly Charged']['Billing Amount (Rs.)'].sum()
    
    summary_amounts = pd.Series({
        'Overcharged': abs(overcharged_amt), 
        'Undercharged': abs(undercharged_amt), 
        'Correctly Charged': correctly_charged_amt
    })
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    if not summary_counts.empty:
        plt.pie(summary_counts, labels=summary_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
        plt.title('Proportion of Order Status')
    
    plt.subplot(1, 2, 2)
    if not summary_amounts.empty:
        summary_amounts.plot(kind='bar', color=['#ff9999','#66b3ff','#99ff99'])
        plt.title('Total Amount by Status (Absolute)')
        plt.ylabel('Amount (Rs.)')
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('Reconciliation_Summary.png')
    
    print("Reconciliation complete. Files saved: Reconciliation_Report.xlsx, Reconciliation_Summary.png")

if __name__ == '__main__':
    main()
