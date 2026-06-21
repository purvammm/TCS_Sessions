# Implementation Plan: Spring Boot Session 1 Training Materials

## Overview

This plan builds two standalone, self-contained HTML artifacts — `springboot-session1-theory.html` (a 30–40 slide presenter slideshow) and `springboot-session1-lab.html` (a single scrollable lab manual) — plus a small JavaScript test harness for the pure functions and state invariants.

Implementation language is **JavaScript** (inline ES6 in each HTML file). Property-based tests use **fast-check** (minimum 100 iterations each), and structural/content requirements are covered by example/DOM smoke tests and error-path tests.

The four pure functions (`clampIndex`, `formatCounter`, `computeProgress`, `getSnippetText`) are authored once in a testable module and then duplicated **verbatim** into the HTML files. The THEME-SYNC token block is authored in the theory file and copied byte-identically into the lab file, guarded by a textual equality test.

## Tasks

- [ ] 1. Set up test harness and shared pure-function module
  - [x] 1.1 Initialize the JavaScript test project
    - Create `package.json`, install `fast-check`, `vitest`, and `jsdom`, add a `test` script that runs once (no watch mode)
    - Add a vitest config with the `jsdom` environment for DOM-based invariant tests
    - _Requirements: Testing Strategy (property-based + DOM assertions)_

  - [ ] 1.2 Implement the shared pure-functions module
    - Create `src/pure-functions.js` exporting `clampIndex(i, total)`, `formatCounter(current, total)`, `computeProgress(ticked, total)`, and `getSnippetText(el)` (text-only variant accepting a string for isolated testing)
    - This exact code is the canonical source later duplicated verbatim into both HTML files
    - _Requirements: 3.6, 3.7, 4.1, 4.5, 8.4, 8.5, 8.6, 8.7, 10.2, 17.3_

  - [ ]* 1.3 Write property test for `clampIndex`
    - **Property 1: Clamp stays in range**
    - **Validates: Requirements 3.6, 3.7**
    - fast-check, ≥100 iterations, tagged `Feature: springboot-session1-training-materials, Property 1: Clamp stays in range`; assert `0` when `total === 0`, else in `[0, total-1]`, with `clampIndex(-1,total)===0` and `clampIndex(total,total)===total-1`

  - [ ]* 1.4 Write property test for `formatCounter`
    - **Property 4: Counter correctness**
    - **Validates: Requirements 4.1, 4.3, 4.5**
    - fast-check, ≥100 iterations, tagged `Feature: springboot-session1-training-materials, Property 4: Counter correctness`; assert exact `"{current} of {total}"` string and `"0 of 0"` for empty deck

  - [ ]* 1.5 Write property test for `computeProgress`
    - **Property 5: Progress is the rounded ticked ratio**
    - **Validates: Requirements 8.4, 8.5, 8.6, 8.7**
    - fast-check, ≥100 iterations, tagged `Feature: springboot-session1-training-materials, Property 5: Progress is the rounded ticked ratio`; assert `0` when `total===0`, else `Math.round(ticked/total*100)`, integer in `[0,100]`, `0` at `ticked=0`, `100` at `ticked=total`

  - [ ]* 1.6 Write property test for `getSnippetText`
    - **Property 7: Snippet text fidelity**
    - **Validates: Requirements 10.2, 17.3**
    - fast-check, ≥100 iterations, tagged `Feature: springboot-session1-training-materials, Property 7: Snippet text fidelity`; assert captured text is byte-for-byte equal to authored content including newlines and leading/trailing whitespace

- [ ] 2. Build the Theory Slideshow shell and MacBook theme
  - [x] 2.1 Create `springboot-session1-theory.html` skeleton with THEME-SYNC token block and window chrome
    - DOCTYPE/head/body skeleton; `<style>` with `/* THEME-SYNC START */ … /* THEME-SYNC END */` `:root` custom properties (colors, `--mac-font`, `--mac-mono`, `--slide-anim`); no external `<link>`, `<script src>`, `@import`, or remote `url(...)`
    - macOS window chrome with exactly three traffic-light dots in source order red → yellow → green via horizontal flex; title bar
    - Defensive `init()` invoked on `DOMContentLoaded` wrapped in a single `try/catch`
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 2.1, 2.3, 2.4_

  - [ ] 2.2 Add slideshow viewport, navigation controls, counter, and base slide CSS
    - Always-visible prev/next controls positioned within the viewport; slide-counter element; `.slide` CSS where only `.active` is visible (exactly one slide shown); monospace/bordered/padded code-block styling with `white-space: pre` and `overflow-x: auto`
    - _Requirements: 3.1, 3.8, 4.1, 17.2, 17.4_

- [ ] 3. Implement the Theory Slideshow navigation engine
  - [ ] 3.1 Implement the slide navigator
    - Inline `clampIndex`/`formatCounter` copied verbatim from `src/pure-functions.js`; state `{ index, total, isTransitioning }`; `init`, `goTo`, `next`, `prev`, `render`
    - Wire next/prev controls, Right/Left arrow keys; disable boundary control and no-op at first/last slide; ignore requests while transitioning; clear `isTransitioning` on `transitionend` with a timeout safety net; load shows current `1`; zero-slide handling shows `"0 of 0"`
    - _Requirements: 1.5, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 3.2 Write property test for the navigation invariant
    - **Property 2: Navigation invariant — exactly one active slide, counter in range**
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.8, 4.2**
    - fast-check, ≥100 iterations, tagged `Feature: springboot-session1-training-materials, Property 2: Navigation invariant — exactly one active slide, counter in range`; drive a lightweight in-memory model with random next/prev sequences; assert exactly one active slide, current in `[1,total]`, boundary requests no-op

  - [ ]* 3.3 Write property test for navigation during a transition
    - **Property 3: Navigation during a transition is ignored**
    - **Validates: Requirements 3.9**
    - fast-check, ≥100 iterations, tagged `Feature: springboot-session1-training-materials, Property 3: Navigation during a transition is ignored`; assert in-transition requests leave `index` unchanged and the single-active invariant holds throughout

  - [ ]* 3.4 Write example/DOM smoke + error-path tests for navigation and counter
    - Boundary disabling at first/last slide; counter format `"current of total"`; on load shows `1`; zero-slides renders `"0 of 0"` without throwing (parse theory HTML via jsdom)
    - _Requirements: 3.1, 3.6, 3.7, 4.4, 4.5_

- [ ] 4. Author the Theory Slideshow content slides (30–40 total)
  - [ ] 4.1 Add cover, agenda, and traditional-Spring problem slides
    - Title/cover slide; agenda slide with Agenda_Tracker listing topics in slide order; traditional-Spring problem slides (XML config, manual wiring, no embedded server), splitting any topic over 7 bullets
    - _Requirements: 5.2, 5.3, 5.4, 5.18_

  - [ ] 4.2 Add Spring Boot definition, comparison table, and feature deep-dive slides
    - "What is Spring Boot" slides (convention over config, auto-config, embedded server, starters, production-ready); Spring vs Spring Boot comparison table (≥3 attribute rows, header row, ≥2 columns, visible borders); deep dives for auto-config, embedded server, starters, opinionated defaults, Actuator
    - _Requirements: 5.5, 5.6, 5.8, 6.3, 5.18_

  - [ ] 4.3 Add starters table, `@SpringBootApplication` decomposition, and dependency-injection slides
    - Common-starters table (≥5 starters, name + purpose, header row, ≥2 columns, borders); `@SpringBootApplication` decomposed into `@Configuration`, `@EnableAutoConfiguration`, `@ComponentScan`; DI slides (tight vs loose coupling, `@Component`, `@Autowired`, IoC container)
    - _Requirements: 5.9, 5.10, 5.11, 6.3_

  - [ ] 4.4 Add Initializr, project structure, config, preview, recap, and closing slides
    - Spring Initializr walkthrough; project structure deep dive; `pom.xml` anatomy; `application.properties` slide; Session 2 preview; recap checklist (≥5 items each referencing an earlier topic); closing slide. Confirm total slide count lands in `[30, 40]`
    - _Requirements: 5.1, 5.12, 5.13, 5.14, 5.15, 5.16, 5.17_

  - [ ]* 4.5 Write example/DOM smoke tests for the slide inventory
    - Slide count in `[30,40]`; all required slides present; comparison and starter tables have header row, ≥2 columns, visible borders, required row counts; recap has ≥5 items (parse theory HTML via jsdom)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12, 5.13, 5.14, 5.15, 5.16, 5.17, 6.3_

- [ ] 5. Implement Theory Slideshow visual aids
  - [ ] 5.1 Build the CSS architecture diagram with text fallback
    - Architecture-diagram slide with 7 labeled `.arch-node` boxes (Browser → HTTP Request → DispatcherServlet → Controller → Service → Repository → Database) connected by CSS connectors; hidden `.arch-fallback` text listing the same flow; diagram setup in `try/catch` with a sentinel size check that reveals the fallback on failure while preserving remaining slide text
    - _Requirements: 5.7, 6.1, 6.5_

  - [ ] 5.2 Implement slide transition animation with reduced-motion fallback
    - Fade + slight translate on the incoming slide via the `--slide-anim` token (200–800 ms), beginning on the next frame; `@media (prefers-reduced-motion: reduce)` sets duration `0s`; feature-detect `matchMedia` and skip JS-driven animation for immediate final placement
    - _Requirements: 6.2, 6.4_

  - [ ]* 5.3 Write example/DOM smoke tests for the diagram, tables, and code blocks
    - Diagram has 7 labeled node shapes plus connector elements and a fallback element; code blocks use the monospace token, a distinct bordered/padded container, `white-space: pre`, and `overflow-x: auto`
    - _Requirements: 6.1, 6.5, 17.2, 17.4_

  - [ ]* 5.4 Write error-path tests for diagram fallback and reduced-motion
    - Diagram-failure path reveals `.arch-fallback` and keeps slide text; reduced-motion places the incoming slide immediately; zero-slides path is a safe no-op
    - _Requirements: 6.4, 6.5, 4.5_

- [ ] 6. Checkpoint — Theory Slideshow
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Build the Lab Sheet shell, theme, and section layout
  - [ ] 7.1 Create `springboot-session1-lab.html` skeleton with the THEME-SYNC block and window chrome
    - Copy the `/* THEME-SYNC START */ … /* THEME-SYNC END */` block and window-chrome markup **byte-identically** from the theory file (traffic lights red → yellow → green); no external references; defensive `init()` on `DOMContentLoaded` in a single `try/catch`; no slide engine or per-slide navigation control
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 2.4, 7.1, 7.2, 7.3_

  - [ ] 7.2 Lay out the seven sections with distinct headings and the sticky progress header
    - Sections in fixed top-to-bottom order: (1) header with checklist + progress bar, (2) pre-requisites, (3) Lab 1, (4) Lab 2, (5) Lab 3, (6) Lab 4, (7) quick reference card; each with a distinct heading; progress bar pinned via `position: sticky; top: 0`
    - _Requirements: 7.4, 7.5, 8.1, 8.2_

- [ ] 8. Implement Lab Sheet progress tracking, expandable sections, and copy buttons
  - [ ] 8.1 Implement the progress tracker
    - Inline `computeProgress` copied verbatim; `recomputeProgress()` counts checked items, sets bar width + label, and toggles the readiness message when all four prerequisite items are checked; checklist change handlers; loads at 0%
    - _Requirements: 8.3, 8.4, 8.5, 8.6, 8.7, 11.4_

  - [ ] 8.2 Implement expandable sections
    - Native `<details>`/`<summary>` (or button + `aria-expanded` + collapsible panel) with a collapsed/expanded indicator; reveal/hide within 500 ms; each section toggles independently leaving others unchanged
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ] 8.3 Implement copy buttons
    - Inline `getSnippetText` copied verbatim; `copySnippet(text)` uses `navigator.clipboard.writeText` with a hidden-textarea `execCommand('copy')` fallback; `attachCopyButtons()` inserts exactly one button per snippet; success confirmation shown within 500 ms and kept ≥2 s; failure shows error and leaves clipboard untouched; empty snippet short-circuits with "nothing to copy"
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 17.3_

  - [ ]* 8.4 Write property test for one copy button per snippet
    - **Property 6: Exactly one copy button per snippet**
    - **Validates: Requirements 10.1**
    - fast-check, ≥100 iterations, tagged `Feature: springboot-session1-training-materials, Property 6: Exactly one copy button per snippet`; build a random collection of snippets in a jsdom DOM, run `attachCopyButtons`, assert button count equals snippet count and each snippet has exactly one

  - [ ]* 8.5 Write property test for independent expandable sections
    - **Property 8: Expandable sections toggle independently**
    - **Validates: Requirements 9.4**
    - fast-check, ≥100 iterations, tagged `Feature: springboot-session1-training-materials, Property 8: Expandable sections toggle independently`; apply a random toggle sequence to an in-memory/jsdom model and assert each toggle changes only its own section's state

  - [ ]* 8.6 Write error-path tests for copy buttons
    - Clipboard-failure path shows error and leaves the clipboard untouched (stub `clipboard.writeText` to reject and `execCommand` to fail); empty-snippet path shows "nothing to copy" with no write attempt
    - _Requirements: 10.4, 10.5_

- [ ] 9. Author the Lab Sheet content
  - [ ] 9.1 Write the pre-requisites section
    - Four tickable items (JDK 17+, IDE = IntelliJ/Eclipse/VS Code, Maven 3.6+, active internet); each with a verification command and expected observable result; readiness indication when all four checked
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ] 9.2 Write Lab 1 (create and run the first project) with common-issues subsection
    - `start.spring.io` generation (Group `com.tcs.training`, Artifact `springboot-demo`, Java 17, Jar, `spring-boot-starter-web`); import steps for IntelliJ and Eclipse with completion confirmation; run via IDE main class and `mvn spring-boot:run`; expected console output (port 8080 + started line with startup time); common-issues (port-in-use, Maven download failure, reimport) with symptom/cause/resolution; port-8080-in-use guidance and observable indication. Each code snippet uses the shared code-block styling
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

  - [ ] 9.3 Write Lab 2 (project structure) and Lab 3 (first REST controller)
    - Lab 2 numbered steps describing `pom.xml`, main application class, and `application.properties` roles; Lab 3 `@RestController` with `@GetMapping("/hello")` returning a specified String literal, GET request URL with host/port and matching expected response body, and a "try it yourself" subsection with 2–4 variation exercises
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 14.1, 14.2, 14.3, 14.4_

  - [ ] 9.4 Write Lab 4 (dependency injection) and the quick reference card
    - Lab 4: `@Service GreetingService` with a public greeting method; inject via `@Autowired`; expected greeting output; observation question on the unsatisfied-dependency startup failure when `@Service` is removed; run-and-verify steps. Quick reference card at the bottom: annotations cheatsheet (≥5), `application.properties` keys (≥3), URL patterns (≥2 with example URLs)
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 16.1, 16.2, 16.3, 16.4_

  - [ ]* 9.5 Write example/DOM smoke tests for lab structure and content
    - Seven sections present in required order with distinct headings and no slide-navigation control; progress bar is `position: sticky` in the header; four prerequisites each have a verification step; Labs 1–4 and quick-reference content assertions; code blocks use monospace/bordered/padded/`overflow-x` styling
    - _Requirements: 7.3, 7.4, 7.5, 8.1, 8.2, 11.1, 11.2, 11.3, 12.1, 13.1, 14.1, 15.1, 16.1, 16.2, 16.3, 16.4, 17.1, 17.4_

- [ ] 10. Cross-file consistency and self-containment verification
  - [ ] 10.1 Write the THEME-SYNC equality and self-containment scan tests
    - Extract the text between `/* THEME-SYNC START */` and `/* THEME-SYNC END */` from both HTML files and assert byte-identical; compare the window-chrome markup; assert three traffic-lights in source order red → yellow → green in each file; grep both files for `<link`, `<script src`, `@import`, `fetch`, `XMLHttpRequest`, and remote `url(...)` and assert none present
    - _Requirements: 1.1, 1.2, 1.4, 2.1, 2.2, 2.3, 2.4_

  - [ ]* 10.2 Write the independence smoke test
    - Assert the two files declare no colliding global identifiers or shared storage keys, so simultaneous use produces no cross-talk
    - _Requirements: 1.6_

- [ ] 11. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional (tests) and can be skipped for a faster MVP; core implementation tasks are never optional.
- The four pure functions are authored once in `src/pure-functions.js`, tested in isolation, then copied verbatim into each HTML file's inline script.
- The THEME-SYNC block is authored in the theory file (2.1) and copied byte-identically into the lab file (7.1); task 10.1 guards against drift.
- Property tests use fast-check with a minimum of 100 iterations and the required `Feature: springboot-session1-training-materials, Property {n}: ...` tag.
- Example/DOM smoke and error-path tests cover fixed structure, content inventory, and graceful-degradation paths.
- Timing-sensitive behaviors (transition start <100 ms / duration 200–800 ms, copy confirmation ≥2 s) and true two-window independence are verified manually per the design's Testing Strategy and are not coding tasks.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1"] },
    { "id": 1, "tasks": ["1.2", "2.2", "7.1"] },
    { "id": 2, "tasks": ["1.3", "1.4", "1.5", "1.6", "3.1", "7.2"] },
    { "id": 3, "tasks": ["3.2", "3.3", "3.4", "4.1", "8.1"] },
    { "id": 4, "tasks": ["4.2", "8.2"] },
    { "id": 5, "tasks": ["4.3", "8.3"] },
    { "id": 6, "tasks": ["4.4", "8.4", "8.5", "8.6", "9.1"] },
    { "id": 7, "tasks": ["4.5", "5.1", "9.2"] },
    { "id": 8, "tasks": ["5.2", "9.3"] },
    { "id": 9, "tasks": ["5.3", "5.4", "9.4"] },
    { "id": 10, "tasks": ["9.5", "10.1", "10.2"] }
  ]
}
```
