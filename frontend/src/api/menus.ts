import type { Menu } from "../types/menu";

export async function fetchMenu(restaurantId: string, signal?: AbortSignal): Promise<Menu> {
  const response = await fetch(
    `http://127.0.0.1:8000/restaurants/${encodeURIComponent(restaurantId)}/menu`,
    { signal },
  );
  if (response.status === 404) throw new Error("This restaurant is no longer available.");
  if (!response.ok) throw new Error("Unable to load the menu. Please try again.");
  return response.json();
}
