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

1. **TypeScript & Angular basics** — a jargon-buster covering every term used on day one, then what Angular and single-page applications are, framework vs library, the AngularJS-vs-Angular split, and where Angular sits relative to your Spring Boot API. TypeScript is taught in twelve graded steps (inference, the built-in types, the `any` trap, interfaces, optionals with `?.`/`??`, unions, arrays and the six array methods, tuples, the three loops, functions, arrow functions, classes, access modifiers and the constructor shorthand) and closes with a one-page cheat sheet. Then Node + the Angular CLI, `ng new` → `ng serve`, a guided tour of every generated file, the boot chain from `index.html` to your component, what an `NgModule` is for, and a table of the errors you will hit on day one. **Output:** a Hello World app you edited yourself, plus a typed `Employee` array rendering on screen.
2. **Components & data binding** — components as class + metadata + template, generated with the CLI, nested into a tree, with automatically scoped styles. All four bindings introduced one at a time with the direction each flows (interpolation, property, event with `$event`, two-way with `ngModel`), structural directives (`*ngIf` with `else`, `*ngFor` with `index` and `trackBy`, `*ngSwitch`), attribute directives (`ngClass`, `ngStyle`) and pipes with parameters and chaining. Then parent–child communication with `@Input` and `@Output`/`EventEmitter`, and the `ngOnInit` lifecycle hook. **Output:** a working login form, a colour-coded employee table, and a reusable employee card whose delete button updates the parent's data.
3. **Forms, services & HTTP** — why `ngModel` alone isn't enough, then the *same form built twice*: template-driven (with `ngForm`, the `touched`/`dirty`/`valid` state flags and attribute validation) and reactive (`FormGroup`, `FormControl`, `Validators`, `FormBuilder`, `patchValue`), followed by a decision table. Services, `@Injectable`, dependency injection and why `providedIn: 'root'` makes a singleton. `HttpClient` (GET/POST/PUT/DELETE) mapped one-for-one onto Spring Boot annotations, Observables explained against Promises, `subscribe({ next, error })`, loading/error/empty states, the `async` pipe, and CORS. **Output:** employee data moves from a hardcoded array into a service — with two components proving they share one instance — then live data arrives from a real API.
4. **Routing & full CRUD** — why routing matters, what a route is, `RouterModule.forRoot`, `<router-outlet>`, `routerLink` vs `href`, `routerLinkActive`, a default redirect, a 404 wildcard, why route order matters, route parameters read via `ActivatedRoute` (and the string-vs-number trap), and navigating from code with `Router.navigate`. Then the Customer Management case study — list, search, insert, update-with-one-form, delete-with-confirm — built **three times**: against an in-memory array, then through a service, then over `HttpClient`. Closes with `ng build`, deployment, and where to go next. **Output:** a complete, navigable, service-backed application with five routed screens.

### Putting the two halves together

The Angular series is designed to sit directly on top of the Spring Boot series. Session 4's final stretch task points the Angular app at your own Spring Boot API by changing **one line** (`baseUrl`) plus adding `@CrossOrigin` on the controller — giving you a genuine full-stack application built end to end.

### The teaching thread that runs through all four sessions

Two ideas are deliberately reinforced across every session rather than mentioned once:

- **Swapping the data layer never changes the template.** The employee table is written in Session 2 against a hardcoded array, then re-pointed at a service, then at an HTTP call, and in Session 4 the CRUD moves onto a service again. Four complete changes to how data is fetched, and the template is never touched. Each session stops and points this out.
- **Most Angular bugs are silent.** A missing `*`, a missing `()`, a self-closing component tag, a wildcard route in the wrong place, a route parameter compared as a string — none of these report an error. Every lab deliberately walks the reader *into* these bugs and back out again, and every lab ends with a troubleshooting table organised by symptom rather than by error message.

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

Three callout types were added for the beginner-first rewrite and are used throughout both the decks and the labs:

| Callout | Colour | Purpose |
|---------|--------|---------|
| **Analogy** | teal (`#00b3a4`) | An everyday mental model for an abstract idea — an Observable as a coffee ticket, a component as a LEGO brick. |
| **In plain English** | blue (`#0a84ff`) | The same idea restated in the simplest possible words, for anyone who lost the thread. |
| **Jargon buster** | accent red | A term-and-meaning grid; Session 1 opens with one covering every word used that day. |

The labs also use a **line-by-line explanation table** (`table.lines`) under longer snippets, so beginners can see *why* each line is written the way it is rather than only what to copy.

### Regenerating the Angular files

The eight Angular files share a large amount of chrome — the `THEME-SYNC` token block, the full stylesheet, the slideshow navigator, and the lab progress/clipboard script — and keeping eight hand-maintained copies in sync is error-prone. They are therefore assembled from a small build script that holds the shared parts once and injects each file's slides or tasks. If you are making a change that affects **all** the files (a token, a callout style, the navigator), change it in one place and rebuild; if you are only editing one session's content, editing the generated HTML directly is perfectly fine.

## Viewing on GitHub

GitHub shows raw HTML rather than rendering it. To view a file rendered:

- **Quick preview:** prepend `https://htmlpreview.github.io/?` to the file's raw URL.
- **Best experience:** enable **GitHub Pages** for the repo (Settings → Pages) and browse to `index.html`.

## Editing from the web / phone

- **Quick edits:** open the repo and press `.` (period), or replace `github.com` with `github.dev` in the URL — a browser VS Code opens. Works on mobile browsers too.
- **Full dev environment (to run the Java or Angular projects):** use GitHub Codespaces from the green **Code** button.

## Spec documents

The `.kiro/specs/` folder holds the design and task specs used to generate these materials.
