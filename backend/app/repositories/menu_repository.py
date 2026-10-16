import json
from pathlib import Path


class MenuRepository:
    def __init__(self, data_path: Path):
        self.data_path = data_path

    def get_by_restaurant_id(self, restaurant_id: str) -> dict | None:
        with self.data_path.open("r", encoding="utf-8") as file:
            menus = json.load(file)

        for menu in menus:
            if menu["restaurant_id"] == restaurant_id:
                return menu
        return None
