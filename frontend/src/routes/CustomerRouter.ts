import type { Restaurant } from "../types/restaurant";

export const fetchRestaurants = async (): Promise<Restaurant[]> => {
  const response = await fetch("http://127.0.0.1:8000/restaurants");

  if (!response.ok) {
    throw new Error("Failed to fetch restaurants");
  }

  return response.json();
};

export const fetchRestaurantById = async (restaurantId: string): Promise<Restaurant> => {
  const response = await fetch(
    `http://127.0.0.1:8000/restaurants/${encodeURIComponent(restaurantId)}`
  );
  if (response.status === 404) {
    throw new Error("This restaurant is no longer available. Return to the restaurant list.");
  }
  if (!response.ok) {
    throw new Error("Unable to load restaurant details. Please try again.");
  }
  return response.json();
};
