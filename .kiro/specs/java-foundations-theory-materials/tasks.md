# Implementation Plan: Java Foundations Theory Materials

## Overview

This plan builds a single standalone, self-contained HTML artifact — `java-foundations-theory.html` (a ~40 slide presenter-driven theory slideshow for Java foundations) — plus a small JavaScript test harness for the pure functions and state invariants.

The new deck is a sibling of the existing `springboot-session1-theory.html` at the workspace root and deliberately reuses that file's mechanics: the MacBook window chrome, the THEME-SYNC design-token block, the slide navigation engine (`clampIndex` / `formatCounter` / `goTo` / `render`), the slide counter, the transition + reduced-motion behavior, the code-block styling, and the `try/catch`-guarded graceful-degradation pattern.

Implementation language is **JavaScript** (inline ES6 in the HTML file). Property-based tests use **fast-check** (minimum 100 iterations each), and structural/content requirements are covered by example/DOM smoke tests and error-path tests.

The two pure functions (`clampIndex`, `formatCounter`) plus a text-only `getSnippetText` helper are authored once in a testable module and then duplicated **verbatim** into the HTML file. The THEME-SYNC token block is copied byte-identically from `springboot-session1-theory.html`, guarded by a textual equality test.

## Tasks

- [ ] 1. Set up test harness and shared pure-function module
  - [ ] 1.1 Initialize the JavaScript test project
    - Create `package.json`, install `fast-check`, `vitest`, and `jsdom`, add a `test` script that runs once (no watch mode)
    - Add a vitest config with the `jsdom` environment for DOM-based invariant and snippet-fidelity tests
    - _Requirements: Testing Strategy (property-based + DOM assertions)_

  - [ ] 1.2 Implement the shared pure-functions module
    - Create `src/pure-functions.js` exporting `clampIndex(i, total)`, `formatCounter(current, total)`, and `getSnippetText(textOrEl)` (string-accepting variant for isolated testing)
    - `clampIndex` returns `0` when `total <= 0`, else constrains `i` to `[0, total-1]`; `formatCounter` returns `"{current} of {total}"`
    - This exact code is the canonical source later duplicated verbatim into the HTML file's inline script
    - _Requirements: 3.6, 3.7, 4.1, 4.5, 14.2_

  - [ ]* 1.3 Write property test for `clampIndex`
    - **Property 1: Clamp stays in range**
    - **Validates: Requirements 3.6, 3.7**
    - fast-check, ≥100 iterations, tagged `Feature: java-foundations-theory-materials, Property 1: Clamp stays in range`; assert `0` when `total === 0`, else in `[0, total-1]`, with `clampIndex(-1,total)===0` and `clampIndex(total,total)===total-1`

  - [ ]* 1.4 Write property test for `formatCounter`
    - **Property 4: Counter correctness**
    - **Validates: Requirements 4.1, 4.3, 4.5**
    - fast-check, ≥100 iterations, tagged `Feature: java-foundations-theory-materials, Property 4: Counter correctness`; assert exact `"{current} of {total}"` string and `"0 of 0"` for an empty deck

  - [ ]* 1.5 Write property test for `getSnippetText`
    - **Property 5: Snippet text fidelity**
    - **Validates: Requirements 14.2**
    - fast-check, ≥100 iterations, tagged `Feature: java-foundations-theory-materials, Property 5: Snippet text fidelity`; render randomized strings (incl. newlines + leading/trailing whitespace) entity-escaped into `<pre><code>` via jsdom and assert captured `textContent` is byte-for-byte equal to the authored content

- [ ] 2. Build the Theory Slideshow shell and MacBook theme
  - [ ] 2.1 Create `java-foundations-theory.html` skeleton with the THEME-SYNC token block and window chrome
    - DOCTYPE/head/body skeleton at the workspace root; `<style>` with the `/* THEME-SYNC START */ … /* THEME-SYNC END */` `:root` custom properties (colors, `--mac-font`, `--mac-mono`, `--slide-anim`) copied **byte-identically** from `springboot-session1-theory.html`; zero external `<link>`, `<script src>`, `@import`, or remote `url(...)`
    - macOS window chrome with exactly three traffic-light dots in source order red → yellow → green via horizontal flex; title bar whose visible text contains the phrase "Java Foundations"
    - _Requirements: 1.1, 1.3, 1.4, 1.6, 2.1, 2.2, 2.3, 2.4_

  - [ ] 2.2 Add slideshow viewport, navigation controls, counter, and base slide/code CSS
    - Always-visible prev/next controls positioned within the viewport; slide-counter element; `.slide` CSS where only `.active` is visible (exactly one slide shown); reusable content-component classes (`.cover`, `.agenda`, `.cards`/`.card`, `.flow`, `.stack`, `table.cmp`, `.keybox`/`.warnbox`/`.note`, `.checklist`)
    - Code-block styling: `--mac-mono`, background (`--mac-code-bg`) distinct from the slide, a visible four-sided border, ≥ 8 px padding, `white-space: pre`, and `overflow-x: auto`
    - _Requirements: 3.1, 3.8, 4.1, 14.1, 14.3_

- [ ] 3. Implement the navigation engine and transitions
  - [ ] 3.1 Implement the slide navigator
    - Inline `clampIndex`/`formatCounter` copied verbatim from `src/pure-functions.js`; state `{ index, total, isTransitioning }`; `init`, `goTo`, `next`, `prev`, `render`; all logic inside a single `try/catch`-guarded `init()` invoked on `DOMContentLoaded` so static HTML survives a scripting failure
    - Wire next/prev controls and Right/Left arrow keys; disable the boundary control and no-op at the first/last slide; ignore navigation requests while `isTransitioning`; ignore Arrow keys when `document.activeElement` is an `<input>`/`<textarea>`/editable element; load shows current `1`; zero-slide handling shows `"0 of 0"`
    - _Requirements: 1.5, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 4.2, 4.3, 4.4, 4.5_

  - [ ] 3.2 Implement slide transition animation with reduced-motion fallback
    - Fade + slight translate on the incoming slide via the `--slide-anim` token (200–800 ms), beginning on the next frame; clear `isTransitioning` on `animationend` with a `setTimeout` safety net so the deck can never get stuck
    - `@media (prefers-reduced-motion: reduce)` sets the animation duration to `0s`; feature-detect `matchMedia`/animation support and skip the JS-driven animation for immediate final placement; re-entrant changes always settle with exactly one slide displayed
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 3.3 Write property test for the navigation invariant
    - **Property 2: Navigation invariant — exactly one active slide, counter in range**
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.8, 4.2**
    - fast-check, ≥100 iterations, tagged `Feature: java-foundations-theory-materials, Property 2: Navigation invariant — exactly one active slide, counter in range`; drive a lightweight in-memory model with random next/prev sequences; assert exactly one active slide, current in `[1,total]`, and boundary requests are no-ops

  - [ ]* 3.4 Write property test for navigation during a transition
    - **Property 3: Navigation during a transition is ignored**
    - **Validates: Requirements 3.9, 5.4**
    - fast-check, ≥100 iterations, tagged `Feature: java-foundations-theory-materials, Property 3: Navigation during a transition is ignored`; apply random sequences in which some requests arrive while `isTransitioning` is true and assert `index` is unchanged for those requests and the single-active invariant holds throughout

  - [ ]* 3.5 Write example/DOM smoke + error-path tests for navigation, counter, and degradation
    - Parse `java-foundations-theory.html` via jsdom: boundary disabling at first/last slide; counter format `"current of total"`; on load shows `1`; zero-slides renders `"0 of 0"` without throwing; arrow keys inside a text input are ignored; reduced-motion/unsupported-animation places the incoming slide immediately; an `init()` failure leaves static slide text/headings/code visible
    - _Requirements: 1.5, 3.1, 3.6, 3.7, 3.10, 4.4, 4.5, 5.2, 5.3_

- [ ] 4. Checkpoint — engine and shell
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Author cover, agenda, and Java Fundamentals slides
  - [ ] 5.1 Add the cover and agenda slides
    - Title/cover slide identifying the session as the "Java Foundations" session of the training series; agenda slide whose Agenda_Tracker lists the seven topics (Java Fundamentals, JVM, Eclipse IDE, JDK & Eclipse Setup, Datatypes, Variables, Conditional Statements) in the same order they appear in the deck
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 5.2 Add the Java Fundamentals content slides
    - What Java is + origin (developer org, initial release year); key features (platform independence, object orientation, automatic memory management) each described in ≥ 1 sentence; "write once, run anywhere" via bytecode on any JVM; structure of a Java program (class, `main`, statements, packages) each named and described; keep each slide to 3–7 bullets, splitting where needed
    - _Requirements: 6.3, 6.4, 6.5, 6.6, 7.1, 7.2, 7.3, 7.4_

  - [ ] 5.3 Add the Java Fundamentals code snippet
    - A complete, compilable Java program containing a class with a `main` method that prints at least one line of console output, rendered in the shared `<pre><code>` styling
    - _Requirements: 7.5_

- [ ] 6. Author the JVM deep-dive slides
  - [ ] 6.1 Add the JVM content slides
    - JDK vs JRE vs JVM (contents + relationships); Bytecode definition + role as the platform-independent intermediate; compile/execute pipeline `.java` → `javac` → `.class` → JVM in order; classloading (classes loaded into memory before execution); runtime memory areas (heap, stack, method area, with the data each holds); garbage collection (auto reclamation of unreferenced heap objects); JIT compilation (bytecode → native at runtime, for performance); keep each slide to 3–7 bullets, splitting dense topics
    - _Requirements: 6.3, 6.5, 6.6, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ] 6.2 Add the JVM terminal-commands code snippet
    - A Code_Snippet showing the terminal commands that compile and run a Java program, presenting `javac` followed by `java` in that order
    - _Requirements: 8.8_

- [ ] 7. Author the Eclipse IDE and Setup slides
  - [ ] 7.1 Add the Eclipse IDE slides
    - Define what an IDE is and state ≥ 3 distinct benefits over a plain text editor (each ≥ 1 sentence); introduce Eclipse as a Java IDE and describe ≥ 3 distinct features (e.g., editor with code completion, build/run tooling, debugger), each ≥ 1 sentence
    - _Requirements: 6.3, 6.4, 6.6, 9.1, 9.2_

  - [ ] 7.2 Add the JDK & Eclipse setup slides and snippet
    - Numbered steps (≥ 2) to install the JDK; verify-JDK step (`java -version`) with the expected version-string output; numbered steps (≥ 2) to install & launch Eclipse; numbered steps (≥ 2) to create a Java project + class; steps to run a class with the expected Eclipse-console output; a Code_Snippet showing the verification command output or the first Eclipse class source
    - _Requirements: 6.3, 6.6, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [ ] 8. Author the Datatypes slides
  - [ ] 8.1 Add the eight-primitive-types table slide
    - A bordered `table.cmp` with a header row, eight data rows (one per primitive: `byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean`), and ≥ 3 columns (type, size in bits, min/max range), with visible cell borders
    - _Requirements: 11.1, 11.2_

  - [ ] 8.2 Add the reference-types, casting, and literals slides
    - Primitive vs reference types (objects, arrays, strings identified as reference types); casting/conversion distinguishing implicit widening from explicit narrowing and noting narrowing may lose data (via `.warnbox`); literals for integer, floating-point, char, boolean, and string with ≥ 1 example each; keep each slide to 3–7 bullets
    - _Requirements: 6.6, 11.3, 11.4, 11.5_

  - [ ] 8.3 Add the Datatypes code snippets
    - One Code_Snippet declaring variables of two or more primitive types and one Code_Snippet demonstrating a type cast
    - _Requirements: 11.6_

- [ ] 9. Author the Variables slides
  - [ ] 9.1 Add the Variables content slides
    - Declaration (name + type) vs initialization (assigning a value); naming rules (start with letter/underscore/`$`; may contain letters, digits, underscores, `$`; not a reserved keyword; case-sensitive) + camelCase convention; local vs instance vs static (declaration site + scope); `final` for constants (cannot be reassigned after initialization); keep each slide to 3–7 bullets
    - _Requirements: 6.6, 12.1, 12.2, 12.3, 12.4_

  - [ ] 9.2 Add the Variables code snippet
    - A Code_Snippet demonstrating declaration + initialization of a local variable, an instance variable, a static variable, and a `final` variable
    - _Requirements: 12.5_

- [ ] 10. Author the Conditional Statements slides
  - [ ] 10.1 Add the Conditional Statements content slides
    - `if` / `if`-`else` / `else`-`if` ladder / nested `if`; `switch` (case labels, `break`, `default`, fall-through); switch expressions (Java 14+, `->` form, yields a value); ternary operator (`cond ? a : b`); relational (`==`, `!=`, `<`, `>`, `<=`, `>=`) and logical (`&&`, `||`, `!`) operators forming conditions; keep each slide to 3–7 bullets
    - _Requirements: 6.6, 13.1, 13.2, 13.3, 13.4, 13.5_

  - [ ] 10.2 Add the Conditional Statements code snippets
    - A Code_Snippet for each of: an `if`-`else if`-`else` ladder, a `switch` statement, a switch expression, and a ternary operator usage
    - _Requirements: 13.6_

- [ ] 11. Finalize the deck and verify consistency
  - [ ] 11.1 Add the recap and closing slides
    - Recap slide with a `.checklist` of ≥ 5 items, each referencing a Topic covered earlier; closing slide naming the next session (Spring Boot Session 1); confirm topics remain contiguous in agenda order and no slide exceeds 7 bullets
    - _Requirements: 6.3, 6.6, 6.7, 6.8_

  - [ ]* 11.2 Write example/DOM smoke tests for the full deck inventory
    - Parse `java-foundations-theory.html` via jsdom: cover identifies the Java Foundations session; agenda lists the seven topics in slide order; topic slides are contiguous and ordered; every content slide has 3–7 bullets and none exceeds 7; the eight-row bordered table has ≥ 3 columns; required code snippets exist (complete `main`, `javac`-before-`java`, setup, primitive decls + cast, four variable kinds, the four conditional forms); recap has ≥ 5 items; closing names Spring Boot Session 1
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 9.1, 9.2, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 12.1, 12.2, 12.3, 12.4, 12.5, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

  - [ ]* 11.3 Write THEME-SYNC equality and self-containment scan tests
    - Extract the text between `/* THEME-SYNC START */` and `/* THEME-SYNC END */` from `java-foundations-theory.html` and `springboot-session1-theory.html` and assert byte-identical; assert three traffic-lights in source order red → yellow → green and the `.mac-title` text contains "Java Foundations"; grep the file for `<link`, `<script src`, `@import`, `fetch`, `XMLHttpRequest`, and remote `url(...)` and assert none present; assert the file exists at the workspace root
    - _Requirements: 1.1, 1.4, 1.6, 2.1, 2.2, 2.3, 2.4_

- [ ] 12. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional (tests) and can be skipped for a faster MVP; core implementation tasks are never optional.
- The pure functions are authored once in `src/pure-functions.js`, tested in isolation, then copied verbatim into the HTML file's inline script.
- The THEME-SYNC block is copied byte-identically from `springboot-session1-theory.html`; task 11.3 guards against drift and confirms the shared font stack and palette values match the series file.
- Property tests use fast-check with a minimum of 100 iterations and the required `Feature: java-foundations-theory-materials, Property {n}: ...` tag.
- Example/DOM smoke and error-path tests cover the fixed structure, content inventory, and graceful-degradation paths.
- Timing-sensitive behaviors (slide change < 500 ms, transition begins < 100 ms and lasts 200–800 ms, reduced-motion immediate placement, first-render < 3 s) and zero-network operation are verified manually per the design's Testing Strategy and are not coding tasks.
- All content-authoring tasks edit the single file `java-foundations-theory.html`; the dependency graph schedules them in separate waves to avoid write conflicts.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1"] },
    { "id": 1, "tasks": ["1.2", "2.2"] },
    { "id": 2, "tasks": ["1.3", "1.4", "1.5", "3.1"] },
    { "id": 3, "tasks": ["3.2"] },
    { "id": 4, "tasks": ["3.3", "3.4", "3.5", "5.1"] },
    { "id": 5, "tasks": ["5.2"] },
    { "id": 6, "tasks": ["5.3"] },
    { "id": 7, "tasks": ["6.1"] },
    { "id": 8, "tasks": ["6.2"] },
    { "id": 9, "tasks": ["7.1"] },
    { "id": 10, "tasks": ["7.2"] },
    { "id": 11, "tasks": ["8.1"] },
    { "id": 12, "tasks": ["8.2"] },
    { "id": 13, "tasks": ["8.3"] },
    { "id": 14, "tasks": ["9.1"] },
    { "id": 15, "tasks": ["9.2"] },
    { "id": 16, "tasks": ["10.1"] },
    { "id": 17, "tasks": ["10.2"] },
    { "id": 18, "tasks": ["11.1"] },
    { "id": 19, "tasks": ["11.2", "11.3"] }
  ]
}
```
