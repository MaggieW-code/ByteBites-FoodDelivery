
import { useState, type FormEvent } from "react";
import {
  updateRestaurant,
  type Restaurant,
  type UpdateRestaurantRequest,
} from "../api/restaurants";

export function UpdateRestaurantForm() {
  const [restaurantId, setRestaurantId] = useState("");
  const [name, setName] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [address, setAddress] = useState("");

  const [updatedRestaurant, setUpdatedRestaurant] =
    useState<Restaurant | null>(null);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setUpdatedRestaurant(null);

    if (!restaurantId.trim()) {
      setError("Restaurant ID is required.");
      return;
    }

    const updates: UpdateRestaurantRequest = {};

    if (name.trim()) {
      updates.name = name.trim();
    }

    if (cuisine.trim()) {
      updates.cuisine = cuisine.trim();
    }

    if (address.trim()) {
      updates.address = address.trim();
    }

    if (Object.keys(updates).length === 0) {
      setError("Enter at least one field to update.");
      return;
    }

    setLoading(true);

    try {
      const restaurant = await updateRestaurant(
        restaurantId.trim(),
        updates
      );

      setUpdatedRestaurant(restaurant);

      setName("");
      setCuisine("");
      setAddress("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h2>Update Restaurant</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="update-id">Restaurant ID</label>
          <input
            id="update-id"
            type="text"
            value={restaurantId}
            onChange={(event) => setRestaurantId(event.target.value)}
            placeholder="e.g. rest_001"
            required
          />
        </div>

        <p>Leave any field blank to keep its current value.</p>

        <div>
          <label htmlFor="update-name">New Restaurant Name</label>
          <input
            id="update-name"
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </div>

        <div>
          <label htmlFor="update-cuisine">New Cuisine</label>
          <input
            id="update-cuisine"
            type="text"
            value={cuisine}
            onChange={(event) => setCuisine(event.target.value)}
          />
        </div>

        <div>
          <label htmlFor="update-address">New Address</label>
          <input
            id="update-address"
            type="text"
            value={address}
            onChange={(event) => setAddress(event.target.value)}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Updating..." : "Update Restaurant"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {updatedRestaurant && (
        <div role="status">
          <h3>Restaurant updated successfully!</h3>
          <p>
            <strong>ID:</strong> {updatedRestaurant.id}
          </p>
          <p>
            <strong>Name:</strong> {updatedRestaurant.name}
          </p>
          <p>
            <strong>Cuisine:</strong> {updatedRestaurant.cuisine}
          </p>
          <p>
            <strong>Address:</strong> {updatedRestaurant.address}
          </p>
        </div>
      )}
    </section>
  );
}
