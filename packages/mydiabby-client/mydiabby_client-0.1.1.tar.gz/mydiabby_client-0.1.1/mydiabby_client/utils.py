import csv

def export_to_csv(data, filename="mydiabby_data.csv"):
    """Export list of dicts to CSV."""
    if not data:
        return

    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
