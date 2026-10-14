import json
from pathlib import Path

from backend.app.models.menu_Item_model import MenuItem


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

    def add(self, item: MenuItem):
        # read
        menus = self.get_all()
        # append item to menus
        menus.append(item.model_dump())
        with self.data_path.open("w", encoding = "utf-8") as file:
            json.dump(menus, file, indent = 2)

    def update(self, item: MenuItem):
        # read
        menus = self.get_all()
        # search all round and update that has the same id
        for index, menu in enumerate(menus):
            if menu["id"] == item.id:
                menus[index] = item.model_dump()
        with self.data_path.open("w", encoding = "utf-8") as file:
            json.dump(menus, file, indent = 2)

    def get_all(self) -> list[dict]:
        try:
            with self.data_path.open("r", encoding ="utf-8") as file:
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
            raise MenuDataError(
                "Menu is not in the list"
            ) 
        
        return data