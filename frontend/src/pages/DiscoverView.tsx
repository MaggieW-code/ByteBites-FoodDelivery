import { useEffect, useState } from "react";
import { fetchRestaurants } from "../api/restaurants";
import type { Restaurant } from "../types/restaurant";
import { Link } from "react-router-dom";

export function Discover() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
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

  return (
    <main>
      <h1>What are you craving?</h1>
      {loading && <p role="status">Loading restaurants…</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && !error && restaurants.length === 0 && <p>No restaurants