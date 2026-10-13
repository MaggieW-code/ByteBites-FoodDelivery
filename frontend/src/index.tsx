import { createRoot } from "react-dom/client";
import App from "./App";
import { fetchRestaurants } from "./routes/CustomerRouter";

const rootElement = document.getElementById("root");
if (!rootElement) {
    throw new Error("Could not find the root element")
}

createRoot(rootElement).render(<App />);

fetchRestaurants()
  .then((restaurants) => console.log(restaurants))
  .catch((error) => console.error(error));
