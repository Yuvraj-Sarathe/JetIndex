from datetime import date

from pipeline.parsers.makemytrip_parser import parse


def test_makemytrip_parser():
    payload = {
        "searchResult": {
            "flightOffers": [
                {
                    "airline": {"code": "6E", "name": "IndiGo"},
                    "flightNumber": "6E-123",
                    "departure": "2026-10-13T06:55:00",
                    "fare": {
                        "totalFare": 6057,
                        "currency": "INR",
                        "breakdown": {
                            "baseFare": 4395,
                            "taxes": 1662,
                            "convenienceFee": 0,
                        },
                    },
                    "refundable": False,
                    "seatsLeft": 5,
                    "stops": 0,
                    "soldOut": False,
                }
            ]
        }
    }

    job_meta = {
        "source": "makemytrip",
        "route_code": "DEL-BOM",
        "origin": "DEL",
        "destination": "BOM",
        "scrape_date": date(2026, 10, 6),
        "scraped_at": "2026-10-06T13:47:36",
        "lead_time": 7,
    }

    quotes = parse(payload, job_meta)

    assert len(quotes) == 1

    quote = quotes[0]

    assert quote.source == "makemytrip"
    assert quote.route_code == "DEL-BOM"
    assert quote.origin == "DEL"
    assert quote.destination == "BOM"
    assert quote.carrier == "6E"
    assert quote.flight_no == "6E-123"
    assert quote.total_fare == 6057
    assert quote.currency == "INR"
    assert quote.fare_breakdown["baseFare"] == 4395
    assert quote.fare_breakdown["taxes"] == 1662