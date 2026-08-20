# Java, Spring Boot & Angular Training Materials

Slide decks and hands-on lab sheets for a full-stack training series, authored by **Purvam Prajapati** (Faculty, AHD).

Each session ships two self-contained HTML files — open them directly in any browser, no build step needed.

## Start here

Open [`index.html`](index.html) — a landing page that links every slideshow and lab in one place.

## Contents

### Foundations

| Session | Theory (slideshow) | Hands-on lab |
|--------:|--------------------|--------------|
| Java Foundations | `java-foundations-theory.html` | — |
| Collections, Class Relationships & File I/O | `java-collections-theory.html` | — |
| JDBC — Database Connectivity | `jdbc-theory.html` | `jdbc-lab.html` |

### Spring Boot — 4-part series (backend)

| Session | Theory (slideshow) | Hands-on lab |
|--------:|--------------------|--------------|
| 1 — Spring Boot foundations | `springboot-session1-theory.html` | `springboot-session1-lab.html` |
| 2 — REST Web Services | `springboot-session2-theory.html` | `springboot-session2-lab.html` |
| 3 — DTO, layers & exception handling | `springboot-session3-theory.html` | `springboot-session3-lab.html` |
| 4 — Microservices with Spring Cloud | `springboot-session4-theory.html` | `springboot-session4-lab.html` |

### Angular — 4-part series (frontend)

| Session | Theory (slideshow) | Hands-on lab |
|--------:|--------------------|--------------|
| 1 — TypeScript & Angular basics | `angular-session1-theory.html` | `angular-session1-lab.html` |
| 2 — Components & data binding | `angular-session2-theory.html` | `angular-session2-lab.html` |
| 3 — Forms, services & HTTP | `angular-session3-theory.html` | `angular-session3-lab.html` |
| 4 — Routing & full CRUD | `angular-session4-theory.html` | `angular-session4-lab.html` |

- **Theory files** are interactive slideshows (arrow keys / on-screen controls, slide counter, progress rail).
- **Lab files** are scrollable companions with a progress checklist and copy-to-clipboard code blocks.

## The journey

### Spring Boot — from a Hello World endpoint to a microservices architecture

1. **Foundations** — what Spring Boot is, auto-configuration, and a first running REST endpoint.
2. **REST Web Services** — a complete Student CRUD API with JSON, HTTP methods, and status codes.
3. **DTO, layers & exception handling** — layered architecture (Controller → Service → Repository), DTOs, custom exceptions, Lombok, and an H2 database; plus a first look at Spring Security and microservices.
4. **Microservices with Spring Cloud** — a Eureka service registry, two microservices, multiple load-balanced instances, and an API Gateway with round-robin routing.

### Angular — from `ng new` to a full-CRUD single-page application

The four Angular sessions build **one application**, adding a layer each time. Nothing is thrown away.

1. **TypeScript & Angular basics** — what Angular and single-page applications are, the AngularJS-vs-Angular split, and TypeScript from scratch (inference, interfaces, optionals, unions, loops, arrays, tuples, classes, arrow functions). Then Node + the Angular CLI, `ng new` → `ng serve`, a full tour of a generated project, and the boot chain from `index.html` to your component. **Output:** a Hello World app you edited yourself.
2. **Components & data binding** — components as class + metadata + template, generated with the CLI and nested into a tree. All four bindings (interpolation, property, event, two-way with `ngModel`), structural directives (`*ngIf`, `*ngFor`, `*ngSwitch`), attribute directives (`ngClass`, `ngStyle`) and pipes. **Output:** a working login form and a colour-coded employee table.
3. **Forms, services & HTTP** — template-driven *and* reactive forms with `Validators` and friendly error messages; services, `@Injectable` and dependency injection; `HttpClient` (GET/POST/PUT/DELETE) and Observables. **Output:** employee data moves from a hardcoded array into a service, then live data arrives from a real API.
4. **Routing & full CRUD** — routing with `<router-outlet>`, `routerLink`, route parameters, a default redirect and a 404 page; then the Customer Management case study (list, search, insert, update with read-only ID/Name, delete-with-confirm) built against an in-memory array and then refactored onto a service with `HttpClient`. **Output:** a complete, navigable, service-backed application.

### Putting the two halves together

The Angular series is designed to sit directly on top of the Spring Boot series. Session 4's final stretch task points the Angular app at your own Spring Boot API by changing **one line** (`baseUrl`) plus adding `@CrossOrigin` on the controller — giving you a genuine full-stack application built end to end.

## Delivery model

The theory files and lab files are designed to run **in parallel**: keep the theory deck on the main screen and narrate from it, while associates keep the lab sheet open on their own machines and build hands-on, task by task.

Every Angular lab task carries a **"Theory slides …"** badge in its heading, so the two files stay in lockstep instead of the lab running ahead of or behind the explanation. Each lab ends with a **checkpoint** — if the room isn't at the checkpoint when you reach the theory recap slide, that's the natural place to pause rather than pushing on.

Stretch tasks are always optional; never block the group on them.

## Design notes

All theory and lab files share one "MacBook window" design system — the same window chrome, spacing, type scale, callout boxes, tables and code blocks. The design tokens live in a `THEME-SYNC` block that is **byte-identical across every file** in a series; don't edit one copy without the others.

The two series are distinguished only by their accent ramp:

- **Spring Boot** — Boot blue (`#0a84ff`) with indigo (`#5e5ce6`).
- **Angular** — Angular brand red (`#dd0031`) with Angular purple (`#9327f0`).

The Angular files also add a few components on top of the shared system: a version **timeline**, a **mock browser** frame that shows associates exactly what they should be seeing, a **data-flow map** for the four binding directions, a **component-tree** visual, and "Ask the batch" discussion callouts for the trainer.

## Viewing on GitHub

GitHub shows raw HTML rather than rendering it. To view a file rendered:

- **Quick preview:** prepend `https://htmlpreview.github.io/?` to the file's raw URL.
- **Best experience:** enable **GitHub Pages** for the repo (Settings → Pages) and browse to `index.html`.

## Editing from the web / phone

- **Quick edits:** open the repo and press `.` (period), or replace `github.com` with `github.dev` in the URL — a browser VS Code opens. Works on mobile browsers too.
- **Full dev environment (to run the Java or Angular projects):** use GitHub Codespaces from the green **Code** button.

## Spec documents

The `.kiro/specs/` folder holds the design and task specs used to generate these materials.
