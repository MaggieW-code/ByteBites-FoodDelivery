import json
from pathlib import Path


class RestaurantDataError(Exception):
    pass

class RestaurantDataMalformedError(Exception):
    pass

class RestaurantDataNotFoundError(Exception):
    pass

class RestaurantRepository:
    def __init__(self, data_path: Path):
        self.data_path = data_path

    def get_all(self) -> list[dict]:
        """
        Open provided path as file and load json expected contents. 
        
        ### Catches:
        FileNotFoundError \n
        JSONDecodeError   \n
        Data not being a list after instantiation.  \n
        """
        try:
            with self.data_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError as e:
            raise RestaurantDataNotFoundError(
                f"Restuarant Data Not Found: {self.data_path}"
            ) from e
        except json.JSONDecodeError as e:
            raise RestaurantDataMalformedError(
                f"Restaurant data is malformed: {self.data_path}"
            ) from e

        if not isinstance(data, list):
            raise RestaurantDataError(
                "Restaurant Persistance Must Contain a List"
            )

        return data