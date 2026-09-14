<!-- generated-by: gsd-doc-writer -->

# Index Methodology

This document describes the mathematical methodology behind the APIx airfare price index.

## Primary Index: DGCA-Weighted Laspeyres

The APIx index uses the **Laspeyres price index** with DGCA passenger volume weights:

```
I_t = Σ(P_it × Q_i0) / Σ(P_i0 × Q_i0) × 100
```

Where:
- `i` = route in basket (20 routes)
- `P_it` = median total_fare for route i on day t
- `Q_i0` = DGCA passenger volume weight (base period)
- `P_i0` = base period price (first 7 days of data = 100)

## Base Period

The base period is defined as the **first 7 days of live data collection**. During this period, the index is normalized to 100. All subsequent daily values are relative to this base.

```python
# Base period configuration
base_period:
  method: "first_n_days"
  n_days: 7
```

Base period prices (`P_i0`) are computed as the average `total_fare` per route over the first 7 days of `fare_quotes` data with `quality_flag = 'ok'`.

## DGCA Weights

Route weights are derived from DGCA "City Pair Wise Passenger Traffic" for FY 2024–25:

```
weight_i = passengers_on_route_i / total_passengers_across_all_6_routes
```

Top 6 routes by weight:

| Route | Passengers (FY 2024–25) | Weight |
|-------|------------------------:|-------:|
| DEL–BOM | 68,50,869 | 0.2958 |
| DEL–BLR | 46,81,042 | 0.2021 |
| BOM–BLR | 41,14,574 | 0.1776 |
| DEL–CCU | 27,70,386 | 0.1196 |
| MAA–DEL | 24,52,761 | 0.1059 |
| BLR–HYD | 22,93,602 | 0.0990 |

The full 20-route basket is defined in `config/routes.yaml` and `config/dgca_weights.csv`.

## Price Aggregation

For each route on each day, prices are aggregated across carriers and lead times:

1. **Per (route, lead_time):** Median `total_fare` across all carriers
2. **Per route:** Mean or median of the 5 lead-time medians (configurable via `price_agg`)

The default aggregation is **median** for robustness against outliers.

## Index Computation Flow

```
1. Fetch median fares per route for compute_date
   └─ Fallback: ±3 day window if no data for exact date

2. Fetch DGCA weights from dgca_weights table

3. Fetch base period prices (first 7 days average)

4. Compute Laspeyres index:
   I_t = Σ(P_it × Q_i0) / Σ(P_i0 × Q_i0) × 100

5. Write result to apix_daily table
```

## Additional Index Formulas

### Fisher Ideal Index

```
I_F = √(I_L × I_P)
```

Geometric mean of Laspeyres and Paasche. Considered the "ideal" index because it corrects for substitution bias.

### Paasche Index

```
I_P = Σ(p₁ × q₁) / Σ(p₀ × q₁) × 100
```

Uses current-period quantity weights derived from price elasticity (ε = -0.85):

```
q_1r ∝ w_r × R_r^(1+ε)  where R_r = p_1r/p_0r
```

### Jevons Index

```
J_r = (∏ p_1k / p_0k)^(1/n)
```

Unweighted geometric mean of price relatives.

### Geometric Young Index

```
I_t = Π(P_it / P_i0)^(Q_i0) × 100
```

Weighted geometric mean.

### Törnqvist Index

```
I_T = ∏(p_1/p_0)^((s_0+s_1)/2) × 100
```

Where s_0 and s_1 are base and current period expenditure shares.

### Walsh Index

```
I_W = Σ(p_1 × √(q_0 × q_1)) / Σ(p_0 × √(q_0 × q_1)) × 100
```

Quantity-weighted with geometric mean of base and current quantities.

### Base-Only Index

Laspeyres computed using only `base_fare` (excluding unbundled components), providing a view of underlying ticket price movements without fee distortion.

## CPI Transmission

The APIx index is designed to feed into India's Consumer Price Index:

| Parameter | Value | Source |
|-----------|-------|--------|
| Airfare share in transport CPI | 3.85% | MoSPI |
| Transport CPI weight in headline | 8.59% | MoSPI |
| Effective headline CPI weight | 0.003307 | Computed |

**Transmission calculation:**

```
daily_pct_change = (I_t - I_{t-1}) / I_{t-1} × 100
transport_bps = daily_pct_change × 3.85 / 100 × 10000
headline_bps = transport_bps × 8.59 / 100
```

## Substitution Bias

Laspeyres systematically overstates inflation because it assumes fixed quantities (consumers cannot substitute away from routes that become relatively more expensive). The Fisher index corrects for this.

```
bias_index_points = I_L - I_F
bias_pct = (I_L - I_F) / I_F × 100
```

The substitution bias is reported alongside the primary index for transparency.

## Weekly and Monthly Rollups

### Weekly

```sql
SELECT
    date_trunc('week', date)::date AS week_start,
    AVG(apix) AS apix,
    SUM(n_quotes) AS n_quotes
FROM apix_daily
GROUP BY date_trunc('week', date)
```

### Monthly

```sql
SELECT
    date_trunc('month', date)::date AS month_start,
    AVG(apix) AS apix,
    SUM(n_quotes) AS n_quotes
FROM apix_daily
GROUP BY date_trunc('month', date)
```

## Backtest Methodology

The APIx index is validated against DGCA monthly average fares:

- **Period:** January 2024 – November 2025 (32 data points)
- **Metrics:** MAPE, RMSE, Pearson r
- **Rebasing:** APIx values are rebased to match DGCA fare levels for comparison

DGCA data sourced from Kaggle ["India Aviation Traffic Data"](https://github.com/Vonter/india-aviation-traffic) by Vonter — compiled from DGCA published reports.

## Limitations

1. **Coverage:** Only 20 domestic routes — does not include international or regional routes
2. **Sources:** Currently 2 active scrapers (IndiGo, MakeMyTrip) — not all carriers/OTAs
3. **Lead times:** 5 advance purchase windows — does not capture same-day or last-minute fares comprehensively
4. **Base period:** First 7 days may not be representative of "normal" market conditions
5. **Substitution:** Laspeyres overstates inflation; Fisher corrects for this but is not the primary index
6. **Seasonality:** No seasonal adjustment applied to the daily index
7. **Data freshness:** DGCA weight data is from FY 2024–25 — may not reflect current traffic patterns
