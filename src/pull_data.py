"""
This module is responsible for fetching all Pokémon data directly from the PokeAPI.

It is a self-contained script that should not depend on the application's
internal backend, as it is used to generate the initial data source.
"""
import asyncio
import json
import os
import httpx

BASE_URL = "https://pokeapi.co/api/v2"
JSON_PATH = os.path.join("data", "dex.json")

async def get_pokemon_details(client: httpx.AsyncClient, pokemon_url: str) -> dict | None:
    """Fetches detailed information for a single Pokémon."""
    try:
        response = await client.get(pokemon_url)
        response.raise_for_status()
        data = response.json()

        species_url = data["species"]["url"]
        species_response = await client.get(species_url)
        species_response.raise_for_status()
        species_data = species_response.json()

        flavor_text = ""
        for entry in species_data["flavor_text_entries"]:
            if entry["language"]["name"] == "en":
                flavor_text = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                break

        return {
            "name": data["name"],
            "id": data["id"],
            "types": [t["type"]["name"] for t in data["types"]],
            "abilities": [a["ability"]["name"] for a in data["abilities"]],
            "height": data["height"],
            "weight": data["weight"],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            "flavor_text": flavor_text,
        }
    except httpx.HTTPStatusError as e:
        print(f"Error fetching {pokemon_url}: {e.response.status_code}")
        return None
    except Exception as e:
        print(f"An unexpected error for {pokemon_url}: {type(e).__name__} - {e}")
        return None

async def main():
    """
    Main function to fetch all data, process it, and save to a JSON file.
    """
    print("Fetching master Pokémon list...")
    sem = asyncio.Semaphore(100)  # Limit to 100 concurrent requests

    async def fetch_with_semaphore(client: httpx.AsyncClient, url: str):
        async with sem:
            return await get_pokemon_details(client, url)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/pokemon?limit=1025")
            response.raise_for_status()
            pokemon_list = response.json()["results"]

            tasks = [fetch_with_semaphore(client, p["url"]) for p in pokemon_list]
            
            all_pokemon_data = []
            for i, task in enumerate(asyncio.as_completed(tasks)):
                result = await task
                if result:
                    all_pokemon_data.append(result)
                print(f"Processed Pokémon ({len(all_pokemon_data)}/{len(pokemon_list)})...", end="\r")

    except httpx.HTTPStatusError as e:
        print(f"Failed to fetch master list: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    # Sort data by ID before saving
    all_pokemon_data.sort(key=lambda p: p["id"])

    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    print(f"\nSaving {len(all_pokemon_data)} entries to {JSON_PATH}...")
    with open(JSON_PATH, "w") as f:
        json.dump(all_pokemon_data, f, indent=2)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())