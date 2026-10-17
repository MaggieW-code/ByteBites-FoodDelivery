import { useEffect, useState } from "react";
import { fetchRestaurants } from "../api/restaurants";
import type { Restaurant } from "../types/restaurant";
import { Link } from "react-router-dom";

export function Discover() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [cuisines, setCuisines] = useState<string[]>([]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    fetchRestaurants(cuisine)
      .then((data) => {
        if (!active) return;
        setRestaurants(data);
        if (!cuisine) {
          const options = new Map<string, string>();
          data.forEach((restaurant) => {
            const label = restaurant.cuisine.trim();
            options.set(label.toLowerCase(), label);
          });
          setCuisines([...options.values()].sort((a, b) => a.localeCompare(b)));
        }
      })
      .catch(() => { if (active) setError("Unable to load restaurants. Please reload to try again."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [cuisine]);

  return (
    <main>
      <h1>What are you craving?</h1>
      <label htmlFor="cuisine-filter">Cuisine </label>
      <select id="cuisine-filter" value={cuisine} onChange={(event) => setCuisine(event.target.value)}>
        <option value="">All cuisines</option>
        {cuisines.map((option) => <option key={option} value={option}>{option}</option>)}
      </select>
      {loading && <p role="status">Loading restaurants…</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && !error && restaurants.length === 0 && <p>{cuisine ? "No restaurants match this cuisine." : "No restaurants available."}</p>}
      {!loading && !error && <ul>
        {restaurants.map((restaurant) => (
          <li key={restaurant.id}>
            <Link to={`/restaurants/${encodeURIComponent(restaurant.id)}`}>
              <h2>{restaurant.name}</h2>
              <p>{restaurant.cuisine} · {restaurant.rating}/5</p>
              <p>{restaurant.address}</p>
              <span>View details</span>
            </Link>
          </li>
        ))}
      </ul>}
    </main>
  );
}
