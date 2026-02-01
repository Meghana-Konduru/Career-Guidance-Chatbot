import pandas as pd
import os

CSV_DIR = os.path.dirname(__file__)
TXT_DIR = os.path.dirname(__file__)

def convert(csv_file):
    df = pd.read_csv(csv_file)

    # Combine all text columns into one paragraph
    text_data = []

    for _, row in df.iterrows():
        line = " ".join([str(v) for v in row.values if isinstance(v, str)])
        text_data.append(line)

    # Save output
    out_path = os.path.join(TXT_DIR, os.path.basename(csv_file).replace(".csv", ".txt"))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(text_data))

    print(f"Created: {out_path}")

if __name__ == "__main__":
    for file in os.listdir(CSV_DIR):
        if file.endswith(".csv"):
            convert(os.path.join(CSV_DIR, file))
