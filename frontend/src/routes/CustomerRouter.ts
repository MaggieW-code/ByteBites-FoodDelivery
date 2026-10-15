import type { Restaurant } from "../types/restaurant";

export const fetchRestaurants = async (): Promise<Restaurant[]> => {
  const response = await fetch("http://127.0.0.1:8000/restaurants");

  if (!response.ok) {
    throw new Error("Failed to fetch restaurants");
  }

  return response.json();
};
