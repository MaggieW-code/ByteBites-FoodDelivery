import { useEffect, useState } from "react";
import { fetchRestaurantById } from "../routes/CustomerRouter";
import type { Restaurant } from "../types/restaurant";

type Props = { restaurantId: string; onBack: () => void };

export function RestaurantDetails({ restaurantId, onBack }: Props) {
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
      <button type="button" onClick={onBack}>Back to restaurants</button>
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
        </article>
      )}
    </main>
  );
}
