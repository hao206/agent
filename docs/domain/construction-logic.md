# Construction Math & Deterministic BOQ Calculation Methodology (TCVN)

## 1. Gross Floor Area (GFA) Formula

Total Gross Floor Area (GFA / Tổng diện tích sàn xây dựng) is computed deterministically using standard Vietnamese construction practice coefficients:

$$ \text{GFA} = (\text{Land Area} \times K_{\text{foundation}}) + (\text{Land Area} \times N_{\text{floors}}) + (\text{Land Area} \times K_{\text{roof}}) $$

### Foundation Coefficients ($K_{\text{foundation}}$)
- **Móng đơn (Single Foundation)**: $30\%$ ($0.30$)
- **Móng cọc (Pile Foundation)**: $40\%$ ($0.40$)
- **Móng băng (Strip Foundation)**: $50\%$ ($0.50$)
- **Móng bè (Mat Foundation)**: $80\%$ ($0.80$)

### Roof Coefficients ($K_{\text{roof}}$)
- **Mái tôn (Corrugated Iron)**: $30\%$ ($0.30$)
- **Mái Bê tông cốt thép (Flat Concrete)**: $50\%$ ($0.50$)
- **Mái ngói BTCT (Tile Roof)**: $70\%$ ($0.70$)

---

## 2. Quantity Takeoff (BOQ) Estimation Formulas

- **Concrete Volume ($m^3$)**:
  $$ \text{Concrete } m^3 = \text{GFA} \times 0.35 $$
- **Steel Tonnage (Tấn)**:
  $$ \text{Steel Tons} = \frac{\text{GFA} \times 100 \text{ kg/m}^2}{1000} $$
- **Brick Count (Viên)**:
  $$ \text{Brick Count} = \text{GFA} \times 80 \text{ viên/m}^2 $$

---

## 3. Cost Breakdown Components

1. **Foundation Cost**: $\text{Land Area} \times K_{\text{foundation}} \times P_{\text{rough}}$
2. **Structure Rough Cost**: $(\text{Floors Area} + \text{Roof Area}) \times P_{\text{rough}}$
3. **Finishing Cost**: $\text{Actual Floor Area} \times P_{\text{finishing}}$ *(Refactored logic)*
4. **Labor Cost**: $\text{Actual Floor Area} \times P_{\text{labor}}$ *(Refactored logic)*
5. **Permits & Legal**: $15,000,000$ VND fixed baseline
6. **Contingency Buffer**: $5\%$ of construction subtotal
