export type MenuItem = {
  id: string;
  name: string;
  description: string;
  price: string;
  is_available: boolean;
};

export type Menu = {
  restaurant_id: string;
  currency: string;
  items: MenuItem[];
};
