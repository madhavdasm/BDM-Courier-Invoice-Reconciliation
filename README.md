# BDM Courier Invoice Reconciliation

## Overview
This project is an automated BDM (Business Development & Management) pipeline designed to audit and reconcile e-commerce courier invoices. By independently calculating the correct shipment weight, delivery zone, and expected courier charge for each order, the system compares the expected costs against the courier's billed amounts to identify logistics cost leakage and billing anomalies.

## Key Features
- **Data Integration**: Merges 5 distinct datasets (Order Report, SKU Master, Pincodes, Courier Invoice, Courier Rates) into a unified analysis pipeline.
- **Automated Rate Calculation**: Dynamically calculates expected weight slabs (0.5 kg increments) and applies complex pricing logic (Forward vs. Forward + RTO) based on the specific delivery zone.
- **Discrepancy Detection**: Classifies every shipment as Correctly Charged, Overcharged, or Undercharged.
- **Executive Dashboard**: Generates a highly polished, multi-sheet Excel presentation dashboard (`Final_Reconciliation_Dashboard.xlsx`) containing high-level KPIs, embedded visualization charts (via Matplotlib), isolated analysis of the top 5 overcharged orders, and strategic business findings.

## Key Business Findings
Through this automated reconciliation pipeline, we identified significant systemic anomalies in the courier's billing:
1. **Total Overcharge**: ₹4,426.60 was identified as overcharged, affecting **32.43%** of the total invoiced value.
2. **Zone Routing Errors**: **Zone D** was the primary culprit (₹3,997.40 overcharged). The courier systematically misclassified closer Zone B shipments as farther Zone D shipments.
3. **Weight Calibration Issues**: Over 90% of the financial leakage occurred in the smallest weight tiers (0.5 kg and 1.0 kg), pointing to potential dead-weight volumetric surcharges.

## Tech Stack
- **Python 3.x**
- **Pandas**: For robust data manipulation and merging.
- **Matplotlib / NumPy**: For generating pie and bar charts detailing the overcharge distribution.
- **XlsxWriter**: For the programmatic generation and formatting of the Excel presentation dashboard.

## Usage
To run the reconciliation pipeline and generate the dashboard:

1. Install the required dependencies:
   ```bash
   pip install pandas matplotlib numpy xlsxwriter openpyxl
   ```

2. Place the primary data file (`BDM project.xlsx`) in the root directory.

3. Execute the primary reconciliation calculations:
   ```bash
   python reconciliation.py
   ```

4. Generate the final Excel dashboard and unified analysis charts:
   ```bash
   python generate_dashboard.py
   ```

5. Open `Final_Reconciliation_Dashboard.xlsx` to view the comprehensive BDM report.
