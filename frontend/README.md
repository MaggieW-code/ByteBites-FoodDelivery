# Frontend Architecture

## Stack
- React
- Parcel 
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