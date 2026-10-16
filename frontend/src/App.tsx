import { GenericLayout } from "./layouts/generic_layout/GenericLayout";
import { Discover } from "./pages/DiscoverView"

export default function App() {
  return (
    <GenericLayout>
        <Discover />
    </GenericLayout>
  );
}
