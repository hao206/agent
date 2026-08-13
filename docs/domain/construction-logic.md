# Simplified Estimation Logic — Construction AI Copilot Prototype

This document outlines the simplified estimation formulas and assumptions used in this educational prototype.

---

## 1. Gross Floor Area (GFA) Calculation

- **Purpose**: Preliminary area conversion taking into account foundation and roof area coefficients.
- **Formula**:
  $$ \text{GFA} = (\text{Land Area} \times K_{\text{foundation}}) + (\text{Land Area} \times N_{\text{floors}}) + (\text{Land Area} \times K_{\text{roof}}) $$
- **Unit**: $m^2$
- **Assumption**: Standard coefficients (Strip foundation $K_{\text{foundation}} = 0.50$, Flat concrete roof $K_{\text{roof}} = 0.50$).
- **Limitation**: Illustrative approximation for conceptual estimation; actual architectural floor plans must be measured directly from CAD/BIM drawings.

---

## 2. Preliminary Concrete Volume Takeoff

- **Purpose**: Early-stage conceptual concrete estimation.
- **Formula**:
  $$ \text{Concrete } m^3 = \text{GFA} \times 0.35 $$
- **Unit**: $m^3$
- **Assumption**: Demo ratio of $0.35 \text{ m}^3$ concrete per $m^2$ GFA.
- **Limitation**: **Not** a structural engineering design value. Actual concrete volume depends on structural member design, beam depth, and column schedules.

---

## 3. Preliminary Steel Tonnage Takeoff

- **Purpose**: Early-stage conceptual steel reinforcement estimation.
- **Formula**:
  $$ \text{Steel Tons} = \frac{\text{GFA} \times 100 \text{ kg/m}^2}{1000} $$
- **Unit**: Metric tons
- **Assumption**: Demo ratio of $100 \text{ kg}$ steel per $m^2$ GFA.
- **Limitation**: **Not** a structural rebar schedule. Actual reinforcement rebar tonnage must be calculated by licensed structural engineers.

---

## 4. Preliminary Brick Count Takeoff

- **Purpose**: Early-stage wall masonry estimation.
- **Formula**:
  $$ \text{Brick Count} = \text{GFA} \times 80 \text{ bricks/m}^2 $$
- **Unit**: Bricks (viên)
- **Assumption**: Demo ratio of $80 \text{ bricks}$ per $m^2$ GFA.
- **Limitation**: Simplified demo assumption; wall openings, window ratios, and wall thickness (100mm vs 200mm) are not modeled.

---

## 5. Cost Breakdown Ratios

- **Foundation Cost**: $\text{Land Area} \times K_{\text{foundation}} \times P_{\text{rough}}$
- **Structure Rough Cost**: $(\text{Actual Floor Area} + \text{Roof Area}) \times P_{\text{rough}}$
- **Finishing Cost**: $\text{Actual Floor Area} \times P_{\text{finishing}}$ *(Calculated strictly on actual floor usable area)*
- **Labor Cost**: $(\text{Actual Floor Area} + \text{Foundation Area}) \times P_{\text{labor}}$
- **Permits & Legal**: $15,000,000$ VND fixed baseline demo fee
- **Contingency Buffer**: $5\%$ of direct construction subtotal
