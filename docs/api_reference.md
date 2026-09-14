<!-- generated-by: gsd-doc-writer -->

# API Reference

All endpoints require `Authorization: Bearer <token>` header except `/health` and `/docs`.

**Base URL:** `http://localhost:8000/api/v1` (local) or `https://jetindex-api.onrender.com/api/v1` (production)

## Authentication

```bash
curl -H "Authorization: Bearer SJSSF01-zSIe6SqSVBaVHx1kh7_jBNKUPyVUWtnw6eA" \
     http://localhost:8000/api/v1/apix/daily
```

## Endpoints

### Health

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/health` | Health check | No |

### APIx Index

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/apix/daily` | Daily APIx index values | `from_date`, `to_date` |
| `GET` | `/apix/weekly` | Weekly rolled-up values | `from_date`, `to_date` |
| `GET` | `/apix/monthly` | Monthly rolled-up values | `from_date`, `to_date` |
| `GET` | `/apix/scraped-vs-dgca` | Monthly scraped fare vs DGCA benchmark | — |

**Example Response:**

```json
[
  {
    "date": "2025-01-15",
    "apix": 102.3456,
    "apix_base_only": 101.8923,
    "n_quotes": 24,
    "n_routes": 6
  }
]
```

### Routes

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/routes` | DGCA sector basket with weights | — |
| `GET` | `/routes/heatmap` | Per-route avg fare, volatility, lat/lon | `route_date` |

### Quotes

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/quotes` | Clean quotes with unbundled components | `route_id`, `route_date`, `lead_time`, `carrier`, `limit` (1-500, default 50) |

**Example Response:**

```json
[
  {
    "source": "indigo",
    "route_code": "DEL-BOM",
    "carrier": "6E",
    "flight_no": "6E-234",
    "depart_date": "2025-01-22",
    "lead_time": 7,
    "base_fare": 4500.0,
    "udf": 500.0,
    "taxes": 300.0,
    "convenience_fee": 200.0,
    "other_fees": 0.0,
    "total_fare": 5500.0,
    "quality_flag": "ok"
  }
]
```

### Elasticity

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/elasticity` | Lead-time elasticity matrix | `route_id` (required), `route_date` |

### Backtest

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/backtest` | APIx vs DGCA monthly avg + summary stats | — |

### Forecast

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/forecast/national` | National index forecast with 95% CI | `horizon_days` (1-60, default 14) |
| `GET` | `/forecast/route/{route_code}` | Route-specific forecast | `horizon_days` (1-60, default 14) |

### Anomalies

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/anomalies` | Fare spikes, drops, corridor divergences | `target_date` (YYYY-MM-DD) |

### Analytics

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/analytics/pressure` | Airfare Inflation Pressure Score (0-100) | `target_date` |
| `GET` | `/analytics/cpi-decomposition` | Route-level CPI contribution waterfall | — |
| `GET` | `/analytics/cpi-impact` | Macro CPI transmission sensitivity matrix | — |
| `GET` | `/analytics/pressure-score` | AIPS with component breakdown | `target_date` |
| `GET` | `/analytics/heatmap` | 20×5 airfare heatmap matrix | `target_date`, `sort_by`, `route_filter` |

### Scenario

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `POST` | `/scenario/simulate` | Policy shock simulation | Body: `ScenarioInput` |

**Request Body:**

```json
{
  "scenario_name": "ATF Fuel Shock",
  "airfare_shock_pct": 10.0,
  "demand_change_pct": 5.0,
  "capacity_change_pct": -3.0,
  "atf_fuel_shock_pct": 12.0,
  "seasonal_factor": 1.0
}
```

### Alerts

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/alerts/rules` | Configurable alert rule definitions | — |
| `GET` | `/alerts/live` | Live triggered alerts feed | `limit` (1-100, default 20) |

### Data Quality

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/data-quality` | Composite Data Trust Score (0-100) + 7 dimensions | `target_date` |

### Reports

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/reports/daily` | Daily intelligence dossier | `target_date` |
| `GET` | `/reports/export` | Export report as CSV | `target_date` |

### Route Intelligence

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/route-intelligence/{route_code}` | 360° route dossier | — |

### Source Analytics

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/source-analytics/carriers` | Per-carrier pricing analytics | — |
| `GET` | `/source-analytics/otas` | Per-OTA pricing analytics | — |

### Source Consensus

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/source-consensus/consensus` | Cross-portal dispersion analysis | `route_code` (default "DEL-BOM") |

### Provenance

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/provenance/quote/{quote_id}` | Trace quote through cleaning lifecycle | — |
| `GET` | `/provenance/cell-drilldown` | Drill down from aggregate to underlying quotes | `route_code`, `advance_window`, `calculation_date`, `limit` |

### Validation

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/validation` | Multi-model validation report (Pearson R, MAPE, R²) | — |

### AI Analyst

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `POST` | `/ai-analyst/ask` | Natural language policy questions | Body: `{"question": "...", "user_role": "POLICY_ECONOMIST"}` |

### Telemetry

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/telemetry` | Dashboard telemetry: collection status, freshness | — |

### Temporal

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/temporal/temporal` | Day-of-week multipliers, advance yield curve, seasonal factors | — |

### ML

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `POST` | `/ml/train` | Train the econometric nowcast ensemble | Body: `{"force_retrain": false}` |
| `POST` | `/ml/nowcast` | Generate multi-horizon forward nowcast | Body: `{"horizon_days": 14}` |
| `GET` | `/ml/model/status` | Check trained model metadata | — |

### Admin

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `GET` | `/admin/status` | System health: scrape times, quote counts, coverage | — |
| `POST` | `/admin/trigger-sweep` | Trigger daily scrape sweep manually | — |

### Auth

| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| `POST` | `/auth/login` | Authenticate and get JWT token | Body: `{"username_or_email": "...", "password": "..."}` |
| `GET` | `/auth/demo-users` | List pre-seeded demo users | — |
| `POST` | `/auth/demo-login` | Quick login as demo user | `username` |
| `GET` | `/auth/me` | Get current user profile | — |
| `POST` | `/auth/switch-role` | Switch demo role | Body: `SwitchRoleRequest` |
| `GET` | `/auth/roles` | List all roles and permissions | — |
| `POST` | `/auth/logout` | Logout (client-side token removal) | — |

### WebSocket

| Protocol | Path | Description |
|----------|------|-------------|
| `WS` | `/ws` | Real-time index updates and anomaly broadcasts |

**WebSocket Messages:**

```json
// Subscribe to channels
{"type": "subscribe", "channels": ["national_index", "anomalies"]}

// Ping/pong
{"type": "ping"}
// Response: {"type": "pong", "timestamp": "now"}
```

## RBAC Roles

| Role | Description |
|------|-------------|
| `MOSPI_ADMIN` | Full system access |
| `MOSPI_ANALYST` | Read + analysis |
| `RBI_MPC` | Monetary Policy Committee read access |
| `RBI_ECONOMIST` | Economist read access |
| `DGCA_REGULATOR` | Regulator read access |
| `DGCA_INSPECTOR` | Inspector limited access |
| `SYSTEM_ADMIN` | Infrastructure management |
| `PUBLIC_AUDITOR` | Read-only public data |

## Mock Mode

When `MOCK_MODE=true` (default), all endpoints return realistic fake data from `data/mock/`. No database is required. Set `MOCK_MODE=false` to use real data.
