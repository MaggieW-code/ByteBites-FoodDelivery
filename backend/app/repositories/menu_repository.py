import json
from pathlib import Path

from backend.app.models.menu_item_model import MenuItem


# if the menu data is not exist
class MenuDataNotFoundError(Exception):
    pass

# if the file isn't valid json
class MenuDataMalformedError(Exception):
    pass

# if the file is not a list
class MenuDataError(Exception):
    pass


class MenuRepository:
    def __init__(self, data_path: Path):
        self.data_path = data_path

    def get_all(self) -> list[dict]:
        try:
            with self.data_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError as e:
            raise MenuDataNotFoundError(
                f"Menu Data is not found: {self.data_path}"
            ) from e
        except json.JSONDecodeError as e:
            raise MenuDataMalformedError(
                f"The file isn't valid json: {self.data_path}"
            ) from e
        if not isinstance(data, list):
            raise MenuDataError("Menu is not in the list")

        return data

    def _save(self, menus: list[dict]) -> None:
        with self.data_path.open("w", encoding="utf-8") as file:
            json.dump(menus, file, indent=2)

    def get_by_restaurant_id(self, restaurant_id: str) -> dict | None:
        with self.data_path.open("r", encoding="utf-8") as file:
            menus = json.load(file)

        for menu in menus:
            if menu["restaurant_id"] == restaurant_id:
                return menu
        return None

    def find_item(self, restaurant_id: str, item_id: str) -> dict | None:
        menu = self.get_by_restaurant_id(restaurant_id)
        if menu is None:
            return None
        for item in menu["items"]:
            if item["id"] == item_id:
                return item
        return None

    def add(self, item: MenuItem) -> None:
        menus = self.get_all()
        entry = item.model_dump(exclude={"restaurant_id"})

        for menu in menus:
            if menu["restaurant_id"] == item.restaurant_id:
                menu["items"].append(entry)
                break
        else:
            menus.append(
                {"restaurant_id": item.restaurant_id, "currency": "CAD", "items": [entry]}
            )

        self._save(menus)

    def update(self, item: MenuItem) -> None:
        menus = self.get_all()
        entry = item.model_dump(exclude={"restaurant_id"})

        for menu in menus:
            if menu["restaurant_id"] == item.restaurant_id:
                for index, existing in enumerate(menu["items"]):
                    if existing["id"] == item.id:
                        menu["items"][index] = entry

        self._save(menus)