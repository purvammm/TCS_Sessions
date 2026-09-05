# Spring Boot Training Materials

Slide decks and hands-on lab sheets for a Spring Boot training series, authored by **Purvam Prajapati** (Faculty, AHD).

Each session ships two self-contained HTML files — open them directly in any browser, no build step needed. The two **Servlets** sessions additionally ship Markdown **study notes** that double as a trainer's guide.

## Start here

Open [`index.html`](index.html) — a landing page that links every slideshow and lab in one place.

## Contents

| Session | Theory (slideshow) | Hands-on lab | Study notes |
|--------:|--------------------|--------------|-------------|
| Java Foundations | `java-foundations-theory.html` | — | — |
| Collections, Class Relationships & File I/O | `java-collections-theory.html` | — | — |
| JDBC — Database Connectivity | `jdbc-theory.html` | `jdbc-lab.html` | — |
| Servlets 1 — Web, HTTP & your first servlet | `servlets-session1-theory.html` | `servlets-session1-lab.html` | [`notes`](servlets-session1-theory-notes.md) |
| Servlets 2 — MVC architecture & CRUD with JDBC | `servlets-session2-theory.html` | `servlets-session2-lab.html` | [`notes`](servlets-session2-theory-notes.md) |
| 1 — Spring Boot foundations | `springboot-session1-theory.html` | `springboot-session1-lab.html` | — |
| 2 — REST Web Services | `springboot-session2-theory.html` | `springboot-session2-lab.html` | — |
| 3 — DTO, layers & exception handling | `springboot-session3-theory.html` | `springboot-session3-lab.html` | — |
| 4 — Microservices with Spring Cloud | `springboot-session4-theory.html` | `springboot-session4-lab.html` | — |

- **Theory files** are interactive slideshows (arrow keys / on-screen controls, slide counter, progress rail).
- **Lab files** are scrollable companions with a progress checklist and copy-to-clipboard code blocks.
- **Study notes** are Markdown — they render directly on GitHub, no preview tool needed.

## Study notes (Markdown)

The two Servlets sessions also ship **written notes** that work as a standalone course *and* as a
trainer's guide:

| File | What's in it |
|---|---|
| [`servlets-session1-theory-notes.md`](servlets-session1-theory-notes.md) | 24 chapters — web & HTTP foundations through a complete login servlet |
| [`servlets-session2-theory-notes.md`](servlets-session2-theory-notes.md) | 22 chapters — MVC, the five layers, Derby, and full CRUD |

Each chapter has a plain explanation, a real-world analogy, runnable code, an ASCII diagram, a
**🎓 Teaching tip**, and **✅ Check yourself** questions (all answered in an appendix). Both files
end with a **Teaching Guide** containing a timed session plan, the demos worth doing live, the
analogies that land, and the questions your audience will actually ask — with answers.

Read them top-to-bottom to learn the topic, or jump to Appendix D to prepare to teach it.

## The journey

The foundation sessions run in order — **JDBC** (how Java reaches a database), then the two **Servlets** sessions (how Java answers a browser):

1. **Servlets 1** — the mechanics: HTTP, the servlet lifecycle, and one login servlet built properly.
2. **Servlets 2** — the architecture: five MVC layers and a full CRUD app on top of JDBC.

Servlets 2 extends the same Eclipse project created in Servlets 1, so the two sessions are best taken in order. Together they build by hand exactly the architecture the Spring Boot sessions then rebuild with far less boilerplate.

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
