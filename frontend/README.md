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
|``pages/``| The specific UI elements for a given display |
|``components/``| Reusable UI pieces |
|``routes/``| Handles going from page to page |
|``types/``| Definitions for what specific data should look like |
