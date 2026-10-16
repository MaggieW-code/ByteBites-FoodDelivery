# Frontend Architecture

## Stack
- React
- Parcel Build Tool (Typescript, Code Splitting)
- Typscript & JSX
- npm
- Node.js

## Warning!
**Don't** touch `package-lock.json`, let npm manage this file. 

## Typescript & JSX -> .tsx
- Typescript, like Javascript, but with typesafety, used for Network and API calls.
- JSX, the visual side of the file that signals to the Typescript compiler that HTML style tags may be present within the file. 

## When to use .tsx and .ts
Use `.tsx` when developing a feature that has a UI. If something can be offloaded and does not need a UI, such as HTTP endpoint requests then use `.ts` as this is pure logic.

## Naming Convetions
- PascalCase: React components and files. Also Typescript types and interfaces
- camelCase: Functions and variables

## Type Validation
- Exists only during compiling. Doesn't check user inputs during runtime, so type validation falls back to the service layer

# Vertical Stack 
|Directory|Responsibility|
|:---|---:|
|``layouts/``| General layouts of pages, examples being a dedicated page layout for customers vs admin |
|``pages/``| The specific UI elements for a given display & the page specific logic |
|``components/``| Reusable UI pieces |
|``routes/``| Handles going from page to page |
|``types/``| Definitions for what specific data should look like |

## Restaurant details (#41)

Run the backend on `http://127.0.0.1:8000` and the frontend with `npm start`.
The landing page retrieves persisted restaurants from `GET /restaurants`.
Selecting **View details** requests `GET /restaurants/{restaurant_id}` and shows
all fields returned by the API. **Back to restaurants** returns to the list.

Manual browser verification:
- Load the page and select different restaurants; confirm the name, ID, cuisine,
  rating, address, and status match the selected restaurant's API response.
- Throttle requests in browser developer tools and confirm the loading message.
- Intercept a details request with a 404 response and confirm the unavailable
  restaurant message and working back button.
- Block the details request or return a 500 response and confirm an error is
  displayed and the back button still works.

The browser checks above are manual; automated frontend interaction tests are
not configured in this repository.
