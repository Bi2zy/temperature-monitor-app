from pathlib import Path
import sys

# A quick test runner to execute our new tests without pytest installed.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from tests.test_export_csv import test_to_csv_bytes_basic, test_to_csv_bytes_empty_dataframe


def main():
    test_to_csv_bytes_basic()
    print("test_to_csv_bytes_basic PASS")

    test_to_csv_bytes_empty_dataframe()
    print("test_to_csv_bytes_empty_dataframe PASS")


if __name__ == "__main__":
    main()
