// @vitest-environment jsdom
// F35: the empty-state message shows only after loading finishes without an error.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup, waitForElementToBeRemoved } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Discover } from "../DiscoverView";
import { fetchRestaurants } from "../../api/restaurants";
import type { Restaurant } from "../../types/restaurant";

// Replace the real API with a mock
vi.mock("../../api/restaurants", () => ({ fetchRestaurants: vi.fn() }));
const mockFetch = vi.mocked(fetchRestaurants);

const sushiPlace: Restaurant = {
  id: "r1",
  name: "Sushi Place",
  cuisine: "Japanese",
  rating: 4.5,
  address: "1 Main St",
  is_active: true,
};

// Router needed for <Link>
const renderDiscover = () =>
  render(
    <MemoryRouter>
      <Discover />
    </MemoryRouter>,
  );

const EMPTY = "No restaurants available.";
const NO_CUISINE_MATCH = "No restaurants match this cuisine.";

describe("Discover empty state", () => {
  // Clear the mock's return values and calls so each test starts fresh
  beforeEach(() => {
    mockFetch.mockReset();
  });
  // Unmount the page after each test
  afterEach(cleanup);

  it("shows no empty message while loading", () => {
    // Never resolves, so the page stays loading
    mockFetch.mockReturnValue(new Promise(() => {}));
    renderDiscover();
    expect(screen.getByRole("status")).toBeTruthy();
    expect(screen.queryByText(EMPTY)).toBeNull();
  });

  it("shows only the error when loading fails", async () => {
    mockFetch.mockRejectedValue(new Error("network"));
    renderDiscover();
    await screen.findByRole("alert");
    expect(screen.queryByText(EMPTY)).toBeNull();
  });

  it("shows the empty message when there are no restaurants", async () => {
    mockFetch.mockResolvedValue([]);
    renderDiscover();
    // Wait for loading to finish so the check sees the final state
    await waitForElementToBeRemoved(() => screen.queryByRole("status"));
    expect(screen.getByText(EMPTY)).toBeTruthy();
  });

  it("shows the no-match message when a cuisine filter matches nothing", async () => {
    // First load returns a restaurant, filtered load returns none
    mockFetch.mockResolvedValueOnce([sushiPlace]).mockResolvedValueOnce([]);
    renderDiscover();
    // Wait for the first load, which fills the cuisine options
    await screen.findByText("Sushi Place");

    // Pick a cuisine, which triggers the filtered load
    fireEvent.change(screen.getByLabelText("Cuisine"), { target: { value: "Japanese" } });

    // Result: the user sees the no-match message
    expect(await screen.findByText(NO_CUISINE_MATCH)).toBeTruthy();
    // Interaction: the filter is sent to the API
    expect(mockFetch).toHaveBeenLastCalledWith("Japanese");
  });

  it("shows no empty message when restaurants load", async () => {
    mockFetch.mockResolvedValue([sushiPlace]);
    renderDiscover();
    await screen.findByText("Sushi Place");
    expect(screen.queryByText(EMPTY)).toBeNull();
  });
});
