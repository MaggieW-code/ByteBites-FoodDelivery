import { useEffect, useState } from "react";
import { fetchRestaurants } from "../api/restaurants";
import type { Restaurant } from "../types/restaurant";
import { Link } from "react-router-dom";

import { useDebounce } from "../hooks/useDebounce";
import { searchRestaurants } from "../lib/searchRestaurants";

export function Discover() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const debouncedSearch = useDebounce(searchTerm, 250);
  const visible = searchRestaurants(restaurants, debouncedSearch);

  useEffect(() => {
    let active = true;
    fetchRestaurants()
      .then((data) => { if (active) setRestaurants(data); })
      .catch(() => { if (active) setError("Unable to load restaurants. Please reload to try again."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return (
    <main>
      <h1>What are you craving?</h1>
      {loading && <p role="status">Loading restaurants…</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && !error && restaurants.length === 0 && <p>No restaurants available.</p>}
      <input
        type="search"
        aria-label="Search restaurants"
        placeholder="Search restaurants"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      {restaurants.length > 0 && visible.length === 0 && <p>No restaurants match "{debouncedSearch}".</p>}
      <ul>
        {visible.map((restaurant) => (
          <li key={restaurant.id}>
            <Link to={`/restaurants/${encodeURIComponent(restaurant.id)}`}>
              <h2>{restaurant.name}</h2>
              <p>{restaurant.cuisine} · {restaurant.rating}/5</p>
              <p>{restaurant.address}</p>
              <span>View details</span>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
