import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { fetchRestaurantById } from "../api/restaurants";
import type { Restaurant } from "../types/restaurant";
import { RestaurantMenu } from "./RestaurantMenuView";

type Props = { restaurantId: string };

export function RestaurantDetails({ restaurantId }: Props) {
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setRestaurant(null);
    setError("");
    fetchRestaurantById(restaurantId)
      .then((data) => { if (active) setRestaurant(data); })
      .catch((failure: Error) => { if (active) setError(failure.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [restaurantId]);

  return (
    <main>
      <Link to="/restaurants">Back to restaurants</Link>
      {loading && <p role="status">Loading restaurant details…</p>}
      {error && <p role="alert">{error}</p>}
      {restaurant && (
        <article>
          <h1>{restaurant.name}</h1>
          <dl>
            <dt>Restaurant ID</dt><dd>{restaurant.id}</dd>
            <dt>Cuisine</dt><dd>{restaurant.cuisine}</dd>
            <dt>Rating</dt><dd>{restaurant.rating}/5</dd>
            <dt>Address</dt><dd>{restaurant.address}</dd>
            <dt>Status</dt><dd>{restaurant.is_active ? "Active" : "Inactive"}</dd>
          </dl>
          <RestaurantMenu key={restaurant.id} restaurantId={restaurant.id} />
        </article>
      )}
    </main>
  );
}
