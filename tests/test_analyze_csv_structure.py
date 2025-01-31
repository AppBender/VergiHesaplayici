import pandas as pd


def analyze_csv_structure(file_path):
    df = pd.read_csv(file_path, encoding='utf-8', header=None)

    print("\nCSV Structure Analysis:")
    print("=" * 50)

    for idx, row in df.iterrows():
        if row.empty or pd.isna(row.iloc[0]):
            print(f"Skipping empty or invalid row {idx}")
            continue

        if row.iloc[0] == 'Statement':
            if row.iloc[1] == 'Header':
                print(f"Row {idx}: Statement Header")
            elif row.iloc[1] == 'Data':
                print(f"Row {idx}: Statement Data - {row.iloc[2]}: {row.iloc[3]}")
        elif row.iloc[0] == 'Account Information':
            print(f"Row {idx}: Account Info - {row.iloc[2]}: {row.iloc[3]}")
        elif 'Trades' in str(row.values):
            print(f"Row {idx}: Trades section start")
        elif pd.isna(row.iloc[0]):
            print(f"Row {idx}: Empty row")
        else:
            print(f"Row {idx}: Other type - {row.iloc[0]}")


# Test function
def test_analyze_csv_structure():
    analyze_csv_structure('U7470952_20241202_20250103.csv')


if __name__ == "__main__":
    test_analyze_csv_structure()
