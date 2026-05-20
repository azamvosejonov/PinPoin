PRICE_PER_KM = 500  # so'm/km

def calculate_fuel_cost(distance_km: float) -> dict:
    cost = round(distance_km * PRICE_PER_KM)
    return {
        "distance_km": distance_km,
        "cost_uzs": cost,
        "price_per_km": PRICE_PER_KM,
        "summary": f"{distance_km} km → {cost:,} so'm",
    }
