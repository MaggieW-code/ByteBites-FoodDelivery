import { BrowserRouter, Link, Route, Routes, useParams } from "react-router-dom";
import { GenericLayout } from "./layouts/generic_layout/GenericLayout";
import { Discover } from "./pages/DiscoverView";
import { Landing } from "./pages/LandingView";
import { RestaurantDetails } from "./pages/RestaurantDetailsView";

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
            <main>
              <h2>Manage restaurants</h2>
              <p>Restaurant management is coming soon.</p>
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
