# Spring Boot Training Materials

Slide decks and hands-on lab sheets for a Spring Boot training series, authored by **Purvam Prajapati** (Faculty, AHD).

Each session ships two self-contained HTML files — open them directly in any browser, no build step needed.

## Start here

Open [`index.html`](index.html) — a landing page that links every slideshow and lab in one place.

## Contents

| Session | Theory (slideshow) | Hands-on lab |
|--------:|--------------------|--------------|
| Java Foundations | `java-foundations-theory.html` | — |
| JDBC — Database Connectivity | `jdbc-theory.html` | `jdbc-lab.html` |
| 1 — Spring Boot foundations | `springboot-session1-theory.html` | `springboot-session1-lab.html` |
| 2 — REST Web Services | `springboot-session2-theory.html` | `springboot-session2-lab.html` |
| 3 — DTO, layers & exception handling | `springboot-session3-theory.html` | `springboot-session3-lab.html` |
| 4 — Microservices with Spring Cloud | `springboot-session4-theory.html` | `springboot-session4-lab.html` |

- **Theory files** are interactive slideshows (arrow keys / on-screen controls, slide counter, progress rail).
- **Lab files** are scrollable companions with a progress checklist and copy-to-clipboard code blocks.

## The journey

The four Spring Boot sessions build on each other — from a Hello World endpoint to a running microservices architecture:

1. **Foundations** — what Spring Boot is, auto-configuration, and a first running REST endpoint.
2. **REST Web Services** — a complete Student CRUD API with JSON, HTTP methods, and status codes.
3. **DTO, layers & exception handling** — layered architecture (Controller → Service → Repository), DTOs, custom exceptions, Lombok, and an H2 database; plus a first look at Spring Security and microservices.
4. **Microservices with Spring Cloud** — a Eureka service registry, two microservices, multiple load-balanced instances, and an API Gateway with round-robin routing.

## Viewing on GitHub

GitHub shows raw HTML rather than rendering it. To view a file rendered:

- **Quick preview:** prepend `https://htmlpreview.github.io/?` to the file's raw URL.
- **Best experience:** enable **GitHub Pages** for the repo (Settings → Pages) and browse to `index.html`.

## Editing from the web / phone

- **Quick edits:** open the repo and press `.` (period), or replace `github.com` with `github.dev` in the URL — a browser VS Code opens. Works on mobile browsers too.
- **Full dev environment (to run the Java projects):** use GitHub Codespaces from the green **Code** button.

## Spec documents

The `.kiro/specs/` folder holds the design and task specs used to generate these materials.
