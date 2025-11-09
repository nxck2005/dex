"""
A driver script to control the data pipeline for the Pokedex application.

This script provides a step-by-step process to:
1. Fetch all Pokémon data from the PokeAPI and save it to a local JSON file.
2. Populate the SQLite database from the local JSON file.

The user is prompted for confirmation before each major step.
"""

import asyncio
import json
import sqlite3
from pathlib import Path

from src.pull_data import get_all_pokemon_data
from src.database import (
    create_tables,
    insert_pokemon_data,
    insert_evolution_data,
    db_path,
    data_path,
)


def confirm_step(prompt: str) -> bool:
    """Gets user confirmation for a given step."""
    while True:
        response = input(f"{prompt} [y/n]: ").lower().strip()
        if response in ["y", "yes"]:
            return True
        if response in ["n", "no"]:
            return False
        print("Invalid input. Please enter 'y' or 'n'.")


def populate_database_from_json():
    """
    Populates the database using the data from dex.json.
    """
    print("--- Starting Database Population ---")

    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        print("Please run the API fetching step first.")
        return

    print(f"Loading data from {data_path}...")
    with open(data_path, "r") as f:
        all_data = json.load(f)

    pokemon_data = all_data.get("pokemon", [])
    evolution_data = all_data.get("evolutions", [])

    if not pokemon_data:
        print("No Pokémon data found in the JSON file. Aborting.")
        return

    print(f"Connecting to database at {db_path}...")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    try:
        print("Creating database tables (if they don't exist)...")
        create_tables(conn)

        print(f"Inserting data for {len(pokemon_data)} Pokémon...")
        insert_pokemon_data(conn, pokemon_data)

        if evolution_data:
            print(f"Inserting data for {len(evolution_data)} evolution chains...")
            insert_evolution_data(conn, evolution_data)
        
        conn.commit()
        print("--- Database Population Complete! ---")
    except Exception as e:
        print(f"An error occurred during database population: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")


async def main():
    """Main driver function."""
    print("--- Pokedex Data Pipeline Driver ---")

    # Phase 1: Fetch data from API
    if confirm_step("Phase 1: Do you want to fetch all data from the PokeAPI?"):
        print("Starting API data fetch. This may take a few moments...")
        await get_all_pokemon_data()
        print("API data fetch complete. Data saved to dex.json.")
    else:
        print("Skipping API data fetch.")

    print("-" * 20)

    # Phase 2: Populate database
    if confirm_step("Phase 2: Do you want to populate the database from dex.json?"):
        populate_database_from_json()
    else:
        print("Skipping database population.")

    print("\nData pipeline finished.")


if __name__ == "__main__":
    asyncio.run(main())
