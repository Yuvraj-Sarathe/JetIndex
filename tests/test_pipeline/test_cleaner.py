import polars as pl

from pipeline.cleaner import dedupe, flag_sold_out, iqr_filter


def test_dedupe_removes_duplicates():

    df = pl.DataFrame(
        [
            {
                "source": "indigo",
                "route_code": "DEL-BOM",
                "carrier": "6E",
                "flight_no": "6470",
                "depart_date": "2026-10-13",
                "scrape_date": "2026-10-06",
            },
            {
                "source": "indigo",
                "route_code": "DEL-BOM",
                "carrier": "6E",
                "flight_no": "6470",
                "depart_date": "2026-10-13",
                "scrape_date": "2026-10-06",
            },
        ]
    )

    result = dedupe(df)

    assert len(result) == 1


def test_flag_sold_out():

    df = pl.DataFrame(
        [
            {
                "flight_no": "6470",
                "sold_out": True,
                "quality_flag": None,
            },
            {
                "flight_no": "6471",
                "sold_out": False,
                "quality_flag": None,
            },
        ]
    )

    result = flag_sold_out(df)

    assert result["quality_flag"][0] == "sold_out"
    assert result["quality_flag"][1] != "sold_out"


def test_iqr_filter_creates_quality_flag():

    df = pl.DataFrame(
        [
            {
                "route_code": "DEL-BOM",
                "lead_time": 7,
                "scrape_date": "2026-10-06",
                "total_fare": 3000.0,
                "quality_flag": None,
            },
            {
                "route_code": "DEL-BOM",
                "lead_time": 7,
                "scrape_date": "2026-10-06",
                "total_fare": 3100.0,
                "quality_flag": None,
            },
            {
                "route_code": "DEL-BOM",
                "lead_time": 7,
                "scrape_date": "2026-10-06",
                "total_fare": 3200.0,
                "quality_flag": None,
            },
            {
                "route_code": "DEL-BOM",
                "lead_time": 7,
                "scrape_date": "2026-10-06",
                "total_fare": 100000.0,
                "quality_flag": None,
            },
        ]
    )

    result = iqr_filter(df)

    assert "quality_flag" in result.columns
