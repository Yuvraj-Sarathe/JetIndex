"""Engine CLI — compute daily index and run backtest."""

import argparse


def main():
    """CLI entry point for engine operations."""
    parser = argparse.ArgumentParser(description="APIx Engine — index computation and backtest")
    parser.add_argument("--date", help="Date to compute index for (YYYY-MM-DD)")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild index from scratch")
    parser.add_argument("--backtest", action="store_true", help="Run backtest against DGCA benchmark")
    args = parser.parse_args()

    if args.backtest:
        from db.session import SessionLocal
        from engine.backtest import run_backtest

        session = SessionLocal()
        try:
            result = run_backtest(session)
            print("\nBacktest Results:")
            print(f"  MAPE: {result['summary']['mape']:.2f}%")
            print(f"  RMSE: {result['summary']['rmse']:.2f}")
            print(f"  Correlation: {result['summary']['corr']:.4f}")
        finally:
            session.close()

    elif args.date:
        from engine.index_calculator import compute_daily

        result = compute_daily(args.date)
        print(f"\nDaily Index for {args.date}:")
        print(f"  APIx: {result['apix']:.4f}")
        print(f"  APIx (base only): {result['apix_base_only']:.4f}")
        print(f"  Quotes: {result['n_quotes']}")
        print(f"  Routes: {result['n_routes']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
