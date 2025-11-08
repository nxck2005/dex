import httpx
import random

BASE_URL = "https://pokeapi.co/api/v2/pokemon"

async def get_all_pokemon() -> list[dict]:
    url = f"{BASE_URL}?limit=1025"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data["results"]
    except (httpx.HTTPStatusError, httpx.RequestError):
        return []

async def get_dex_entry(name_or_id: str) -> dict:
    if name_or_id == "1773":
        return {
            "name": "Definery",
            "id": 1773,
            "types": ["dark"],
            "abilities": ["thief"],
            "height": random.randint(1, 100),
            "weight": random.randint(1, 2000),
            "stats": {
                "hp": random.randint(1, 255),
                "attack": random.randint(1, 255),
                "defense": random.randint(1, 255),
                "special-attack": random.randint(1, 255),
                "special-defense": random.randint(1, 255),
                "speed": random.randint(1, 255),
            },
            "flavor_text": "sonned by all",
        }

    sanitized_name = name_or_id.lower().replace(" ", "-")
    if "mega-" in sanitized_name:
        parts = sanitized_name.split("-")
        sanitized_name = f"{parts[1]}-mega"

    url = f"{BASE_URL}/{sanitized_name}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
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
                "name": data["name"].capitalize(),
                "id": data["id"],
                "types": [t["type"]["name"] for t in data["types"]],
                "abilities": [a["ability"]["name"] for a in data["abilities"]],
                "height": data["height"],
                "weight": data["weight"],
                "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
                "flavor_text": flavor_text,
            }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Entry '{name_or_id}' not found."}
        else:
            return {"error": f"HTTP error: {e}"}
    except httpx.RequestError as e:
        return {"error": f"Network error: {e}"}