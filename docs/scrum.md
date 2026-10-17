# Scrum Log

This document records team meetings, task distribution, key decisions, progress, blockers, and milestone reviews for the ByteBites Food Delivery project.

---

# Milestone 0 — Foundation Gate

## September 23, 2026 — Planning Meeting

### Meeting Goals

- Review the requirements for Milestone 0.
- Distribute Milestone 0 tickets among team members.
- Agree on the persistence format for representative restaurant data.
- Establish expected completion timelines.

### Task Distribution

| Team Member | Assigned Tickets |
|---|---|
| Yibing Wang | M0-01, M0-02, M0-09, M0-11 |
| Maison Gulyas | M0-05, M0-07, M0-08 |
| Junho Kim | M0-06, M0-10 |
| Guransh Sandhu | M0-03, M0-04 |

### Outcome

- Planning the completion before Friday Lab. 
- The team discussed how representative restaurant data should be stored.
- Milestone 0 work was divided among team members.
- Each assigned task had a clear owner.
- JSON was selected as the persistence format.
- Team members began working on their assigned tickets.

---

## September 25, 2026 — Lab Work Session

### Activities

During the lab, team members:

- Worked on their assigned Milestone 0 tickets.
- Discussed implementation questions as they came up.
- Helped each other resolve questions related to different sections of Milestone 0.
- Reviewed progress toward the Milestone 0 submission.

### Outcome

Milestone 0 implementation and documentation work continued toward the submission deadline.

---

## September 25, 2026 — 9:00 PM Submission Meeting

### Meeting Goals

- Review the completed Milestone 0 work.
- Confirm that team members were satisfied with the documentation and submission.
- Identify any final changes required before submission.

### Outcome

The team reviewed the submission materials together and confirmed that everyone was satisfied with the document to be submitted.

---

# Milestone 1 — Restaurant Discovery and Menu Management

## October 2, 2026 — Planning Meeting

### Meeting Goals

- Review the requirements for Milestone 1.
- Split the restaurant discovery, restaurant management, and menu management epics into sub-tickets.
- Agree on the frontend structure.

### Task Distribution

| Team Member | Assigned Work |
|---|---|
| Maison Gulyas | Frontend architecture, restaurant list view (sub-29), restaurant search (sub-36)|
| Yibing Wang | Restaurant details view (sub-41), menu details view (sub-48), landing page, restaurant filter (sub-36)|
| Junho Kim | Menu management: add and update menu items (epic-28) |
| Guransh Sandhu | Restaurant creation and update, with React forms |

### Outcome

- Milestone 1 work was divided into epics, and each sub-ticket had a clear owner.
- Team members began working on their assigned tickets.

---

## October 9, 2026 — Weekly Meeting

### Meeting Goals

- Review progress on assigned tickets.
- Discuss blockers and implementation questions.

### Progress Reported

- The `MenuItem` model and `MenuRepository` add method were in place.
- Restaurant creation and update were implemented on the backend.
- Frontend architecture work was about to begin.

### Outcome

- Team members continued work on their tickets, aiming to have features ready for the next meeting.

---

## October 16, 2026 — Weekly Meeting

### Meeting Goals

- Review the completed Milestone 1 features.
- Integrate the feature branches and resolve merge issues.

### Progress Reported

- Frontend architecture, restaurant list, details, and menu views, and the landing page were merged.
- Menu add and update endpoints were completed with tests.
- React forms for creating and updating restaurants were completed.

### Outcome

- Menu add and update were adapted to the shared `menus.json` structure.
- Merge issues in the frontend (`DiscoverView` and dependencies) were fixed.

---

## Progress Log

| Date | Member | Work Completed |
|---|---|---|
| October 8, 2026 | Junho Kim | Added the `MenuItem` model and `MenuRepository` with an add method. |
| October 8, 2026 | Guransh Sandhu | Implemented restaurant creation and updates (`POST`/`PATCH /restaurants`). |
| October 12, 2026 | Maison Gulyas | Set up the React frontend architecture, layout, routing, and restaurant list view. |
| October 13, 2026 | Junho Kim | Added `MenuService`, `POST` and `PATCH` menu item routes, and their tests. |
| October 15, 2026 | Yibing Wang | Implemented the restaurant details feature. |
| October 15, 2026 | Guransh Sandhu | Added React forms for creating and updating restaurants. |
| October 16, 2026 | Yibing Wang | Implemented the menu endpoint and frontend menu display; added the landing page and URL navigation. Implementing restaurant filtering. |
| October 16, 2026 | Junho Kim | Adapted menu add and update to the `menus.json` structure; restored `DiscoverView` and fixed frontend dependencies. |
| October 16, 2026 | Maison Gulyas | Implemented restaurant search. |

---

## Key Decisions

- Menus are stored per restaurant in `menus.json` (`restaurant_id`, `currency`, `items`), and menu add and update were adapted to this shared structure.
- `MenuService` checks that the restaurant exists, using `RestaurantRepository`.
- Frontend API calls are grouped under `frontend/src/api/`.

## Blockers

- Two features modelled menu data differently. This was resolved by moving menu add and update onto the `menus.json` structure.
- Merging the branches broke `DiscoverView` and the frontend dependencies. This was fixed by restoring `DiscoverView` from `main` and reinstalling the dependencies.


