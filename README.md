# Java &amp; Spring Boot Training Materials

Slide decks and hands-on lab sheets for a Java and Spring Boot training programme, authored by **Purvam Prajapati** (Faculty, AHD).

Each session ships two self-contained HTML files — open them directly in any browser, no build step needed.

## Start here

Open [`index.html`](index.html) — a landing page that links every slideshow and lab in one place.

## Contents

### Foundations

| Session | Theory (slideshow) | Hands-on lab |
|--------:|--------------------|--------------|
| Java Foundations | `java-foundations-theory.html` | — |
| Collections, Class Relationships & File I/O _(superseded — see Java Core 3 & 4)_ | `java-collections-theory.html` | — |

### Java Core — 4-part series

| Session | Theory (slideshow) | Hands-on lab |
|--------:|--------------------|--------------|
| 1 — Exception Handling | `java-core-session1-theory.html` | `java-core-session1-lab.html` |
| 2 — Inheritance & Polymorphism | `java-core-session2-theory.html` | `java-core-session2-lab.html` |
| 3 — Collections: List Classes & Relationships | `java-core-session3-theory.html` | `java-core-session3-lab.html` |
| 4 — Set, Map & Basic File I/O | `java-core-session4-theory.html` | `java-core-session4-lab.html` |

### Database & process

| Session | Theory (slideshow) | Hands-on lab |
|--------:|--------------------|--------------|
| JDBC — Database Connectivity | `jdbc-theory.html` | `jdbc-lab.html` |
| Agile & Scrum | `agile-theory.html` | — |

### Spring Boot — 4-part series

| Session | Theory (slideshow) | Hands-on lab |
|--------:|--------------------|--------------|
| 1 — Spring Boot foundations | `springboot-session1-theory.html` | `springboot-session1-lab.html` |
| 2 — REST Web Services | `springboot-session2-theory.html` | `springboot-session2-lab.html` |
| 3 — DTO, layers & exception handling | `springboot-session3-theory.html` | `springboot-session3-lab.html` |
| 4 — Microservices with Spring Cloud | `springboot-session4-theory.html` | `springboot-session4-lab.html` |

- **Theory files** are interactive slideshows (arrow keys / on-screen controls, slide counter, progress rail).
- **Lab files** are scrollable companions with a progress checklist and copy-to-clipboard code blocks.
- **Every Java Core lab ends with graded take-home tasks** — three compulsory, one for distinction — with expected output, hints, submission instructions and an assessment rubric.

## The journeys

### Java Core

The four Java Core sessions build **one application**, adding a layer each time. Nothing is thrown away — each session's output is the next session's starting point:

1. **Exception Handling** — the `Throwable` hierarchy, checked vs unchecked, `try`/`catch`/`finally`, multi-catch, try-with-resources and `AutoCloseable`, `throw` vs `throws`, custom exceptions, cause chaining and layer translation. **Output:** a `BankAccount` whose balance can never go negative, and a console app no input can crash.
2. **Inheritance & Polymorphism** — `extends`, `super`, constructor chaining, overriding rules, `@Override`, overloading vs overriding, dynamic method dispatch (and why fields aren't polymorphic), casting and `instanceof` pattern matching, abstract classes vs interfaces, `final`, and `equals`/`hashCode`/`toString`. **Output:** an abstract `Account` hierarchy where one loop applies four different interest rates with no type checks.
3. **Collections: List Classes & Relationships** — the framework map, generics, `ArrayList` and `LinkedList` internals with measured performance, iteration and `ConcurrentModificationException`, `Comparable` vs `Comparator`, the `Collections` utility class and immutability traps; then **class relationships** — association, aggregation, composition, dependency injection, and why composition beats inheritance for reuse. **Output:** a growable, sortable bank model with every relationship deliberately chosen.
4. **Set, Map & Basic File I/O** — uniqueness, the `equals`/`hashCode` contract explained through actual hash buckets, `HashSet`/`LinkedHashSet`/`TreeSet`, set algebra, `HashMap` internals, `merge` and `computeIfAbsent`, then byte vs character streams, buffering, charsets, NIO.2 `Path`/`Files`, CSV round-trips and serialization. **Output:** a bank that guarantees unique account numbers, finds any account in O(1), and **survives a restart**.

### Spring Boot

The four Spring Boot sessions build on each other — from a Hello World endpoint to a running microservices architecture:

1. **Foundations** — what Spring Boot is, auto-configuration, and a first running REST endpoint.
2. **REST Web Services** — a complete Student CRUD API with JSON, HTTP methods, and status codes.
3. **DTO, layers & exception handling** — layered architecture (Controller → Service → Repository), DTOs, custom exceptions, and an H2 database; plus a first look at Spring Security and microservices.
4. **Microservices with Spring Cloud** — a Eureka service registry, two microservices, multiple load-balanced instances, and an API Gateway with round-robin routing.

> The Java Core series is deliberately sequenced as a prerequisite for the Spring Boot series: exception handling underpins `@ControllerAdvice`, interfaces and dependency injection underpin `@Service`, and collections underpin every repository method.

## Viewing on GitHub

GitHub shows raw HTML rather than rendering it. To view a file rendered:

- **Quick preview:** prepend `https://htmlpreview.github.io/?` to the file's raw URL.
- **Best experience:** enable **GitHub Pages** for the repo (Settings → Pages) and browse to `index.html`.

## Editing from the web / phone

- **Quick edits:** open the repo and press `.` (period), or replace `github.com` with `github.dev` in the URL — a browser VS Code opens. Works on mobile browsers too.
- **Full dev environment (to run the Java projects):** use GitHub Codespaces from the green **Code** button.

## Spec documents

The `.kiro/specs/` folder holds the design and task specs used to generate these materials.
