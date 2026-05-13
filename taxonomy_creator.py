import requests
import sys
import pandas as pd
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Para autenticacion
def get_auth():
    return HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)

# Busca el elemento por nombre, devuelve el elemento si existe o None
def find_tag(taxonomy_name: str, taxonomy: str) -> dict | None:
    response = requests.get(
        f"{WP_URL}/{taxonomy}",
        params={"search": taxonomy_name, "per_page": 20},
        auth=get_auth()
    )
    response.raise_for_status()

    for tax in response.json():
        if tax["name"].lower() == taxonomy_name.lower():
            return tax
    return None

# Crea el elemento y devuelve el objeto del elemento
def create_tag(taxonomy_name: str, taxonomy: str) -> dict:
    response = requests.post(
        f"{WP_URL}/{taxonomy}",
        json={"name": taxonomy_name},
        auth=get_auth()
    )
    response.raise_for_status()
    return response.json()

# Comprueba si el elemento existe y, si no, lo crea
def ensure_tag_exists(taxonomy_name: str, taxonomy: str) -> bool:
    existing = find_tag(taxonomy_name, taxonomy)
    if existing:
        print(f"  ✔ Exists {taxonomy} — '{taxonomy_name}' (ID: {existing['id']})")
        return False
    else:
        new_tag = create_tag(taxonomy_name, taxonomy)
        print(f"  ✚ Created {taxonomy} — '{taxonomy_name}' (ID: {new_tag['id']})")
        return True

# Lee las columnas name y taxonomy y devuelve un diccionario con una lista por cada columna
def load_tags_from_excel(filepath: str) -> dict[list]:
    df = pd.read_excel(filepath, usecols=["name", "taxonomy"], dtype={"name": str, "taxonomy": str})
    out = {}
    out["taxonomy_name"] = df["name"].dropna().str.strip().loc[lambda s: s != ""].tolist()
    out["taxonomy"] = df["taxonomy"].dropna().str.strip().loc[lambda s: s != ""].tolist()
    return out

# Funcion principal
def process_excel(filepath: str):
    print(f"Reading tags from: {filepath}\n")
    # Lee las columnas del excel
    tags = load_tags_from_excel(filepath)

    # Si no encuentra las columnas return
    if not tags["taxonomy"] or not tags["taxonomy_name"]:
        print("Missing columns.")
        return

    # Muestra el numero de elementos encontrados
    print(f"Found {len(tags["taxonomy"])} tag(s) to process:\n")
    results = {"exists": [], "created": [], "failed": []}

    # Recorre las listas del diccionario
    for i in range(len(tags["taxonomy"])):
        try:
            was_created = ensure_tag_exists(tags["taxonomy_name"][i], tags["taxonomy"][i])
            results["created" if was_created else "exists"].append(tags["taxonomy_name"][i])
        except requests.HTTPError as e:
            print(f"  ✘ Failed   — '{tags["taxonomy_name"][i]}' ({e.response.status_code}: {e.response.text})")
            results["failed"].append(tags["taxonomy_name"][i])

    print(f"\n--- Summary ---")
    print(f"  Processed : {len(tags["taxonomy"])}")
    print(f"  Failed    : {len(results['failed'])}")
    if results["created"]:
        print(f"  Created tags: {', '.join(results['failed'])}")
    if results["failed"]:
        print(f"  Failed tags: {', '.join(results['failed'])}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_excel_file.xlsx>")
        sys.exit(1)

    load_dotenv()

    # --- Configuration ---
    WP_URL = os.getenv("WP_BASE_URL")  # No trailing slash
    WP_USER = os.getenv("WP_USER")
    WP_APP_PASSWORD = os.getenv("WP_PASSWORD") # Use an Application Password

    process_excel(sys.argv[1])