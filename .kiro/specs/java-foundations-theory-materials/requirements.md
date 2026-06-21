# Requirements Document

## Introduction

This feature delivers a single standalone, browser-openable HTML training artifact for a "Java Foundations Session" — the foundational entry that precedes the existing Spring Boot training series authored by Purvam Prajapati. The session is theory-focused and aimed at complete beginners to Java, so each slide is intentionally text-dense and is accompanied by code examples.

The single deliverable is:

1. **Theory Slideshow** (`java-foundations-theory.html`): A presenter-driven, full-screen interactive slideshow that teaches Java fundamentals, the JVM (in depth), the Eclipse IDE, JDK/Eclipse setup, datatypes, variables, and conditional statements. It is the projection backbone of the session, displayed on the big screen and advanced by the presenter while teaching.

The file is self-contained (HTML + inline CSS + inline JavaScript, no external build step or server dependency) and reuses the established MacBook visual identity, slideshow navigation engine, slide counter, transition behavior, code-block styling, and graceful-degradation patterns already defined for the series (notably `springboot-session1-theory.html`). It lives at the workspace root alongside the existing session files (`springboot/java-foundations-theory.html`).

Because this is a theory-heavy deck for beginners, the requirements explicitly allow a single topic to be split across multiple slides when its content is large, and they require code examples to be present throughout.

## Glossary

- **Theory_Slideshow**: The HTML artifact `java-foundations-theory.html` that presents Java foundations concepts as a navigable slide deck.
- **Slide**: A single full-viewport content unit within the Theory_Slideshow, displayed one at a time.
- **Slide_Navigator**: The control system within the Theory_Slideshow responsible for moving between slides (on-screen controls, keyboard, counter).
- **Slide_Counter**: The on-screen indicator showing the current slide number and total slide count (for example, "7 of 42").
- **Agenda_Tracker**: A visual list on the Theory_Slideshow agenda slide showing the session topic sequence.
- **MacBook_Theme**: The shared visual style emulating macOS used across the training series, including window chrome with traffic-light buttons (red/yellow/green), macOS system fonts, and a macOS-inspired color palette.
- **Code_Snippet**: A formatted, monospaced block of Java code or terminal commands within the Theory_Slideshow.
- **Presenter**: The trainer who drives the Theory_Slideshow on the projected screen.
- **Learner**: A complete beginner to Java attending the session.
- **Topic**: One of the seven subject areas covered by the session: Java Fundamentals, the JVM, the Eclipse IDE, JDK and Eclipse Setup, Datatypes, Variables, and Conditional Statements.
- **JDK**: Java Development Kit — the toolset for developing Java programs, including the compiler and the JRE.
- **JRE**: Java Runtime Environment — the runtime that executes Java programs.
- **JVM**: Java Virtual Machine — the engine that loads and executes Java bytecode.
- **Bytecode**: The intermediate `.class` instruction format produced by the Java compiler and executed by the JVM.

## Requirements

### Requirement 1: Standalone, Self-Contained Artifact

**User Story:** As a presenter, I want the deliverable to be a self-contained HTML file, so that I can open it directly in a browser without any server or build step.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL be a single HTML file named `java-foundations-theory.html` containing all required CSS and JavaScript inline, with zero references to external CSS, JavaScript, font, or media files.
2. WHEN the Theory_Slideshow is opened via a `file://` path in a browser supporting HTML5, CSS3, and ES6, THE Theory_Slideshow SHALL render the first slide and all navigation controls within 3 seconds and enable every interactive control (slide navigation, and any in-slide interactive elements) without requiring a web server.
3. WHEN the Theory_Slideshow is opened via a `file://` path in a browser supporting HTML5, CSS3, and ES6, THE Theory_Slideshow SHALL display all slide text, headings, code blocks, and embedded images defined in its inline content with no missing or broken elements.
4. WHILE no network connection is available, THE Theory_Slideshow SHALL enable navigation across all slides and operation of all interactive controls, and SHALL issue zero outbound network requests.
5. IF an inline script throws an error during execution, THEN THE Theory_Slideshow SHALL keep all already-rendered slide text, headings, and images visible and selectable, and SHALL indicate the failure of the affected interactive control to the user.
6. THE Theory_Slideshow SHALL be located at the workspace root directory alongside the existing series HTML files.

### Requirement 2: Shared MacBook Theme Consistency

**User Story:** As a presenter, I want the deck styled with the same MacBook theme as the rest of the series, so that the foundational session looks cohesive with the Spring Boot sessions.

#### Acceptance Criteria

1. WHEN the Theory_Slideshow is rendered, THE Theory_Slideshow SHALL apply the MacBook_Theme, displaying macOS-style window chrome that contains exactly three traffic-light buttons ordered left-to-right as red, then yellow, then green.
2. THE Theory_Slideshow SHALL apply the same macOS-inspired system font stack used by the existing series theory file `springboot-session1-theory.html`, such that the identical primary font family is used.
3. THE Theory_Slideshow SHALL apply the same shared color palette used by the existing series theory file `springboot-session1-theory.html`, such that the background color, the primary text color, and the accent color each use color values identical to the corresponding elements in that file.
4. WHEN the Theory_Slideshow is rendered, THE Theory_Slideshow SHALL display, within the macOS-style window chrome title bar, a window title whose visible text contains the phrase "Java Foundations".

### Requirement 3: Slideshow Navigation Controls

**User Story:** As a presenter, I want to navigate the slides with on-screen controls and the keyboard, so that I can advance the presentation hands-free or by clicking.

#### Acceptance Criteria

1. WHILE the slideshow is active, THE Theory_Slideshow SHALL display a next-slide control and a previous-slide control that remain within the visible slideshow viewport bounds without requiring scrolling.
2. WHEN the Presenter activates the next-slide control AND a following slide exists, THE Slide_Navigator SHALL replace the currently displayed slide with the next slide within 500 milliseconds.
3. WHEN the Presenter activates the previous-slide control AND a preceding slide exists, THE Slide_Navigator SHALL replace the currently displayed slide with the previous slide within 500 milliseconds.
4. WHEN the Presenter presses the Right Arrow key AND a following slide exists, THE Slide_Navigator SHALL replace the currently displayed slide with the next slide within 500 milliseconds.
5. WHEN the Presenter presses the Left Arrow key AND a preceding slide exists, THE Slide_Navigator SHALL replace the currently displayed slide with the previous slide within 500 milliseconds.
6. WHILE the first slide is displayed, THE Slide_Navigator SHALL render the previous-slide control in a non-interactive state with a persistent visual disabled indication, and SHALL keep the first slide displayed and initiate no transition when a previous-navigation request (control activation or Left Arrow key press) is received.
7. WHILE the last slide is displayed, THE Slide_Navigator SHALL render the next-slide control in a non-interactive state with a persistent visual disabled indication, and SHALL keep the last slide displayed and initiate no transition when a next-navigation request (control activation or Right Arrow key press) is received.
8. THE Theory_Slideshow SHALL display exactly one slide at a time in the viewport.
9. IF a navigation request is received while a slide transition is in progress, THEN THE Slide_Navigator SHALL ignore the request and complete the in-progress transition, leaving exactly one slide displayed.
10. IF a Right Arrow or Left Arrow key press is received while keyboard focus is within a text input field, THEN THE Slide_Navigator SHALL ignore the key press and keep the currently displayed slide unchanged.

### Requirement 4: Slide Counter

**User Story:** As a presenter, I want a slide counter, so that I know my position in the deck and can manage time.

#### Acceptance Criteria

1. WHILE the slideshow is active AND the Theory_Slideshow contains at least one slide, THE Theory_Slideshow SHALL display a Slide_Counter within the visible viewport without requiring scrolling, showing the current slide number and the total number of slides in the format "current of total" (for example, "3 of 12"), where the current slide number is an integer between 1 and the total number of slides inclusive.
2. WHEN the displayed slide changes, THE Slide_Counter SHALL update within 200 milliseconds to show the current slide number, where the current slide number is an integer between 1 and the total number of slides inclusive.
3. THE Slide_Counter total SHALL equal the actual number of slides present in the Theory_Slideshow.
4. WHEN the Theory_Slideshow finishes loading AND it contains at least one slide, THE Slide_Counter SHALL display the current slide number as 1.
5. IF the Theory_Slideshow contains zero slides, THEN THE Slide_Counter SHALL display the current slide number as 0 and the total number of slides as 0.

### Requirement 5: Slideshow Transitions and Graceful Degradation

**User Story:** As a presenter, I want animated slide transitions that degrade gracefully, so that the deck is engaging on the projected screen and remains usable in any environment.

#### Acceptance Criteria

1. WHEN the displayed slide changes, THE Theory_Slideshow SHALL apply a single visual transition animation to the incoming slide that begins within 100 milliseconds of the change and completes within a duration between 200 and 800 milliseconds.
2. IF the viewing environment indicates a reduced-motion preference, THEN THE Theory_Slideshow SHALL display the incoming slide immediately in its final position, fully rendered and legible, without animation.
3. IF the viewing environment does not support the transition animation, THEN THE Theory_Slideshow SHALL display the incoming slide immediately in its final position, fully rendered and legible, without animation.
4. IF the displayed slide changes again while a transition animation is still in progress, THEN THE Theory_Slideshow SHALL complete with exactly one slide displayed in its final position, fully rendered and legible.

### Requirement 6: Deck Scope and Topic Coverage

**User Story:** As a learner, I want the deck to cover the seven Java foundation topics across many theory-dense slides, so that I build a solid base before later sessions.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL include a title/cover slide identifying the session as the Java Foundations session of the training series.
2. THE Theory_Slideshow SHALL include an agenda slide that presents, via the Agenda_Tracker, the seven session topics (Java Fundamentals, the JVM, the Eclipse IDE, JDK and Eclipse Setup, Datatypes, Variables, and Conditional Statements) in the same order those topics appear in the slideshow.
3. THE Theory_Slideshow SHALL present the seven topics in the agenda order, such that all slides for one topic appear before the first slide of the next topic.
4. THE Theory_Slideshow SHALL present each of the seven topics on at least one content slide that contains between 3 and 7 bullet points inclusive.
5. WHERE a Topic's content would require more than 7 bullet points to present, THE Theory_Slideshow SHALL split that Topic across multiple Slides such that each resulting Slide contains between 3 and 7 bullet points inclusive.
6. THE Theory_Slideshow SHALL contain at most 7 bullet points on each Slide.
7. THE Theory_Slideshow SHALL include a recap slide containing at least 5 recap items, each item referencing a Topic covered earlier in the slideshow.
8. THE Theory_Slideshow SHALL include a closing slide that names the next session in the training series.

### Requirement 7: Java Fundamentals Content

**User Story:** As a learner, I want to understand what Java is and its core characteristics, so that I know why and how Java is used.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL include content that states a definition of what Java is and summarizes the origin of Java, covering at least the original developer organization and the initial public release year.
2. THE Theory_Slideshow SHALL include content describing the key features of Java, covering at least platform independence, object orientation, and automatic memory management, with a one-sentence-or-more description of each.
3. THE Theory_Slideshow SHALL include content explaining the "write once, run anywhere" principle in terms of compiling source code to bytecode that runs on any JVM.
4. THE Theory_Slideshow SHALL include content describing the structure of a Java program, covering classes, the `main` method, statements, and packages, with each of these four elements named and described.
5. THE Theory_Slideshow SHALL include at least one Code_Snippet showing a complete, compilable Java program that contains a class with a `main` method and prints at least one line of output to the console.

### Requirement 8: JVM Deep-Dive Content

**User Story:** As a learner, I want an in-depth explanation of the JVM, so that I understand how Java code is compiled and executed.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL include content distinguishing the JDK, the JRE, and the JVM, stating for each what it contains and how it relates to the other two.
2. THE Theory_Slideshow SHALL include content defining Bytecode and explaining its role as the platform-independent intermediate format produced from Java source.
3. THE Theory_Slideshow SHALL include content describing the compilation and execution pipeline from `.java` source through `javac` to a `.class` file executed by the JVM, presenting these stages in order.
4. THE Theory_Slideshow SHALL include content explaining classloading, stating that the JVM loads classes into memory before they are executed.
5. THE Theory_Slideshow SHALL include content describing the JVM runtime memory areas, covering the heap, the stack, and the method area, and stating the kind of data each area holds.
6. THE Theory_Slideshow SHALL include content explaining garbage collection as the automatic reclamation of heap objects that are no longer referenced.
7. THE Theory_Slideshow SHALL include content explaining JIT compilation as the runtime translation of bytecode to native machine code, and stating that its purpose is to improve execution performance.
8. THE Theory_Slideshow SHALL include at least one Code_Snippet showing the terminal commands that compile and run a Java program, presenting `javac` followed by `java` in that order.

### Requirement 9: Eclipse IDE Content

**User Story:** As a learner, I want to understand what an IDE is and what Eclipse offers, so that I know the tool I will use to write Java.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL include content defining what an IDE is and stating at least three distinct benefits of using an IDE over a plain text editor, with each benefit described in at least one sentence.
2. THE Theory_Slideshow SHALL include content introducing Eclipse as a Java IDE and describing at least three distinct Eclipse features (for example, the editor with code completion, the build and run tooling, and the debugger), with each named feature described in at least one sentence.

### Requirement 10: JDK and Eclipse Setup Content

**User Story:** As a learner, I want step-by-step setup guidance, so that I can install the tools and run my first Java program in Eclipse.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL include content providing a numbered sequence of two or more ordered steps to install the JDK on the developer machine.
2. THE Theory_Slideshow SHALL include content providing a step to verify the JDK installation (for example, running `java -version`) and stating the expected observable result (the console displays a JDK version string).
3. THE Theory_Slideshow SHALL include content providing a numbered sequence of two or more ordered steps to install and launch Eclipse on the developer machine.
4. THE Theory_Slideshow SHALL include content providing a numbered sequence of two or more ordered steps to create a new Java project and a new class in Eclipse.
5. THE Theory_Slideshow SHALL include content providing the steps to run a Java class from within Eclipse and stating the expected observable result (program output appears in the Eclipse console).
6. THE Theory_Slideshow SHALL include at least one Code_Snippet showing the verification command output or the first Eclipse class source.

### Requirement 11: Datatypes Content

**User Story:** As a learner, I want to understand Java datatypes, so that I can choose the correct type for my data.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL include content listing the eight Java primitive types (`byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean`) together with each type's size expressed in bits and its minimum and maximum representable value range.
2. THE Theory_Slideshow SHALL present the eight primitive types and their sizes and ranges as a table containing a header row, eight data rows (one per primitive type), and at least three columns, with visible cell borders separating rows and columns.
3. THE Theory_Slideshow SHALL include content distinguishing primitive types from reference types, identifying objects, arrays, and strings as reference types.
4. THE Theory_Slideshow SHALL include content explaining type casting and conversion, distinguishing implicit widening conversion from explicit narrowing casts and stating that narrowing casts may lose data.
5. THE Theory_Slideshow SHALL include content describing literals for the primitive types, covering integer, floating-point, character, boolean, and string literals, with at least one example literal per category.
6. THE Theory_Slideshow SHALL include at least one Code_Snippet declaring variables of two or more primitive types and at least one Code_Snippet demonstrating a type cast.

### Requirement 12: Variables Content

**User Story:** As a learner, I want to understand variables, so that I can declare, initialize, and use them correctly.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL include content explaining variable declaration (introducing a name and type) and variable initialization (assigning an initial value).
2. THE Theory_Slideshow SHALL include content stating the Java variable naming rules (a name starts with a letter, underscore, or dollar sign; may contain letters, digits, underscores, and dollar signs; must not be a reserved keyword; and is case-sensitive) and the conventional camelCase naming style.
3. THE Theory_Slideshow SHALL include content distinguishing local variables, instance variables, and static variables, stating for each where it is declared and its scope.
4. THE Theory_Slideshow SHALL include content explaining the `final` keyword for declaring constants, stating that a `final` variable cannot be reassigned after initialization.
5. THE Theory_Slideshow SHALL include at least one Code_Snippet demonstrating declaration and initialization of a local variable, an instance variable, a static variable, and a `final` variable.

### Requirement 13: Conditional Statements Content

**User Story:** As a learner, I want full-depth coverage of conditional statements, so that I can control program flow based on conditions.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL include content explaining the `if` statement, the `if`-`else` statement, the `else`-`if` ladder, and the nested `if` statement.
2. THE Theory_Slideshow SHALL include content explaining the `switch` statement, including `case` labels, the `break` statement, the `default` label, and fall-through behavior when `break` is omitted.
3. THE Theory_Slideshow SHALL include content explaining switch expressions introduced in Java 14 and later, including the arrow (`->`) form, and stating that a switch expression yields a value.
4. THE Theory_Slideshow SHALL include content explaining the ternary conditional operator (`condition ? a : b`), stating that it evaluates to `a` when the condition is true and to `b` when the condition is false.
5. THE Theory_Slideshow SHALL include content describing the relational operators (`==`, `!=`, `<`, `>`, `<=`, `>=`) and the logical operators (`&&`, `||`, `!`) as they are used to form conditions.
6. THE Theory_Slideshow SHALL include at least one Code_Snippet for each of the following: an `if`-`else if`-`else` ladder, a `switch` statement, a switch expression, and a ternary operator usage.

### Requirement 14: Code Snippet Readability

**User Story:** As a learner, I want code examples to be clearly formatted, so that I can read them accurately during the session.

#### Acceptance Criteria

1. THE Theory_Slideshow SHALL render every Code_Snippet in a monospaced font within a block whose background color differs from the surrounding slide background, with a visible four-sided border and padding of at least 8 pixels.
2. THE Theory_Slideshow SHALL preserve the original line breaks and leading-whitespace indentation of each Code_Snippet exactly as authored, with no characters added, removed, or substituted.
3. WHERE a Code_Snippet contains a line wider than its container, THE Theory_Slideshow SHALL keep the full line content accessible via horizontal scrolling within the container without truncating, hiding, or altering any characters.
