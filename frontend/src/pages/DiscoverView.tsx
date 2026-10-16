import { useEffect, useState } from "react";
import { fetchRestaurants } from "../routes/CustomerRouter";
import type { Restaurant } from "../types/restaurant";
import { RestaurantDetails } from "./RestaurantDetailsView";

export function Discover() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    fetchRestaurants()
      .then((data) => { if (active) setRestaurants(data); })
      .catch(() => { if (active) setError("Unable to load restaurants. Please reload to try again."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  if (selectedId) {
    return <RestaurantDetails restaurantId={selectedId} onBack={() => setSelectedId(null)} />;
  }

  return (
    <main>
      <h1>What are you craving?</h1>
      {loading && <p role="status">Loading restaurants…</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && !error && restaurants.length === 0 && <p>No restaurants available.</p>}
      <ul>
        {restaurants.map((restaurant) => (
          <li key={restaurant.id}>
            <button type="button" onClick={() => setSelectedId(restaurant.id)}>
              <h2>{restaurant.name}</h2>
              <p>{restaurant.cuisine} · {restaurant.rating}/5</p>
              <p>{restaurant.address}</p>
              <span>View details</span>
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
