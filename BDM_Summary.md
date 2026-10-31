# BDM Courier Invoice Reconciliation & Audit Summary

## Executive Overview
- **Total Invoiced Spend:** ₹13,648.20 across 124 completed orders
- **Contractually Expected Spend:** ₹9,852.20
- **Total Overcharge Amount:** ₹4,426.60 (32.43% of total invoiced value)
- **Overcharged Orders:** 79 out of 124 orders (63.71%)
- **Correctly Charged Orders:** 22 out of 124 orders (17.74%, ₹2,075.30)
- **Undercharged Orders:** 23 out of 124 orders (18.55%, ₹630.60)
- **Net Financial Discrepancy:** -₹3,796.00 (Carrier net overbilling)

---

## Proof of Originality & Notebook Links
- **Public Benchmark Dataset:** [Kaggle B2B Courier Charges Accuracy Benchmark](https://www.kaggle.com/datasets/thedevastator/b2b-courier-charges-accuracy)
- **Interactive Jupyter Notebook:** [`courier_invoice_reconciliation.ipynb`](courier_invoice_reconciliation.ipynb)
- **GitHub Repository:** [https://github.com/madhavdasm/BDM-Courier-Invoice-Reconciliation](https://github.com/madhavdasm/BDM-Courier-Invoice-Reconciliation)
- **Full Capstone Report:** [`BDM_Courier_Invoice_Reconciliation_Report.md`](BDM_Courier_Invoice_Reconciliation_Report.md) / [`BDM_Courier_Invoice_Reconciliation_Report.html`](BDM_Courier_Invoice_Reconciliation_Report.html)
- **Excel Audit Dashboard:** [`Final_Reconciliation_Dashboard.xlsx`](Final_Reconciliation_Dashboard.xlsx)

---

## Descriptive Statistics Summary Table

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

## Results & Findings: Root Causes

### 1. Delivery Zone Discrepancies (Zone D Dominance)
- **Zone D Overcharges:** ₹3,997.40 (**90.31%** of all overcharges)
- **Zone B Overcharges:** ₹429.20 (**9.69%** of all overcharges)
- **Why?** Out of 79 orders contractually destined for Zone B, **60 were erroneously billed under Zone D** by the courier company.
  - *Zone B Forward Rate:* ₹33.00 base + ₹28.30 / addl 0.5 kg slab.
  - *Zone D Forward Rate:* ₹45.40 base (+37.6%) + ₹44.80 / addl 0.5 kg slab (+58.3%).
  - Misclassifying Zone B as Zone D applies an immediate compounding penalty to every order.

### 2. Weight Slabs & Small-Weight Dominance (Figure 4)
- **0.5 kg slab:** ₹2,485.70 (56.15% of overcharges, 49 orders)
- **1.0 kg slab:** ₹1,615.50 (36.49% of overcharges, 25 orders)
- **Combined $\le 1.0\text{ kg}$:** **₹4,101.20 (92.65% of all overcharges)**
- **Why Small-Weight Parcels Suffer Most?**
  1. **Volumetric vs Gross Weight Arbitrage:** Couriers bill on $\max(\text{gross weight}, \frac{L \times W \times H}{5000})$. Small items (100g–300g) packed into standard $20 \times 15 \times 10\text{ cm}$ shipper cartons with void fill yield a volumetric weight of $0.60\text{ kg}$, forcing a 150g item into the 1.0 kg bracket.
  2. **Step-Function Slab Boundary Penalties:** Rounding up into the next 0.5 kg slab incurs an immediate 50%–100% price increase on a lightweight parcel.
  3. **High Catalog Volume Density:** Small items represent >75% of customer orders, concentrating total loss in these tiers.
  4. **Sub-Threshold Leakage:** Small per-parcel discrepancies (₹30–₹60) pass beneath manual AP review thresholds.

### 3. Top 5 Most Overcharged Orders
1. **Order 2001807970:** Overcharged by **₹342.50** (Expected: ₹61.30, Billed: ₹403.80). Zone B billed as D; weight escalated from 0.56kg (1.0kg slab) to 1.70kg (2.0kg slab).
2. **Order 2001807328:** Overcharged by **₹191.60** (Expected: ₹33.00, Billed: ₹224.60). Zone B billed as D; 170g parcel billed at 1.0kg slab.
3. **Order 2001808832:** Overcharged by **₹163.30** (Expected: ₹61.30, Billed: ₹224.60). Zone B billed as D; weight escalated to 2.47kg.
4. **Order 2001810697:** Overcharged by **₹163.30** (Expected: ₹61.30, Billed: ₹224.60). Zone B billed as D.
5. **Order 2001808739:** Overcharged by **₹146.80** (Expected: ₹33.00, Billed: ₹179.80). Zone B billed as D.

---

## Automated Pre-Payment Invoice Auditing & Predictive ML

### Architecture & Implementation
1. **WMS Ingestion:** Capture actual SKU weights and packaging box codes at packing stations.
2. **Pre-Billing Computation:** Compute contractual slab, expected delivery zone, and expected charge before dispatch.
3. **3-Way Matching Gate:** Electronically match courier invoice line items on AWB/Order ID with tolerance $\le \pm \text{₹}0.10$.
4. **Automated ERP Lock & Debit Notes:** Hold payment on overcharged items, issue automated debit notes with attached CSV audit trails, and debit carrier settlement balances.

### Predictive Machine Learning Framework
- **Model 1: Pre-Billing Freight Cost Regression (XGBoost / DNN):** Predicts expected freight cost at checkout/packing ($R^2 \ge 0.98, \text{MAE} \le \text{₹}3.50$) to support dynamic shipping fee calculations and protect gross margins.
- **Model 2: Overcharge Anomaly Classification (Random Forest):** Classifies the risk of invoice discrepancy ($P(\text{Overcharge}) > \tau$), routing high-risk parcels to automated optical scale re-checks.
- **Model 3: Optical Computer Vision Cubing:** Overhead stereoscopic cameras segment parcel bounding boxes ($L \times W \times H$), creating cryptographic proof that refutes carrier volumetric weight claims.
