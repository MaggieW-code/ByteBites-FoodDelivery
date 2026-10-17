import type { Restaurant } from "../types/restaurant";

/** Restaurants whose name contains the query (case-insensitive). Empty query returns all. */
export function searchRestaurants(restaurants: Restaurant[], query: string): Restaurant[] {
    const q = query.trim().toLocaleLowerCase();
    if (q == "") return restaurants;

    return restaurants.filter(r => r.name.toLocaleLowerCase().includes(q));
};