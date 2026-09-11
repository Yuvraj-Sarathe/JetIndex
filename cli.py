"""
JetIndex - Command-Line Interface (CLI) Management Tool
Enterprise DevOps operations, data ingestion, ML forecasting, anomaly scanning,
scenario simulation, and AI Policy Analyst CLI.
"""

import argparse
import datetime

from auth import authenticate_user, get_demo_users
from data_quality.trust_score import get_latest_data_quality
from engine.analytics.cpi_decomposition import get_cpi_decomposition
from engine.analytics.heatmap import get_airfare_heatmap
from engine.analytics.pressure_score import get_inflation_pressure_score
from engine.model_trainer import train_nowcast_model
from engine.nowcast_predictor import InflationNowcastPredictor
from scrapers.market_feed import MarketFeedGenerator, SimulationConfig


def cmd_auth(args):
    """List or test demo user authentication credentials."""
    if args.login:
        username_or_email, pwd = args.login.split(":") if ":" in args.login else (args.login, "")
        res = authenticate_user(username_or_email, pwd)
        if res:
            print(f"[+] Authentication SUCCESS: {res.user.full_name} ({res.user.role.value})")
            print(f"    Token: {res.access_token[:30]}...")
            print(f"    Permissions: {', '.join(res.user.permissions)}")
        else:
            print(f"[-] Authentication FAILED for {username_or_email}")
        return

    demos = get_demo_users()
    print("=" * 80)
    print("JETINDEX - OFFICIAL DEMO & RBAC CREDENTIAL REGISTRY")
    print("=" * 80)
    for u in demos:
        print(f"\n[{u['role']}] {u['full_name']}")
        print(f"  Designation : {u['designation']}")
        print(f"  Organization: {u['organization']}")
        print(f"  Email/Login : {u['email']} (or username '{u['username']}')")
        print(f"  Password    : {u['default_password']}")
        print(f"  Key Features: {', '.join(u['key_features'])}")
    print("=" * 80)


def cmd_serve(args):
    print(f"[*] Starting JetIndex Production Service on {args.host}:{args.port} (Workers: {args.workers})...")
    import uvicorn

    uvicorn.run("app.main:app", host=args.host, port=args.port, workers=args.workers)


def cmd_ingest(args):
    date_str = args.date or datetime.date.today().isoformat()
    booking_date = datetime.date.fromisoformat(date_str)

    print(f"[*] Executing Ingestion Cycle for {date_str}...")
    feed = MarketFeedGenerator(SimulationConfig(seed=None, anomaly_rate=0.015))
    raw_quotes = feed.generate_quotes_for_date(booking_date, day_index=1)

    print("[+] Ingestion Complete:")
    print(f"    - Raw Quotes Generated: {len(raw_quotes)}")
    print("    - Routes: 20 DGCA top domestic routes")
    print("    - Advance Windows: T+1, T+7, T+15, T+30, T+45")


def cmd_train(args):
    print("[*] Training Econometric Nowcast Ensemble (Ridge + GBDT)...")
    ensemble, metrics = train_nowcast_model()
    print("[+] Model Training Successful!")
    print(f"    - Model Version: {metrics.model_version}")
    print(f"    - Training R²: {metrics.r2_train:.4f}")
    print(f"    - Test RMSE: {metrics.rmse_test:.4f}")
    print(f"    - Test MAPE: {metrics.mape_test:.2f}%")
    print(f"    - Total Observations: {metrics.sample_size}")


def cmd_forecast(args):
    print(f"[*] Generating Multi-Model Forecast (Horizon: {args.horizon} days)...")
    predictor = InflationNowcastPredictor()
    rep = predictor.generate_nowcast(horizon_days=args.horizon)
    print(f"[+] Forecast Output (As of {rep.as_of_date}):")
    print(f"    - Current Index: {rep.current_index:.2f}")
    print(f"    - Mean Forecast: {rep.summary_mean_forecast:.2f}")
    print(f"    - Net CPI Impact: {rep.net_projected_headline_cpi_bps:+.4f} bps")
    print(f"    - Alert: {rep.monetary_policy_alert}")


def cmd_pressure(args):
    rep = get_inflation_pressure_score()
    print(f"[+] Airfare Inflation Pressure Score: {rep.pressure_score:.1f}/100 ({rep.pressure_level})")
    print(f"    - 24h Change: {rep.score_change_24h:+.1f} pts")
    print(f"    - RBI MPC Alert: {rep.rbi_monetary_policy_alert}")
    print("    - Top Drivers:")
    for d in rep.ranked_drivers[:4]:
        print(f"      • {d}")


def cmd_cpi_decomp(args):
    rep = get_cpi_decomposition()
    print(
        f"[+] Headline CPI Impact: {rep.total_headline_cpi_impact_bps:+.4f} bps (Transport: {rep.total_transport_impact_bps:+.2f} bps)"
    )
    print("    - Top Contributors:")
    for r in rep.top_positive_contributors[:4]:
        print(
            f"      • {r.route_code} ({r.corridor_name}): {r.headline_cpi_impact_bps:+.4f} bps ({r.share_of_total_inflation_pct:.1f}% share)"
        )


def cmd_heatmap(args):
    rep = get_airfare_heatmap(sort_by=args.sort or "weight", route_filter=args.route)
    print(f"[+] Airfare Heatmap (As of {rep.as_of_date}):")
    print(f"    - Routes: {rep.total_routes}")
    print(f"    - Horizons: {rep.total_horizons}")
    print(f"    - Surge Cells: {rep.summary_surge_count}")
    print(f"    - Discount Cells: {rep.summary_discount_count}")


def cmd_data_quality(args):
    dq = get_latest_data_quality()
    print(f"[+] Overall Data Trust Score: {dq.overall_trust_score:.1f}/100 ({dq.status_rating})")
    print(f"    - Freshness: {dq.freshness_pct:.1f}%")
    print(f"    - Completeness: {dq.completeness_pct:.1f}%")
    print(f"    - Route Coverage: {dq.route_coverage_pct:.1f}%")
    print(f"    - Source Health: {dq.source_health_pct:.1f}%")


def cmd_backtest(args):
    from engine.backtest import DGCABacktestEngine

    engine = DGCABacktestEngine()
    res = engine.run_backtest(num_days=args.days)
    print(f"[+] Backtest Validation Report ({res.sample_days} Days / {res.total_quotes_evaluated:,} Quotes):")
    print(f"    - Pearson r: {res.pearson_r:.4f}")
    print(f"    - MAPE: {res.mape:.2f}%")
    print(f"    - Status: {res.validation_status}")


def main():
    parser = argparse.ArgumentParser(
        prog="jetindex", description="JetIndex - National Airfare Intelligence & Inflation Decision Platform CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve
    p_serve = subparsers.add_parser("serve", help="Start FastAPI production server")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--workers", type=int, default=1)
    p_serve.set_defaults(func=cmd_serve)

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Run on-demand scraping & calculation")
    p_ingest.add_argument("--date", help="Optional YYYY-MM-DD date")
    p_ingest.set_defaults(func=cmd_ingest)

    # train
    p_train = subparsers.add_parser("train", help="Train AI Nowcast ML Ensemble")
    p_train.set_defaults(func=cmd_train)

    # forecast
    p_fc = subparsers.add_parser("forecast", help="Generate forward forecast")
    p_fc.add_argument("--horizon", type=int, default=14)
    p_fc.set_defaults(func=cmd_forecast)

    # pressure
    p_press = subparsers.add_parser("pressure", help="Get Inflation Pressure Score")
    p_press.set_defaults(func=cmd_pressure)

    # cpi-decomp
    p_dec = subparsers.add_parser("cpi-decomp", help="Get CPI route contribution waterfall")
    p_dec.set_defaults(func=cmd_cpi_decomp)

    # heatmap
    p_heat = subparsers.add_parser("heatmap", help="Generate airfare heatmap")
    p_heat.add_argument("--sort", choices=["weight", "fare_desc", "fare_asc", "change"], default="weight")
    p_heat.add_argument("--route", help="Filter by route code")
    p_heat.set_defaults(func=cmd_heatmap)

    # data-quality
    p_dq = subparsers.add_parser("data-quality", help="Inspect Data Trust Scorecard")
    p_dq.set_defaults(func=cmd_data_quality)

    # backtest
    p_bt = subparsers.add_parser("backtest", help="Run DGCA backtesting validation")
    p_bt.add_argument("--days", type=int, default=35)
    p_bt.set_defaults(func=cmd_backtest)

    # auth
    p_auth = subparsers.add_parser("auth", help="List and verify RBAC credentials")
    p_auth.add_argument("--login", help="Test credentials in format user:password")
    p_auth.set_defaults(func=cmd_auth)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
