import { useEffect, useState } from "react";
import { fetchMenu } from "../api/menus";
import type { Menu } from "../types/menu";

export function RestaurantMenu({ restaurantId }: {
  restaurantId: string;
}) {
  const [menu, setMenu] = useState<Menu | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setMenu(null);
    setError("");
    fetchMenu(restaurantId, controller.signal)
      .then((data) => { if (!controller.signal.aborted) setMenu(data); })
      .catch((failure: Error) => {
        if (!controller.signal.aborted) setError(failure.message);
      });
    return () => controller.abort();
  }, [restaurantId, attempt]);

  return (
    <section aria-labelledby="restaurant-menu-heading">
      <h2 id="restaurant-menu-heading">Menu</h2>
      {!menu && !error && <p role="status">Loading menu…</p>}
      {error && <div role="alert"><p>{error}</p>
        <button type="button" onClick={() => setAttempt((value) => value + 1)}>Try again</button>
      </div>}
      {menu && menu.items.length === 0 && <p>No menu items available yet.</p>}
      {menu && <ul>{menu.items.map((item) => (
        <li key={item.id}>
          <h3>{item.name}</h3>
          <p>{item.description}</p>
          <p>{new Intl.NumberFormat("en-CA", {
            style: "currency", currency: menu.currency,
          }).format(Number(item.price))} {menu.currency}</p>
          {!item.is_available && <p>Currently unavailable</p>}
        </li>
      ))}</ul>}
    </section>
  );
}
