# BDM Courier Invoice Reconciliation & Pre-Payment Audit Pipeline

[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![IIT Madras BS Degree](https://img.shields.io/badge/IIT%20Madras-BDM%20Capstone-red.svg)](https://study.iitm.ac.in/ds/)

## 1. Executive Summary
This project delivers an automated **Business Data Management (BDM)** pipeline designed to audit, reconcile, and govern e-commerce courier invoices. By conducting independent **3-way matching** between internal Warehouse Management System (WMS) SKU weights, origin-destination postal code matrices, and contractual 3PL carrier rate cards, the system identifies systematic logistics overbilling, prevents financial leakage, and provides predictive machine learning modeling for freight cost governance.

### Key Audit Metrics
- **Total Invoiced Spend:** ₹13,648.20 across 124 completed orders
- **Contractually Expected Spend:** ₹9,852.20
- **Total Overcharged Amount:** **₹4,426.60** (**32.43%** of total invoiced spend)
- **Overcharged Order Proportion:** **79 out of 124 shipments (63.71%)**
- **Correctly Charged:** 22 orders (17.74%, totaling ₹2,075.30)
- **Undercharged:** 23 orders (18.55%, totaling ₹630.60)
- **Net Recoverable Discrepancy:** -₹3,796.00

---

## 2. Proof of Originality & Project Deliverables

- **Public Benchmark Dataset:** [Kaggle B2B Courier Charges Accuracy Benchmark](https://www.kaggle.com/datasets/purvanahar/b2b-ecommerce-courier-dataset)
- **Interactive Jupyter Analysis Notebook:** [`courier_invoice_reconciliation.ipynb`](courier_invoice_reconciliation.ipynb) ([GitHub Direct Link](https://github.com/madhavdasm/BDM-Courier-Invoice-Reconciliation/blob/main/courier_invoice_reconciliation.ipynb))
- **Comprehensive Capstone Project Report:**
  - Markdown Report: [`BDM_Courier_Invoice_Reconciliation_Report.md`](BDM_Courier_Invoice_Reconciliation_Report.md)
  - Interactive HTML Report: [`BDM_Courier_Invoice_Reconciliation_Report.html`](BDM_Courier_Invoice_Reconciliation_Report.html)
- **Executive Audit Dashboard:** [`Final_Reconciliation_Dashboard.xlsx`](Final_Reconciliation_Dashboard.xlsx) (Contains Dashboard KPIs, Visualizations, Descriptive Statistics, Top 5 Overcharged Orders, and Full Order-Level Audit)
- **Author Information:** Madhavdas M | Roll Number: `24f1001336` | IIT Madras BS in Data Science & Applications

---

## 3. Descriptive Statistics Summary

Parametric and non-parametric summary statistics calculated across all operational variables:

| Numerical Variable | N | Mean (μ) | Std Dev (σ) | Min | Q1 (25%) | Median (Q2) | Q3 (75%) | IQR | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Order Quantity (Order Report)** | 400 | 1.2975 | 0.9198 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 8.0000 |
| **Item Weight (g) (SKU Master)** | 66 | 219.7424 | 146.8555 | 10.0000 | 116.2500 | 165.0000 | 290.0000 | 173.7500 | 600.0000 |
| **Total Weight (kg) [Actual]** | 124 | 0.7135 | 0.4995 | 0.0650 | 0.5000 | 0.5560 | 0.8325 | 0.3325 | 3.0800 |
| **Expected Weight Slab (kg)** | 124 | 0.9274 | 0.5692 | 0.5000 | 0.5000 | 1.0000 | 1.0000 | 0.5000 | 3.5000 |
| **Charged Weight (kg) [Courier]** | 124 | 0.9560 | 0.6628 | 0.1500 | 0.6675 | 0.7250 | 1.1000 | 0.4325 | 4.1300 |
| **Weight Difference (kg) [Charged - Actual]** | 124 | 0.2425 | 0.5334 | -0.5760 | 0.0000 | 0.1580 | 0.2020 | 0.2020 | 3.3650 |
| **Expected Charge (Rs.) [Contractual]** | 124 | 79.4532 | 64.2853 | 33.0000 | 33.0000 | 61.3000 | 90.2000 | 57.2000 | 355.5000 |
| **Billing Amount (Rs.) [Invoiced]** | 124 | 110.0661 | 64.0608 | 33.0000 | 86.7000 | 90.2000 | 135.0000 | 48.3000 | 403.8000 |
| **Difference (Rs.) [Expected - Billed]** | 124 | -30.6129 | 54.2380 | -342.5000 | -57.2000 | -28.9000 | 0.0000 | 57.2000 | 160.7000 |
| **Overcharge Amount (Rs.) [Overcharged Cohort]** | 79 | 56.0329 | 48.7690 | 4.7000 | 28.9000 | 44.8000 | 57.2000 | 28.3000 | 342.5000 |

---

## 4. Results & Findings: Root-Cause Diagnostics

### A. Delivery Zone Misclassification (Zone D Dominance)
- **Zone D Overcharges:** ₹3,997.40 (**90.31%** of all overcharges)
- **Root Cause:** 60 orders destined for Zone B were erroneously billed under Zone D.
- **Contractual Compounding:**
  - *Zone B Forward:* ₹33.00 base + ₹28.30 / additional 0.5 kg slab.
  - *Zone D Forward:* ₹45.40 base (+37.6%) + ₹44.80 / additional 0.5 kg slab (+58.3%).
  - Misclassifying a parcel from Zone B to Zone D causes an immediate compounding base and incremental slab penalty.

### B. Small-Weight Item Overcharging (Figure 4)
- **0.5 kg slab:** ₹2,485.70 (56.15% of overcharges, 49 orders)
- **1.0 kg slab:** ₹1,615.50 (36.49% of overcharges, 25 orders)
- **Combined $\le 1.0\text{ kg}$:** **₹4,101.20 (92.65% of all overcharges)**
- **Why Small-Weight Parcels Suffer Most?**
  1. **Volumetric vs Dead Weight Arbitrage:** Couriers bill on $\max(\text{gross weight}, \frac{L \times W \times H}{5000})$. Small items (100g–300g) packed into standard $20 \times 15 \times 10\text{ cm}$ boxes ($0.60\text{ kg}$ volumetric weight) automatically jump into the 1.0 kg billing slab.
  2. **Step-Function Slab Boundary Penalties:** Crossing a 0.5 kg slab boundary doubles or drastically escalates the parcel cost (+50% to +100%).
  3. **High Catalog Volume Density:** Small items represent >75% of customer orders, concentrating cumulative financial leakage in lightweight tiers.
  4. **Sub-Threshold Auditing Blind-Spots:** Accounts payable sampling ignores small per-parcel discrepancies (₹30–₹60), allowing systematic leakage to pass undetected.

---

## 5. Automated Pre-Payment Invoice Auditing & Predictive ML

### Operational Architecture
```
WMS Order Fulfillment ---> Calculate Real Weights & Zones ---> Contractual Rate Engine
                                                                       |
                                                                       v
Courier Invoiced Line Item (EDI 210) -------------> Automated 3-Way Match Gateway
                                                                       |
                            +------------------------------------------+------------------------------------------+
                            | Variance <= +/- Rs. 0.10                                                            | Variance < -Rs. 0.10 (Overcharged)
                            v                                                                                     v
                     [AUTO-APPROVE]                                                                    [AUTOMATED PAYMENT HOLD]
                  ERP Payment Released                                                               Auto-Issue Audit Debit Note
                                                                                                     Deduct from 3PL Settlement
```

### Predictive Machine Learning Models
1. **Pre-Billing Freight Cost Regression (XGBoost / DNN):** Predicts expected logistics charges at order placement ($R^2 \ge 0.98, \text{MAE} \le \text{₹}3.50$) to support dynamic checkout shipping fees and protect gross margins.
2. **Overcharge Anomaly Risk Classifier (Random Forest):** Predicts the probability ($P(\text{Overcharge}) > \tau$) that a shipment will be contested, routing high-risk parcels to automated optical scale re-checks.
3. **Computer Vision Optical Cubing:** Overhead stereoscopic cameras capture 3D bounding boxes ($L \times W \times H$) in 200ms, creating immutable cryptographic logs that refute courier volumetric weight disputes.

---

## 6. Project Reproduction & Execution Guide

```bash
# 1. Clone repository
git clone https://github.com/madhavdasm/BDM-Courier-Invoice-Reconciliation.git
cd BDM-Courier-Invoice-Reconciliation

# 2. Install dependencies
pip install pandas numpy matplotlib openpyxl xlsxwriter scikit-learn

# 3. Execute order reconciliation and compute descriptive statistics
python reconciliation.py

# 4. Generate the multi-sheet Excel dashboard and charts
python generate_dashboard.py

# 5. Launch interactive analysis notebook
jupyter notebook courier_invoice_reconciliation.ipynb
```
