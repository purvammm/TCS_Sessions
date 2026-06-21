# Requirements Document

## Introduction

This feature delivers two standalone, browser-openable HTML training artifacts for a Spring Boot "Session 1" training (1:00–1:15 hour duration) aimed at associates and freshers. The session follows a 60% theory / 40% hands-on structure. Both artifacts share a MacBook (macOS) visual theme.

The two deliverables are:

1. **Theory Slideshow** (`springboot-session1-theory.html`): A presenter-driven, full-screen interactive slideshow expanded to approximately 30–40 slides. It is the projection backbone of the session, displayed on the big screen and advanced by the presenter while teaching.

2. **Hands-on Lab Sheet** (`springboot-session1-lab.html`): A single-page, scrollable lab manual that associates keep open on their own machines while coding. It is NOT a slideshow; it has a sticky progress tracker, expandable sections, and copy buttons on every code snippet.

Both files are self-contained (HTML + inline CSS + inline JavaScript, no external build step or server dependency) so they can be opened directly in a browser and used simultaneously.

## Glossary

- **Theory_Slideshow**: The HTML artifact `springboot-session1-theory.html` that presents Spring Boot concepts as a navigable slide deck.
- **Lab_Sheet**: The HTML artifact `springboot-session1-lab.html` that provides step-by-step hands-on lab instructions on a single scrollable page.
- **Slide**: A single full-viewport content unit within the Theory_Slideshow, displayed one at a time.
- **Slide_Navigator**: The control system within the Theory_Slideshow responsible for moving between slides (arrows, keyboard, counter).
- **Slide_Counter**: The on-screen indicator showing the current slide number and total slide count (e.g., "7 / 36").
- **Agenda_Tracker**: A visual progress tracker on the Theory_Slideshow agenda slide showing the session topic sequence.
- **Progress_Bar**: The sticky completion indicator at the top of the Lab_Sheet that reflects how many lab steps have been checked off.
- **Checklist_Item**: A tickable lab step in the Lab_Sheet whose checked state contributes to the Progress_Bar.
- **Expandable_Section**: A collapsible/expandable content block within the Lab_Sheet.
- **Copy_Button**: A control attached to each code snippet that copies the snippet text to the system clipboard.
- **MacBook_Theme**: A shared visual style emulating macOS, including a window chrome with traffic-light buttons (red/yellow/green), macOS system fonts, and a macOS-inspired color palette.
- **Code_Snippet**: A formatted, monospaced block of code or terminal commands within either artifact.
- **Presenter**: The trainer who drives the Theory_Slideshow on the projected screen.
- **Associate**: A fresher/trainee who follows the Lab_Sheet on their own machine.
- **Lab**: A numbered hands-on exercise within the Lab_Sheet (Lab 1 through Lab 4).

## Requirements

### Requirement 1: Standalone, Simultaneously-Openable Artifacts

**User Story:** As a presenter, I want both deliverables to be self-contained HTML files, so that I can open them directly in a browser without any server or build step and run them at the same time.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL be a single HTML file named `springboot-session1-theory.html` containing all required CSS and JavaScript inline, with zero references to external CSS, JavaScript, font, or media files.
2. THE Lab_Sheet SHALL be a single HTML file named `springboot-session1-lab.html` containing all required CSS and JavaScript inline, with zero references to external CSS, JavaScript, font, or media files.
3. WHEN either artifact is opened via a `file://` path in a browser supporting HTML5, CSS3, and ES6, THE artifact SHALL render its complete visible content and enable all interactive controls without requiring a web server.
4. WHEN either artifact runs with no network connection available, THE artifact SHALL function fully and make zero outbound network requests.
5. IF an inline script throws an error during execution, THEN THE artifact SHALL keep its static content readable.
6. WHILE both artifacts are open simultaneously in separate browser windows or tabs, THE artifacts SHALL operate independently such that interaction with one produces no change to the displayed state of the other.

### Requirement 2: Shared MacBook Theme

**User Story:** As a presenter, I want both files styled with a consistent MacBook theme, so that the materials look polished and cohesive on screen.

#### Acceptance Criteria

1. WHEN the Theory_Slideshow is rendered, THE Theory_Slideshow SHALL apply the MacBook_Theme, displaying macOS-style window chrome that contains exactly three traffic-light buttons ordered left-to-right as red, then yellow, then green.
2. WHEN the Lab_Sheet is rendered, THE Lab_Sheet SHALL apply the MacBook_Theme, displaying macOS-style window chrome that contains exactly three traffic-light buttons ordered left-to-right as red, then yellow, then green.
3. THE Theory_Slideshow and THE Lab_Sheet SHALL apply the same macOS-inspired system font stack, such that the identical primary font family is used in both artifacts.
4. THE Theory_Slideshow and THE Lab_Sheet SHALL apply the same shared color palette, such that equivalent visual elements (background, primary text, and accent elements) use identical color values across both artifacts.

### Requirement 3: Slideshow Navigation Controls

**User Story:** As a presenter, I want to navigate the theory slides with on-screen arrows and the keyboard, so that I can advance the presentation hands-free or by clicking.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL display a next-slide control and a previous-slide control that are visible within the slideshow viewport at all times while the slideshow is active.
2. WHEN the Presenter activates the next-slide control AND a following slide exists, THE Slide_Navigator SHALL replace the currently displayed slide with the next slide within 500 milliseconds.
3. WHEN the Presenter activates the previous-slide control AND a preceding slide exists, THE Slide_Navigator SHALL replace the currently displayed slide with the previous slide within 500 milliseconds.
4. WHEN the Presenter presses the Right Arrow key AND a following slide exists, THE Slide_Navigator SHALL replace the currently displayed slide with the next slide within 500 milliseconds.
5. WHEN the Presenter presses the Left Arrow key AND a preceding slide exists, THE Slide_Navigator SHALL replace the currently displayed slide with the previous slide within 500 milliseconds.
6. WHILE the first slide is displayed, THE Slide_Navigator SHALL disable the previous-slide control and SHALL keep the first slide displayed when a previous-navigation request (control activation or Left Arrow key press) is received.
7. WHILE the last slide is displayed, THE Slide_Navigator SHALL disable the next-slide control and SHALL keep the last slide displayed when a next-navigation request (control activation or Right Arrow key press) is received.
8. THE Theory_Slideshow SHALL display exactly one slide at a time in the viewport.
9. IF a navigation request is received while a slide transition is in progress, THEN THE Slide_Navigator SHALL ignore the request and complete the in-progress transition, leaving exactly one slide displayed.

### Requirement 4: Slide Counter

**User Story:** As a presenter, I want a slide counter, so that I know my position in the deck and can manage time.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL display a Slide_Counter showing the current slide number and the total number of slides in the format "current of total" (for example, "3 of 12").
2. WHEN the displayed slide changes, THE Slide_Counter SHALL update within 200 milliseconds to show the current slide number, where the current slide number is an integer between 1 and the total number of slides inclusive.
3. THE Slide_Counter total SHALL equal the actual number of slides present in the Theory_Slideshow, recalculated whenever slides are added to or removed from the Theory_Slideshow.
4. WHEN the Theory_Slideshow finishes loading, THE Slide_Counter SHALL display the current slide number as 1.
5. IF the Theory_Slideshow contains zero slides, THEN THE Slide_Counter SHALL display the current slide number as 0 and the total number of slides as 0.

### Requirement 5: Slideshow Scope and Content Coverage

**User Story:** As an associate, I want the theory deck to cover Spring Boot fundamentals in detail across many slides, so that I understand the concepts before the hands-on labs.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL contain between 30 and 40 slides inclusive.
2. THE Theory_Slideshow SHALL include a title/cover slide identifying the session as Spring Boot Session 1.
3. THE Theory_Slideshow SHALL include an agenda slide that presents, via the Agenda_Tracker, the complete sequence of session topics in the same order those topics appear in the slideshow.
4. THE Theory_Slideshow SHALL include slides explaining the problems with traditional Spring covering XML configuration, manual wiring, and absence of an embedded server.
5. THE Theory_Slideshow SHALL include slides defining Spring Boot covering convention over configuration, auto-configuration, embedded server, starter dependencies, and production-ready features.
6. THE Theory_Slideshow SHALL include a comparison table contrasting Spring with Spring Boot across at least 3 distinguishing attributes, with one row per attribute and one column per framework.
7. THE Theory_Slideshow SHALL include an architecture diagram slide showing the request flow Browser → HTTP Request → DispatcherServlet → Controller → Service → Repository → Database with each of the 7 elements labeled.
8. THE Theory_Slideshow SHALL include deep-dive slides for key features covering auto-configuration, embedded server, starters, opinionated defaults, and Actuator.
9. THE Theory_Slideshow SHALL include a table listing at least 5 common Spring Boot starters, with each row identifying the starter name and its purpose.
10. THE Theory_Slideshow SHALL include slides that decompose `@SpringBootApplication` into `@Configuration`, `@EnableAutoConfiguration`, and `@ComponentScan`.
11. THE Theory_Slideshow SHALL include dependency injection slides covering tight versus loose coupling, `@Component`, `@Autowired`, and the IoC container.
12. THE Theory_Slideshow SHALL include a Spring Initializr walkthrough slide.
13. THE Theory_Slideshow SHALL include a project structure deep-dive slide.
14. THE Theory_Slideshow SHALL include a `pom.xml` anatomy slide.
15. THE Theory_Slideshow SHALL include an `application.properties` slide.
16. THE Theory_Slideshow SHALL include a Session 2 preview slide.
17. THE Theory_Slideshow SHALL include a recap checklist slide containing at least 5 checklist items, each item referencing a topic covered earlier in the slideshow.
18. WHERE a topic's content would require more than 7 bullet points to present, THE Theory_Slideshow SHALL split that topic across multiple slides such that each resulting slide contains at most 7 bullet points.

### Requirement 6: Slideshow Visual Aids and Animations

**User Story:** As a presenter, I want diagrams and animated slide transitions, so that the material is engaging and clear on the projected screen.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL render the architecture diagram such that each architectural component appears as a distinct visual shape with an attached text label and is connected to related components by lines or arrows, rather than as paragraph prose.
2. WHEN the displayed slide changes, THE Theory_Slideshow SHALL apply a visual transition animation to the incoming slide that begins within 100 milliseconds of the change and completes within a duration between 200 and 800 milliseconds.
3. THE Theory_Slideshow SHALL render comparison and starter content as tables, each containing a header row and at least two columns, with visible cell borders separating rows and columns.
4. IF the transition animation cannot be applied because the viewing environment indicates a reduced-motion preference or does not support the animation, THEN THE Theory_Slideshow SHALL display the incoming slide immediately in its final position without animation.
5. IF the architecture diagram fails to render, THEN THE Theory_Slideshow SHALL display a fallback indication that the diagram is unavailable while preserving the remaining textual content of the slide.

### Requirement 7: Lab Sheet Structure (Single Scrollable Page)

**User Story:** As an associate, I want the lab to be a single scrollable page rather than a slideshow, so that I can keep it open and scroll freely while coding.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL present all of its content within a single vertically scrollable page such that the Associate can reach any section by scrolling without triggering a page or slide change.
2. WHEN the Associate scrolls up or down, THE Lab_Sheet SHALL move the visible content along the vertical axis while keeping all sections within the same continuous page.
3. THE Lab_Sheet SHALL disable single-slide-at-a-time navigation such that no navigation control advances or returns content one slide at a time.
4. THE Lab_Sheet SHALL organize content into the following sections, displayed in this top-to-bottom order: (1) header with checklist, (2) pre-requisites check, (3) Lab 1, (4) Lab 2, (5) Lab 3, (6) Lab 4, and (7) quick reference card.
5. THE Lab_Sheet SHALL delineate each of the seven sections with a distinct section heading that identifies the section, such that any section can be located by its heading.

### Requirement 8: Lab Sheet Sticky Progress Tracking

**User Story:** As an associate, I want a sticky progress bar and checklist, so that I can track which lab steps I have completed as I scroll.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL display a Progress_Bar within the header region positioned above the lab step content.
2. WHILE the Associate scrolls the page, THE Lab_Sheet SHALL keep the Progress_Bar continuously visible by pinning it to the top edge of the viewport with no portion scrolling out of view.
3. THE Lab_Sheet SHALL present each lab step as a distinct tickable Checklist_Item within the header region.
4. WHEN an Associate ticks a Checklist_Item, THE Lab_Sheet SHALL update the Progress_Bar completion proportion to equal the number of ticked Checklist_Items divided by the total number of Checklist_Items, expressed as a percentage rounded to the nearest whole percent.
5. WHEN an Associate unticks a Checklist_Item, THE Lab_Sheet SHALL update the Progress_Bar completion proportion to equal the number of ticked Checklist_Items divided by the total number of Checklist_Items, expressed as a percentage rounded to the nearest whole percent.
6. WHEN all Checklist_Items are ticked, THE Progress_Bar SHALL indicate 100% completion.
7. WHEN the Lab_Sheet loads with zero Checklist_Items ticked, THE Progress_Bar SHALL indicate 0% completion.

### Requirement 9: Expandable Sections

**User Story:** As an associate, I want lab sections to expand and collapse, so that I can focus on the current step and hide the rest.

#### Acceptance Criteria

1. WHEN the Lab_Sheet is rendered, THE Lab_Sheet SHALL render its lab sections as Expandable_Sections, each displaying a visual indicator distinguishing its collapsed versus expanded state.
2. WHEN an Associate activates a collapsed Expandable_Section, THE Lab_Sheet SHALL reveal that section's content within 500 milliseconds and update its state indicator to the expanded state.
3. WHEN an Associate activates an expanded Expandable_Section, THE Lab_Sheet SHALL hide that section's content within 500 milliseconds and update its state indicator to the collapsed state.
4. WHEN an Associate activates one Expandable_Section, THE Lab_Sheet SHALL leave the expanded/collapsed state of all other Expandable_Sections unchanged.

### Requirement 10: Copy Buttons on Code Snippets

**User Story:** As an associate, I want a copy button on every code snippet, so that I can paste commands and code accurately without typos.

#### Acceptance Criteria

1. WHEN a Lab_Sheet is rendered, THE Lab_Sheet SHALL attach exactly one Copy_Button to every Code_Snippet displayed.
2. WHEN an Associate activates a Copy_Button, THE Lab_Sheet SHALL copy the complete associated Code_Snippet text, preserving all characters, line breaks, and leading and trailing whitespace, to the system clipboard.
3. WHEN a copy action completes successfully, THE Lab_Sheet SHALL display a visible copy confirmation within 500 milliseconds of the copy completing and SHALL keep the confirmation visible for at least 2 seconds.
4. IF the clipboard copy fails, THEN THE Lab_Sheet SHALL display a visible error indication within 500 milliseconds informing the Associate that the copy did not succeed, and SHALL leave the prior system clipboard contents unchanged.
5. IF an Associate activates a Copy_Button for a Code_Snippet that contains zero characters, THEN THE Lab_Sheet SHALL display a visible indication that there is no content to copy and SHALL leave the prior system clipboard contents unchanged.

### Requirement 11: Pre-requisites Check

**User Story:** As an associate, I want a pre-requisites checklist, so that I can confirm my machine is ready before starting the labs.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL include a pre-requisites section listing the following four items with their required versions: JDK version 17 or higher, an IDE (one of IntelliJ IDEA, Eclipse, or Visual Studio Code), Maven version 3.6 or higher, and active internet access.
2. THE Lab_Sheet SHALL present each of the four pre-requisites as a separate tickable Checklist_Item that can be marked as either checked (verified) or unchecked (not verified).
3. THE Lab_Sheet SHALL provide, for each Checklist_Item, a verification step stating the command to run and the expected observable result that confirms the pre-requisite is satisfied.
4. WHEN all four Checklist_Items are marked as checked, THE Lab_Sheet SHALL indicate that the machine is ready to begin the labs.

### Requirement 12: Lab 1 — Create First Spring Boot Project

**User Story:** As an associate, I want guided steps to create and run my first Spring Boot project, so that I produce a running application.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL provide Lab 1 instructions to generate a project via `start.spring.io` using Group `com.tcs.training`, Artifact `springboot-demo`, Java 17, Jar packaging, and the `spring-boot-starter-web` dependency.
2. THE Lab_Sheet SHALL provide step-by-step import instructions for both IntelliJ IDEA and Eclipse, where each set lists the menu navigation to import the generated Maven project and the action that confirms import completion (project tree visible with resolved Maven dependencies and no unresolved-dependency markers).
3. THE Lab_Sheet SHALL provide instructions to run the application using at least two methods: running the main application class from within the IDE and running the Maven command `mvn spring-boot:run` from the project root directory.
4. THE Lab_Sheet SHALL show the expected console output for a run that reaches the started state, including the embedded server listening on port 8080 and the application started confirmation line containing the startup time.
5. THE Lab_Sheet SHALL provide a common-issues subsection that, for each of port 8080 already in use, Maven dependency download failure, and project reimport, states the trigger symptom, the cause, and the ordered resolution steps the associate must perform to recover.
6. IF the application fails to start because port 8080 is already in use, THEN THE Lab_Sheet SHALL instruct the associate to either free port 8080 or configure an alternate server port, and SHALL describe the observable indication (startup failure message referencing the port) that confirms this condition.

### Requirement 13: Lab 2 — Explore Project Structure

**User Story:** As an associate, I want to explore the generated project structure, so that I understand what each file does.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL provide Lab 2 instructions that identify and describe the purpose of at least the following three project artifacts: the `pom.xml` file, the main application class, and the `application.properties` file.
2. THE Lab_Sheet SHALL describe, for the `pom.xml` file, its role in declaring project dependencies and build configuration.
3. THE Lab_Sheet SHALL describe, for the main application class, its role as the application entry point that starts the application.
4. THE Lab_Sheet SHALL describe, for the `application.properties` file, its role in holding configurable application settings.
5. THE Lab_Sheet SHALL present the Lab 2 instructions as a sequence of numbered steps, where each of the three artifacts is addressed in at least one step.

### Requirement 14: Lab 3 — First REST Controller

**User Story:** As an associate, I want to build my first REST controller, so that I can serve an HTTP response from my application.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL provide Lab 3 instructions to create a class annotated with `@RestController` containing a method annotated with `@GetMapping` mapped to the `/hello` path that returns a String value.
2. THE Lab_Sheet SHALL specify the exact String literal the `/hello` method returns and show that exact literal as the expected response body.
3. WHEN the Lab_Sheet documents accessing the `/hello` endpoint, THE Lab_Sheet SHALL state the request method (GET), the full request URL including host and port, and the expected plain-text response body that matches the returned String literal.
4. THE Lab_Sheet SHALL include a "try it yourself" subsection containing between 2 and 4 variation exercises, where each exercise states the task to perform and the expected observable result.

### Requirement 15: Lab 4 — Dependency Injection

**User Story:** As an associate, I want to practice dependency injection, so that I understand how Spring wires beans together.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL provide Lab 4 instructions to create a `@Service` named `GreetingService` that exposes at least one public method returning a greeting string.
2. THE Lab_Sheet SHALL provide instructions to inject `GreetingService` into the controller using `@Autowired` field, constructor, or setter injection.
3. THE Lab_Sheet SHALL show the expected output, including the exact greeting string returned by the controller endpoint after `GreetingService` is wired in.
4. THE Lab_Sheet SHALL include an observation question asking the associate to record the application behavior, specifically the startup failure indicating an unsatisfied dependency, that results from removing the `@Service` annotation.
5. THE Lab_Sheet SHALL provide instructions to run the application and invoke the controller endpoint to verify the wired greeting output.

### Requirement 16: Quick Reference Card

**User Story:** As an associate, I want a quick reference card, so that I can recall key annotations and settings at a glance.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL include a quick reference card positioned at the bottom of the page below all other content sections.
2. THE quick reference card SHALL include an annotations cheatsheet listing at least 5 annotations, where each entry shows the annotation name and a one-line description of its purpose.
3. THE quick reference card SHALL include a list of at least 3 common `application.properties` keys, where each entry shows the key name and a one-line description of its effect.
4. THE quick reference card SHALL include at least 2 URL patterns, where each entry shows the pattern and a corresponding example URL.

### Requirement 17: Code Snippet Readability

**User Story:** As an associate, I want code snippets to be clearly formatted, so that I can read and copy them accurately.

#### Acceptance Criteria

1. THE Lab_Sheet SHALL render every Code_Snippet in a monospaced font within a block whose background color and bordered, padded container are visually distinct from the surrounding page content.
2. THE Theory_Slideshow SHALL render every code example in a monospaced font within a block whose background color and bordered, padded container are visually distinct from the surrounding slide content.
3. THE Lab_Sheet AND THE Theory_Slideshow SHALL preserve the original line breaks and leading-whitespace indentation of each Code_Snippet exactly as authored.
4. WHERE a Code_Snippet contains a line wider than its container, THE Lab_Sheet AND THE Theory_Slideshow SHALL keep the full line content accessible via horizontal scrolling without truncating, hiding, or altering any characters.
