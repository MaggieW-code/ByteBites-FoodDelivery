
const API_BASE_URL = "http://127.0.0.1:8000";

export interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  address: string;
  rating: number;
  is_active: boolean;
}

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
