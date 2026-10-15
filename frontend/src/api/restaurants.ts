import type { Restaurant } from "../types/restaurant";

const API_BASE_URL = "http://127.0.0.1:8000";

export interface CreateRestaurantRequest {
  name: string;
  cuisine: string;
  address: string;
}

export interface UpdateRestaurantRequest {
  name?: string;
  cuisine?: string;
  address?: string;
}

export const fetchRestaurants = async (): Promise<Restaurant[]> => {
  const response = await fetch(`${API_BASE_URL}/restaurants`);

  if (!response.ok) {
    throw new Error("Failed to fetch restaurants");
  }

  return response.json();
};

export const fetchRestaurantById = async (restaurantId: string): Promise<Restaurant> => {
  const response = await fetch(
    `${API_BASE_URL}/restaurants/${encodeURIComponent(restaurantId)}`
  );
  if (response.status === 404) {
    throw new Error("This restaurant is no longer available. Return to the restaurant list.");
  }
  if (!response.ok) {
    throw new Error("Unable to load restaurant details. Please try again.");
  }
  return response.json();
};

// Issue #56: Create Restaurant
export async function createRestaurant(
  data: CreateRestaurantRequest
): Promise<Restaurant> {
  const response = await fetch(`${API_BASE_URL}/restaurants`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create restaurant: ${error}`);
  }

  return response.json();
}

// Issue #63: Update Restaurant
export async function updateRestaurant(
  restaurantId: string,
  data: UpdateRestaurantRequest
): Promise<Restaurant> {
  const response = await fetch(
    `${API_BASE_URL}/restaurants/${encodeURIComponent(restaurantId)}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to update restaurant: ${error}`);
  }

  return response.json();
}