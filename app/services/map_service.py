import httpx
from geopy.distance import geodesic

OSRM_BASE = "http://router.project-osrm.org/route/v1/driving"

async def get_route(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> dict:
    """OSRM orqali eng qisqa yo'lni hisoblaydi (bepul, OpenStreetMap)"""
    url = f"{OSRM_BASE}/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
    params = {"overview": "full", "geometries": "geojson", "steps": "true"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    route = data["routes"][0]
    steps = []
    for leg in route["legs"]:
        for step in leg["steps"]:
            maneuver = step.get("maneuver", {})
            instruction = maneuver.get("type", "")
            modifier = maneuver.get("modifier", "")
            name = step.get("name", "")
            distance = round(step.get("distance", 0))
            steps.append(f"{instruction} {modifier} — {name} ({distance}m)".strip(" —"))

    coords = route["geometry"]["coordinates"]
    route_points = [{"lat": c[1], "lon": c[0]} for c in coords]

    distance_km = round(route["distance"] / 1000, 2)
    estimated_minutes = max(1, int(route["duration"] / 60))

    return {
        "route": route_points,
        "distance_km": distance_km,
        "estimated_minutes": estimated_minutes,
        "navigation_steps": steps,
    }

def find_nearest_courier(couriers: list[dict], dest_lat: float, dest_lon: float) -> dict | None:
    """Eng yaqin kuryerni topadi"""
    if not couriers:
        return None
    return min(couriers, key=lambda c: geodesic((c["lat"], c["lon"]), (dest_lat, dest_lon)).km)

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Ikki nuqta orasidagi masofani km da qaytaradi"""
    return round(geodesic((lat1, lon1), (lat2, lon2)).km, 3)
