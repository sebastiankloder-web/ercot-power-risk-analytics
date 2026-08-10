import urllib.request
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")


class ERCOTHTMLParser(HTMLParser):
    """Pure Python HTML parser for ERCOT public settlement tables."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = []
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag in ("td", "th"):
            self.in_cell = True

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.in_cell = False
        elif tag == "tr" and self.current_row:
            self.rows.append(self.current_row)
            self.current_row = []

    def handle_data(self, data):
        if self.in_cell:
            cleaned = data.strip()
            if cleaned:
                self.current_row.append(cleaned)


def parse_interval_ending(ie):
    """Converts ERCOT Interval Ending string (e.g., '0015', '0100', '2400')

    into standard DeliveryHour (1-24) and DeliveryInterval (1-4).
    """
    ie_str = str(ie).zfill(4)
    hours = int(ie_str[:2])
    minutes = int(ie_str[2:])
    if minutes == 0:
        return hours, 4
    else:
        return hours + 1, minutes // 15


def fetch_ercot_real_data(days_back=7, filename="ercot_rtm_real.csv"):
    """Fetches real ERCOT Real-Time Settlement Point Prices directly from ERCOT public servers."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[FETCHING] Direct connection to ERCOT CDR web server (last {days_back} days)...")

    all_dfs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    today = datetime.now()  # noqa: DTZ005

    for i in range(days_back):
        target_date = today - timedelta(days=i)
        date_str = target_date.strftime("%Y%m%d")

        # Today's live endpoint vs daily archives
        if i == 0:
            url = "https://www.ercot.com/content/cdr/html/real_time_spp.html"
        else:
            url = f"https://www.ercot.com/content/cdr/html/{date_str}_real_time_spp.html"

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                html_content = response.read().decode("utf-8")

            parser = ERCOTHTMLParser()
            parser.feed(html_content)

            if len(parser.rows) > 1:
                cols = parser.rows[0]
                data = parser.rows[1:]
                df = pd.DataFrame(data, columns=cols)
                all_dfs.append(df)
                print(f"  ✓ Fetched {len(df)} price intervals for {target_date.strftime('%Y-%m-%d')}")
        except Exception:  # noqa: BLE001, S112
            # Skip if date is unavailable or not yet posted
            continue

    if not all_dfs:
        raise RuntimeError("Could not retrieve real ERCOT data from web feeds.")

    combined_raw = pd.concat(all_dfs, ignore_index=True)

    # Parse interval endings
    combined_raw[["DeliveryHour", "DeliveryInterval"]] = combined_raw[
        "Interval Ending"
    ].apply(lambda x: pd.Series(parse_interval_ending(x)))

    target_hubs = [
        col
        for col in ["HB_BUSAVG", "HB_HOUSTON", "HB_NORTH", "HB_WEST", "HB_SOUTH"]
        if col in combined_raw.columns
    ]

    # Melt to long format matching standard pipeline schema
    df_long = combined_raw.melt(
        id_vars=["Oper Day", "DeliveryHour", "DeliveryInterval"],
        value_vars=target_hubs,
        var_name="SettlementPointName",
        value_name="SettlementPointPrice",
    )

    df_long = df_long.rename(columns={"Oper Day": "DeliveryDate"})
    df_long["SettlementPointPrice"] = pd.to_numeric(
        df_long["SettlementPointPrice"], errors="coerce"
    )
    df_long["DSTFlag"] = "N"

    final_df = df_long[
        [
            "DeliveryDate",
            "DeliveryHour",
            "DeliveryInterval",
            "SettlementPointName",
            "SettlementPointPrice",
            "DSTFlag",
        ]
    ].dropna(subset=["SettlementPointPrice"])

    out_path = RAW_DIR / filename
    final_df.to_csv(out_path, index=False)
    print(f"[SUCCESS] Saved live ERCOT market data to: {out_path} ({len(final_df):,} rows)")


if __name__ == "__main__":
    fetch_ercot_real_data()