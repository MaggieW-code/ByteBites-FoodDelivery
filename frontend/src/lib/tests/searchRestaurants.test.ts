import { describe, it, expect } from "vitest";
import { searchRestaurants } from "../searchRestaurants";
import type { Restaurant } from "../../types/restaurant";

const make = (id: string, name: string): Restaurant => ({
    id, name, cuisine: "Test", rating: 4, address: "1 Test St", is_active: true,
});

const data = [
    make("rest_001","Burger Joint"),
    make("rest_002","Cool Food"),
    make("rest_003","Joint De Wrap")
];

const ids = (rs: Restaurant[]) => rs.map(r => r.id);

describe("searchRestaurants", () => {
    it("returns everything for an empty query",() => {
        expect(searchRestaurants(data, "")).toEqual(data);
    });

    it("treats a whitespace-only query as empty", () => {
        expect(searchRestaurants(data, "   ")).toEqual(data);
    });

    it("matches case-insensitively", () => {
        expect(ids(searchRestaurants(data, "COOL"))).toEqual(["rest_002"]);
    });

    it("matches a substring anywhere in the name", () => {
        expect(ids(searchRestaurants(data, "burger"))).toEqual(["rest_001"]);
    });

    it("ignores surrounding whitespace", () => {
        expect(ids(searchRestaurants(data, "  Wrap  "))).toEqual(["rest_003"]);
    });

    it("returns every match, not just the first", () => {
        expect(ids(searchRestaurants(data, "o"))).toEqual(["rest_001", "rest_002", "rest_003"]);
    });

    it("returns [] when nothing matches", () => {
        expect(searchRestaurants(data, "pizza")).toEqual([]);
    });

    it("does not mutate the input", () => {
        const copy = [...data];
        searchRestaurants(data, "taco");
        expect(data).toEqual(copy);
    });
});