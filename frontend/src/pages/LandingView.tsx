import { Link } from "react-router-dom";

export function Landing() {
  return (
    <main>
      <h2>Welcome to ByteBites</h2>
      <p>What would you like to do?</p>
      <section aria-label="Discover restaurants">
        <h3>Discover restaurants</h3>
        <Link to="/restaurants">Discover restaurants</Link>
      </section>
      <section aria-label="Manage restaurants">
        <h3>Manage restaurants</h3>
        <Link to="/manage/restaurants">Manage restaurants</Link>
      </section>
    </main>
  );
}
