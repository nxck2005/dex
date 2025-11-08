import httpx

BASE_URL = "https://pokeapi.co/api/v2/pokemon"

def _sanitize_input(name_or_id: str) -> str:
    """Sanitizes the input string for the PokeAPI."""
    name = name_or_id.lower()
    if "mega " in name:
        parts = name.split(" ")
        return f"{parts[1]}-mega"
    return name.replace(" ", "-")

async def get_dex_entry(name_or_id: str) -> dict:
    """
    Fetches dex entry data from the PokeAPI.

    Args:
        name_or_id: The name or ID of the entry to fetch.

    Returns:
        A dictionary containing the entry's data, or an error message.
    """
    sanitized_name = _sanitize_input(name_or_id)
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

