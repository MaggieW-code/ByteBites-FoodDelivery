# Architecture

Food Delivery uses a layered architecture:

**Frontend → FastAPI Routes → Services → Repositories → JSON/CSV Persistence**

- **Frontend:** Presents the application interface and communicates with the API.
- **Routes:** Define HTTP paths, receive parameters and requests, return responses and
  status codes, and call the appropriate service.
- **Services:** Contain business rules, validation, calculations, state transitions,
  and workflow orchestration.
- **Repositories:** Encapsulate storage operations and hide JSON/CSV file handling
  from the rest of the application.
- **JSON/CSV persistence:** Stores representative application data without requiring
  a database.

Business logic belongs in services rather than routes so it can be reused and tested
without an HTTP request. Persistence belongs behind repositories so storage details
can change without coupling services to file formats or file operations.

## Feature layer mapping

| Feature | Route | Service | Repository | Data file |
|---|---|---|---|---|
| Restaurants | `routes/restaurant_routes.py` | `services/restaurant_service.py` | `repositories/restaurant_repository.py` | `data/restaurants.json` |
| Menus | `routes/menu_routes.py` | `services/menu_service.py` | `repositories/menu_repository.py` | `data/menus.json` |

All backend paths are relative to `backend/app/`. Request and response shapes are
Pydantic models in `models/`. Services raise domain errors (for example,
`MenuItemNotFoundError`), and routes translate them into HTTP status codes.

`MenuService` also uses `RestaurantRepository` so that it can check whether a
restaurant exists before returning its menu.

## Frontend structure

The React frontend (`frontend/src/`) follows a similar separation:

- **`api/`:** Functions that call the FastAPI endpoints, so that components do
  not call `fetch` directly.
- **`pages/`:** Top-level views such as the landing, discovery, restaurant
  details, and menu pages.
- **`components/`:** Reusable UI pieces such as restaurant cards and the
  create and update forms.
- **`hooks/`:** React logic that utilize React's memory.
- **`layouts/`:** Shared page layout.
- **`lib`:** Regular functions that take and return data.
- **`routes/`:** URL-to-page routing.
- **`types/`:** TypeScript types that mirror the backend models.

