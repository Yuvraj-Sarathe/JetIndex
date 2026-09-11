"""Google Flights scraper — extracts structured fare data with airline info."""

import asyncio
import json
import re
from datetime import date, timedelta
from pathlib import Path


async def scrape_route(origin: str, dest: str, depart: str) -> list[dict]:
    """Navigate to Google Flights and extract structured fare data."""
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth

    fares = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-IN",
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        url = f"https://www.google.com/travel/flights?q=flights+from+{origin}+to+{dest}+on+{depart}+one+way&curr=INR"

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(10)  # Wait for dynamic content

            # Extract structured flight data from the page
            flight_data = await page.evaluate("""() => {
                const flights = [];
                // Google Flights renders flight cards as list items
                // Each card has: airline name, times, duration, stops, price
                const cards = document.querySelectorAll('li[data-resultid], ul.Rk10dc > li, div.pIav2d');

                // Fallback: scan all text blocks that contain flight info
                const allText = document.body.innerText;
                const blocks = allText.split(/\\n/);

                let current = null;
                for (const line of blocks) {
                    const trimmed = line.trim();
                    if (!trimmed) continue;

                    // Detect airline names
                    const airlines = ['IndiGo', 'Air India', 'SpiceJet', 'Vistara', 'GoFirst',
                                     'Akasa Air', 'Air India Express', 'Star Air', 'Alliance Air',
                                     'Zoom Air', 'TruJet', 'FlyBig'];
                    const foundAirline = airlines.find(a => trimmed.includes(a));

                    if (foundAirline && !current) {
                        current = { airline: foundAirline };
                    }

                    // Detect times (e.g., "11:00 PM – 1:25 AM")
                    const timeMatch = trimmed.match(/(\\d{1,2}:\\d{2}\\s*(?:AM|PM))\\s*[–-]\\s*(\\d{1,2}:\\d{2}\\s*(?:AM|PM))/);
                    if (timeMatch && current) {
                        current.depart_time = timeMatch[1];
                        current.arrive_time = timeMatch[2];
                    }

                    // Detect duration
                    const durMatch = trimmed.match(/(\\d+\\s*hr\\s*\\d+\\s*min|\\d+\\s*hr|\\d+\\s*min)/);
                    if (durMatch && current) {
                        current.duration = durMatch[1];
                    }

                    // Detect stops
                    if ((trimmed === 'Nonstop' || trimmed.match(/\\d+\\s*stop/)) && current) {
                        current.stops = trimmed;
                    }

                    // Detect price
                    const priceMatch = trimmed.match(/₹([\d,]+)/);
                    if (priceMatch && current) {
                        const price = parseInt(priceMatch[1].replace(/,/g, ''));
                        if (price > 1000 && price < 80000) {
                            current.total_fare = price;
                            current.currency = 'INR';
                        }
                    }

                    // If we have both airline and price, save and reset
                    if (current && current.airline && current.total_fare) {
                        flights.push({...current});
                        current = null;
                    }
                }

                // Also capture any remaining flight
                if (current && current.airline && current.total_fare) {
                    flights.push({...current});
                }

                return flights;
            }""")

            for fd in flight_data or []:
                if fd.get("total_fare") and fd.get("airline"):
                    fares.append(
                        {
                            "source": "google_flights",
                            "route_code": f"{origin}-{dest}",
                            "origin": origin,
                            "destination": dest,
                            "depart_date": depart,
                            "carrier": fd["airline"],
                            "depart_time": fd.get("depart_time", ""),
                            "arrive_time": fd.get("arrive_time", ""),
                            "duration": fd.get("duration", ""),
                            "stops": fd.get("stops", "Nonstop"),
                            "total_fare": fd["total_fare"],
                            "currency": "INR",
                            "scrape_date": date.today().isoformat(),
                            "scraped_at": date.today().isoformat(),
                        }
                    )

            # Fallback: regex extraction if structured extraction missed
            if not fares:
                content = await page.content()
                price_matches = re.findall(r"₹([\d,]+)", content)
                seen = set()
                for pm in price_matches:
                    val = int(pm.replace(",", ""))
                    if 1000 < val < 50000 and val not in seen:
                        seen.add(val)
                        fares.append(
                            {
                                "source": "google_flights",
                                "route_code": f"{origin}-{dest}",
                                "origin": origin,
                                "destination": dest,
                                "depart_date": depart,
                                "total_fare": val,
                                "currency": "INR",
                                "scrape_date": date.today().isoformat(),
                                "scraped_at": date.today().isoformat(),
                            }
                        )

            # Screenshot
            Path("data/raw/google_flights").mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=f"data/raw/google_flights/{origin}_{dest}.png")

        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")

        await browser.close()

    return fares


async def main():
    depart = (date.today() + timedelta(days=7)).isoformat()
    routes = [
        ("DEL", "BOM"),
        ("DEL", "BLR"),
        ("BOM", "BLR"),
        ("DEL", "CCU"),
        ("DEL", "HYD"),
        ("BOM", "GOI"),
    ]

    all_fares = []
    for origin, dest in routes:
        print(f"Scraping {origin}-{dest}...")
        fares = await scrape_route(origin, dest, depart)
        airlines = [f"{f.get('carrier', '?')}: {f['total_fare']}" for f in fares[:5]]
        print(f"  Found {len(fares)} fares — {', '.join(airlines)}")
        all_fares.extend(fares)
        await asyncio.sleep(3)

    out_path = Path("data/raw/google_flights/all_fares.json")
    with open(out_path, "w") as f:
        json.dump(all_fares, f, indent=2)

    print(f"\nTotal: {len(all_fares)} fares across {len(routes)} routes")
    print(f"Saved to {out_path}")
    return all_fares


if __name__ == "__main__":
    asyncio.run(main())
