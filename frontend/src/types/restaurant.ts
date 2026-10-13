// Matches the restaurant data returned by the backend.
export type Restaurant = {
  id: string;
  name: string;
  cuisine: string;
  rating: number;
  address: string;
  is_active: boolean;
};
