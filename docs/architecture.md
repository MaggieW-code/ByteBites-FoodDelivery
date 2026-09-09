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

