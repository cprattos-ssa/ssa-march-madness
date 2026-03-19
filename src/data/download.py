"""Download competition data from Kaggle and external sources."""

import os
import subprocess
from pathlib import Path


def download_kaggle_data(data_dir: str = "data/raw/kaggle") -> None:
    """Download competition data using the Kaggle CLI."""
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    competition = "march-machine-learning-mania-2026"
    subprocess.run(
        ["kaggle", "competitions", "download", "-c", competition, "-p", data_dir],
        check=True,
    )
    # Unzip if downloaded as zip
    zip_path = Path(data_dir) / f"{competition}.zip"
    if zip_path.exists():
        import zipfile
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(data_dir)
        zip_path.unlink()
    print(f"Kaggle data downloaded to {data_dir}")


if __name__ == "__main__":
    download_kaggle_data()
