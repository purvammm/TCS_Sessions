# Spring Boot Training Materials

Slide decks and hands-on lab sheets for a Spring Boot training series, authored by **Purvam Prajapati** (Faculty, AHD).

Each session ships two self-contained HTML files — open them directly in any browser, no build step needed — plus a written study-notes file for self-paced learning.

## Start here

- **To present or follow along:** open [`index.html`](index.html) — a landing page linking every slideshow and lab.
- **To learn it yourself, or prepare to teach it:** open [`notes/`](notes/README.md) — the four theory sessions written out as readable study notes.

## Contents

| Session | Theory (slideshow) | Hands-on lab | Study notes |
|--------:|--------------------|--------------|-------------|
| Java Foundations | `java-foundations-theory.html` | — | — |
| Collections, Class Relationships & File I/O | `java-collections-theory.html` | — | — |
| JDBC — Database Connectivity | `jdbc-theory.html` | `jdbc-lab.html` | — |
| 1 — Spring Boot foundations | `springboot-session1-theory.html` | `springboot-session1-lab.html` | [notes](notes/session-1-spring-boot-foundations.md) |
| 2 — REST APIs & Web Services | `springboot-session2-theory.html` | `springboot-session2-lab.html` | [notes](notes/session-2-rest-apis.md) |
| 3 — Databases, DTOs & exception handling | `springboot-session3-theory.html` | `springboot-session3-lab.html` | [notes](notes/session-3-data-jpa-dtos-exceptions.md) |
| 4 — Microservices with Spring Cloud | `springboot-session4-theory.html` | `springboot-session4-lab.html` | [notes](notes/session-4-microservices-spring-cloud.md) |

- **Theory files** are interactive slideshows (arrow keys / on-screen controls, slide counter, progress rail).
- **Lab files** are scrollable companions with a progress checklist and copy-to-clipboard code blocks.
- **Study notes** are Markdown — the same material as prose, with diagrams, self-tests, glossaries and a *"Teaching this session"* guide. They render directly on GitHub, including the diagrams.

## The journey

The four Spring Boot sessions build on each other — from a Hello World endpoint to a running microservices architecture:

1. **Foundations** — what Spring Boot is, auto-configuration, beans and dependency injection, and a first running REST endpoint.
2. **REST APIs & Web Services** — a complete Student CRUD API with JSON, HTTP methods, and correct status codes.
3. **Databases, DTOs & exception handling** — Spring Data JPA with an H2 database, layered architecture (Controller → Service → Repository), DTOs, and global exception handling; plus a first look at Spring Security and microservices.
4. **Microservices with Spring Cloud** — a Eureka service registry, two microservices, multiple load-balanced instances, and an API Gateway with round-robin routing.

Each session removes a constraint the next one relies on: Session 2's *statelessness* and Session 3's *shared database* are exactly what make Session 4's load balancing possible.

### ⚠️ The Golden Rule

Every class you create must live in the **same package as the main class, or a sub-package of it** — otherwise Spring's component scanning never finds it, the app starts with *no error*, and every request returns a 404 Whitelabel page.

This matters because Spring Initializr derives your package name by joining **Group + Artifact** (stripping hyphens), so the two fields you type produce a third value you didn't. The labs print each project's exact base package, and [Session 1's notes](notes/session-1-spring-boot-foundations.md#part-5--the-entry-point-and-the-golden-rule) cover it in full.

## Viewing on GitHub

GitHub shows raw HTML rather than rendering it. To view a file rendered:

- **Quick preview:** prepend `https://htmlpreview.github.io/?` to the file's raw URL.
- **Best experience:** enable **GitHub Pages** for the repo (Settings → Pages) and browse to `index.html`.

## Editing from the web / phone

- **Quick edits:** open the repo and press `.` (period), or replace `github.com` with `github.dev` in the URL — a browser VS Code opens. Works on mobile browsers too.
- **Full dev environment (to run the Java projects):** use GitHub Codespaces from the green **Code** button.

## Spec documents

The `.kiro/specs/` folder holds the design and task specs used to generate these materials.
