import asyncio
import json
from backend import get_all_pokemon, get_dex_entry

async def main():
    print("Fetching all Pokémon...")
    all_pokemon_list = await get_all_pokemon()
    all_pokemon_data = []

    for i, p in enumerate(all_pokemon_list):
        print(f"Fetching data for {p['name']} ({i+1}/{len(all_pokemon_list)})...")
        data = await get_dex_entry(p['name'])
        if "error" not in data:
            all_pokemon_data.append(data)

    print("Saving data to pokedex.json...")
    with open("pokedex.json", "w") as f:
        json.dump(all_pokemon_data, f, indent=2)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
