from __future__ import annotations
import argparse
import subprocess
import sys

# Keep this in sync with pyproject optional-dependencies
GROUPS = {
    "ml-basic": [
        "numpy==1.26.4",
        "pandas==2.2.2",
        "scikit-learn==1.5.2",
        "scipy==1.13.1",
        "matplotlib==3.9.0",
        "seaborn==0.13.2",
        "joblib==1.4.2",
        "openpyxl==3.1.5",
        "tqdm==4.66.4",
    ],
    "ml-advanced": [
        "xgboost==2.1.1",
        "lightgbm==4.3.0",
        "catboost==1.2.5",
        "category-encoders==2.6.3",
        "imbalanced-learn==0.12.3",
        "feature-engine==1.8.1",
    ],
    "dl-basic": [
        "tensorflow==2.17.0",
        "torch==2.4.0",
    ],
    "dl-advanced": [
        "torchvision==0.19.0",
        "torchaudio==2.4.0",
        "tensorflow-probability==0.24.0",
        "einops==0.7.0",
        "transformers==4.43.3",
    ],
    "viz": [
        "plotly==5.24.0",
        "pydot==1.4.2",
        "graphviz==0.20.3",
    ],
    "nlp": [
        "nltk==3.9.1",
        "gensim==4.3.3",
        "spacy==3.7.5",
        "datasets==2.20.0",
        "transformers==4.43.3",
    ],
    "utils": [
        "python-dotenv==1.0.1",
        "requests==2.32.3",
    ],
}

ORDER = [
    "ml-basic", "ml-advanced", "dl-basic", "dl-advanced", "viz", "nlp", "utils"
]

def install_group(group: str) -> None:
    """Install all packages in a group using pip."""
    if group not in GROUPS:
        print(f"Unknown group: {group}")
        sys.exit(1)
    for package in GROUPS[group]:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def list_groups() -> None:
    """List available groups."""
    print("Available groups:")
    for g in GROUPS:
        print(f" - {g}")

def show_group(group: str) -> None:
    """Show packages in a group."""
    if group not in GROUPS:
        print(f"Unknown group: {group}")
        sys.exit(1)
    print(f"Packages in {group}:")
    for pkg in GROUPS[group]:
        print(f"   {pkg}")

def main() -> None:
    parser = argparse.ArgumentParser(description="AxonSuite Installer CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List available groups")

    show_parser = subparsers.add_parser("show", help="Show packages in a group")
    show_parser.add_argument("group", type=str)

    install_parser = subparsers.add_parser("install", help="Install a package group")
    install_parser.add_argument("group", type=str)

    args = parser.parse_args()

    if args.command == "list":
        list_groups()
    elif args.command == "show":
        show_group(args.group)
    elif args.command == "install":
        install_group(args.group)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
