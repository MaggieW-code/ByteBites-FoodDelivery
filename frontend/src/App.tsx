import { BrowserRouter, Link, Route, Routes, useParams } from "react-router-dom";
import { GenericLayout } from "./layouts/generic_layout/GenericLayout";
import { Discover } from "./pages/DiscoverView";
import { Landing } from "./pages/LandingView";
import { RestaurantDetails } from "./pages/RestaurantDetailsView";
import { CreateRestaurantForm } from "./components/CreateRestaurantForm";
import { UpdateRestaurantForm } from "./components/UpdateRestaurantForm";

function RestaurantDetailsRoute() {
  const { restaurantId } = useParams();
  return <RestaurantDetails key={restaurantId} restaurantId={restaurantId!} />;
}

export default function App() {
  return (
    <BrowserRouter>
      <GenericLayout>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/restaurants" element={<Discover />} />
          <Route path="/restaurants/:restaurantId" element={<RestaurantDetailsRoute />} />
          <Route path="/manage/restaurants" element={
            <main style={{ maxWidth: "700px", margin: "40px auto", padding: "20px" }}>
              <h1>Restaurant Management</h1>

              <div style={{ marginBottom: "40px" }}>
                <CreateRestaurantForm />
              </div>

              <div>
                <UpdateRestaurantForm />
              </div>
            </main>
          } />
          <Route path="*" element={
            <main><h2>Page not found</h2><Link to="/">Back to home</Link></main>
          } />
        </Routes>
      </GenericLayout>
    </BrowserRouter>
  );
}