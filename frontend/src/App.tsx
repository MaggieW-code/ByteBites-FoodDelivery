
import { GenericLayout } from "./layouts/generic_layout/GenericLayout";
import { Discover } from "./pages/DiscoverView";
import { CreateRestaurantForm } from "./components/CreateRestaurantForm";
import { UpdateRestaurantForm } from "./components/UpdateRestaurantForm";

export default function App() {
  return (
    <GenericLayout>
      <Discover />

      <main style={{ maxWidth: "700px", margin: "40px auto", padding: "20px" }}>
        <h1>Restaurant Management</h1>

        <div style={{ marginBottom: "40px" }}>
          <CreateRestaurantForm />
        </div>

        <div>
          <UpdateRestaurantForm />
        </div>
      </main>
    </GenericLayout>
  );
}
