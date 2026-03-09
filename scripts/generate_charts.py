"""
cian.ru -- Business Charts Generator
Reads data/data.csv and writes charts/ PNG files.
"""

import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

DATA_PATH   = Path(__file__).parent.parent / "data" / "data.csv"
CHARTS_PATH = Path(__file__).parent.parent / "charts"
CHARTS_PATH.mkdir(exist_ok=True)

# Palette
C = ["#1F77B4","#FF7F0E","#2CA02C","#D62728","#9467BD",
     "#8C564B","#E377C2","#7F7F7F","#BCBD22","#17BECF"]

MATERIAL_LABELS = {
    "monolith":       "Monolith",
    "monolithBrick":  "Monolith-Brick",
    "brick":          "Brick",
    "panel":          "Panel",
    "block":          "Block",
    "stalin":         "Stalin-era",
    "wood":           "Wood",
    "":               "Unknown",
}
SALE_LABELS = {
    "free":        "Free Sale",
    "fz214":       "FZ-214 (New Build)",
    "dupt":        "Assignment",
    "alternative": "Alternative",
    "pdkp":        "Pre-contract",
    "":            "Other",
}
FLAT_LABELS = {
    "rooms":      "Multi-room",
    "studio":     "Studio",
    "openPlan":   "Open Plan",
}

M = 1_000_000   # million RUB

def rub_m(x, _=None):
    return f"{x:.0f}M" if x < 1000 else f"{x/1000:.1f}B"

def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHARTS_PATH / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}")


# ---------------------------------------------------------------------------
def load():
    rows = []
    with open(DATA_PATH, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            try:
                r["_price"] = int(r["price_rub"]) if r["price_rub"].isdigit() else None
            except Exception:
                r["_price"] = None
            try:
                r["_area"] = float(r["total_area"]) if r["total_area"].replace(".", "").isdigit() else None
            except Exception:
                r["_area"] = None
            try:
                r["_floor"] = int(r["floor_number"]) if r["floor_number"].isdigit() else None
            except Exception:
                r["_floor"] = None
            try:
                r["_floors_total"] = int(r["floors_total"]) if r["floors_total"].isdigit() else None
            except Exception:
                r["_floors_total"] = None
            if r["_price"] and r["_area"]:
                r["_ppsm"] = r["_price"] / r["_area"]
            else:
                r["_ppsm"] = None
            rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# 1. Listings by room count
def chart_rooms(rows):
    order = ["Studio", "1-room", "2-room", "3-room", "4-room", "5-room", "6+"]
    def label(r):
        ft = r.get("flat_type", "")
        rc = r.get("rooms_count", "")
        if ft == "studio": return "Studio"
        if rc == "1": return "1-room"
        if rc == "2": return "2-room"
        if rc == "3": return "3-room"
        if rc == "4": return "4-room"
        if rc == "5": return "5-room"
        if rc and int(rc) >= 6: return "6+"
        return None

    counts = defaultdict(int)
    for r in rows:
        lb = label(r)
        if lb: counts[lb] += 1

    labels = [l for l in order if l in counts]
    vals   = [counts[l] for l in labels]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, vals, color=C[:len(labels)])
    ax.set_title("Number of Listings by Apartment Type", fontsize=14, fontweight="bold", pad=10)
    ax.set_ylabel("Listings")
    ax.bar_label(bars, fmt="%d", padding=3)
    save(fig, "01_listings_by_rooms.png")


# ---------------------------------------------------------------------------
# 2. Median price by room count
def chart_price_by_rooms(rows):
    order = ["Studio", "1-room", "2-room", "3-room", "4-room", "5-room"]
    def label(r):
        ft = r.get("flat_type", "")
        rc = r.get("rooms_count", "")
        if ft == "studio": return "Studio"
        if rc in ("1","2","3","4","5"): return f"{rc}-room"
        return None

    buckets = defaultdict(list)
    for r in rows:
        if r["_price"]:
            lb = label(r)
            if lb: buckets[lb].append(r["_price"])

    labels  = [l for l in order if l in buckets]
    medians = [statistics.median(buckets[l]) / M for l in labels]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, medians, color=C[1])
    ax.set_title("Median Sale Price by Apartment Type (RUB millions)", fontsize=14, fontweight="bold", pad=10)
    ax.set_ylabel("Median Price (RUB millions)")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(rub_m))
    ax.bar_label(bars, labels=[f"{v:.1f}M" for v in medians], padding=3, fontsize=9)
    save(fig, "02_median_price_by_rooms.png")


# ---------------------------------------------------------------------------
# 3. Price per sqm by rooms (shows value per unit area)
def chart_ppsm_by_rooms(rows):
    order = ["Studio", "1-room", "2-room", "3-room", "4-room", "5-room"]
    def label(r):
        ft = r.get("flat_type", "")
        rc = r.get("rooms_count", "")
        if ft == "studio": return "Studio"
        if rc in ("1","2","3","4","5"): return f"{rc}-room"
        return None

    buckets = defaultdict(list)
    for r in rows:
        if r["_ppsm"]:
            lb = label(r)
            if lb: buckets[lb].append(r["_ppsm"])

    labels  = [l for l in order if l in buckets]
    medians = [statistics.median(buckets[l]) / 1000 for l in labels]  # thousands

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, medians, color=C[2])
    ax.set_title("Median Price per sq.m by Apartment Type (RUB thousands)", fontsize=14, fontweight="bold", pad=10)
    ax.set_ylabel("Price / sq.m (RUB thousands)")
    ax.bar_label(bars, labels=[f"{v:.0f}K" for v in medians], padding=3, fontsize=9)
    save(fig, "03_ppsm_by_rooms.png")


# ---------------------------------------------------------------------------
# 4. Listings by building material
def chart_material(rows):
    counts = defaultdict(int)
    for r in rows:
        lb = MATERIAL_LABELS.get(r["material_type"], "Unknown")
        counts[lb] += 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top = [(l, v) for l, v in top if l != "Unknown"]
    labels, vals = zip(*top)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, vals, color=C[:len(labels)])
    ax.set_title("Listings by Building Material", fontsize=14, fontweight="bold", pad=10)
    ax.set_ylabel("Number of Listings")
    ax.bar_label(bars, fmt="%d", padding=3)
    plt.xticks(rotation=15, ha="right")
    save(fig, "04_listings_by_material.png")


# ---------------------------------------------------------------------------
# 5. Median price per sqm by building material
def chart_ppsm_by_material(rows):
    order = ["Monolith-Brick", "Monolith", "Brick", "Block", "Panel"]
    buckets = defaultdict(list)
    for r in rows:
        lb = MATERIAL_LABELS.get(r["material_type"], "")
        if lb and lb in order and r["_ppsm"]:
            buckets[lb].append(r["_ppsm"])

    labels  = [l for l in order if l in buckets]
    medians = [statistics.median(buckets[l]) / 1000 for l in labels]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(list(reversed(labels)), list(reversed(medians)), color=C[3])
    ax.set_title("Median Price per sq.m by Building Material (RUB thousands)", fontsize=14, fontweight="bold", pad=10)
    ax.set_xlabel("Price / sq.m (RUB thousands)")
    for bar, v in zip(bars, reversed(medians)):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                f"{v:.0f}K", va="center", fontsize=9)
    save(fig, "05_ppsm_by_material.png")


# ---------------------------------------------------------------------------
# 6. Price distribution buckets
def chart_price_ranges(rows):
    buckets = [
        (0,         20*M,   "< 20M"),
        (20*M,      40*M,   "20-40M"),
        (40*M,      80*M,   "40-80M"),
        (80*M,      150*M,  "80-150M"),
        (150*M,     300*M,  "150-300M"),
        (300*M,     float("inf"), "300M+"),
    ]
    counts = [sum(1 for r in rows if r["_price"] and lo <= r["_price"] < hi)
              for lo, hi, _ in buckets]
    labels = [b[2] for b in buckets]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(labels, counts, color=C[0])
    ax.set_title("Price Range Distribution of Listings", fontsize=14, fontweight="bold", pad=10)
    ax.set_xlabel("Price Range (RUB)")
    ax.set_ylabel("Number of Listings")
    ax.bar_label(bars, fmt="%d", padding=3)
    save(fig, "06_price_distribution.png")


# ---------------------------------------------------------------------------
# 7. Floor level distribution
def chart_floor_distribution(rows):
    buckets = [(1,1,"Ground (1)"),(2,5,"Low (2-5)"),(6,10,"Mid (6-10)"),(11,20,"High (11-20)"),(21,200,"Skyscraper (21+)")]
    counts = []
    for lo, hi, _ in buckets:
        counts.append(sum(1 for r in rows if r["_floor"] and lo <= r["_floor"] <= hi))
    labels = [b[2] for b in buckets]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, counts, color=C[4])
    ax.set_title("Listings by Floor Level", fontsize=14, fontweight="bold", pad=10)
    ax.set_ylabel("Number of Listings")
    ax.bar_label(bars, fmt="%d", padding=3)
    save(fig, "07_floor_distribution.png")


# ---------------------------------------------------------------------------
# 8. Median price by floor tier
def chart_price_by_floor(rows):
    tiers = [(1,1,"Ground"),(2,5,"Low (2-5)"),(6,10,"Mid (6-10)"),(11,20,"High (11-20)"),(21,200,"Skyscraper (21+)")]
    labels, medians = [], []
    for lo, hi, lb in tiers:
        p = [r["_price"] for r in rows if r["_floor"] and lo <= r["_floor"] <= hi and r["_price"]]
        if p:
            labels.append(lb)
            medians.append(statistics.median(p) / M)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, medians, color=C[5])
    ax.set_title("Median Price by Floor Level (RUB millions)", fontsize=14, fontweight="bold", pad=10)
    ax.set_ylabel("Median Price (RUB millions)")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(rub_m))
    ax.bar_label(bars, labels=[f"{v:.0f}M" for v in medians], padding=3, fontsize=9)
    save(fig, "08_price_by_floor.png")


# ---------------------------------------------------------------------------
# 9. Sale type breakdown
def chart_sale_types(rows):
    counts = defaultdict(int)
    for r in rows:
        lb = SALE_LABELS.get(r["sale_type"], "Other")
        if lb != "Other": counts[lb] += 1
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    labels, vals = zip(*top)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, vals, color=C[6:6+len(labels)])
    ax.set_title("Listings by Sale Type", fontsize=14, fontweight="bold", pad=10)
    ax.set_ylabel("Number of Listings")
    ax.bar_label(bars, fmt="%d", padding=3)
    plt.xticks(rotation=10, ha="right")
    save(fig, "09_sale_types.png")


# ---------------------------------------------------------------------------
# 10. Total area distribution
def chart_area_distribution(rows):
    buckets = [(0,40,"< 40 sqm"),(40,60,"40-60"),(60,80,"60-80"),(80,120,"80-120"),(120,200,"120-200"),(200,10000,"200+ sqm")]
    counts = [sum(1 for r in rows if r["_area"] and lo <= r["_area"] < hi)
              for lo, hi, _ in buckets]
    labels = [b[2] for b in buckets]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(labels, counts, color=C[2])
    ax.set_title("Listings by Total Area", fontsize=14, fontweight="bold", pad=10)
    ax.set_xlabel("Area Range (sq.m)")
    ax.set_ylabel("Number of Listings")
    ax.bar_label(bars, fmt="%d", padding=3)
    save(fig, "10_area_distribution.png")


# ---------------------------------------------------------------------------
# 11. Stacked: rooms × sale type
def chart_stacked_rooms_sale(rows):
    sale_order = ["Free Sale", "FZ-214 (New Build)", "Assignment", "Alternative"]
    def room_label(r):
        if r.get("flat_type") == "studio": return "Studio"
        rc = r.get("rooms_count","")
        if rc in ("1","2","3","4"): return f"{rc}-room"
        if rc and rc.isdigit() and int(rc) >= 5: return "5-room+"
        return None

    from collections import defaultdict as dd
    data = dd(lambda: dd(int))
    for r in rows:
        lb = room_label(r)
        st = SALE_LABELS.get(r["sale_type"], "Other")
        if lb and st in sale_order:
            data[lb][st] += 1

    room_order = ["Studio","1-room","2-room","3-room","4-room","5-room+"]
    x_labels = [l for l in room_order if l in data]
    x = np.arange(len(x_labels))

    fig, ax = plt.subplots(figsize=(12, 6))
    bottoms = np.zeros(len(x_labels))
    for i, st in enumerate(sale_order):
        vals = np.array([data[lb].get(st, 0) for lb in x_labels])
        ax.bar(x, vals, bottom=bottoms, label=st, color=C[i], width=0.6)
        bottoms += vals

    ax.set_title("Apartment Type vs Sale Method (Stacked)", fontsize=14, fontweight="bold", pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    ax.set_ylabel("Number of Listings")
    ax.legend(title="Sale Type", loc="upper right")
    save(fig, "11_rooms_by_sale_type.png")


# ---------------------------------------------------------------------------
# 12. Mortgage availability by price range
def chart_mortgage_by_price(rows):
    buckets = [(0,20*M,"< 20M"),(20*M,40*M,"20-40M"),(40*M,80*M,"40-80M"),(80*M,150*M,"80-150M"),(150*M,float("inf"),"150M+")]
    labels, yes_vals, no_vals = [], [], []
    for lo, hi, lb in buckets:
        seg = [r for r in rows if r["_price"] and lo <= r["_price"] < hi]
        if not seg: continue
        yes = sum(1 for r in seg if r.get("mortgage_allowed") == "True")
        no  = len(seg) - yes
        labels.append(lb)
        yes_vals.append(yes)
        no_vals.append(no)

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x, yes_vals, label="Mortgage Available", color=C[2], width=0.6)
    ax.bar(x, no_vals, bottom=yes_vals, label="No Mortgage Info", color=C[7], width=0.6, alpha=0.6)
    ax.set_title("Mortgage Availability by Price Range", fontsize=14, fontweight="bold", pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Number of Listings")
    ax.legend()
    save(fig, "12_mortgage_by_price.png")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Loading {DATA_PATH} ...")
    rows = load()
    print(f"  {len(rows)} rows")

    print("Generating charts ...")
    chart_rooms(rows)
    chart_price_by_rooms(rows)
    chart_ppsm_by_rooms(rows)
    chart_material(rows)
    chart_ppsm_by_material(rows)
    chart_price_ranges(rows)
    chart_floor_distribution(rows)
    chart_price_by_floor(rows)
    chart_sale_types(rows)
    chart_area_distribution(rows)
    chart_stacked_rooms_sale(rows)
    chart_mortgage_by_price(rows)

    print(f"Done. Charts in {CHARTS_PATH}")
