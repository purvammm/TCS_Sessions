# Java Servlets — Part 2: MVC Architecture & CRUD with JDBC

**Complete study notes + teaching guide**

Companion to `servlets-session2-theory.html` (26 slides) and `servlets-session2-lab.html` (11 labs).
Author: **Purvam Prajapati**, Faculty — AHD.

---

## What this document is

This is a **written, self-contained course**. You can learn servlet architecture from
`servlets-session1-theory-notes.md` onwards by reading it top to bottom, and then use the same
document to **teach the topic to someone else**.

| If you are… | Read it like this |
|---|---|
| **Learning for the first time** | Read straight through. Do the "Check yourself" questions. Skip the 🎓 Teaching tips on the first pass. |
| **Preparing to teach** | Read the chapter, then the 🎓 Teaching tip. Then jump to [Appendix D — Teaching Guide](#appendix-d--teaching-guide). |

### What you need before starting

| Requirement | Why |
|---|---|
| **Part 1 completed** | We extend the same `ServletBasics` project. You need `doGet`, `PrintWriter`, `getParameter` and `web.xml` mapping to be second nature. |
| **JDBC basics** | `Connection`, `PreparedStatement`, `ResultSet`, `executeQuery` vs `executeUpdate`. If hazy, skim the JDBC lab first — today's DAO assumes them. |
| **Basic SQL** | `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `WHERE`. |

> **Didn't do Part 1?** You can still start here. You need a Dynamic Web Project named
> `ServletBasics` with a Tomcat 9 target runtime and a generated `web.xml` containing a
> `<welcome-file-list>`. That's the only inheritance Part 2 needs.

### What you'll be able to do at the end

1. Explain **why** one servlet doing everything fails, with concrete examples.
2. Explain MVC and place any class into the correct layer.
3. Write a five-layer CRUD application from scratch.
4. Route multiple operations through one servlet using an `action` parameter.
5. Explain what Spring Boot's `@Controller`, `@Service` and `@Repository` are actually doing.

---

## Table of contents

**Part A — Why we need architecture**
1. [Where we left off](#1-where-we-left-off)
2. [The problem: one servlet doing everything](#2-the-problem-one-servlet-doing-everything)
3. [Model–View–Controller](#3-modelviewcontroller)
4. [The five packages](#4-the-five-packages)

**Part B — The layers, one at a time**

5. [Layer 1 — `bean`: the Product POJO](#5-layer-1--bean-the-product-pojo)
6. [Layer 2 — `helper`: DBHelper](#6-layer-2--helper-dbhelper)
7. [Layer 3 — `dao`: ProductDao](#7-layer-3--dao-productdao)
8. [Layer 4 — `service`: ProductService](#8-layer-4--service-productservice)
9. [Layer 5 — `web`: ProductServlet](#9-layer-5--web-productservlet)
10. [The call chain, both directions](#10-the-call-chain-both-directions)
11. [Why the layers are worth it](#11-why-the-layers-are-worth-it)

**Part C — The database**

12. [Connecting to Derby](#12-connecting-to-derby)
13. [The `product` table](#13-the-product-table)
14. [Two traps that cost an hour](#14-two-traps-that-cost-an-hour)
15. [Why `WEB-INF/lib` is special](#15-why-web-inflib-is-special)

**Part D — The CRUD patterns**

16. [One servlet, four actions](#16-one-servlet-four-actions)
17. [Links vs forms](#17-links-vs-forms)
18. [The boolean-return pattern](#18-the-boolean-return-pattern)
19. [Killing duplicated code (DRY)](#19-killing-duplicated-code-dry)
20. [The complete ProductServlet](#20-the-complete-productservlet)

**Part E — Honest limitations & what's next**

21. [The gap: nothing is protected](#21-the-gap-nothing-is-protected)
22. [Servlets → JSP → Spring MVC](#22-servlets--jsp--spring-mvc)

**Appendices**

- [Appendix A — Common mistakes and how to spot them](#appendix-a--common-mistakes-and-how-to-spot-them)
- [Appendix B — Glossary](#appendix-b--glossary)
- [Appendix C — Cheat sheet](#appendix-c--cheat-sheet)
- [Appendix D — Teaching Guide](#appendix-d--teaching-guide)
- [Appendix E — Answers to all Check-yourself questions](#appendix-e--answers-to-all-check-yourself-questions)

---
---

# Part A — Why we need architecture

## 1. Where we left off

Part 1 gave you the complete **mechanical vocabulary** of servlets. Everything below should feel
familiar. If any line doesn't, revisit it now — today builds directly on all of it.

| Thing | What you should remember |
|---|---|
| `extends HttpServlet` | Makes your class a servlet the container can load, create and call. |
| `doGet` / `doPost` | Called **once per request**. GET reads, POST writes. Missing `doPost` on a POST form = **405**. |
| `setContentType` **then** `getWriter` | In that order, always. Reversed, it's silently ignored and tags render as text. |
| `out.println` vs `System.out` | `out` → the browser. `System.out` → the console. **Today the console becomes our error log.** |
| `request.getParameter("x")` | Always returns a `String` or `null`. You parse it, and you handle `NumberFormatException`. |
| `web.xml` `<url-pattern>` | Binds a URL to a class. Edit it → **restart Tomcat**, or you get a 404. |
| One instance, many threads | Per-request data in **locals, never fields**. *(This rule reappears today, twice.)* |
| 404 vs 500 | 404 = wrong URL. 500 = your code threw; read the console. |

### What we built — and what was missing

We built a login servlet that reads a form and answers in HTML. But look at **where all the code
lived**:

```java
protected void doGet(HttpServletRequest request, HttpServletResponse response) {

    response.setContentType("text/html");
    PrintWriter out = response.getWriter();

    String action = request.getParameter("action");     // reading input
    int id = Integer.parseInt(request.getParameter("id"));   // conversion

    if (id == VALID_ID && VALID_PWD.equals(pwd)) {      // business logic
        out.println("<h3>Login successful</h3>");       // HTML generation
    }
}
```

**Reading input, checking credentials, and generating HTML — all in one method.**

That is completely fine for one hardcoded check. Today we find out **why it stops being fine**,
and what to do about it.

> 🎓 **Teaching tip**
> Spend a genuine five minutes here. Ask the room to tell *you* what `getParameter` returns, or
> what a 404 means — don't just read the table out. Part 2 is much harder than Part 1, and any
> gap in the fundamentals will compound. If several people are shaky on `setContentType` order
> or the threads rule, re-teach those two before moving on; it will save you time later.

> ✅ **Check yourself**
> **Q1.1** What does `getParameter` return for a numeric form field?
> **Q1.2** You edited `web.xml` and still get a 404. What did you forget?

---

## 2. The problem: one servlet doing everything

Imagine writing a **product manager** — view, add, update, delete products — the way we wrote the
login servlet: everything in `doGet`.

It works. For about a week. Here's what you end up with:

```java
protected void doGet(HttpServletRequest request, HttpServletResponse response) {

    response.setContentType("text/html");
    PrintWriter out = response.getWriter();

    // ---- reading input ----
    int id = Integer.parseInt(request.getParameter("id"));
    double price = Double.parseDouble(request.getParameter("price"));

    // ---- validation rules ----
    if (price < 0) { out.println("<h3>Bad price</h3>"); return; }

    // ---- connection details ----
    Connection con = DriverManager.getConnection("jdbc:derby:C:/db/productdb", "sa", "");

    // ---- SQL ----
    PreparedStatement ps = con.prepareStatement("UPDATE product SET price=? WHERE id=?");
    ps.setDouble(1, price);
    ps.setInt(2, id);
    ps.executeUpdate();

    // ---- HTML generation ----
    out.println("<table border='1'>");
    // ... 15 more lines of table building ...

    // ---- and now repeat ALL of the above for insert, delete and view ----
    // 400 lines. Four copies of the connection code. Four copies of the table loop.
}
```

### Three things are now wrong

```text
   ┌──────────────────────────────────────────────────────────────┐
   │  🔍  NOTHING IS FINDABLE                                     │
   │      Where's the SQL? Somewhere in a 400-line method,        │
   │      between HTML strings. Changing a query means            │
   │      reading all of it.                                     │
   ├──────────────────────────────────────────────────────────────┤
   │  📋  EVERYTHING IS DUPLICATED                                │
   │      The connection URL appears four times. Change           │
   │      database and you must find every copy — and             │
   │      you WILL miss one.                                     │
   ├──────────────────────────────────────────────────────────────┤
   │  🧪  NOTHING IS TESTABLE                                     │
   │      To test "reject negative prices" you'd need a           │
   │      running Tomcat AND a live database. So nobody           │
   │      tests it.                                              │
   └──────────────────────────────────────────────────────────────┘
```

### The one question that drives all of today's design

> ## "When one thing changes, how many places must I edit?"

In the code above, the answer is always *"several, and I'm not sure which."*

**The goal of MVC is to make the answer "one."**

Keep that question in your head for the rest of this session. Every design decision we make is
an answer to it.

> 🎓 **Teaching tip**
> **Do not skip this chapter.** If you jump straight to "here are five packages, create them",
> people follow the instructions without understanding *why*, and they'll abandon the structure
> the moment they build something on their own.
> The most effective delivery: show the 400-line monster on screen, then ask a concrete
> question — *"the boss says show prices with 2 decimals. Where do you edit?"* Let them realise
> the answer is "everywhere, and I'd probably miss one." **Create the pain before offering the
> cure.**

> ✅ **Check yourself**
> **Q2.1** Name the three problems with putting everything in one servlet method.
> **Q2.2** What single question motivates layered design?

---

## 3. Model–View–Controller

**MVC** splits code by **responsibility**, so each class has exactly **one reason to change**.
It's the most widely used architectural pattern in application development, and it long predates
the web.

### The three parts

| Part | What it is | Knows about |
|---|---|---|
| 🗃️ **Model** | The **data** — what the app is *about*. A `Product`, an `Employee`. Plus the code that stores and fetches it. | **Nothing** about the web |
| 🖥️ **View** | **What the user sees.** Today HTML built by `PrintWriter`; later JSP or a template engine. | No business rules |
| 🎛️ **Controller** | The **traffic cop.** Receives the request, decides what should happen, calls the model, picks the view. | Coordinates; **doesn't do the work itself** |

```text
   ┌─────────┐      ┌──────────────┐      ┌────────────────────┐      ┌──────────┐
   │ BROWSER │ ───▶ │  CONTROLLER  │ ───▶ │       MODEL        │ ───▶ │ DATABASE │
   │         │      │  (servlet)   │      │ service+dao+bean   │      │          │
   │         │ ◀─── │              │ ◀─── │                    │ ◀─── │          │
   └─────────┘      └──────────────┘      └────────────────────┘      └──────────┘
                     decides what           does the actual
                     should happen          work with data
```

### Why bother — one concrete sentence

> When the boss says *"show prices with two decimals,"* you want to touch **one** place — not
> hunt through SQL, validation and HTML tangled in a single method.

**Separation of concerns isn't neatness. It's the ability to change one thing safely.**

### An analogy: a restaurant

| MVC part | Restaurant |
|---|---|
| **View** | The **menu and the plate** — what the customer sees |
| **Controller** | The **waiter** — takes your order, decides what to do with it, brings the result |
| **Model** | The **kitchen and the pantry** — where food is actually stored and prepared |

The waiter doesn't cook. The chef doesn't take orders. The pantry doesn't decide the menu.
**Each has one job, and you can replace any one of them without retraining the others.**

> 🎓 **Teaching tip**
> The restaurant analogy is worth ten minutes of abstract explanation. Push it a bit further to
> make the payoff obvious: *"if you change your supplier (the database), does the waiter need
> retraining? No. If you redesign the menu (the HTML), does the chef care? No."* That's exactly
> the property we're buying.

> ✅ **Check yourself**
> **Q3.1** Which MVC part contains your SQL?
> **Q3.2** Which part decides what colour the error message is?

---

## 4. The five packages

MVC in the abstract becomes **five concrete packages**. Every file you create today belongs to
**exactly one** of them, and each layer talks only to the next one down.

| Package | Role | What goes in it | What must **never** go in it |
|---|---|---|---|
| `web` | **View / Web layer** | The **servlets** — read parameters, call the service, write HTML | **SQL**, connection code |
| `service` | **Controller / Service layer** | **Business logic and validation** — "is the price negative? refuse" | **HTML**, SQL, anything HTTP |
| `dao` | **Data Access Object** | **All SQL** — via `PreparedStatement` | **HTML**, validation rules |
| `bean` | **The Model objects** | **POJOs** — private fields, getters/setters, constructors | **Any logic at all** |
| `helper` | **Infrastructure** | **Connection management** — the only class that knows the JDBC URL | SQL statements, HTML |

### The chain

```text
   ┌──────────────┐   ┌──────────────────┐   ┌───────────────┐   ┌────────────┐   ┌──────────┐
   │     web      │──▶│     service      │──▶│      dao      │──▶│   helper   │──▶│ DATABASE │
   │              │   │                  │   │               │   │            │   │          │
   │ProductServlet│   │ ProductService   │   │  ProductDao   │   │  DBHelper  │   │  Derby   │
   │              │   │                  │   │               │   │            │   │          │
   │ params in    │   │ validation       │   │ all the SQL   │   │ the URL,   │   │          │
   │ HTML out     │   │ business rules   │   │               │   │ open/close │   │          │
   └──────────────┘   └──────────────────┘   └───────────────┘   └────────────┘   └──────────┘

                    ┌───────────────────────────────────────────┐
                    │            bean : Product                 │
                    │   the CURRENCY passed between all layers  │
                    └───────────────────────────────────────────┘
```

### Where does `bean` sit in that chain?

**Everywhere — it's the currency, not a step.**

A `Product` object is what the layers **hand to each other**:

```text
   servlet builds one from form data   ──▶  new Product(5, "Webcam", 2500.0, 15)
   service validates it               ──▶  is the price negative?
   dao writes it to the database       ──▶  ps.setInt(1, p.getId()); ...
   dao SELECT returns a List<Product>  ──▶  back up the chain to the servlet
```

That's why it lives in its own package that **everyone imports**.

### The golden rule of layering

> **Each layer talks only to the one directly below it.**
>
> The servlet never touches the DAO. The service never touches the database.
> No layer ever passes an `HttpServletRequest` or a `ResultSet` across a boundary.

That last sentence is the discipline that keeps the layers independent — and it's what makes the
service testable without a server.

> 🎓 **Teaching tip**
> Have everyone **write the five package names in their notebook** before creating a single file,
> with one line each on what belongs there. It takes two minutes and dramatically reduces
> "where does this class go?" questions for the rest of the session.
> Then make it a game throughout the lab: hold up each new file and ask *"which package?"* By
> the fourth file they'll answer instantly, and the structure is internalised rather than
> copied.

> ✅ **Check yourself**
> **Q4.1** You need to add a new SQL query. Which package?
> **Q4.2** You need to add the rule "quantity can't exceed 1000". Which package?
> **Q4.3** Why is `bean` not shown as a step in the chain?


---
---

# Part B — The layers, one at a time

We build **bottom-up**: bean → helper → dao → service → web.

**Why bottom-up?** Each layer only depends on the one below it. Build in this order and by the
time you write the servlet, everything it calls already exists and compiles. Build top-down and
you'd spend the session staring at red errors for classes that don't exist yet.

```text
   Build order:   bean  →  helper  →  dao  →  service  →  web
                  ────     ──────     ───     ───────     ───
                   no       no       needs     needs      needs
                   deps     deps    bean+     dao+       service+
                                    helper    bean       bean
```

---

## 5. Layer 1 — `bean`: the Product POJO

A **POJO** (Plain Old Java Object), also called a **bean**, is a class that does nothing but
**hold data**.

- Private fields
- Public getters and setters
- Constructors
- **No SQL. No HTML. No logic.**

Its plainness is the point: it's the neutral currency the layers pass around, so no layer needs
to know about any other.

### The rule: one field per table column

```text
   TABLE product                          class Product
   ┌────────────────────────────┐         ┌──────────────────────────┐
   │ id        INT PRIMARY KEY  │  ────▶  │ private int    id;       │
   │ name      VARCHAR(50)      │  ────▶  │ private String name;     │
   │ price     DOUBLE           │  ────▶  │ private double price;    │
   │ quantity  INT              │  ────▶  │ private int    quantity; │
   └────────────────────────────┘         └──────────────────────────┘
```

### The code

```java
package com.tcs.bean;

/**
 * One row of the product table, as a Java object.
 * Field names and types mirror the columns exactly.
 */
public class Product {

    private int    id;         // id       INT PRIMARY KEY
    private String name;       // name     VARCHAR(50)
    private double price;      // price    DOUBLE
    private int    quantity;   // quantity INT

    // No-argument constructor: needed if you create an empty object
    // and fill it via setters. Frameworks require it too.
    public Product() {
    }

    // All-arguments constructor: build a complete object in one line.
    // This is the one the DAO and the servlet use.
    public Product(int id, String name, double price, int quantity) {
        this.id       = id;
        this.name     = name;
        this.price    = price;
        this.quantity = quantity;
    }

    // ===== getters and setters =====
    public int getId()                 { return id; }
    public void setId(int id)          { this.id = id; }

    public String getName()            { return name; }
    public void setName(String name)   { this.name = name; }

    public double getPrice()           { return price; }
    public void setPrice(double price) { this.price = price; }

    public int getQuantity()                    { return quantity; }
    public void setQuantity(int quantity)       { this.quantity = quantity; }

    // Handy for System.out debugging — prints readable values instead
    // of something like com.tcs.bean.Product@1b6d3586
    @Override
    public String toString() {
        return "Product [id=" + id + ", name=" + name
             + ", price=" + price + ", quantity=" + quantity + "]";
    }
}
```

### Why two constructors?

| Constructor | When you use it |
|---|---|
| `Product()` — no-arg | When you create an empty object and fill it with setters. **Frameworks require it** (JSP tags, JSON libraries, JPA). |
| `Product(id, name, price, quantity)` — all-args | Build a complete object in one line. **This is the one we use** in the DAO and servlet. |

### Why private fields with public getters, not just public fields?

Fair question — right now the getter literally just returns the value, so it looks like pure
extra typing.

**The answer is encapsulation.** The moment a rule appears, a setter gives you **one place** to
enforce it, and **no calling code changes**:

```java
// Later, a rule appears: prices can never be negative.
public void setPrice(double price) {
    if (price < 0) {
        throw new IllegalArgumentException("Price cannot be negative");
    }
    this.price = price;
}
// Every caller in the entire application is now protected. Nothing else changed.
```

With `public double price;` there is **nowhere** to put that rule.

### ⚠️ The naming convention is not cosmetic

`getPrice()` / `setPrice()` is the **JavaBeans** convention, and real tooling depends on it. It
means *"there is a property called `price`."*

That's how:
- JSP tags find your data (`${product.price}`)
- Spring form binding works
- JSON libraries serialise your object

> **Name them wrong — `fetchPrice()`, `price()`, `GetPrice()` — and the frameworks stop seeing
> your fields.** The convention is `get` + capitalised field name.

### 💡 Don't type all this by hand

Declare the four fields, then let Eclipse generate the rest:

| What you want | How |
|---|---|
| Getters and setters | **Source → Generate Getters and Setters** (`Alt+Shift+S`, then `R`) → Select All |
| All-args constructor | **Source → Generate Constructor using Fields** |
| `toString()` | **Source → Generate toString()** |

**Every Java developer uses these.** Typing forty lines of boilerplate is not a rite of passage.

> 🎓 **Teaching tip**
> Show the Eclipse generation shortcuts **the first time** — it's a genuine productivity gift and
> it earns you credibility. But type **one** getter by hand first so they see what's being
> generated; otherwise it's magic.
> The encapsulation argument needs the *future rule* framing to land. If you just say
> "encapsulation is good practice", beginners hear "arbitrary ceremony". Show the negative-price
> setter and it becomes obvious.

> ✅ **Check yourself**
> **Q5.1** Why does a bean need a no-argument constructor if we never call it?
> **Q5.2** What breaks if you name your getter `fetchPrice()` instead of `getPrice()`?

---

## 6. Layer 2 — `helper`: DBHelper

One class whose **only** job is opening and closing database connections.

The JDBC URL lives here and **nowhere else**. That's what makes "switch from Derby to MySQL" a
one-file change instead of a treasure hunt.

```java
package com.tcs.helper;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * The ONLY class that knows how to reach the database.
 * Change the URL here and the whole application follows.
 */
public class DBHelper {

    // <<< PASTE YOUR OWN URL FROM THE DATA SOURCE EXPLORER HERE >>>
    // Must be an ABSOLUTE path, with forward slashes, and must be the
    // SAME path Eclipse uses — otherwise Tomcat quietly creates a
    // second, empty database and "view" shows nothing. (See chapter 14.)
    private static final String URL  = "jdbc:derby:C:/derbydb/productdb;create=true";
    private static final String USER = "sa";
    private static final String PASS = "";

    /** Opens a connection. Returns null if it fails — callers MUST check. */
    public static Connection connect() {
        try {
            // No Class.forName() needed: JDBC 4.0+ auto-discovers the driver
            // from the JAR — which is why the JAR's location matters (ch. 15).
            return DriverManager.getConnection(URL, USER, PASS);

        } catch (SQLException e) {
            // System.out -> Eclipse console. This is your debugging channel;
            // the user never sees it. Read it when a page says "failed".
            System.out.println("DB connect failed [" + e.getSQLState() + "]: " + e.getMessage());
            return null;
        }
    }

    /** Closes a connection. Null-tolerant, so callers can call it blindly. */
    public static void close(Connection con) {
        try {
            if (con != null) {
                con.close();
            }
        } catch (SQLException e) {
            System.out.println("DB close failed: " + e.getMessage());
        }
    }
}
```

### Three design decisions worth understanding

**1. Why `static` methods?**
There's no state to keep, so there's nothing to instantiate. `DBHelper.connect()` reads cleanly
from anywhere.

**2. Why return `null` on failure instead of throwing?**
It keeps the DAO simple for a first build. But be honest with yourself: **it is a compromise.**
Null-returning methods are easy to misuse — which is exactly why every DAO method below starts
with an `if (con == null)` guard.

> Production code would throw a custom `DataAccessException` carrying the reason.

**3. Why is `close()` null-tolerant?**
So a `finally` block can call it **unconditionally** without its own null check:

```java
} finally {
    DBHelper.close(con);      // safe even if con is null
}
```

Fewer branches, fewer bugs.

### The payoff, visualised

```text
   ONE place knows the URL:

   ┌──────────────────────────────────────┐
   │  DBHelper                            │
   │    URL = "jdbc:derby:..."   ◀── edit ONLY here to change database
   └──────────────────┬───────────────────┘
                      │ used by
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
   insertProduct  getAll...   updateProduct  deleteProduct
        (all four DAO methods — none of them know the URL)
```

### You've met this class before — and you'll meet it again

| Where | What it's called |
|---|---|
| The JDBC session | `DBConnector` — identical idea |
| **Here** | `DBHelper` |
| Spring Boot | **This entire class disappears** — replaced by four lines in `application.properties` |

```properties
# Spring Boot equivalent of DBHelper — the whole class, as config
spring.datasource.url=jdbc:derby:C:/derbydb/productdb
spring.datasource.username=sa
spring.datasource.password=
```

> **Same job, less typing, every time you move up a layer of abstraction.**

> 🎓 **Teaching tip**
> Be honest about the `null` return. Beginners are quick to spot inconsistency, and saying *"this
> is a simplification, here's what production does, here's why we're not doing it yet"* builds
> far more trust than pretending it's ideal. It also plants the exception-handling topic for later.
> The `application.properties` comparison is a great motivator — it shows the direction of travel
> and makes today's work feel like a foundation rather than busywork.

> ✅ **Check yourself**
> **Q6.1** Why must every DAO method check `if (con == null)`?
> **Q6.2** You're switching from Derby to MySQL. How many files change?

---

## 7. Layer 3 — `dao`: ProductDao

The **Data Access Object** is the only place in the entire application where **SQL** appears.

Four methods, one per CRUD operation. They all share the same shape — learn the shape, not the
lines.

### The shape, annotated

```java
public boolean updateProduct(int id, double price) {

    String sql = "UPDATE product SET price = ? WHERE id = ?";      // 1. parameterised SQL

    Connection con = DBHelper.connect();
    if (con == null) { return false; }                             // 2. guard the null

    try (PreparedStatement ps = con.prepareStatement(sql)) {       // 3. auto-closed

        ps.setDouble(1, price);      // 4. bind in the ? order, 1-based
        ps.setInt(2, id);

        return ps.executeUpdate() > 0;                             // 5. rows -> boolean

    } catch (SQLException e) {
        System.out.println("Update failed [" + e.getSQLState() + "]: " + e.getMessage());
        return false;
    } finally {
        DBHelper.close(con);                                       // 6. always release
    }
}
```

### The six rules, explained

| # | Rule | Why it matters |
|---|---|---|
| **1** | **`PreparedStatement` with `?`, always** | Parameters are bound as **data** and can never become SQL — so **SQL injection is impossible**. It's also faster: the database compiles the template once. |
| **2** | **Guard the null connection** | `DBHelper.connect()` can fail. Skip this and you get a `NullPointerException` and a **500** page instead of a clean "failed" message. |
| **3** | **try-with-resources** | Closes the statement on success **and** on exception. |
| **4** | **Bind in the `?` order, 1-based** | `SET price = ? WHERE id = ?` → `setDouble(1, price)` then `setInt(2, id)`. **Reverse them and you'd update the wrong thing.** Note: **1-based, not 0-based.** |
| **5** | **Match the method to the SQL verb** | `executeUpdate()` for INSERT/UPDATE/DELETE (returns a row count). `executeQuery()` for SELECT (returns a `ResultSet`). Swap them → 0 rows or an exception. |
| **6** | **Close the connection in `finally`** | So it's released even when something throws. **Leaked connections eventually exhaust the database.** |

### Why `?` prevents SQL injection — the 30-second version

```java
// ❌ String concatenation — INJECTABLE
String sql = "SELECT * FROM users WHERE name = '" + name + "'";
// if name = "admin' --"  the query becomes:
// SELECT * FROM users WHERE name = 'admin' --'      ← rest is commented out!

// ✅ PreparedStatement — SAFE
String sql = "SELECT * FROM users WHERE name = ?";
ps.setString(1, name);
// the driver sends the TEMPLATE and the VALUE separately.
// "admin' --" is treated as a literal name. The quote cannot escape.
```

> **The template and the values travel separately.** That's the whole mechanism. A parameter can
> never become SQL syntax.

### The SELECT is different: it returns data, not HTML

```java
public List<Product> getAllProducts() {

    String sql = "SELECT id, name, price, quantity FROM product ORDER BY id";

    // Return an EMPTY list rather than null on failure — then callers
    // can always safely write "for (Product p : list)".
    List<Product> list = new ArrayList<Product>();

    Connection con = DBHelper.connect();
    if (con == null) { return list; }

    try (PreparedStatement ps = con.prepareStatement(sql);
         ResultSet rs = ps.executeQuery()) {                    // SELECT -> executeQuery

        // rs.next() starts BEFORE row 1; each call advances one row
        // and returns false when the rows run out.
        while (rs.next()) {
            Product p = new Product(
                    rs.getInt("id"),
                    rs.getString("name"),
                    rs.getDouble("price"),
                    rs.getInt("quantity"));
            list.add(p);
        }

    } catch (SQLException e) {
        System.out.println("Select failed [" + e.getSQLState() + "]: " + e.getMessage());
    } finally {
        DBHelper.close(con);
    }

    return list;
}
```

### How `ResultSet` iteration works

```text
   ResultSet cursor starts HERE, before the first row:
        │
        ▼
   ┌─────────────────────────────────────┐
   │  (before row 1)                     │  rs.next() → true,  now on row 1
   ├─────────────────────────────────────┤
   │  1 | Laptop   | 55000.0 | 10        │  rs.next() → true,  now on row 2
   ├─────────────────────────────────────┤
   │  2 | Mouse    | 750.5   | 100       │  rs.next() → true,  now on row 3
   ├─────────────────────────────────────┤
   │  3 | Keyboard | 1200.0  | 45        │  rs.next() → false, loop ends
   └─────────────────────────────────────┘
```

That's why the loop is `while (rs.next()) { ... }` — the call **both advances and tests**.

### ⚠️ Two deliberate design choices in the SELECT

**1. It returns `List<Product>`, not printed HTML.**

It would be *shorter* to print the table right there — and completely wrong. **The DAO must not
know that its caller is a web page.** Returning data keeps it reusable by:

- a servlet (today)
- a REST endpoint
- a scheduled report
- a unit test

> **Data layers return data. Presentation layers decide how it looks.**

**2. It returns an empty list, never `null`.**

```java
// Because of this, callers NEVER need a null check:
for (Product p : service.getAllProducts()) { ... }     // safe even if the DB is down
```

Returning `null` from a collection-returning method just pushes a `NullPointerException` onto
every caller. **Empty collection > null.** That's a general Java principle worth teaching.

> 🎓 **Teaching tip**
> Don't write all four methods on screen — it's repetitive and attention will drift. Write
> **`updateProduct` fully**, walking the six rules. Then say *"the other three are the same shape
> with different SQL"* and let the lab supply them.
> Do spend proper time on **`executeQuery` vs `executeUpdate`** — mixing them up is a top-three
> beginner bug, and the symptom (0 rows, no error) is baffling.
> If your group has done the JDBC session, the SQL-injection recap can be 60 seconds. If not,
> do the full `admin' --` demo; it's memorable and it's the reason `?` exists.

> ✅ **Check yourself**
> **Q7.1** Why does `getAllProducts()` return a list instead of printing the table itself?
> **Q7.2** `ps.setDouble(1, price)` — why `1` and not `0`?
> **Q7.3** You use `executeUpdate()` for a SELECT. What happens?

---

## 8. Layer 4 — `service`: ProductService

Here's the fair objection students raise: *"if the service just forwards calls to the DAO, why
does it exist?"*

**Correct — and that's why ours does real work: validation.**

```java
package com.tcs.service;

import java.util.List;

import com.tcs.bean.Product;
import com.tcs.dao.ProductDao;

/**
 * Business rules live here. Knows nothing about HTTP (no request/response)
 * and nothing about SQL (no statements) — it sits cleanly between the two.
 */
public class ProductService {

    private ProductDao dao = new ProductDao();

    // ===== CREATE — validate BEFORE touching the database =====
    public boolean addProduct(Product p) {

        if (p == null)                                            { return false; }
        if (p.getId() <= 0)                                       { return false; }  // ids positive
        if (p.getName() == null || p.getName().trim().isEmpty())   { return false; }  // name required
        if (p.getPrice() < 0 || p.getQuantity() < 0)               { return false; }  // no negatives

        // Only now do we hit the database.
        return dao.insertProduct(p);
    }

    // ===== READ — nothing to validate, so pass it through =====
    public List<Product> getAllProducts() {
        return dao.getAllProducts();
    }

    // ===== UPDATE =====
    public boolean updateProduct(int id, double price) {
        if (id <= 0 || price < 0) { return false; }
        return dao.updateProduct(id, price);
    }

    // ===== DELETE =====
    public boolean deleteProduct(int id) {
        if (id <= 0) { return false; }
        return dao.deleteProduct(id);
    }
}
```

### Why validation belongs *here*, and nowhere else

```text
   ❌ In the SERVLET?
      A second UI — a REST API, an admin page, a mobile endpoint —
      would have to DUPLICATE every rule. And one copy would drift.

   ❌ In the DAO?
      The DAO's job is data ACCESS, not company POLICY.
      Mixing them means you can't change a rule without touching SQL.

   ✅ In the SERVICE
      One place. Every caller inherits it automatically.
```

```text
                    ┌─────────────────┐
   web servlet ────▶│                 │
                    │ ProductService  │──▶ dao ──▶ database
   REST endpoint ──▶│  (the rules)     │
                    │                 │
   admin page ─────▶│  written ONCE   │
                    └─────────────────┘
```

### The real payoff: it's testable

Look at what this class does **not** contain:

- No `HttpServletRequest`
- No `PrintWriter`
- No SQL
- No HTML

That means you can test it as a **plain Java class**, with **no server running**:

```java
// A real unit test — no Tomcat, no browser
ProductService service = new ProductService();

Product bad = new Product(1, "Laptop", -500.0, 10);   // negative price
assert service.addProduct(bad) == false;              // rule enforced ✅
```

> **You cannot do that if the rule lives in a servlet.** That's the concrete, practical reason
> this layer exists.

### ⚠️ The honest limitation of returning `boolean`

`false` tells the servlet **that** something failed, never **why**:

| What went wrong | What the servlet sees |
|---|---|
| Blank name | `false` |
| Duplicate id | `false` |
| Database unreachable | `false` |
| Negative price | `false` |

All identical. That's an acceptable simplification while learning — **and it's exactly why the
DAO logs the real `SQLException` to the console.** The detail isn't lost, just not surfaced.

> The proper fix is **custom exceptions** carrying a reason, which is what you'll build with
> `@ControllerAdvice` in the Spring Boot sessions.

### 🌟 The demonstration that proves this layer earns its place

This is the best moment in the Part 2 lab. Two failures, **same message, completely different
code paths**:

| You submit | Page says | Console says |
|---|---|---|
| **Duplicate id** (5 twice) | 🔴 Insertion failed | `Insert failed [23505]: duplicate key...` ← **the DAO caught a real DB error** |
| **Negative price** (-100) | 🔴 Insertion failed | **Nothing at all** ← **the service rejected it before any SQL ran** |

> **That silence is your service layer working.** The database was never even contacted.

> 🎓 **Teaching tip**
> **Anticipate the "this layer is pointless" objection out loud** before someone raises it —
> it shows you've thought about it and makes the answer land better. The validation-duplication
> diagram is the argument that convinces people.
> Then make sure you **actually run the two-failure demo in the lab** and point at the silent
> console. Abstract arguments about layering convince nobody; a silent console that *should*
> have had an error in it convinces everybody.

> ✅ **Check yourself**
> **Q8.1** Why not put the "no negative prices" rule in the servlet?
> **Q8.2** How can you unit-test `ProductService` without starting Tomcat?
> **Q8.3** Insert fails and the console is silent. Which layer rejected it?

---

## 9. Layer 5 — `web`: ProductServlet

The servlet's job **shrinks dramatically** once the other layers exist. It does exactly three
things:

```text
   1. READ parameters      ──▶  2. CALL the service   ──▶  3. WRITE HTML
      (and convert them)          (delegate the work)       (report the result)
```

**No SQL. No connections. No business rules.**

```java
public class ProductServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;

    // Safe as a FIELD: the service holds no per-request state, so all
    // threads can share this one object. Contrast with an id or a name,
    // which must NEVER be a field (Part 1, chapter 15).
    private ProductService service = new ProductService();

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/html");
        PrintWriter out = response.getWriter();

        String action = request.getParameter("action");
        if (action == null) { action = "view"; }        // default, don't crash

        // ... route on action, then print ...
    }

    // ---------- one handler per operation ----------
    private void handleUpdate(HttpServletRequest request, PrintWriter out) {
        try {
            // 1. READ + convert
            int    id    = Integer.parseInt(request.getParameter("id"));
            double price = Double.parseDouble(request.getParameter("price"));

            // 2. DELEGATE
            if (service.updateProduct(id, price)) {
                // 3. REPORT
                out.println("<h3><font color='green'>Product updated.</font></h3>");
            } else {
                out.println("<h3><font color='red'>Updation failed — no id " + id + ".</font></h3>");
            }

        } catch (NumberFormatException e) {
            out.println("<h3><font color='red'>ID and price must be numbers.</font></h3>");
        }
    }
}
```

### Notice how thin this got

**Parse, delegate, report.** That's the whole controller.

All the interesting decisions moved **down** into the service, and all the SQL into the DAO — so
this file now changes **only when the user interface changes.**

> That is the definition of a well-placed responsibility.

### ⚠️ Two things in this file to look at twice

**1. `service` IS an instance field — and that's fine.**

```java
private ProductService service = new ProductService();   // ✅ OK
private int id;                                          // ❌ SERIOUS BUG
```

Remember Part 1, chapter 15: one instance, many threads. So why is `service` safe?

| | |
|---|---|
| `ProductService` | **Stateless** — it has no mutable fields of its own, it just calls the DAO. All threads can share it safely. |
| `int id` | **Per-request data** — thread A would overwrite thread B's value. |

> **The rule is about per-request data, not about fields in general.**

**2. `out` is passed as a parameter, not stored as a field.**

```java
private void handleUpdate(HttpServletRequest request, PrintWriter out) {   // ✅ parameter
```

For exactly the same reason. A `PrintWriter` field would be shared between simultaneous users —
and user A's output could end up in user B's page.

> 🎓 **Teaching tip**
> This chapter is where Part 1's threading rule finally pays off, so **link back to it explicitly**:
> "remember one instance, many threads? Here's where it decides your code."
> The `service` field vs `id` field contrast is worth a full two minutes, because it's the
> nuance that separates rule-following from understanding. Ask them: *"why is one safe and the
> other a bug?"* and make them articulate "stateless vs per-request".

> ✅ **Check yourself**
> **Q9.1** Why is `private ProductService service` safe but `private int id` a bug?
> **Q9.2** What are the only three things a servlet should do in a layered app?

---

## 10. The call chain, both directions

Here's what actually happens when someone submits the "add product" form. Notice the `Product`
object travelling **down**, and the result travelling back **up**.

```text
   ⬇ DOWN: a Product object                      ⬆ UP: a boolean
   ═══════════════════════════════════════════════════════════════════

   1  web · ProductServlet
      Receives 4 STRINGS from the form.
      Parses them, builds a Product, calls service.addProduct(p).
                            │
                            ▼  Product
   2  service · ProductService
      Checks id > 0, name not blank, price/quantity not negative.
      If OK, calls dao.insertProduct(p).
                            │
                            ▼  Product
   3  dao · ProductDao
      Asks DBHelper for a connection, binds the fields to a
      PreparedStatement, executes.
                            │
                            ▼  (asks for a connection)
   4  helper · DBHelper
      Hands back an open Connection (or null).
                            │
                            ▼  SQL
   5  Derby
      Runs the INSERT, reports 1 ROW AFFECTED.
                            │
                            ▲  1
   6  dao
      Converts the row count to TRUE, closes the connection.
                            │
                            ▲  true
   7  service
      Passes the boolean straight up.
                            │
                            ▲  true
   8  web
      Sees true → prints a GREEN success message,
      then the refreshed table.
```

### The two things flowing through that chain

| Direction | What travels |
|---|---|
| **Going down** | A **`Product`** — the bean, the shared currency |
| **Coming up** | A **`boolean`** (for writes) or a **`List<Product>`** (for reads) |

### The discipline that keeps layers independent

> **No layer ever passes an `HttpServletRequest` or a `ResultSet` across a boundary.**

Why that matters:

```java
// ❌ NEVER do this — it couples the service to the web
public boolean addProduct(HttpServletRequest request) { ... }
//   Now the service can ONLY be called from a servlet.
//   No unit tests. No reuse from a REST endpoint or a batch job.

// ✅ DO this — plain Java in, plain Java out
public boolean addProduct(Product p) { ... }
//   Callable from anywhere.
```

The same applies to `ResultSet`: if the DAO returned one, the servlet would have to know about
JDBC, and closing it correctly would become someone else's problem.

> **Plain Java objects in, plain Java objects out.** That single rule is what makes layers real
> rather than decorative.

> 🎓 **Teaching tip**
> Walk this diagram **aloud, twice** — once downward, once upward. Then run it as a role-play:
> assign five people to be the five layers, hand a piece of paper labelled "Product(5, Webcam,
> 2500, 15)" to the servlet, and have them physically pass it down and pass a "true" back up.
> It sounds childish; it works remarkably well and people remember it weeks later.
> The "never pass `HttpServletRequest` down" rule is the most important takeaway of the chapter —
> state it explicitly and explain the testability cost.

> ✅ **Check yourself**
> **Q10.1** What object travels from the servlet down to the DAO?
> **Q10.2** Why shouldn't `addProduct` take an `HttpServletRequest` parameter?

---

## 11. Why the layers are worth it

Five packages for a four-column table feels like overkill. That's a fair objection — so here's
what you actually **buy**, in situations you will genuinely face.

| The change request | All-in-one servlet | **Layered (MVC)** |
|---|---|---|
| "Switch from Derby to MySQL" | ❌ Hunt through every servlet for connection code | ✅ **Edit `DBHelper`. One file.** |
| "Reject negative prices" | ❌ Add the same `if` everywhere a price is written — and miss one | ✅ **Add it once in `ProductService`**; every path covered |
| "Also expose this as a JSON API" | ❌ Copy-paste the logic and edit the copy — two versions to maintain | ✅ **New servlet, same service.** Zero logic duplicated |
| "Write unit tests" | ❌ Nearly impossible — logic needs a running server | ✅ Test `ProductService` as a **plain Java class** |
| "Redesign the page" | ❌ Risk breaking SQL while editing HTML — same method | ✅ Touch only the `web` layer. **Data code untouched** |

### The honest caveat

For a genuinely tiny app, layering **is** extra ceremony. You should know that rather than treat
it as gospel.

But: **applications don't stay tiny**, and retrofitting structure into tangled code is far more
expensive than starting with it.

> **The habit is what you're learning today, not the file count.**

### You've seen this shape before — and you'll see it again

```text
   JDBC session:      Tester  ──▶  DAO  ──▶  DBConnector
                        │            │            │
   Servlets (today):  Servlet ──▶ Service ──▶ DAO ──▶ DBHelper
                        │            │         │
   Spring Boot:     @Controller ─▶ @Service ─▶ @Repository
```

> **Learn the shape once and every Java framework afterwards looks familiar.**

That is the real reason we're doing this by hand. Not because you'll write servlets at work, but
because when you meet `@Service` you'll think *"oh — that's the validation layer"* instead of
*"another annotation to memorise."*

> 🎓 **Teaching tip**
> This table is your answer when someone pushes back with "this seems like a lot of files for
> a simple app." **Don't dismiss the objection — validate it, then answer it.** Say the caveat
> out loud: "you're right, for a tiny app it is overhead."
> Then make it personal: ask if anyone has inherited messy code at work. Someone always has, and
> their story will make your argument better than you can.

> ✅ **Check yourself**
> **Q11.1** You must switch database. Which file changes in a layered app?
> **Q11.2** What's the honest downside of layering?


---
---

# Part C — The database

## 12. Connecting to Derby

Before Java touches the database, we prove the connection works **visually**, in Eclipse's Data
Source Explorer.

**Why?** Debugging a broken connection *through a web app* means reading stack traces. Debugging
it in a dedicated tool takes seconds and gives you a clear error message plus a Test button.

### The six steps

| # | Step | Detail |
|---|---|---|
| **1** | Open the view | Window → Show View → Other → **Data Management** → Data Source Explorer |
| **2** | New connection | Right-click **Database Connections** → New → **Derby** → Next |
| **3** | Driver definition | Click **⊕ New Driver Definition** — see the note below |
| **4** | Add the JAR | In the **JAR List** tab, delete any red-✗ entry, then **Add JAR/Zip** → your real `derby.jar` |
| **5** | Set properties | Database `C:/derbydb/productdb` (**absolute path** — see ch. 14), user `sa`, password blank, tick **Create database if it does not exist** |
| **6** | Test | **Test Connection** → you want **"Ping succeeded!"**. Then **copy the generated URL** |

### New Driver Definition vs Edit Driver Definition

This confuses people, so be clear:

| | When you use it |
|---|---|
| **⊕ New Driver Definition** | The **first time**. Eclipse ships the Derby *template* but **not the JAR**, so you must point it at one. |
| **✎ Edit Driver Definition** | On later projects, when the definition already exists — or to **repair a stale JAR path**. |

> **New = first-time setup. Edit = reuse or repair.**

### What "Ping succeeded!" means

```text
   ┌────────────────────────────────────────────┐
   │  Test Connection                           │
   │                                            │
   │      ✅  Ping succeeded!                    │
   │                                            │
   │                            [ OK ]          │
   └────────────────────────────────────────────┘
             ▲
             │
   This is your GREEN LIGHT.
   Do not write a line of Java until you see it.
```

If ping **fails**, the problem is the JAR path or the database path. **Fix it here**, where the
error message is specific — not later, through a `NullPointerException` in a servlet.

> 🎓 **Teaching tip**
> Do this walkthrough **on the projector, slowly**, then do a verification round: *"everyone raise
> a hand when you see Ping succeeded."* Do not move on until every hand is up.
> This is the single biggest time-sink in Part 2. Ten minutes spent making sure everyone has a
> working connection saves forty minutes of scattered debugging later — and it keeps the session
> feeling like teaching rather than firefighting.

> ✅ **Check yourself**
> **Q12.1** Why test the connection in Eclipse before writing Java?
> **Q12.2** When do you use "New Driver Definition" vs "Edit"?

---

## 13. The `product` table

Open a **SQL Scrapbook** (right-click the connection → Open SQL Scrapbook), pick your connection
in the toolbar dropdowns, and run these **one statement at a time** with `Ctrl + Alt + X`.

```sql
CREATE TABLE product (
    id       INT PRIMARY KEY,      -- unique identifier, never duplicated
    name     VARCHAR(50),          -- text, max 50 characters
    price    DOUBLE,               -- decimal number
    quantity INT                   -- whole number in stock
);

INSERT INTO product VALUES (1, 'Laptop',   55000.00, 10);
INSERT INTO product VALUES (2, 'Mouse',      750.50, 100);
INSERT INTO product VALUES (3, 'Keyboard',  1200.00, 45);
INSERT INTO product VALUES (4, 'Monitor',   9500.00, 20);

SELECT * FROM product;    -- always verify: you should see 4 rows
```

### Expected result

```text
   ID | NAME     | PRICE    | QUANTITY
   ---+----------+----------+---------
   1  | Laptop   | 55000.0  | 10
   2  | Mouse    | 750.5    | 100
   3  | Keyboard | 1200.0   | 45
   4  | Monitor  | 9500.0   | 20
```

### Three things to understand about this table

| | |
|---|---|
| 🔑 **Why `id` is the primary key** | It guarantees uniqueness, so `WHERE id = 3` can only ever match **one row**. That's what makes update and delete **precise** instead of accidentally hitting many rows. |
| 💾 **Why we seed sample rows** | So **view** has something to show, and **update**/**delete** have something to work on. Otherwise your first test tells you nothing. |
| 📄 **Save the scrapbook** | Save it as `product-setup.sql`. When you break your data — and you will, while testing delete — you can re-seed in seconds. |

### ⚠️ Two Derby quirks that confuse people

**1. Derby folds unquoted names to UPPERCASE.**

```text
   You write:    CREATE TABLE product
   Explorer shows:            PRODUCT
```

It's the **same table**. Your SQL can still say `product`. Don't "fix" it.

**2. SQL strings use SINGLE quotes.**

```sql
INSERT INTO product VALUES (1, 'Laptop', 55000.00, 10);   -- ✅ single quotes
INSERT INTO product VALUES (1, "Laptop", 55000.00, 10);   -- ❌ error
```

In SQL, **double quotes mean *identifier*** (a column or table name). So `"Laptop"` would be read
as a column name and fail. This is different from Java, and it trips people up constantly.

> 🎓 **Teaching tip**
> Insist on **one statement at a time** with `Ctrl+Alt+X`. Beginners select everything, press
> the wrong shortcut, and get a confusing partial failure.
> Also insist on the final `SELECT * FROM product` — **verify, don't assume.** Building the whole
> Java stack on top of an empty table is a miserable way to spend forty minutes, and it happens
> every single time someone skips this check.

> ✅ **Check yourself**
> **Q13.1** Why does the explorer show `PRODUCT` when you created `product`?
> **Q13.2** Why does `"Laptop"` fail in SQL but `'Laptop'` work?

---

## 14. Two traps that cost an hour

These are not exotic edge cases. They hit almost everyone, and **both produce symptoms that point
in completely the wrong direction.**

---

### 🔴 Trap 1 — The Derby JAR must go in TWO places

You added `derby.jar` to the **driver definition** in chapter 12, and the connection worked. So
why does your servlet fail?

**Because those were two different programs.**

```text
   ┌───────────────────────────────────┐      ┌───────────────────────────────────┐
   │  JAR in the DRIVER DEFINITION     │      │  JAR in WEB-INF/lib/              │
   ├───────────────────────────────────┤      ├───────────────────────────────────┤
   │  Used by ECLIPSE ITSELF           │      │  Used by YOUR APP on TOMCAT       │
   │                                   │      │                                   │
   │  • Data Source Explorer           │      │  • DriverManager.getConnection()  │
   │  • SQL Scrapbook                  │      │  • packaged into the .war         │
   │                                   │      │                                   │
   │  An IDE convenience.              │      │  MANDATORY for real JDBC calls.   │
   │  ❌ Your app CANNOT see it.        │      │  ✅ This is the one that matters. │
   └───────────────────────────────────┘      └───────────────────────────────────┘

              Tomcat runs your code in a SEPARATE JVM
              with its own classpath. Two worlds.
```

**Where it goes:**

```text
WebContent/WEB-INF/lib/derby.jar      ← copy the SAME file here too
```

**The symptom — learn to recognise it instantly:**

> The explorer shows your 4 rows perfectly, but the page returns **500** and the console says:
>
> ```
> java.sql.SQLException: No suitable driver found for jdbc:derby:...
> ```

> **Whenever you see "No suitable driver", this is the answer.** The JAR isn't in `WEB-INF/lib`.

---

### 🔴 Trap 2 — Use an ABSOLUTE database path

A relative URL like `jdbc:derby:productdb` creates the database in the JVM's **current working
directory** — and **Eclipse's working directory is not Tomcat's.**

```text
   Eclipse's Data Source Explorer          Tomcat
   working dir: C:/eclipse-workspace       working dir: C:/tomcat/bin
            │                                       │
            ▼                                       ▼
   C:/eclipse-workspace/productdb          C:/tomcat/bin/productdb
        ┌──────────────┐                       ┌──────────────┐
        │  4 products  │                       │    EMPTY     │  ← created silently
        └──────────────┘                       └──────────────┘
              ▲                                       ▲
        what YOU see                          what your SERVLET sees
```

**The symptom:** the explorer shows your 4 rows, but the servlet reports **"No products found"** —
because it silently created a **second, empty database** somewhere else.

**The fix:**

```java
// ❌ relative — TWO different databases
"jdbc:derby:productdb;create=true"

// ✅ absolute — ONE shared database
"jdbc:derby:C:/derbydb/productdb;create=true"              // Windows
"jdbc:derby:/home/yourname/derbydb/productdb;create=true"  // macOS / Linux
```

Two extra rules:
- **Use forward slashes even on Windows.** Backslashes in a Java string need escaping (`\\`) and
  cause needless errors.
- Use the **same absolute URL** in the Data Source Explorer *and* in `DBHelper`.

---

### 🟡 Bonus trap — embedded Derby allows only ONE program at a time

Embedded Derby loads **inside** whichever JVM opens it, and takes an **exclusive lock**.

So if the Data Source Explorer is **connected** when Tomcat starts:

```text
ERROR XSDB6: Another instance of Derby may have already booted
the database C:\derbydb\productdb.
```

**The fix:** right-click the connection → **Disconnect** before running the app. Reconnect when
you want to inspect rows, then disconnect again.

**Tired of the dance?** Two clean options:

| Option | URL |
|---|---|
| **H2 with `AUTO_SERVER`** — simultaneous access just works | `jdbc:h2:~/productdb;AUTO_SERVER=TRUE` |
| **Derby Network Server** — a separate server process | `jdbc:derby://localhost:1527/productdb;create=true` |

> 🎓 **Teaching tip**
> **Teach these three traps BEFORE the lab, not during it.** If you cover them upfront, people
> recognise the symptom and fix it themselves in thirty seconds. If you don't, you personally
> debug the same problem at fifteen desks.
> Write the three symptoms on the board and leave them there all session:
> ```
>   "No suitable driver"        → JAR not in WEB-INF/lib
>   "No products found"          → relative path, two databases
>   "already booted"            → disconnect the explorer
> ```
> This board is the highest-value square metre in the room during Part 2.

> ✅ **Check yourself**
> **Q14.1** The explorer shows 4 rows but your servlet says "No products found." What's wrong?
> **Q14.2** You get "No suitable driver found". What's missing?
> **Q14.3** Why does `XSDB6 already booted` happen?

---

## 15. Why `WEB-INF/lib` is special

It's worth understanding **why** that folder is magic, because it explains several other things
about web apps at the same time.

### The rule from the servlet specification

> A web application's **classloader automatically picks up every JAR in `WEB-INF/lib/`**.

Drop the file in that folder and it's on your classpath. **No build-path configuration needed.**
That's the entire mechanism.

```text
   WebContent/
   └── WEB-INF/
       ├── web.xml
       ├── classes/          ← your compiled .class files (auto)
       └── lib/              ← EVERY .jar here is on the classpath (auto)
           └── derby.jar
```

### And this is also why `WEB-INF` is browser-inaccessible

The **same specification** forbids serving *anything* under `WEB-INF` to a client. Think about
what's in there:

| File | Why a visitor must never download it |
|---|---|
| `web.xml` | Reveals your servlet classes and URL structure |
| `classes/` | Your compiled code — decompilable |
| `lib/*.jar` | Your dependencies, including their versions (and known vulnerabilities) |

> **The folder is protected by design, not by accident.**

### The practical consequence

This is why you place files where you do:

| File | Where it goes | Why |
|---|---|---|
| `derby.jar` | `WEB-INF/lib/` | App needs it; nobody should download it |
| `product.html` | `WebContent/` | The browser **must** fetch it |
| A CSS file | `WebContent/` | The browser must fetch it |
| A JSP you want protected | `WEB-INF/` | Only reachable via a servlet forward |

> 🎓 **Teaching tip**
> Do the live demo from Part 1 again if you have time — browse to
> `http://localhost:8080/ServletBasics/WEB-INF/web.xml` and get a 404. It takes ten seconds and
> it makes an abstract spec rule concrete.
> The "why a visitor must never download it" table is worth reading aloud; framing it as
> **security** rather than convention makes people respect the folder instead of fighting it.

> ✅ **Check yourself**
> **Q15.1** Why don't you need to configure the build path for a JAR in `WEB-INF/lib`?
> **Q15.2** Why is `WEB-INF` unreachable from the browser?

---
---

# Part D — The CRUD patterns

## 16. One servlet, four actions

CRUD is four operations. You have two design choices:

```text
   OPTION A: four servlets            OPTION B: one servlet + an action parameter
   ┌──────────────────────┐           ┌────────────────────────────────────────┐
   │ ViewServlet   /view  │           │ ProductServlet   /product              │
   │ InsertServlet /insert│           │                                        │
   │ UpdateServlet /update│           │   ?action=view                         │
   │ DeleteServlet /delete│           │   ?action=insert                       │
   └──────────────────────┘           │   ?action=update                       │
                                      │   ?action=delete                       │
                                      └────────────────────────────────────────┘
```

We use **Option B**, because it keeps all product handling in one readable place.

### The routing code

```java
String action = request.getParameter("action");

// Treat "no action given" as a sensible default instead of crashing.
if (action == null) {
    action = "view";
}

if (action.equals("view")) {
    // nothing to do — the table is printed below for EVERY action

} else if (action.equals("insert")) {
    handleInsert(request, out);                // CREATE

} else if (action.equals("update")) {
    handleUpdate(request, out);                // UPDATE

} else if (action.equals("delete")) {
    handleDelete(request, out);                // DELETE

} else {
    out.println("<h3><font color='red'>Unknown action: " + action + "</font></h3>");
}

displayAllProducts(out);                       // READ — runs for ALL of them
```

### Why the `action == null` default matters

```text
   Someone visits  /product   with no parameters
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   WITHOUT the default        WITH the default
          │                         │
   action.equals(...)         action = "view"
          │                         │
   💥 NullPointerException    ✅ shows the table
       → 500 page                  → a useful page
```

**Defaulting instead of crashing** is a small habit that makes an app feel finished.

### The trade-off, honestly

| Approach | Pros | Cons |
|---|---|---|
| **One servlet + `action`** | One mapping, one file, shared helper methods, all behaviour visible at once | Grows long; the `if`-ladder can sprawl as features are added |
| **Four servlets** | Each class is tiny and single-purpose | Four mappings to maintain; shared code needs a common parent or utility class |

Neither is wrong. For four operations on one table, one servlet is clearly simpler.

### 🌟 Where this pattern leads

That `if`-ladder is a hand-written **front controller** — and it's exactly what Spring MVC's
`DispatcherServlet` does industrially.

```text
   YOUR CODE (today)                    SPRING MVC (later)
   ─────────────────────────            ──────────────────────────────
   if (action.equals("view"))     ≈     @GetMapping("/products")
   else if (action.equals("insert")) ≈  @PostMapping("/products")
   else if (action.equals("update")) ≈  @PutMapping("/products/{id}")
   else if (action.equals("delete")) ≈  @DeleteMapping("/products/{id}")

   ...you wrote the ladder by hand.
   Spring's DispatcherServlet is a far more sophisticated version
   of exactly the same idea.
```

> **Write it by hand once and annotations stop being mysterious.**

> 🎓 **Teaching tip**
> The `DispatcherServlet` connection is the payoff of the whole session — **don't leave it to the
> last slide.** Mention it here, while the `if`-ladder is on screen, so the parallel is visible
> rather than abstract.
> If anyone objects that the ladder is ugly: agree, and point out that this is precisely why
> frameworks exist. Then note that Spring's version handles URL patterns, HTTP methods, content
> negotiation and parameter binding — all things their ladder does *not* do. That's a good,
> honest picture of what a framework buys you.

> ✅ **Check yourself**
> **Q16.1** Why default `action` to `"view"` instead of letting it be null?
> **Q16.2** What's the Spring MVC equivalent of the action if-ladder?

---

## 17. Links vs forms

Both put parameters in a request. Which you choose depends on **one question: does the user need
to type anything?**

### 🔗 A link — nothing to type

```html
<a href="product?action=view">View all products</a>

<!-- delete row 3: two parameters -->
<a href="product?action=delete&amp;p=3">Delete</a>
```

- Always a **GET**
- Parameters sit in the **query string**
- Perfect when the values are **already known** — like the row's own id

### 📝 A form — the user types

```html
<form action="product" method="post">
    <input type="hidden" name="action" value="insert" />

    <input type="text" name="id" />
    <input type="text" name="name" />
    <input type="text" name="price" />
    <input type="text" name="quantity" />

    <input type="submit" value="Add" />
</form>
```

- GET or POST, your choice
- Necessary when values come **from the user**
- The **hidden field** carries the action invisibly

### The hidden field vs Part 1's submit-button trick

| Part 1 | Part 2 |
|---|---|
| `<input type="submit" name="action" value="login" />` | `<input type="hidden" name="action" value="insert" />` |
| The action **is** the button's visible label | The action is **independent** of the label |

> The hidden field is clearer: you can change the button text from "Add" to "Save product"
> without breaking the servlet. **Deliberately shown both ways so you've seen each.**

### The per-row Delete link — how it's built

This is the fiddliest string in the lab, so let's dissect it:

```java
out.println("<td><a href='product?action=delete&p=" + p.getId() + "'>Delete</a></td>");
```

```text
   "<td><a href='product?action=delete&p=" + p.getId() + "'>Delete</a></td>"
        ─       ─                                        ─            ─
        │       │                                        │            │
   DOUBLE quotes for the Java string ────────────────────┴────────────┘
        SINGLE quotes for the HTML attribute — no escaping needed
```

| Point | Detail |
|---|---|
| **Quote strategy** | Java string uses `"`, so the HTML attribute uses `'`. **Mixing these up is the usual cause of a broken link.** |
| **Two parameters** | Fixed `action=delete`, plus `p=` and *this row's* id, joined by `&` |
| **Each row differs** | Row 3 renders `product?action=delete&p=3`; row 4 renders `...p=4` |
| **The name is `p`, not `id`** | So `handleDelete` reads `getParameter("p")`. **Mismatch these and you get a silent `null`, then `NumberFormatException`.** |

The result — each row's link already knows which record it refers to, so **the user types nothing**:

```text
   ┌────┬──────────┬─────────┬──────────┬──────────────────────────────────┐
   │ ID │ Name     │ Price   │ Quantity │ Action                           │
   ├────┼──────────┼─────────┼──────────┼──────────────────────────────────┤
   │ 1  │ Laptop   │ 55000.0 │ 10       │ Delete → ?action=delete&p=1      │
   │ 2  │ Mouse    │ 750.5   │ 100      │ Delete → ?action=delete&p=2      │
   │ 3  │ Keyboard │ 1200.0  │ 45       │ Delete → ?action=delete&p=3      │
   └────┴──────────┴─────────┴──────────┴──────────────────────────────────┘
```

### ⚠️ Two honest caveats about that delete link

**1. In HTML, the correct separator is `&amp;`, not a bare `&`.**

Browsers forgive the bare version, so it usually works. But `&amp;` is valid HTML and won't
surprise you when a parameter name happens to collide with an entity name.

**2. It's a GET that changes data — which breaks GET's idempotency rule.**

```text
   Remember from Part 1:  GET should be IDEMPOTENT (safe to repeat)
   But our delete link:   is a GET, and it DELETES

   ⚠️  A search-engine crawler or a browser pre-fetcher following that
       link would SILENTLY DELETE YOUR DATA.
```

It's the pragmatic classic approach and fine for learning. **Real applications use a POST form
(or a `DELETE` request) with a confirmation for destructive actions.**

There's a second issue too: the parameters are **visible and editable**. You can change `p=5` to
`p=1` in the address bar and delete a different row without touching the UI. That's a preview of
why real apps check permissions **on the server**, never trusting the URL.

### The rule

> **Nothing to type → link (GET). Something to type → form (POST for writes).**

Which lines up exactly with Part 1's **GET-to-read / POST-to-write** rule. The design isn't
arbitrary; it follows from HTTP's own semantics.

> 🎓 **Teaching tip**
> Have everyone **hover over a Delete link and read the status bar** — seeing `?action=delete&p=3`
> makes the generated-per-row concept click instantly.
> Then have them **edit `p=` in the address bar** to delete a different row. It's a genuine
> lightbulb moment about client-side trust, and it naturally raises "so how do real apps stop
> that?" — a perfect hook for the sessions/security discussion in chapter 21.
> Don't skip the idempotency caveat. Teaching the pragmatic version *and* naming why it's not
> production-correct is what separates training from cargo-culting.

> ✅ **Check yourself**
> **Q17.1** Why does the delete link use single quotes inside the Java string?
> **Q17.2** The link sends `p=3`. What must `handleDelete` call?
> **Q17.3** What's the risk of deleting via a GET link?

---

## 18. The boolean-return pattern

Your DAO ran an `UPDATE`. **Did it change anything?** Maybe the id didn't exist.

The servlet needs to know, so it can show the right message. That's why **every write method
returns a `boolean`**.

### The DAO turns "rows affected" into a yes/no

```java
public boolean updateProduct(int id, double price) {
    // ... prepare and bind ...
    int rows = ps.executeUpdate();
    return rows > 0;        // 0 rows matched -> false.  1+ -> true.
}
```

### The servlet branches on it

```java
if (service.updateProduct(id, price)) {
    out.println("<h3><font color='green'>Product updated successfully.</font></h3>");
} else {
    out.println("<h3><font color='red'>Updation failed — no product with id " + id + ".</font></h3>");
}
```

### Why this matters — the case it catches

```text
   UPDATE product SET price = 999 WHERE id = 777
                                          ───
                                     (doesn't exist)

   Result:  SQL ran perfectly. No exception. 0 rows changed.

   ┌─────────────────────────────────────────────────────────────┐
   │  WITHOUT the check:  "Product updated successfully!"  ← LIE │
   │  WITH the check:     "Updation failed — no id 777"   ← TRUE │
   └─────────────────────────────────────────────────────────────┘
```

> **"Ran fine but matched nothing"** and **"found it and changed it"** are completely different
> outcomes — and without `rows > 0` they look identical.

### What each layer contributes

| Layer | Its job in this pattern |
|---|---|
| **DAO** | Reports a **fact**: `rows > 0` |
| **Servlet** | Decides the **wording and the colour** |

Presentation stays out of the data layer. The DAO doesn't know what green means.

### 🌟 Watch this in the lab — the clearest proof of the layers

Same message, **two completely different code paths**:

| You submit | Page says | Console says | Who rejected it |
|---|---|---|---|
| **Duplicate id** | 🔴 Insertion failed | `Insert failed [23505]: duplicate key...` | **The DAO** — a real database error |
| **Negative price** | 🔴 Insertion failed | *(silence)* | **The service** — before any SQL ran |

> **Look for the silence.** That's the service layer doing its job. The database was never
> contacted.

### The honest limitation

`false` says **that** it failed, never **why**. "Id not found", "duplicate key" and "database
down" all come back as `false`.

That's acceptable while learning, and it's why the DAO **logs** the real `SQLException` — the
detail isn't lost, just not surfaced to the user.

> The proper fix is **custom exceptions** carrying a reason. That's exactly what you'll build
> with `@ControllerAdvice` in the Spring Boot sessions.

> 🎓 **Teaching tip**
> The `WHERE id = 777` example is the one that convinces people. Ask first: *"the SQL runs, no
> exception is thrown, zero rows change. What should the user see?"* Let them realise that
> "success" would be a lie.
> Then run the two-failure demo and **make them look at the console**, not the page. The silence
> is the lesson. This single demo justifies both the boolean pattern and the service layer at
> once — it's the best five minutes in Part 2.

> ✅ **Check yourself**
> **Q18.1** `UPDATE ... WHERE id = 777` on a missing id — does it throw? What does it return?
> **Q18.2** What's the limitation of returning a `boolean`?

---

## 19. Killing duplicated code (DRY)

After every operation you want to show the updated table. Write that loop four times and you have
four copies to fix when the design changes.

### ❌ Before — the same 15 lines, four times

```java
if (action.equals("view")) {
    // 15 lines of table loop
} else if (action.equals("insert")) {
    // ... insert ...
    // the SAME 15 lines again
} else if (action.equals("update")) {
    // ... update ...
    // the SAME 15 lines again
} else if (action.equals("delete")) {
    // ... delete ...
    // the SAME 15 lines AGAIN
}
```

**60 lines. One design change = four edits — and you'll forget one.**

### ✅ After — one method, called once

```java
if (action.equals("view")) {
    // nothing
} else if (action.equals("insert")) {
    handleInsert(request, out);
} else if (action.equals("update")) {
    handleUpdate(request, out);
} else if (action.equals("delete")) {
    handleDelete(request, out);
}

// runs for EVERY action — written ONCE
displayAllProducts(out);
```

**15 lines, in one place. One design change = one edit.**

### Count the payoff

| | Duplicated in 4 branches | Extracted once |
|---|---|---|
| Lines of table-building code | ~60 | **~15** |
| Edits to add one column | 4 (and you'd miss one) | **1** |
| Places a bug in the loop can hide | 4 | **1** |

### A nice side effect: better UX

```text
   BEFORE: insert → "Product added successfully."
                    ...and you have to navigate back to check it worked

   AFTER:  insert → "Product added successfully."
                    ┌────┬──────────┬─────────┬──────────┬────────┐
                    │ ID │ Name     │ Price   │ Quantity │ Action │
                    ├────┼──────────┼─────────┼──────────┼────────┤
                    │ 1  │ Laptop   │ 55000.0 │ 10       │ Delete │
                    │ 5  │ Webcam   │ 2500.0  │ 15       │ Delete │  ← there it is!
                    └────┴──────────┴─────────┴──────────┴────────┘
```

**Message plus fresh table, for every action.** You can see the result of what you did without
navigating anywhere.

### DRY — Don't Repeat Yourself

> **The trigger to watch for: the moment you'd copy-paste code for the *second* time, extract it
> into a method instead.**

Not before — premature abstraction is its own problem. But definitely then.

> In the lab we deliberately write the duplication first and then refactor, **because feeling
> the pain is what makes the lesson stick.**

### ⚠️ Signature note — the threading rule, again

```java
private void displayAllProducts(PrintWriter out) {     // ✅ parameter
```

**Pass the writer in as a parameter**, don't store it in a field. An instance field would be
shared across all users' threads (Part 1, ch. 15). A parameter is per-call and therefore safe.

> 🎓 **Teaching tip**
> **Resist the urge to give them the refactored version first.** Let them write the duplication in
> Lab 7, feel the "ugh, do I copy that again?" moment in Lab 8, and then refactor in Lab 9. The
> emotional beat is the teaching mechanism — a lecture on DRY teaches nothing by comparison.
> The 60-second "add a Total column" exercise afterwards is the proof: one edit, appears
> everywhere. Do it live.

> ✅ **Check yourself**
> **Q19.1** When should you extract duplicated code into a method?
> **Q19.2** Why is `out` a parameter of `displayAllProducts` rather than a field?

---

## 20. The complete ProductServlet

Everything from Part D, assembled. This is the final file from Lab 9.

```java
package com.tcs.web;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

// On Tomcat 10+ change these four to jakarta.servlet.*
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.tcs.bean.Product;
import com.tcs.service.ProductService;

/**
 * One servlet, four actions — a hand-written "front controller".
 * Spring MVC's DispatcherServlet is an industrial version of this.
 */
public class ProductServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;

    // Stateless helper: safe to share across all request threads.
    private ProductService service = new ProductService();

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/html");
        PrintWriter out = response.getWriter();

        String action = request.getParameter("action");
        if (action == null) {
            action = "view";                     // sensible default
        }

        out.println("<html><body>");
        out.println("<h2>Product Manager</h2>");

        // ===== ROUTING: pick the operation, print only its MESSAGE =====
        if (action.equals("view")) {
            // nothing to do — the table below is the whole point of "view"

        } else if (action.equals("insert")) {
            handleInsert(request, out);

        } else if (action.equals("update")) {
            handleUpdate(request, out);

        } else if (action.equals("delete")) {
            handleDelete(request, out);

        } else {
            out.println("<h3><font color='red'>Unknown action: " + action + "</font></h3>");
        }

        // ===== THE REFACTOR: written once, runs for EVERY action, so the
        // user always sees the up-to-date table right below the message. =====
        displayAllProducts(out);

        out.println("<p><a href='product.html'>&laquo; Back to the form</a></p>");
        out.println("</body></html>");
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }

    // ---------- CREATE ----------
    private void handleInsert(HttpServletRequest request, PrintWriter out) {
        try {
            int    id       = Integer.parseInt(request.getParameter("id"));
            String name     = request.getParameter("name");
            double price    = Double.parseDouble(request.getParameter("price"));
            int    quantity = Integer.parseInt(request.getParameter("quantity"));

            Product p = new Product(id, name, price, quantity);

            if (service.addProduct(p)) {
                out.println("<h3><font color='green'>Product added successfully.</font></h3>");
            } else {
                out.println("<h3><font color='red'>Insertion failed — is the id already used, "
                          + "or a value invalid?</font></h3>");
            }
        } catch (NumberFormatException e) {
            out.println("<h3><font color='red'>ID, price and quantity must be numbers.</font></h3>");
        }
    }

    // ---------- UPDATE ----------
    private void handleUpdate(HttpServletRequest request, PrintWriter out) {
        try {
            int    id    = Integer.parseInt(request.getParameter("id"));
            double price = Double.parseDouble(request.getParameter("price"));

            if (service.updateProduct(id, price)) {
                out.println("<h3><font color='green'>Product updated successfully.</font></h3>");
            } else {
                out.println("<h3><font color='red'>Updation failed — no product with id "
                          + id + ".</font></h3>");
            }
        } catch (NumberFormatException e) {
            out.println("<h3><font color='red'>ID and price must be numbers.</font></h3>");
        }
    }

    // ---------- DELETE ----------
    private void handleDelete(HttpServletRequest request, PrintWriter out) {
        try {
            // the delete link sends ?action=delete&p=<id>
            int id = Integer.parseInt(request.getParameter("p"));

            if (service.deleteProduct(id)) {
                out.println("<h3><font color='green'>Product " + id + " deleted.</font></h3>");
            } else {
                out.println("<h3><font color='red'>Deletion failed — no product with id "
                          + id + ".</font></h3>");
            }
        } catch (NumberFormatException e) {
            out.println("<h3><font color='red'>Invalid product id in the delete link.</font></h3>");
        }
    }

    // ---------- THE EXTRACTED METHOD: written ONCE, used by all four ----------
    // 'out' is a PARAMETER, not a field — one servlet instance, many threads.
    private void displayAllProducts(PrintWriter out) {

        List<Product> list = service.getAllProducts();

        if (list.isEmpty()) {
            out.println("<h3>No products found.</h3>");
            return;                              // nothing to tabulate
        }

        out.println("<table border='1' cellpadding='6'>");
        out.println("<tr><th>ID</th><th>Name</th><th>Price</th>"
                  + "<th>Quantity</th><th>Action</th></tr>");

        for (Product p : list) {
            out.println("<tr>");
            out.println("<td>" + p.getId()       + "</td>");
            out.println("<td>" + p.getName()     + "</td>");
            out.println("<td>" + p.getPrice()    + "</td>");
            out.println("<td>" + p.getQuantity() + "</td>");
            out.println("<td><a href='product?action=delete&p="
                      + p.getId() + "'>Delete</a></td>");
            out.println("</tr>");
        }

        out.println("</table>");
    }
}
```

### The structure at a glance

```text
   doGet()
     ├── setContentType, getWriter
     ├── read + default the action
     ├── ROUTE ──┬── view    → (nothing)
     │           ├── insert  → handleInsert()
     │           ├── update  → handleUpdate()
     │           ├── delete  → handleDelete()
     │           └── else    → "Unknown action"
     └── displayAllProducts()        ← ALWAYS runs

   doPost() → doGet()                 ← so POST forms work

   handleInsert / handleUpdate / handleDelete
     └── parse → delegate to service → report

   displayAllProducts
     └── service.getAllProducts() → build the HTML table
```

### Every failure is handled

| Input | Result |
|---|---|
| valid insert | 🟢 Product added successfully |
| duplicate id | 🔴 Insertion failed *(DAO logged 23505)* |
| negative price | 🔴 Insertion failed *(service blocked it, console silent)* |
| `quantity=ten` | 🔴 must be numbers *(not a 500)* |
| `update id=777` | 🔴 Updation failed — no product with id 777 |
| `delete p=abc` | 🔴 Invalid product id *(not a 500)* |
| no action at all | 🟢 shows the table *(defaulted to view)* |
| `action=banana` | 🔴 Unknown action: banana *(plus the table)* |

> **No input produces a stack trace.** That's the standard to hold yourself to.

> 🎓 **Teaching tip**
> **Do not paste this whole file at once.** The lab builds it in three increments (view → insert →
> update/delete) then refactors, and that progression is deliberate.
> Use this chapter as the **reference** — for people who fell behind, and for your own
> preparation. When teaching, show the "structure at a glance" tree rather than the full listing;
> it's much easier to hold in your head.

> ✅ **Check yourself**
> **Q20.1** Which method runs for every action, and why is that useful?
> **Q20.2** Why does `handleDelete` read `"p"` while `handleUpdate` reads `"id"`?


---
---

# Part E — Honest limitations & what's next

## 21. The gap: nothing is protected

At the end of the lab, try this experiment.

```text
   STEP 1:  Log in successfully at /ServletBasics/
            → "Login successful. Welcome!"

   STEP 2:  Go to /ServletBasics/product?action=view
            → the product manager works ✅   (fair enough, you logged in)

   STEP 3:  Open a BRAND NEW private/incognito window.
            Skip the login entirely.
            Go straight to /ServletBasics/product?action=view

            → IT STILL WORKS. ❌
```

You can view, insert, update and delete **without ever logging in.**

### Why? Because HTTP is stateless — and we did nothing about it

```text
   Request 1:  login   ──▶  "You're valid!"  ...and Tomcat immediately forgets you

   Request 2:  /product ──▶  ProductServlet has NO IDEA who you are.
                             It never asks. It just does the work.
```

Our `ProductServlet` **never checks** whether the caller authenticated. Every CRUD operation is
wide open to anyone who knows the URL.

### The fix — sessions

This is the machinery hinted at by that `Set-Cookie: JSESSIONID=...` header in Part 1:

```java
// ===== In LoginServlet, AFTER credentials check out =====
HttpSession session = request.getSession();
session.setAttribute("user", id);              // remember them, server-side

// ===== At the top of EVERY protected servlet =====
HttpSession session = request.getSession(false);   // false = don't create a new one
if (session == null || session.getAttribute("user") == null) {
    response.sendRedirect("index.html");           // 302 — go log in
    return;                                        // and STOP processing
}
// ... only authenticated users reach this line ...
```

### How sessions work, briefly

```text
   1. Login succeeds
      Server: creates a session object, gives it an ID: A1B2C3
              stores user=123 inside it
              sends  Set-Cookie: JSESSIONID=A1B2C3

   2. Browser stores that cookie automatically

   3. Every later request
      Browser sends:  Cookie: JSESSIONID=A1B2C3
      Server:         "A1B2C3? → that's the session holding user=123"

   ┌──────────────┐                          ┌─────────────────────────┐
   │   BROWSER    │  JSESSIONID=A1B2C3       │        SERVER           │
   │              │ ───────────────────────▶ │  sessions:              │
   │  holds only  │                          │    A1B2C3 → {user:123}  │
   │  the ID      │                          │    D4E5F6 → {user:456}  │
   └──────────────┘                          └─────────────────────────┘
      the ID is the ticket           the actual data stays server-side
```

### Why we're leaving it out today — deliberately

Adding sessions now would mean teaching cookies, session scope, timeouts, redirects and logout —
**on top of** five new layers and a database. That is too much at once.

> **Seeing the hole is the lesson for today.** Filling it is the natural first topic of whatever
> comes next.

**Recognising that your app is insecure is genuinely more valuable than being handed code that
hides the problem.** A developer who knows what's missing can go and learn it. A developer who
thinks their app is secure cannot.

### While we're being honest — three other things this app doesn't do

| Missing | What production would do |
|---|---|
| **Password hashing** | We compare a plain-text constant. Real apps store a **bcrypt/Argon2 hash** and never the password itself. |
| **HTML escaping** | We print user input straight into HTML. A product named `<script>alert(1)</script>` would **execute** — that's **XSS**. Real apps escape output. |
| **Connection pooling** | We open and close a connection per operation. Production uses a **pool** (HikariCP) — opening connections is expensive. |

> None of these are things you did wrong. They're the next things to learn, and it's worth knowing
> they exist so you don't mistake a teaching app for a finished one.

> 🎓 **Teaching tip**
> **Do the incognito-window demo live.** It's genuinely startling — people have just spent two
> hours building this and assume the login "protects" it. The moment they see the CRUD app open
> without logging in, the need for sessions becomes obvious and they'll actually want the next
> session.
> The XSS one is a great optional extra if you have five minutes: insert a product named
> `<b>BOLD</b>` and watch the table render actual bold text. Then let them work out what
> `<script>` would do. It's a memorable introduction to output escaping.

> ✅ **Check yourself**
> **Q21.1** Why can someone use the product manager without logging in?
> **Q21.2** What does `request.getSession(false)` do differently from `getSession()`?

---

## 22. Servlets → JSP → Spring MVC

Let's be honest: building HTML with `out.println()` is **unpleasant**. You should know that's not
a limitation of your skill — it's why the industry moved on.

Here's the real lineage:

| Technology | The idea | Why the next thing replaced it |
|---|---|---|
| **Servlet** *(today)* | Java code that writes HTML strings | HTML inside Java is painful to write, impossible for a designer to edit, and you can't see the page's shape |
| **JSP** | **Inverts it:** an HTML page with Java sprinkled in | Much better for layout — but tempting to bury business logic in the page, recreating the tangle |
| **Servlet + JSP (MVC-2)** | Servlet controls, JSP renders — a clean split | Correct architecture, but heaps of boilerplate: XML config, manual dispatching, manual binding |
| **Spring MVC / Boot** *(next)* | `DispatcherServlet` + annotations + auto-configuration | The same architecture with the boilerplate deleted. **Still servlets underneath.** |

```text
   Servlet            JSP              MVC-2                Spring Boot
   ───────            ───              ─────                ───────────
   Java that     HTML with a       servlet decides,     annotations +
   prints HTML   little Java       JSP renders          auto-config

   out.println   <%= product %>    forward to .jsp      @GetMapping
     ("<b>")                                            + Thymeleaf

   ◀────────────────── all of these ARE servlets underneath ─────────────▶
```

### So why learn servlets at all?

**Because every one of those layers is still a servlet underneath.**

| Spring Boot thing | What it actually is |
|---|---|
| `DispatcherServlet` | **A servlet** |
| `@GetMapping("/products")` | A **URL mapping** |
| `@RequestParam int id` | `getParameter("id")` **+ automatic type conversion** |
| `ResponseEntity` | `HttpServletResponse` with a nicer API |
| Embedded Tomcat | **Tomcat**, started from your `main` |

> **You learned the machine. Now you get the power tools — and you know what they're doing.**

### The direct translation table

Bookmark this for the Spring Boot sessions. Every single thing you built today has an equivalent:

| What you wrote today | Spring Boot equivalent |
|---|---|
| `extends HttpServlet` | `@Controller` / `@RestController` |
| `doGet` | `@GetMapping` |
| `doPost` | `@PostMapping` |
| `getParameter("id")` + `parseInt` | `@RequestParam int id` |
| the `action` if-ladder | `DispatcherServlet` (built in) |
| `web.xml` `<url-pattern>` | the annotation's path |
| `ProductServlet` | `@Controller` |
| `ProductService` | `@Service` |
| `ProductDao` | `@Repository` / `JpaRepository` |
| `Product` bean | `@Entity` |
| `DBHelper` | `application.properties` |
| manual validation in the service | `@Valid` + `@NotNull`, `@Min` |
| `boolean` returns | custom exceptions + `@ControllerAdvice` |
| `out.println("<table>")` | Thymeleaf / JSON serialisation |

### The thing to take away

```text
   You did NOT learn a legacy technology today.

   You learned the FOUNDATION that every Java web framework
   is built on — and you built the architecture (controller,
   service, repository, entity, datasource) by hand.

   When you meet @Service next month, you won't think
   "another annotation to memorise."

   You'll think "oh — that's the validation layer."
```

> 🎓 **Teaching tip**
> **End the session on this chapter, and end it positively.** Some people will be feeling that
> `out.println("<table>")` was tedious — validate that feeling, then reframe the whole session:
> *"you didn't learn an outdated tool, you learned what the modern tools are doing."*
> Put the **translation table on screen** and read a few rows aloud. It converts two hours of
> hard work into visible, transferable value — and it's the single best motivator for the Spring
> Boot sessions.

> ✅ **Check yourself**
> **Q22.1** What is `DispatcherServlet`?
> **Q22.2** Which annotation replaces `ProductService`? Which replaces `ProductDao`?

---
---

# Appendix A — Common mistakes and how to spot them

Part 1's list still applies. These are the **new** ones that come with databases and layers.

| # | Symptom you see | Cause | Fix |
|---|---|---|---|
| 1 | `No suitable driver found for jdbc:derby:...` | `derby.jar` missing from `WEB-INF/lib` | Copy it there. The driver-definition copy is invisible to your app |
| 2 | **"No products found"** but the explorer shows 4 rows | **Relative** Derby path → two different databases | Use an **absolute** path, identical in Eclipse and `DBHelper` |
| 3 | `XSDB6: Another instance may have already booted` | Data Source Explorer is still **connected** | Right-click the connection → **Disconnect** |
| 4 | `NullPointerException` → 500 page | Missing `if (con == null)` guard in a DAO method | Add the guard at the top of every DAO method |
| 5 | Wrong row updated, or nothing updates | `?` binding order wrong | `SET price = ? WHERE id = ?` → `setDouble(1, price)`, `setInt(2, id)`. **1-based!** |
| 6 | SELECT returns 0, or INSERT throws | `executeQuery` / `executeUpdate` swapped | SELECT → `executeQuery`. INSERT/UPDATE/DELETE → `executeUpdate` |
| 7 | Delete always says "Invalid product id" | Link sends `p=3`, servlet reads `getParameter("id")` | Read `"p"` — match the link |
| 8 | Delete link is broken / renders oddly | Quote confusion in the generated HTML | Java string uses `"`, HTML attribute uses `'` |
| 9 | Page says failed, console is empty | **Nothing is wrong** — the **service** rejected it before SQL | This is correct behaviour. Check your validation rules |

## The five-minute triage list

```text
   ┌──────────────────────────────────────────────────────────────────────┐
   │                                                                      │
   │  404?                        → URL / <url-pattern>; restart Tomcat   │
   │  500?                        → console, FIRST line of the trace      │
   │  "No suitable driver"        → JAR not in WEB-INF/lib                │
   │  "No products found"         → relative Derby path (two databases)   │
   │  "already booted"            → disconnect the Data Source Explorer   │
   │  NullPointerException        → missing if (con == null) guard        │
   │  page fails, console silent  → the SERVICE blocked it (correct!)     │
   │                                                                      │
   └──────────────────────────────────────────────────────────────────────┘
```

---

# Appendix B — Glossary

| Term | Meaning |
|---|---|
| **MVC** | Model–View–Controller. Splits code by responsibility. |
| **Model** | The data and the code that stores/fetches it. Knows nothing about the web. |
| **View** | What the user sees. Our generated HTML. |
| **Controller** | Receives the request, decides what happens, calls the model. Our servlet. |
| **Layer** | A group of classes with one responsibility. Talks only to the layer below. |
| **POJO** | Plain Old Java Object — a simple data class. Private fields, getters/setters. |
| **Bean** | Another name for a POJO, following the JavaBeans naming convention. |
| **JavaBeans convention** | `getX()` / `setX()` naming. Tooling depends on it to discover properties. |
| **Encapsulation** | Hiding fields behind accessors so rules can be enforced in one place. |
| **DAO** | Data Access Object. The only class containing SQL. |
| **Service layer** | Where business rules and validation live. |
| **Helper** | Our connection-management class. Holds the JDBC URL. |
| **CRUD** | Create, Read, Update, Delete — the four basic data operations. |
| **`PreparedStatement`** | Parameterised SQL with `?` placeholders. Safe from injection, and faster. |
| **SQL injection** | An attack where user input becomes SQL syntax. Prevented by `?` binding. |
| **`ResultSet`** | A cursor over the rows a SELECT returned. Iterate with `rs.next()`. |
| **`executeQuery`** | Runs a SELECT. Returns a `ResultSet`. |
| **`executeUpdate`** | Runs INSERT/UPDATE/DELETE. Returns the **number of rows affected**. |
| **Rows affected** | How many rows a statement changed. `0` means "matched nothing". |
| **Boolean-return pattern** | Write methods return `rows > 0` so callers can branch on success. |
| **Front controller** | One component that receives all requests and routes them. Our `action` ladder; Spring's `DispatcherServlet`. |
| **DRY** | Don't Repeat Yourself. Extract duplicated code into one method. |
| **`WEB-INF/lib`** | Folder whose JARs are automatically on the web app's classpath. |
| **Data Source Explorer** | Eclipse view for connecting to and browsing a database. |
| **Driver definition** | Eclipse's record of which JAR provides a JDBC driver. |
| **SQL Scrapbook** | Eclipse editor for running ad-hoc SQL against a connection. |
| **Embedded database** | A database running *inside* your JVM. Derby embedded allows only one JVM at a time. |
| **SQLState** | A standard 5-character error code on `SQLException`. `23505` = duplicate key. |
| **Session** | Server-side memory of a user across requests. *(Not implemented in this app.)* |
| **`JSESSIONID`** | The cookie Tomcat uses to identify a session. |
| **XSS** | Cross-Site Scripting — injecting HTML/JS via unescaped user input. |
| **Connection pool** | A reusable set of open connections. Production alternative to open/close per call. |

---

# Appendix C — Cheat sheet

## The five layers

| Package | Class | Holds | Never holds |
|---|---|---|---|
| `web` | `ProductServlet` | Parameters in, HTML out | SQL |
| `service` | `ProductService` | Validation, business rules | HTML or SQL |
| `dao` | `ProductDao` | All the SQL | HTML |
| `bean` | `Product` | Data only | Any logic |
| `helper` | `DBHelper` | The connection + URL | SQL |

**Golden rule:** each layer talks only to the one below. **Never** pass an `HttpServletRequest`
or a `ResultSet` across a boundary.

## Build order (bottom-up)

```text
   bean  →  helper  →  dao  →  service  →  web
```

## JDBC calls used in the DAO

```java
DriverManager.getConnection(url, user, pass)   // open a session
con.prepareStatement(sql)                      // compile a parameterised statement
ps.setInt(1, v) / setString / setDouble        // bind a value — 1-BASED
ps.executeQuery()                              // SELECT → ResultSet
ps.executeUpdate()                             // INSERT/UPDATE/DELETE → row count
rs.next()                                      // advance cursor; false when rows run out
rs.getInt("id") / getString / getDouble        // read a column of the current row
con.close()                                    // release — in finally, ALWAYS
```

## The DAO method shape

```java
public boolean doSomething(...) {
    String sql = "... ? ...";                       // 1. parameterised
    Connection con = DBHelper.connect();
    if (con == null) return false;                  // 2. guard the null
    try (PreparedStatement ps = con.prepareStatement(sql)) {
        ps.setXxx(1, ...);                          // 3. bind, 1-based, in ? order
        return ps.executeUpdate() > 0;              // 4. rows → boolean
    } catch (SQLException e) {
        System.out.println("... [" + e.getSQLState() + "]: " + e.getMessage());
        return false;                               // 5. log the real reason
    } finally {
        DBHelper.close(con);                        // 6. always release
    }
}
```

## The CRUD routing table

| Action | Comes from | Method | Parameters read |
|---|---|---|---|
| `view` | a link | GET | none |
| `insert` | a form | POST | `id, name, price, quantity` |
| `update` | a form | POST | `id, price` |
| `delete` | a per-row link | GET | **`p`** ← *not `"id"`!* |

## Derby SQLState codes

| SQLState | Meaning |
|---|---|
| `23505` | Duplicate primary key — that id already exists |
| `42X05` | Table not found — did you run CREATE TABLE? |
| `42X14` | Column not found — typo in a column name |
| `XSDB6` | Database already booted — disconnect the explorer |
| `08001` | Cannot connect — check the URL and the JAR |

## Seven habits to keep

1. **Absolute** database path, forward slashes, same URL as the explorer.
2. Driver JAR in **`WEB-INF/lib`**, not just the driver definition.
3. `PreparedStatement` with `?` — **never** string concatenation.
4. `if (con == null)` guard at the top of every DAO method.
5. Close the connection in **`finally`**.
6. Return an **empty list**, never `null`, from a read.
7. Validation in the **service**, SQL in the **DAO**, HTML in the **servlet**.

## Translation to Spring Boot

| Today | Spring Boot |
|---|---|
| `ProductServlet` + action ladder | `@RestController` + `@GetMapping`/`@PostMapping` |
| `ProductService` | `@Service` |
| `ProductDao` | `@Repository` / `JpaRepository` |
| `Product` bean | `@Entity` |
| `DBHelper` | `application.properties` |
| `parseInt(getParameter("id"))` | `@RequestParam int id` |
| manual validation | `@Valid`, `@NotNull`, `@Min` |
| `boolean` returns | custom exceptions + `@ControllerAdvice` |

---
---

# Appendix D — Teaching Guide

## D.1 Suggested session plan

A comfortable pace for a **3.5-hour session** including the lab. Part 2 is heavier than Part 1 —
do not try to compress it.

| Time | Topic | Chapters | Delivery notes |
|---:|---|---|---|
| 0:00–0:10 | **Recap of Part 1** | 1 | Ask *them* the questions. Fix gaps now. |
| 0:10–0:25 | **The problem** — one servlet doing everything | 2 | **Create the pain before the cure.** Show the 400-line monster. |
| 0:25–0:40 | MVC + the five packages | 3–4 | Restaurant analogy. Have them write the 5 packages down. |
| 0:40–0:55 | **Traps + Derby setup** | 12–15 | ⚠️ Teach the traps **before** the lab. Write the 3 symptoms on the board. |
| 0:55–1:10 | Derby connection + table, everyone verifies | 12–13 | **Do not proceed until every hand is up for "Ping succeeded".** |
| 1:10–1:20 | ☕ **Break** | | |
| 1:20–1:35 | `bean` + `helper` | 5–6 | Show Eclipse generate-getters. Be honest about the `null` return. |
| 1:35–1:55 | `dao` | 7 | Write **one** method fully. Drill `executeQuery` vs `executeUpdate`. |
| 1:55–2:10 | `service` | 8 | Anticipate "this layer is pointless". Show the testability argument. |
| 2:10–2:25 | `web` + the call chain | 9–10 | **Do the role-play.** Link back to the threading rule. |
| 2:25–2:35 | Why layers pay off | 11 | Validate the "too many files" objection, then answer it. |
| 2:35–3:00 | **CRUD patterns** — routing, links vs forms, boolean, DRY | 16–19 | The two-failure demo goes here. |
| 3:00–3:15 | Lab: build + test | 20 | 12-case test pass. |
| 3:15–3:25 | **The gap** — incognito demo | 21 | Startling and memorable. |
| 3:25–3:30 | Servlets → Spring MVC, translation table | 22 | **End positively.** |

**If you only have 2 hours:** cover chapters 2, 3, 4, 14, then 5–9 briskly, then 16, 18, 19, 22.
Set 10, 11, 15, 21 as reading. **Do not cut chapter 2 or chapter 14** — the first is the
motivation, the second saves the most lab time.

## D.2 The demos that carry the session

| # | Demo | Teaches | Time |
|---|---|---|---|
| 1 | The **400-line monster** on screen, then "where do you edit?" | Why layering exists | 3 min |
| 2 | **Derby ping succeeded**, everyone verifies | Removes the #1 blocker | 10 min |
| 3 | **Duplicate id vs negative price** — watch the console | 🌟 **The service layer earning its place** | 5 min |
| 4 | **`WHERE id = 777`** — SQL succeeds, 0 rows | Why the boolean pattern exists | 2 min |
| 5 | **Hover a Delete link**, then edit `p=` in the address bar | Generated per-row links; client-side trust | 3 min |
| 6 | **Add a Total column** after the refactor | DRY payoff — one edit, appears everywhere | 2 min |
| 7 | **Incognito window** → CRUD works without login | The sessions gap | 2 min |
| 8 | *(optional)* Insert a product named `<b>BOLD</b>` | XSS / output escaping | 2 min |

> **Demo 3 is the most important in the whole session.** If you do only one, do that one.

## D.3 The analogies that work

| Concept | Analogy |
|---|---|
| MVC | **Restaurant** — menu/plate (view), waiter (controller), kitchen/pantry (model) |
| Layers | Each person has **one job** and can be replaced without retraining the others |
| The bean | The **currency** passed between layers — not a step in the chain |
| DAO | The **only door** to the storeroom |
| Service | The **rulebook** — one copy, everyone follows it |
| `DBHelper` | The **one place** the address of the warehouse is written down |
| Boolean returns | A **receipt** saying "done" or "nothing matched" |
| Two-JAR trap | **Eclipse and Tomcat live in different houses** — each needs its own copy of the key |
| Sessions | The **numbered ticket** the amnesiac shop assistant gives you |

## D.4 Questions your associates *will* ask

**"Why so many files for such a simple app? This feels like overkill."**
> **Agree first — for a tiny app it *is* overhead.** Then: apps don't stay tiny, and retrofitting
> structure into tangled code costs far more than starting with it. Show the change-request table
> (ch. 11). Ask if anyone has inherited messy code — their story will make the point for you.

**"Isn't the service layer pointless? It just calls the DAO."**
> It would be, if it only forwarded. Ours **validates**. Put the rule there and *every* caller
> inherits it — a servlet, a REST endpoint, a batch job. Put it in the servlet and you'll
> duplicate it, and one copy will drift. Plus the service is **unit-testable without a server**.

**"Why does the page say 'failed' but the console is empty?"**
> **That's the service layer working.** It rejected the input before any SQL ran, so the DAO
> never logged anything. Compare with a duplicate id, where the console *does* show `23505`.
> Same message, two different code paths.

**"Why is `service` allowed to be a field when Part 1 said no fields?"**
> The rule is about **per-request data**. `ProductService` is **stateless** — no mutable fields —
> so all threads can share it. An `int id` field would be per-request data and a real bug.

**"Why `?` instead of just building the SQL string?"**
> **SQL injection.** With `?`, the template and the values travel separately, so a value can never
> become SQL syntax. Demo `admin' --` if they haven't seen it. It's also faster — the DB compiles
> the template once.

**"Why does my table show `PRODUCT` when I created `product`?"**
> Derby folds unquoted identifiers to uppercase. It's the same table. Don't "fix" it.

**"Why do I have to disconnect in Eclipse before running?"**
> Embedded Derby loads inside one JVM and takes an exclusive lock. Eclipse and Tomcat are two
> JVMs. Use H2 with `AUTO_SERVER=TRUE` or Derby Network Server if you want both at once.

**"Is this app secure?"**
> **No — and that's deliberate.** No sessions (anyone can reach the CRUD URLs), no password
> hashing, no HTML escaping. Do the incognito demo. Knowing what's missing is more valuable than
> being handed code that hides it.

**"Will I write code like this at work?"**
> Probably not — you'll write Spring Boot. But Spring Boot **is this**, with the boilerplate
> removed. Show the translation table (ch. 22). Learning this is why `@Service` will make sense
> instead of being magic.

**"Why can I edit `p=5` to `p=1` in the URL and delete something else?"**
> Because we trust the URL. Real apps check **on the server** whether *this user* may delete
> *this record*. Excellent question — it's exactly the authorisation topic that follows sessions.

## D.5 What to emphasise vs what to skim

| ⭐ Emphasise | ⏩ Skim |
|---|---|
| Why one servlet fails (ch. 2) — **the motivation** | `toString()` in the bean (ch. 5) |
| The five packages + what's forbidden in each (ch. 4) | Derby uppercase quirk (ch. 13) |
| **The three database traps** (ch. 14) — biggest time-saver | `Pragma`/cache headers |
| `executeQuery` vs `executeUpdate` (ch. 7) | `serialVersionUID` |
| The service-layer demo (ch. 8, 18) — **the best proof** | Four servlets vs one, in depth (ch. 16) |
| The `service` field vs `id` field nuance (ch. 9) | Derby Network Server setup |
| The boolean pattern and `WHERE id = 777` (ch. 18) | |
| DRY — let them feel the pain first (ch. 19) | |
| The Spring translation table (ch. 22) | |

## D.6 Before the session — a checklist

- [ ] **Everyone's Part 1 project runs.** Verify before starting; a broken project blocks everything.
- [ ] **Everyone has located `derby.jar`** on disk and knows the path.
- [ ] **You have written the three trap symptoms on the board** (ch. 14). Leave them up all session.
- [ ] Tomcat version confirmed (again) — `javax` vs `jakarta`.
- [ ] You have a **working finished project** to paste from if someone falls badly behind.
- [ ] `product-setup.sql` ready to re-seed data after delete tests.
- [ ] Demos 1, 3 and 7 prepared in tabs.

## D.7 Signs it's going well / going badly

**Going well:** someone asks *"couldn't we reuse this service for a REST API?"* · someone spots
that the delete link is a GET that changes data · someone asks about hashing the password ·
someone notices the silent console before you point it out.

**Going badly — and what to do:**

| Sign | Fix |
|---|---|
| Half the room stuck on "No products found" | **Stop everything.** Do the absolute-path fix together on the projector. |
| People creating classes in the wrong package | Pause and re-draw the five-package diagram. Ask "which package?" for each remaining file. |
| Copy-pasting without reading | Switch to type-along for the DAO. Ask *them* what the next line should be. |
| "I don't see why we need layers" | Go back to ch. 11's table. Don't argue — show the change-request costs. |
| Running out of time | Skip chapters 10, 11, 15 (set as reading). **Never skip the two-failure demo.** |

---

# Appendix E — Answers to all Check-yourself questions

**Q1.1** A **`String`** — always. HTTP carries only text, so you convert with `Integer.parseInt`.
**Q1.2** To **restart Tomcat**. `web.xml` is read only at startup.

**Q2.1** (a) Nothing is **findable** — SQL buried among HTML in a huge method. (b) Everything is
**duplicated** — the connection URL appears four times. (c) Nothing is **testable** — logic needs
a running server and database.
**Q2.2** *"When one thing changes, how many places must I edit?"* The goal is **one**.

**Q3.1** The **Model** — specifically the DAO.
**Q3.2** The **View / Controller** — our servlet. The DAO reports a fact; the servlet decides the
wording and the colour.

**Q4.1** `dao`. All SQL lives there and only there.
**Q4.2** `service`. It's a business rule, so it goes in one place every caller inherits.
**Q4.3** Because it's the **currency**, not a step. A `Product` is what the layers hand to each
other, so every layer imports it.

**Q5.1** Frameworks and tools need it — JSP tags, JSON libraries and JPA create an empty object
and then fill it via setters.
**Q5.2** Tooling that relies on the **JavaBeans convention** stops seeing the property: JSP
`${product.price}`, Spring form binding and JSON serialisation would all fail to find it.

**Q6.1** Because `DBHelper.connect()` returns **`null`** on failure. Using it unguarded gives a
`NullPointerException` and a **500** page instead of a clean "failed" message.
**Q6.2** **One** — `DBHelper`. (Possibly minor SQL-dialect tweaks in the DAO, but the connection
details are in one file.)

**Q7.1** Because the DAO must not know its caller is a web page. Returning `List<Product>` keeps
it reusable by a servlet, a REST endpoint, a report or a unit test. **Data layers return data;
presentation layers decide how it looks.**
**Q7.2** JDBC placeholders are **1-based**, not 0-based. The first `?` is index 1.
**Q7.3** It returns **`0`** and you get no data — no exception, which is what makes the bug
confusing. SELECT needs `executeQuery()`.

**Q8.1** Because a second UI (REST API, admin page, mobile endpoint) would have to **duplicate**
the rule — and one copy would eventually drift out of sync.
**Q8.2** Because it has no `HttpServletRequest`, no `PrintWriter`, no SQL — it's a **plain Java
class**. Just `new ProductService()` and call the method.
**Q8.3** The **service** layer. If the DAO had rejected it, the console would show a
`SQLException` with a SQLState.

**Q9.1** `ProductService` is **stateless** — no mutable fields — so all threads can safely share
one instance. `int id` is **per-request data**, so one thread would overwrite another's value.
**Q9.2** **Read** parameters (and convert them), **call** the service, **write** HTML. Nothing else.

**Q10.1** A **`Product`** object (the bean).
**Q10.2** It would couple the service to the web layer, so it could **only** be called from a
servlet — no unit tests, no reuse from a REST endpoint or batch job. Plain Java in, plain Java out.

**Q11.1** **`DBHelper`** — the only class that knows the JDBC URL.
**Q11.2** For a genuinely **small** app it's extra ceremony — more files and more indirection than
the problem needs. The counter-argument is that apps grow, and retrofitting structure is more
expensive than starting with it.

**Q12.1** Because the error messages are **specific** and there's a Test button. Debugging the
same problem through a web app means reading stack traces and guessing.
**Q12.2** **New** the first time (Eclipse ships the template but not the JAR). **Edit** to reuse
on a later project, or to repair a stale JAR path.

**Q13.1** Derby **folds unquoted identifiers to uppercase**. It's the same table; your SQL can
still say `product`.
**Q13.2** In SQL, **double quotes mean *identifier*** (a column/table name), so `"Laptop"` is read
as a column name. String literals use **single quotes**.

**Q14.1** A **relative** Derby path. Eclipse and Tomcat have different working directories, so
Tomcat silently created a **second, empty** database. Use an absolute path in both places.
**Q14.2** `derby.jar` is not in **`WEB-INF/lib`**. The copy in the driver definition is only used
by Eclipse's own tools.
**Q14.3** Embedded Derby loads **inside one JVM** and takes an exclusive lock. Eclipse's explorer
and Tomcat are two JVMs, so the second one is refused. Disconnect the explorer.

**Q15.1** Because the servlet specification says a web app's classloader **automatically** loads
every JAR in `WEB-INF/lib`.
**Q15.2** The same specification **forbids** serving anything under `WEB-INF`. It holds
`web.xml`, your compiled classes and your JARs — none of which a visitor should be able to
download.

**Q16.1** So a request with no parameters shows a useful page instead of throwing a
`NullPointerException` on `action.equals(...)` and returning a **500**.
**Q16.2** **`DispatcherServlet`** — plus the `@GetMapping` / `@PostMapping` annotations that
declare the routes.

**Q17.1** Because the **Java string** is delimited by double quotes, so using single quotes for
the HTML attribute needs no escaping.
**Q17.2** `request.getParameter("p")` — it must match the link's parameter name, not `"id"`.
**Q17.3** A GET is supposed to be **idempotent** (safe to repeat). A crawler or browser
pre-fetcher following the link would **silently delete data**. Also, the URL is editable, so
anyone can change `p=5` to `p=1`. Real apps use a POST with confirmation, plus server-side
authorisation.

**Q18.1** It does **not** throw — the SQL is perfectly valid. It affects **0 rows**, so
`executeUpdate()` returns `0` and the method returns **`false`**. Without that check you'd report
success falsely.
**Q18.2** It says **that** it failed, never **why**. "Id not found", "duplicate key" and
"database down" all look identical. That's why the DAO logs the real `SQLException`.

**Q19.1** The moment you would copy-paste it for the **second** time. Not before — premature
abstraction is its own problem.
**Q19.2** Because a `PrintWriter` **field** would be shared across all users' threads (one
instance, many threads). A parameter is per-call and therefore safe.

**Q20.1** **`displayAllProducts(out)`**. Running it for every action means the user always sees
the refreshed table right below the status message — so they can confirm the result without
navigating anywhere.
**Q20.2** Because the **delete link** sends `?action=delete&p=3`, while the **update form** has an
input named `id`. Each handler must read the name its own source actually sends.

**Q21.1** Because HTTP is **stateless** and `ProductServlet` **never checks** whether the caller
logged in. The login response was sent and Tomcat immediately forgot the user.
**Q21.2** `getSession()` **creates** a new session if none exists. `getSession(false)` returns
**`null`** instead — which is what you want when *checking* whether someone is logged in.

**Q22.1** **A servlet** — Spring MVC's front controller. It receives every request and routes it
to the right `@Controller` method. It's an industrial version of our `action` if-ladder.
**Q22.2** `ProductService` → **`@Service`**. `ProductDao` → **`@Repository`** (or a
`JpaRepository` interface).

---

## Where to go next

You have now built, by hand, the architecture that Spring Boot generates for you:

```text
   ProductServlet  →  @Controller
   ProductService  →  @Service
   ProductDao      →  @Repository
   Product         →  @Entity
   DBHelper        →  application.properties
```

**Next in the series:**

| Session | What it adds |
|---|---|
| **Spring Boot 1** — Foundations | Auto-configuration, and this whole app in a fraction of the code |
| **Spring Boot 2** — REST Web Services | The same CRUD, as a JSON API |
| **Spring Boot 3** — DTO, layers & exceptions | Proper error handling — the fix for our `boolean` returns |
| **Spring Boot 4** — Microservices | Service registry, gateway, load balancing |

**Immediate next steps you could take on your own:**

1. **Add sessions** — close the gap from chapter 21. The most valuable single addition.
2. **Add search** — `WHERE name LIKE ?` with `ps.setString(1, "%" + keyword + "%")`.
3. **Add an Edit link** that pre-fills a form with the row's current values.
4. **Escape your output** so a product named `<b>x</b>` displays literally.
5. **Do the assignment** — rebuild the whole pattern for a different domain (student, employee, book).

---

*Java Servlets Part 2 — Study notes & teaching guide · Purvam Prajapati, Faculty — AHD*
