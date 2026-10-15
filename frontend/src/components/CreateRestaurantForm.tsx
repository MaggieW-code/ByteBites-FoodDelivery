
import { useState, type FormEvent } from "react";
import {
  createRestaurant,
  type Restaurant,
} from "../api/restaurants";

export function CreateRestaurantForm() {
  const [name, setName] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [address, setAddress] = useState("");

  const [createdRestaurant, setCreatedRestaurant] =
    useState<Restaurant | null>(null);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setCreatedRestaurant(null);

    if (!name.trim() || !cuisine.trim() || !address.trim()) {
      setError("All fields are required.");
      return;
    }

    setLoading(true);

    try {
      const restaurant = await createRestaurant({
        name: name.trim(),
        cuisine: cuisine.trim(),
        address: address.trim(),
      });

      setCreatedRestaurant(restaurant);

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
      <h2>Create Restaurant</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="create-name">Restaurant Name</label>
          <input
            id="create-name"
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
        </div>

        <div>
          <label htmlFor="create-cuisine">Cuisine</label>
          <input
            id="create-cuisine"
            type="text"
            value={cuisine}
            onChange={(event) => setCuisine(event.target.value)}
            required
          />
        </div>

        <div>
          <label htmlFor="create-address">Address</label>
          <input
            id="create-address"
            type="text"
            value={address}
            onChange={(event) => setAddress(event.target.value)}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create Restaurant"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {createdRestaurant && (
        <div role="status">
          <h3>Restaurant created successfully!</h3>
          <p>
            <strong>Name:</strong> {createdRestaurant.name}
          </p>
          <p>
            <strong>ID:</strong> {createdRestaurant.id}
          </p>
          <p>
            <strong>Cuisine:</strong> {createdRestaurant.cuisine}
          </p>
          <p>
            <strong>Address:</strong> {createdRestaurant.address}
          </p>
        </div>
      )}
    </section>
  );
}
