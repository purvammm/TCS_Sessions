# Java Servlets — Part 1: Web, HTTP & Your First Servlet

**Complete study notes + teaching guide**

Companion to `servlets-session1-theory.html` (31 slides) and `servlets-session1-lab.html` (7 labs).
Author: **Purvam Prajapati**, Faculty — AHD.

---

## What this document is

This is a **written, self-contained course**. You can learn servlets from zero by reading it top
to bottom, and then use the same document to **teach the topic to someone else**.

It is written for two readers at once:

| If you are… | Read it like this |
|---|---|
| **Learning for the first time** | Read straight through. Do the "Check yourself" questions. Skip the 🎓 Teaching tips on the first pass. |
| **Preparing to teach** | Read the chapter, then the 🎓 Teaching tip. Then jump to [Appendix D — Teaching Guide](#appendix-d--teaching-guide) for timings, analogies, and the questions people actually ask. |

### What you need to know before starting

- **Core Java** — classes, methods, `String`, `int`, `try/catch`, inheritance (`extends`).
- **Basic HTML** — what `<h1>`, `<table>`, `<form>` and `<input>` are. Nothing advanced.
- **Nothing about the web** is assumed. We start from "what is a web application".

### What you'll be able to do at the end

1. Explain how a browser and a server talk to each other, in HTTP terms.
2. Read and write an HTTP request and response by hand.
3. Explain GET vs POST properly — including the part most people get wrong.
4. Write a servlet that reads a form, validates it, and replies with HTML.
5. Debug the five failures that beginners hit, from the symptom alone.

---

## Table of contents

**Part A — The web, before any Java**
1. [What is a web application?](#1-what-is-a-web-application)
2. [Static vs dynamic pages — why servlets exist](#2-static-vs-dynamic-pages--why-servlets-exist)
3. [Web servers and Tomcat](#3-web-servers-and-tomcat)
4. [Anatomy of a URL](#4-anatomy-of-a-url)
5. [The journey of one request](#5-the-journey-of-one-request)

**Part B — HTTP, the language of the web**

6. [HTTP in two ideas](#6-http-in-two-ideas)
7. [Structure of an HTTP request](#7-structure-of-an-http-request)
8. [Structure of an HTTP response](#8-structure-of-an-http-response)
9. [Status codes](#9-status-codes)
10. [GET vs POST](#10-get-vs-post)

**Part C — Servlets**

11. [What is a servlet?](#11-what-is-a-servlet)
12. [The servlet container](#12-the-servlet-container)
13. [The Servlet API family (and the javax/jakarta trap)](#13-the-servlet-api-family-and-the-javaxjakarta-trap)
14. [The servlet lifecycle](#14-the-servlet-lifecycle)
15. [One instance, many threads](#15-one-instance-many-threads)
16. [URL mapping — how the browser finds your class](#16-url-mapping--how-the-browser-finds-your-class)
17. [Project setup and structure](#17-project-setup-and-structure)

**Part D — Writing the code**

18. [`doGet` line by line](#18-doget-line-by-line)
19. [`PrintWriter` vs `System.out`](#19-printwriter-vs-systemout)
20. [`setContentType` — the silent bug](#20-setcontenttype--the-silent-bug)
21. [Reading form data](#21-reading-form-data)
22. [Everything arrives as a String](#22-everything-arrives-as-a-string)
23. [The complete login servlet](#23-the-complete-login-servlet)
24. [Tracing one real request, end to end](#24-tracing-one-real-request-end-to-end)

**Appendices**

- [Appendix A — Common mistakes and how to spot them](#appendix-a--common-mistakes-and-how-to-spot-them)
- [Appendix B — Glossary](#appendix-b--glossary)
- [Appendix C — Cheat sheet](#appendix-c--cheat-sheet)
- [Appendix D — Teaching Guide](#appendix-d--teaching-guide)
- [Appendix E — Answers to all Check-yourself questions](#appendix-e--answers-to-all-check-yourself-questions)

---
---

# Part A — The web, before any Java

## 1. What is a web application?

A **web application** is a program you use **through a browser** instead of installing it on your
machine. Gmail, Amazon, your bank's website, the college portal — all web applications.

Every one of them is arranged the same way. It's called the **client–server model**:

```text
┌───────────────────┐                                  ┌───────────────────┐
│                   │   1. "Give me the login page"    │                   │
│      CLIENT       │ ───────────────────────────────▶ │      SERVER       │
│    (a browser)    │            REQUEST               │  (Tomcat running  │
│                   │                                  │   your Java code) │
│  Chrome, Firefox, │ ◀─────────────────────────────── │                   │
│  Edge, Safari     │   2. "Here it is: <html>...</html>"                   │
│                   │            RESPONSE              │                   │
└───────────────────┘                                  └───────────────────┘
     your laptop                                        a machine somewhere
                                                      (today: also your laptop)
```

### Who does what

| The **client** (browser) | The **server** |
|---|---|
| **Asks** for something | **Listens** for requests, all day, forever |
| **Renders** whatever HTML comes back | **Runs logic** — validate, calculate, query a database |
| Knows **nothing** about your database or your Java classes | **Replies** with HTML the client can display |

### The one mental shift you must make today

Every Java program you have written so far worked like this:

```java
public static void main(String[] args) {
    Scanner sc = new Scanner(System.in);
    System.out.print("Enter your name: ");   // I decide when to ask
    String name = sc.nextLine();             // I decide when to read
    System.out.println("Hello " + name);     // I decide when to print
}
```

**Your program was in charge.** It decided when to ask for input and when to print.

A web application is the opposite. It is **reactive**:

```text
       Server starts
             │
             ▼
    ┌────────────────┐
    │   waiting...   │ ◀────────────┐
    └────────┬───────┘              │
             │ a request arrives!   │
             ▼                      │
    ┌────────────────┐              │
    │ your code runs │              │
    │  and replies   │              │
    └────────────────┘              │
             │                      │
             └──────────────────────┘
              go back to waiting
```

> **You no longer write `main()`. You write methods that the server calls for you.**

That sentence is the whole session in one line. Everything else is detail.

> 🎓 **Teaching tip**
> Do not start with code. Start by asking the room: *"When you type gmail.com and press
> Enter, what actually happens?"* Let them guess for a minute. Most people have never
> thought about it, and the guessing creates the gap that this session fills.
> Then draw the two-box diagram above on the whiteboard — it is the only diagram you
> need for the first ten minutes.

> ✅ **Check yourself**
> **Q1.1** In a web application, which side runs your Java code — the client or the server?
> **Q1.2** Why can't the browser just query the database directly?
> *(Answers in [Appendix E](#appendix-e--answers-to-all-check-yourself-questions).)*

---

## 2. Static vs dynamic pages — why servlets exist

Before servlets can make sense, you need to see the **problem** they solve.

A server can send back two kinds of thing.

### Static page

A `.html` file sitting on the server's disk. The server finds it and sends it, unchanged.

```html
<!-- about.html — sitting on disk, never changes -->
<h1>About Us</h1>
<p>We are a company founded in 2005.</p>
```

Everyone who visits sees **exactly the same thing**.

### Dynamic page

HTML that is **generated by a program, at the moment of the request**.

```text
Priya visits  ──▶  "Welcome back, Priya — you have 3 items in your cart"
Ravi visits   ──▶  "Welcome back, Ravi — you have 0 items in your cart"
```

Same URL. **Different HTML**, because a program looked up who you are and built a fresh answer.

### Side by side

| | Static page | Dynamic page |
|---|---|---|
| **What it is** | A `.html` file on disk | HTML **generated at request time** |
| **Who builds it** | A developer, once, by hand | Your Java code, freshly, every request |
| **Content** | Identical for everyone, always | Different per user, per query, per moment |
| **Example** | An "About Us" page | A search result, a cart, a bank balance |
| **Needs a database?** | No | Usually yes |

### The point

> A static file **cannot** say *"Welcome back, Priya — you have 3 items in your cart."*
> It has no idea who Priya is.
>
> To produce that sentence you need **code running on the server at the moment of the
> request**, that can look things up and build the HTML on the spot.
>
> **In Java, that code is a servlet.**

### An analogy that works well

| | |
|---|---|
| A **static page** is a **printed poster** | Everyone walking past sees the same thing |
| A **dynamic page** is a **waiter** | They ask who you are, go to the kitchen, and bring back *your* order |

**Today you are building the waiter.**

> 🎓 **Teaching tip**
> The poster-vs-waiter analogy lands better than any technical explanation. Use it, then
> immediately make it concrete: open any e-commerce site in two different browsers, one
> logged in and one not, and show the same URL producing different pages. Thirty seconds,
> and the concept is permanently installed.

> ✅ **Check yourself**
> **Q2.1** Is a login *form* static or dynamic? What about the page showing the login *result*?
> **Q2.2** Give one example of a dynamic page you used today.

---

## 3. Web servers and Tomcat

A **web server** is software that:

1. **listens** on a network port,
2. **accepts** incoming HTTP requests,
3. **sends back** HTTP responses.

It is the permanent receptionist of your application — always on, always listening.

### The ones you'll hear about

| Server | Ecosystem | Used for |
|---|---|---|
| **Apache Tomcat** | Apache, **Java** | Running Java servlets & JSP — **this is ours** |
| **Nginx** | Open source, C | Very fast static files, reverse proxy, load balancing |
| **IIS** | Microsoft | ASP.NET applications on Windows Server |
| **Lighttpd** | Open source, C | Lightweight, low-memory environments |
| **Apache HTTP Server** | Apache, C | The classic general-purpose web server ("httpd") |

### Why Tomcat specifically?

Nginx and IIS can serve files and forward requests, but they **cannot run a Java class**.

Tomcat can, because it contains a **servlet container** — the component that knows how to load
your compiled servlet, create it, and call its methods.

> **Tomcat is a web server that speaks Java.** That is the entire reason we use it.

### Careful: there are two different "Apache" products

| Product | What it is |
|---|---|
| **Apache HTTP Server** (`httpd`) | A general web server written in C. **Not** Java. |
| **Apache Tomcat** | The Java servlet container. **This one.** |

They share a foundation's name and nothing else. When a job advert says "experience with
Tomcat", it means the Java one.

### Web server vs application server

This distinction gets asked in interviews constantly.

| | Web server | Application server |
|---|---|---|
| **Core job** | Serve content over HTTP | Host and run full business applications |
| **Handles** | HTML, CSS, images, and (with a container) servlets | Servlets **plus** EJB, transactions, messaging, connection pooling |
| **Weight** | Light | Heavy — many more moving parts |
| **Examples** | Nginx, Apache HTTP Server, **Tomcat** | WildFly (JBoss), WebLogic, WebSphere, GlassFish |

**Where does Tomcat sit?** Tomcat is usually described as a **web server with a servlet
container**. It does servlets and JSP beautifully, but it does not implement the full Java EE
stack — there is no EJB container, for example.

In practice that is completely fine: **most modern Java web apps only ever need what Tomcat
provides.** Spring Boot even ships an embedded Tomcat *inside* your JAR for exactly this reason.

**The crisp interview answer:**

> "A web server handles HTTP and serves content. An application server adds enterprise
> services — transactions, EJB, messaging — on top. Tomcat is a web server plus a servlet
> container, which is all most applications need."

> 🎓 **Teaching tip**
> Do not spend long on the four non-Java servers. The only thing that matters is
> *"Tomcat is the one that can run Java, that's why we use it."* But **do** drill the
> web-server-vs-application-server answer, because it is a guaranteed interview question
> and your associates will thank you for the ready-made sentence.

> ✅ **Check yourself**
> **Q3.1** Could you run a servlet on Nginx? Why or why not?
> **Q3.2** Is Tomcat a web server or an application server?

---

## 4. Anatomy of a URL

Every request starts with a URL. It looks like one blob of text, but it is really **six labelled
parts**. You will be building these by hand all through the lab, so learn to see the seams.

```text
  http://    localhost   :8080   /ServletBasics/login   ?action=login&id=123   #result
  ───────    ─────────   ─────   ────────────────────   ────────────────────   ───────
     1           2         3              4                     5                6
  protocol   server     port          resource path        query parameters   fragment
             location  (optional)                                            (optional)
```

| # | Part | What it means | The detail that matters |
|---|---|---|---|
| 1 | **Protocol** | The language to speak — `http` or `https` | `https` is the same protocol wrapped in encryption. Always `https` in production. |
| 2 | **Server location** | A domain name or an IP address | `localhost` means *this machine* — it resolves to `127.0.0.1`. That's what you use all lab. |
| 3 | **Port** | Which program on that machine | Optional because there are defaults: **80** for http, **443** for https. Tomcat defaults to **8080**, so we must write it. |
| 4 | **Resource path** | What you're asking for | For us: `/<project-name>/<url-pattern>`. First segment = the app, second = which servlet. |
| 5 | **Query parameters** | Extra data as `key=value` pairs | Starts with `?`, pairs joined by `&`. **This is what `request.getParameter()` reads.** |
| 6 | **Fragment** | A spot *within* the page | **Never sent to the server.** The browser alone uses it to scroll. |

### What a port actually is

A useful mental model:

```text
        One machine (localhost) = one apartment building
        A port                  = one flat number

    ┌─────────────────────────────────────────┐
    │             localhost                   │
    │                                         │
    │   :80    ──▶  a normal web server       │
    │   :3306  ──▶  MySQL                     │
    │   :1527  ──▶  Derby network server      │
    │   :8080  ──▶  TOMCAT  ← our code lives here
    │                                         │
    └─────────────────────────────────────────┘
```

The IP address gets you to the **building**. The port gets you to the right **flat**.

### The URL you'll type a hundred times

```text
http://localhost:8080/ServletBasics/login
└────┘ └───────┘ └──┘ └────────────┘ └───┘
  │        │      │         │          └── url-pattern from web.xml (which servlet)
  │        │      │         └───────────── project name (the "context path")
  │        │      └─────────────────────── Tomcat's port
  │        └────────────────────────────── this machine
  └─────────────────────────────────────── protocol
```

> **If a page 404s in the lab, re-read this line part by part.** The mistake is almost always
> in the project name or the url-pattern.

> 🎓 **Teaching tip**
> Have everyone open a real site and find the `?` in the address bar — a YouTube video URL
> (`?v=...`) or any search result works. Seeing a query parameter *in the wild* makes
> `getParameter()` feel obvious later, instead of arbitrary.
> Also mention the fragment being invisible to the server: it surprises people, and it's a
> nice "huh, I never knew that" moment that keeps attention.

> ✅ **Check yourself**
> **Q4.1** In `http://localhost:8080/Shop/cart?id=9#total`, which part never reaches the server?
> **Q4.2** Why do we have to write `:8080` but you never type `:80` for a normal website?

---

## 5. The journey of one request

This is the most important diagram of the session. Every page you build follows this loop.

```text
  ┌──────────────────────────────────────────────────────────────────────┐
  │                                                                      │
  │  1. BROWSER                                                          │
  │     You type a URL, click a link, or submit a form                   │
  │                              │                                       │
  │                              ▼                                       │
  │  2. WEB SERVER (Tomcat)                                              │
  │     Receives the HTTP request on port 8080                           │
  │                              │                                       │
  │                              ▼                                       │
  │  3. SERVLET CONTAINER                                                │
  │     Matches the URL to your servlet, calls doGet() or doPost()       │
  │                              │                                       │
  │                              ▼                                       │
  │  4. YOUR JAVA CODE                                                   │
  │     Reads parameters, runs logic, decides what to say                │
  │                              │                                       │
  │                              ▼                                       │
  │  5. DATABASE            ...... this step is PART 2 ......            │
  │     (via the JDBC driver, returning rows)                            │
  │                              │                                       │
  │                              ▼                                       │
  │  6. SERVLET BUILDS HTML                                              │
  │     Writes tags as text, using PrintWriter                           │
  │                              │                                       │
  │                              ▼                                       │
  │  7. BROWSER RENDERS IT                                               │
  │     The HTML text becomes a visible page                             │
  │                                                                      │
  └──────────────────────────────────────────────────────────────────────┘
```

### The insight that makes servlets click

Look at step 6 again.

> **Your servlet never sends a heading, or a table, or a button.**
> **It sends a string of text that happens to be HTML.**

The browser is what turns `<h3>Hello</h3>` into big bold letters on screen. Your job is only to
produce **the right characters in the right order**.

That's why this is a perfectly valid servlet body:

```java
out.println("<h3>Hello</h3>");    // you are printing TEXT
```

It looks strange at first — HTML inside a Java string. But once you accept *"I am generating
text, the browser does the drawing"*, servlets stop being mysterious.

> 🎓 **Teaching tip**
> This is the single highest-value idea in Part 1, and it is worth stopping on.
> **Live demo:** open any web page, right-click → **View Page Source**. Show them that a
> web page *is* just text. Then say: "your servlet's whole job is to produce that text."
> Come back to this diagram at the end of the session and walk it again — repetition here
> pays off more than anywhere else.

> ✅ **Check yourself**
> **Q5.1** Which step does a 404 error happen at?
> **Q5.2** Which step does a 500 error happen at?


---
---

# Part B — HTTP, the language of the web

## 6. HTTP in two ideas

**HTTP** stands for **H**yper**T**ext **T**ransfer **P**rotocol. A *protocol* is just an agreed
format for messages — like the agreed format of a postal address.

Two properties define how it feels to program against.

### Idea 1 — It is strictly request–response

```text
    CLIENT                                  SERVER
      │                                       │
      │──────────── request ─────────────────▶│
      │                                       │  (thinks)
      │◀─────────── response ─────────────────│
      │                                       │
      │            exchange over              │
      │                                       │
      X  server CANNOT start a conversation   X
```

The client asks, the server answers, and the exchange is finished. **The server cannot
spontaneously send something to a browser.** It can only reply to a request that arrived.

*(If you've wondered how live chat and notifications work — they use extra technology on top,
such as WebSockets or repeated polling. Plain HTTP cannot do it.)*

### Idea 2 — It is stateless

**Stateless** means: each request is independent. The server remembers **nothing** from the
previous one.

```text
   Request 1:  "Log me in, I'm user 123"     ──▶  Server: "OK, you're valid!"
                                                  ...forgets everything...

   Request 2:  "Show me my cart"             ──▶  Server: "...who are you?"
```

Two requests from the same person look, by default, **like two complete strangers**.

### Why that's a problem worth naming now

You log in on one request. On the very next request — clicking a link — HTTP has already
forgotten who you are.

So how does *any* website keep you logged in?

With extra machinery layered on top: **cookies** and **sessions**. The server hands the browser
a small ID, and the browser sends that ID back with every subsequent request:

```text
   Request 1  ──▶  Server: "You're valid. Here, hold this ID: A1B2C3"
                            (Set-Cookie: JSESSIONID=A1B2C3)

   Request 2  ──▶  Browser automatically includes: JSESSIONID=A1B2C3
                   Server: "A1B2C3? Ah — that's user 123. Here's your cart."
```

You will see that exact `Set-Cookie: JSESSIONID=...` header two chapters from now. That's
Tomcat doing this for you.

### Scope note for this session

Our login servlet checks an id and password and prints the result. It does **not** keep you
logged in afterwards, because we have not added sessions yet — **and that is deliberate.**

> **Today: one request, one answer.** Sessions come later.

> 🎓 **Teaching tip**
> Statelessness is abstract, so make it physical. Analogy that works:
> *"Imagine a shop assistant with total amnesia. Every single time you walk up to the counter
> — even two seconds later — they have no idea who you are. To cope, they give you a numbered
> ticket and ask you to show it every time. That ticket is a session cookie."*
> Ask the room: *"So why does Amazon still know you a week later?"* — that question makes
> them want the answer, which is a good place to leave a hook for a later session.

> ✅ **Check yourself**
> **Q6.1** Can a server push a message to a browser using plain HTTP?
> **Q6.2** In one sentence, what does "stateless" mean?

---

## 7. Structure of an HTTP request

Here is the thing that surprises people most: **an HTTP request is just plain text.** You could
type it by hand. It has a fixed shape of **four parts**, always in this order.

This is literally what travels down the wire when you submit the lab's login form:

```http
GET /ServletBasics/login?action=login&id=123&pwd=Christi HTTP/1.1   ← 1. REQUEST LINE
Host: localhost:8080                                               ← 2. HEADERS start
Accept: text/html,application/xhtml+xml,*/*
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
User-Agent: Mozilla/5.0 (Windows NT 10.0) Chrome/120.0
Content-Length: 0
                                                                   ← 3. ONE BLANK LINE
(body — empty for this GET request)                                ← 4. BODY
```

### The four parts

| Part | What it carries |
|---|---|
| **1 · Request line** | Three things: the **method** (`GET`), the **path + query string**, and the **HTTP version**. Notice the parameters sit right here in the URL — that one fact drives the whole GET-vs-POST discussion. |
| **2 · Headers** | `key: value` metadata, one per line. |
| **3 · Blank line** | A single empty line meaning "headers finished, body begins". Not decoration — it is how the server knows where to stop parsing headers. |
| **4 · Body** | The payload. **Empty for GET.** For POST, this is where the form data lives. |

### The headers worth knowing

| Header | Meaning |
|---|---|
| `Host` | Which site you want. **Required** in HTTP/1.1 (one server can host many sites). |
| `Accept` | "These are the formats I can understand." |
| `Accept-Encoding` | "These are the compressions I can decompress" — that's how gzip works. |
| `Accept-Language` | "I prefer English" — how sites auto-select a language. |
| `User-Agent` | Which browser and OS. How sites detect mobile. |
| `Content-Length` | How many bytes of body follow. `0` here, because GET has no body. |

### Connecting it to your code

```text
   GET /ServletBasics/login?action=login&id=123&pwd=Christi HTTP/1.1
                                        ─────── ──────  ─────────────
                                           │       │         │
                                           │       │         └── getParameter("pwd")  → "Christi"
                                           │       └──────────── getParameter("id")   → "123"
                                           └──────────────────── getParameter("action") → "login"
```

> When you call `request.getParameter("id")`, you are asking Tomcat to **pull `id=123` out of
> that request line** and hand you the `"123"`.

There is nothing magical in a request. It's text, and `getParameter` is a convenient way to
look inside it.

> 🎓 **Teaching tip**
> **The best live demo of the whole session:** open Chrome DevTools (F12) → **Network** tab →
> reload any page → click the first entry → **Headers**. There it all is: the request line,
> the real headers, the response headers. Students often assume slides are simplified
> teaching fictions; showing the real thing in their own browser removes that doubt instantly.
> Lab 6 of Part 1 also builds an "echo servlet" that prints these headers back — mention it
> now so they have something to look forward to.

> ✅ **Check yourself**
> **Q7.1** Where does the data go in a GET request — the request line or the body?
> **Q7.2** What is the blank line for?

---

## 8. Structure of an HTTP response

The reply has the **same four-part shape**, but with a **status line** instead of a request line.

This is what your servlet produces:

```http
HTTP/1.1 200 OK                                        ← 1. STATUS LINE
Content-Type: text/html;charset=UTF-8                  ← 2. HEADERS start
Set-Cookie: JSESSIONID=8A1F3C9D; Path=/ServletBasics
Pragma: no-cache
Cache-Control: no-store, must-revalidate
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Content-Length: 64
                                                       ← 3. ONE BLANK LINE
<h3><font color="green">Login successful</font></h3>   ← 4. BODY
```

### The headers worth knowing

| Header | Its role |
|---|---|
| **`Content-Type`** | **The most important one for us.** Tells the browser *how to interpret the body*. `text/html` → parse the tags and render. `text/plain` → show the characters literally. This is exactly what `response.setContentType("text/html")` sets — and forgetting it is the bug in [chapter 20](#20-setcontenttype--the-silent-bug). |
| `Set-Cookie` | Asks the browser to store a small value and send it back on later requests. `JSESSIONID` is how Tomcat recognises a returning visitor. |
| `Pragma` / `Cache-Control` | Caching instructions. `no-cache` / `no-store` mean "don't keep a copy" — important for live data or private information. |
| `Expires` | Content expiry. A date in the **past** (like the 1970 one above) is the classic trick for "this is already stale, always re-fetch." |
| `Content-Length` | Body size in bytes, so the browser knows when it has received everything. |

### Who writes which part

```text
   ┌─────────────────────────────────────────────────────┐
   │  HTTP/1.1 200 OK                                    │  ┐
   │  Content-Type: text/html;charset=UTF-8              │  │  TOMCAT
   │  Set-Cookie: JSESSIONID=8A1F3C9D                    │  │  writes
   │  Content-Length: 64                                 │  │  these
   │                                                     │  ┘
   │  <h3><font color="green">Login successful</font></h3>│  ← YOU write this
   └─────────────────────────────────────────────────────┘        with out.println()
```

Everything you write with `out.println(...)` lands in **part 4**. Tomcat writes parts 1–3 for
you automatically.

That is mostly a mercy — but it is also **why a missing `setContentType` is invisible** until
the browser renders the wrong thing. You never see the headers, so you never notice one is wrong.

> 🎓 **Teaching tip**
> Draw the "who writes what" box above on the whiteboard. It resolves a question people are
> often too shy to ask: *"if I only print the HTML, where do the status code and headers come
> from?"* Answering it before they ask builds a lot of confidence.

> ✅ **Check yourself**
> **Q8.1** Which header decides whether the browser *renders* your tags or *shows* them as text?
> **Q8.2** Do you write the `200 OK` line yourself?

---

## 9. Status codes

The number in the status line is the server's **one-word verdict** on your request. They are
grouped by first digit, and knowing the groups lets you diagnose problems before reading a
single log line.

| Range | Meaning | Ones you'll actually meet |
|---|---|---|
| **1xx** | Informational | Rare. `100 Continue`. |
| **2xx** | **Success** | `200 OK` — it worked. `201 Created` — a new resource was made (you'll use this in REST). |
| **3xx** | Redirection | `301` moved permanently · `302 Found` — "look over there instead", what `sendRedirect()` sends. |
| **4xx** | **You (the client) erred** | `400` bad request · `401` not authenticated · `403` forbidden · **`404 Not Found`** · `405` method not allowed. |
| **5xx** | **The server erred** | **`500 Internal Server Error`** — your code threw an exception · `503` service unavailable. |

### The memory trick

```text
   4xx  =  "YOU messed up"    (the client asked for something wrong)
   5xx  =  "I messed up"      (the server broke while handling a valid request)
```

### The two you will debug all lab

This is the most practically useful table in Part 1:

| You see | It means | First thing to check |
|---|---|---|
| **404 Not Found** | Tomcat looked for your URL and **found nothing**. Your *address* is wrong. Your code never ran. | Project name in the URL → then `<url-pattern>` in `web.xml` → then **restart Tomcat** |
| **500 Internal Server Error** | Tomcat found your servlet, **ran it, and your code threw an exception**. | **The Eclipse console.** Read the *first* line of the stack trace, not the last. |

```text
    404  ──▶  "I couldn't find your servlet"    ──▶  fix the URL / mapping
    500  ──▶  "I found it and it exploded"      ──▶  fix your code (read the console)
```

**One more worth knowing now:** `405 Method Not Allowed` appears when a form uses
`method="post"` but your servlet only implements `doGet`. Chapter 18 shows the one-line fix.

> 🎓 **Teaching tip**
> Do not just list codes — that's forgettable. Instead, make it a **diagnostic skill**:
> "I'll show you two broken pages, you tell me whether to look at the URL or the console."
> Then actually break something twice (misspell the url-pattern; throw a deliberate
> exception) and let them call it. It takes four minutes and converts trivia into a skill
> they'll use for years.

> ✅ **Check yourself**
> **Q9.1** You get a 404. Is the problem in your Java code or your URL?
> **Q9.2** You get a 500. Where do you look first?

---

## 10. GET vs POST

Both send data to the server. This gets asked in **every interview**, so let's be precise.

### The one difference everything else follows from

```text
   ┌─────────────────────── GET ───────────────────────┐
   │                                                   │
   │   GET /login?id=123&pwd=Christi HTTP/1.1          │  ◀── data is HERE, in the URL
   │   Host: localhost:8080                            │
   │   Content-Length: 0                               │
   │                                                   │
   │   (body empty)                                    │
   └───────────────────────────────────────────────────┘

   ┌─────────────────────── POST ──────────────────────┐
   │                                                   │
   │   POST /login HTTP/1.1                            │  ◀── URL is clean
   │   Host: localhost:8080                            │
   │   Content-Length: 22                              │
   │                                                   │
   │   id=123&pwd=Christi                              │  ◀── data is HERE, in the body
   └───────────────────────────────────────────────────┘
```

**GET puts the data in the URL. POST puts it in the body.** Every other difference is a
consequence of that.

### The full comparison

| Aspect | GET | POST |
|---|---|---|
| **Data goes in** | The **URL** (query string) | The **body** |
| **Visible?** | ❌ Yes — address bar, browser history, server logs, over your shoulder | ✅ No — not shown in the address bar |
| **Data volume** | ❌ Limited — URLs capped in practice (~2000 chars) | ✅ Effectively unlimited — fine for large forms, file uploads |
| **Idempotent?** | ✅ Yes — repeating changes nothing | ❌ No — repeating may create a duplicate |
| **Bookmarkable / shareable?** | ✅ Yes — the whole request is one URL | ❌ No — the body isn't part of the URL |
| **Cached by browsers?** | Yes — makes repeat views fast | No — every submit hits the server |
| **Safe for passwords?** | ❌ Never | ✅ Yes — *with HTTPS* (see below) |
| **Servlet method called** | `doGet(...)` | `doPost(...)` |

### ⚠️ Be precise about "POST is secure"

This is the most-repeated half-truth in web development.

> POST only **hides data from the address bar**. The body still travels as **plain text**, and
> anyone watching the network can read it.
>
> **Only HTTPS makes data secure**, by encrypting the whole exchange.

The correct phrasing to teach:

> *"POST keeps data out of the URL. HTTPS keeps it out of an attacker's hands."*

### Idempotency, explained simply

**Idempotent** is a fancy word for a simple test:

> **If I do this twice, is the result the same as doing it once?**

| Action | Twice = once? | Idempotent? |
|---|---|---|
| Reading a product page | Yes — same page | ✅ Yes |
| Submitting a payment | No — **two charges** | ❌ No |
| Registering an account | No — duplicate user | ❌ No |

This is why you've seen this dialog:

```text
   ┌─────────────────────────────────────────┐
   │  Confirm form resubmission?             │
   │                                         │
   │  This page requires data you already    │
   │  submitted.        [ Cancel ] [ Resend ]│
   └─────────────────────────────────────────┘
```

**That box exists because the browser knows POST isn't safe to repeat.** Refresh a GET result
and it silently re-fetches; refresh a POST result and it asks first.

### When to use which

| Use **GET** when you're **reading** | Use **POST** when you're **changing** |
|---|---|
| Browsing a catalogue | Registration |
| Viewing a product | Login |
| Searching, filtering, paginating | Placing an order |
| Anything you'd want to bookmark or share | Uploading a file |

**The rule:**

> **GET to read. POST to write.**

### Why our lab login form uses GET

Deliberately — **so you can see the parameters in the address bar.**

```text
   http://localhost:8080/ServletBasics/login?action=login&id=123&pwd=Christi
                                                                  ─────────
                                                                  the password,
                                                                  in plain sight
```

Seeing your own password sitting in the URL is a far better lesson than being told about it.
A real login form would use POST — and the lab shows you how to switch it.

> 🎓 **Teaching tip**
> **Do this live, it's the best moment of Part 1.** Have everyone submit the login form with
> `method="get"`, then look at their own address bar. The password is right there.
> Then ask: *"the field said `type="password"` and showed dots — so why can you read it?"*
> Answer: the masking is **cosmetic, on screen only**. That single demo teaches GET vs POST,
> `type="password"`, and healthy security scepticism all at once.
> Follow up by switching the form to `method="post"` and reloading — the URL goes clean, and
> the concept is locked in.

> ✅ **Check yourself**
> **Q10.1** Is POST encrypted?
> **Q10.2** Why can you bookmark a search result but not a completed checkout?
> **Q10.3** Which servlet method does `method="post"` call?


---
---

# Part C — Servlets

## 11. What is a servlet?

A **servlet** is an ordinary Java class that **extends the capability of a web server** — it lets
the server answer a request with content *your code generated*, rather than a file from disk.

Three facts define it:

| | |
|---|---|
| ☕ **It's just a Java class** | No new language, no magic. You `extends HttpServlet` and override a method. Everything you know about Java still applies. |
| 🚫 **But it has no `main()`** | You never run a servlet yourself. **The server runs it**, calling your methods when a matching request arrives. |
| 📤 **Its output is a response** | Instead of `System.out`, you write to the response. The characters you write become the page the user sees. |

### The smallest useful servlet

This is the whole shape of it:

```java
public class HelloServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/html");
        PrintWriter out = response.getWriter();
        out.println("<h1>Hello from a servlet!</h1>");
    }
}
```

That's it. Four lines of body.

### Read those two parameters carefully — they are the whole API

```text
    doGet( HttpServletRequest request , HttpServletResponse response )
           ─────────────────────────    ──────────────────────────────
                      │                              │
                      │                              │
           EVERYTHING THE BROWSER          THE REPLY YOU ARE FILLING IN
              SENT YOU (incoming)                  (outgoing)
                      │                              │
           • getParameter("id")           • setContentType("text/html")
           • getHeader("Host")            • getWriter()  → PrintWriter
           • getMethod()                  • sendRedirect("...")
           • getSession()
```

> **`request` = incoming. `response` = outgoing.**
> Master those two objects and you have mastered servlets.

Everything else in this session is detail about how to use them well.

> 🎓 **Teaching tip**
> Write `request` and `response` on the whiteboard as two boxes and leave them up for the
> whole session. Every time you introduce a new method, add it to the correct box. By the end
> the board *is* the API reference, built by the class rather than handed to them.
> Also: some people are unsettled by "no `main()`". Reassure them explicitly — "you still
> write normal Java, someone else just calls it" — because that quietly worries beginners
> more than you'd expect.

> ✅ **Check yourself**
> **Q11.1** Which object do you read the user's input from?
> **Q11.2** Why doesn't a servlet have a `main` method?

---

## 12. The servlet container

The **servlet container** (also called the *web container*; inside Tomcat the component is named
*Catalina*) is the part of the server that manages your servlets.

Understanding what it does for you is what turns servlets from "magic" into "obvious".

### What the container handles, so you never write it

| The container handles… | …so you never write code for |
|---|---|
| **Socket & port management** | Opening port 8080, accepting TCP connections, reading bytes off the wire |
| **Parsing HTTP** | Splitting that raw text into a request line, headers, and body |
| **URL mapping** | Deciding *which* of your servlets should handle `/login` |
| **Object creation (lifecycle)** | Loading your class, instantiating it, calling `init()`, eventually `destroy()` |
| **Threading** | Serving 500 simultaneous users without you touching `Thread` |
| **Building the response** | Writing the status line, headers and `Content-Length` around your body |

### How big a deal is this?

```text
   WITHOUT a container, "serve a web page in Java" means:

   ┌────────────────────────────────────────────┐
   │ ServerSocket server = new ServerSocket(8080);
   │ while (true) {                             │
   │     Socket s = server.accept();            │   ← accept connections
   │     // read raw bytes                      │
   │     // find where the headers end          │   ← parse HTTP by hand
   │     // split the request line              │
   │     // decode the query string             │
   │     // hand it to a worker thread          │   ← manage a thread pool
   │     // write a status line and headers     │
   │ }                                          │
   └────────────────────────────────────────────┘
      Hundreds of lines BEFORE you display anything.

   WITH a container:

   ┌────────────────────────────────────────────┐
   │ protected void doGet(req, res) {           │
   │     out.println("<h1>Hello</h1>");         │   ← just your logic
   │ }                                          │
   └────────────────────────────────────────────┘
```

> **You write only the part that is unique to your application: the business logic.**

### Inversion of control — remember this phrase

You do not call the container. **The container calls you.**

```text
   Normal Java:        your code  ──calls──▶  a library

   Servlets:           container  ──calls──▶  your code
```

This "don't call us, we'll call you" arrangement has a name: **inversion of control**. It is the
same principle behind Spring's dependency injection.

Servlets are where most Java developers meet it for the first time — so naming it now makes
Spring far less surprising later.

> 🎓 **Teaching tip**
> The "hundreds of lines vs four lines" contrast above is worth showing, because gratitude is
> a great teaching tool: once people see what they're *not* having to write, they stop
> resenting the framework's rules (like "restart Tomcat after editing web.xml").
> The hotel analogy also works well: *"you're a chef in a hotel kitchen. You don't greet
> guests, take bookings, or wash up. You cook when an order arrives. The container is the
> hotel."*

> ✅ **Check yourself**
> **Q12.1** Who creates the object of your servlet class — you or the container?
> **Q12.2** What does "inversion of control" mean in one sentence?

---

## 13. The Servlet API family (and the javax/jakarta trap)

You will write `extends HttpServlet` without thinking. Here's what sits above it — because it
explains where `doGet` actually gets called from.

```text
        ┌──────────────────────────────────────────────────────┐
        │  interface Servlet                                   │
        │  the contract: init(), service(), destroy()          │
        │  protocol-neutral — knows nothing about HTTP         │
        └──────────────────────┬───────────────────────────────┘
                               │ implemented by
        ┌──────────────────────▼───────────────────────────────┐
        │  abstract class GenericServlet                       │
        │  implements the boring parts; still protocol-neutral │
        └──────────────────────┬───────────────────────────────┘
                               │ extended by
        ┌──────────────────────▼───────────────────────────────┐
        │  abstract class HttpServlet                          │
        │  adds HTTP. Its service() inspects the method and    │
        │  dispatches to doGet / doPost / doPut / doDelete     │
        └──────────────────────┬───────────────────────────────┘
                               │ extended by
        ┌──────────────────────▼───────────────────────────────┐
        │  class LoginServlet          ← YOUR CLASS            │
        │  override just the methods you need                  │
        └──────────────────────────────────────────────────────┘
```

### Why do we override `doGet` and not `service`?

Because `HttpServlet.service()` **already contains the if-ladder**:

```java
// Roughly what HttpServlet.service() does for you:
protected void service(HttpServletRequest req, HttpServletResponse res) {
    String method = req.getMethod();

    if (method.equals("GET"))          doGet(req, res);
    else if (method.equals("POST"))    doPost(req, res);
    else if (method.equals("PUT"))     doPut(req, res);
    else if (method.equals("DELETE"))  doDelete(req, res);
    // ...
}
```

By overriding `doGet`, you plug into that ladder **at exactly the right rung**. If you overrode
`service()` yourself, you would break the dispatching.

> **Rule: override `doGet` / `doPost`. Leave `service` alone.**

This also explains `405 Method Not Allowed`: the *default* `doPost` in `HttpServlet` does nothing
but reply 405. If you don't override it, that's the reply a POST gets.

### ⚠️ THE TRAP: `javax` vs `jakarta`

**Read this before you write a single import.** The package name changed when Java EE became
Jakarta EE, and mismatching it is the **#1 reason a servlet won't compile or won't run** for
people following older tutorials.

| Your Tomcat | Import you must use |
|---|---|
| **Tomcat 9 and earlier** | `import javax.servlet.*;` ← **all our lab code** |
| **Tomcat 10 and later** | `import jakarta.servlet.*;` |

The class names are **identical**. Only the package differs.

```java
// Tomcat 9  (what this course uses)
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

// Tomcat 10+  — same names, different package
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
```

### The symptoms, so you recognise them

| What you did | What happens |
|---|---|
| Used `jakarta` on Tomcat 9 | `The import jakarta.servlet cannot be resolved` — a **compile** error, obvious |
| Used `javax` on Tomcat 10+ | **Compiles fine**, but Tomcat returns **404 or 500** and your servlet never runs — much more confusing |

> **Check your Tomcat version first.** On Tomcat 10+, find-and-replace every `javax.servlet`
> with `jakarta.servlet`. **Nothing else in the code changes.**

> 🎓 **Teaching tip**
> Put the Tomcat version on the board before anyone opens Eclipse, and confirm everyone has
> the same one. If half the room is on Tomcat 10 you will spend the session debugging imports
> instead of teaching servlets. **This is the single most valuable five minutes of prep you
> can do.**
> Explain the *why* briefly — Oracle donated Java EE to the Eclipse Foundation and couldn't
> hand over the `javax` trademark — because "someone renamed a package for legal reasons"
> is much easier to remember than an arbitrary rule.

> ✅ **Check yourself**
> **Q13.1** Why is overriding `service()` a bad idea?
> **Q13.2** You're on Tomcat 10 and your servlet 404s even though it compiled. What's the likely cause?

---

## 14. The servlet lifecycle

A servlet passes through **three phases**, and the container drives every one. The middle phase
is the one that repeats.

```text
   Tomcat starts
        │
        │  (nothing happens yet — servlets are usually created lazily)
        │
        ▼  first request for /login ever arrives
   ┌─────────────────────────────────────────────────────┐
   │  1. LOAD + CREATE                                   │
   │     Container loads LoginServlet.class              │
   │     and creates ONE object of it                    │
   └─────────────────────┬───────────────────────────────┘
                         ▼
   ┌─────────────────────────────────────────────────────┐
   │  2. init()                       ◀── ONCE, EVER     │
   │     one-time setup                                  │
   └─────────────────────┬───────────────────────────────┘
                         ▼
   ┌─────────────────────────────────────────────────────┐
   │  3. service()                    ◀── EVERY REQUEST  │
   │        │                                            │
   │        ├── GET  ──▶ doGet(req, res)   ← YOUR CODE   │  ◀─┐
   │        └── POST ──▶ doPost(req, res)  ← YOUR CODE   │    │ repeats
   └─────────────────────┬───────────────────────────────┘    │ forever
                         │                                    │
                         └────────────────────────────────────┘
                         ▼  Tomcat shuts down / app redeployed
   ┌─────────────────────────────────────────────────────┐
   │  4. destroy()                    ◀── ONCE, EVER     │
   │     release resources, then garbage collected       │
   └─────────────────────────────────────────────────────┘
```

### The three phases in words

| Phase | When | What it's for |
|---|---|---|
| **`init()`** | **Once**, on the first request ever | One-time setup — reading config, opening a connection pool. You usually don't override it. |
| **`service()` → `doGet()`/`doPost()`** | **Once per request** | **This is where all your code lives.** A thousand requests = a thousand `doGet` calls — on the same object. |
| **`destroy()`** | **Once**, at shutdown | Release resources. Called when Tomcat stops or the app is redeployed. |

### The count that matters

> **`init()` once. `doGet()` many times. `destroy()` once.**
>
> **1 — many — 1**

If you remember one thing about the lifecycle, remember those three numbers. The next chapter
shows why they have real consequences for your code.

### A very common misconception

❌ *"A new servlet object is created for each request."*
✅ **One object. Many requests. Many threads.**

That is the next chapter, and it matters.

> 🎓 **Teaching tip**
> Prove the lifecycle rather than asserting it. Have them add print statements:
> ```java
> public void init() { System.out.println(">>> init called"); }
> protected void doGet(...) { System.out.println(">>> doGet called"); }
> public void destroy() { System.out.println(">>> destroy called"); }
> ```
> Then hit the page **five times** and look at the console: **one** `init`, **five** `doGet`.
> Then stop Tomcat: `destroy`. Seeing the counts in their own console beats any diagram.

> ✅ **Check yourself**
> **Q14.1** You refresh a page 10 times. How many times does `init()` run? How many times `doGet()`?
> **Q14.2** How many objects of your servlet class exist?

---

## 15. One instance, many threads

Here's the part that surprises people. The container creates **exactly one object** of your
servlet class, no matter how many users arrive.

Concurrency is handled by giving each request its own **thread** — all running through the same
object.

```text
    User A ──┐  thread 1 ──┐
             │             │
    User B ──┤  thread 2 ──┼──▶  ┌─────────────────────────┐
             │             │     │   ONE LoginServlet      │
    User C ──┘  thread 3 ──┘     │        object           │
                                 │   (shared by all three) │
                                 └─────────────────────────┘
```

### Why this matters — a real bug

```java
public class BadServlet extends HttpServlet {

    private String userName;          // ⚠️ ONE copy, shared by EVERY user

    protected void doGet(HttpServletRequest request, HttpServletResponse response) {
        userName = request.getParameter("name");

        // ...if User B's thread runs right here, it OVERWRITES userName...

        out.println("Hello " + userName);   // A may be greeted with B's name
    }
}
```

That is a genuine, hard-to-reproduce production bug. It works perfectly when you test alone and
fails under load.

### The fix — use local variables

```java
public class GoodServlet extends HttpServlet {

    // no request state as a field

    protected void doGet(HttpServletRequest request, HttpServletResponse response) {

        String userName = request.getParameter("name");   // ✅ LOCAL

        out.println("Hello " + userName);                 // always the right name
    }
}
```

**Why locals are safe:** each thread gets its own **stack**, and local variables live on the
stack. Thread 1's `userName` and thread 2's `userName` are **different pieces of memory**.

```text
   thread 1 stack        thread 2 stack        thread 3 stack
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │ userName =   │      │ userName =   │      │ userName =   │
   │   "Priya"    │      │   "Ravi"     │      │   "Karan"    │
   └──────────────┘      └──────────────┘      └──────────────┘
        separate               separate              separate
                    ▲
                    │  all calling methods on...
                    │
          ┌─────────────────────┐
          │  ONE servlet object │   ← fields here are SHARED
          └─────────────────────┘
```

### The rule

> **Never store per-request data in an instance field.**
> Keep it in **local variables** inside `doGet` / `doPost`.

### When *are* fields acceptable?

Only for things that are **the same for everybody and never change**:

```java
public class LoginServlet extends HttpServlet {

    // ✅ FINE — constants, identical for all users, never modified
    private static final int    VALID_ID  = 123;
    private static final String VALID_PWD = "Christi";

    // ✅ FINE (you'll see this in Part 2) — a stateless helper object
    private ProductService service = new ProductService();

    // ❌ NEVER — per-request data
    private int currentUserId;
    private String currentName;
}
```

> **The rule is about per-request data, not about fields in general.**

This distinction comes back in Part 2, so it's worth getting straight now.

> 🎓 **Teaching tip**
> This is the most commonly *misunderstood* topic in Part 1, and also the one that separates
> people who "know servlets" from people who really understand them — so give it proper time.
> The three-stacks diagram is the one to draw.
> If you want to make it vivid: *"imagine one waiter with a single notepad, serving three
> tables at once, rubbing out the previous order each time. That's an instance field. Now
> give each table its own notepad — that's a local variable."*
> Optional aside for stronger groups: this is also why `SimpleDateFormat` as a servlet field
> is a classic production bug.

> ✅ **Check yourself**
> **Q15.1** Why is `private String userName;` in a servlet dangerous?
> **Q15.2** Is `private static final int MAX = 10;` dangerous? Why or why not?

---

## 16. URL mapping — how the browser finds your class

The browser knows **nothing** about Java class names. It only sends a URL.

Something must connect `/login` to `com.tcs.web.LoginServlet`. That connection is a **URL
mapping**, and there are two ways to declare it.

### Option 1 — `web.xml` (what we use first)

```xml
<servlet>
    <servlet-name>LoginServlet</servlet-name>
    <servlet-class>com.tcs.web.LoginServlet</servlet-class>
</servlet>

<servlet-mapping>
    <servlet-name>LoginServlet</servlet-name>
    <url-pattern>/login</url-pattern>
</servlet-mapping>
```

**How the two blocks connect:**

```text
   <servlet>                              <servlet-mapping>
     <servlet-name>LoginServlet</...>       <servlet-name>LoginServlet</...>
                    ─────────────                          ─────────────
                          │                                      │
                          └──────── same nickname ───────────────┘
                                     joins them

     <servlet-class>                        <url-pattern>
        com.tcs.web.LoginServlet               /login
     </servlet-class>                        </url-pattern>
            │                                     │
       WHICH CLASS                            WHICH URL
```

The nickname (`LoginServlet`) is **just a label**. It could be `banana` — as long as it's the
same in both blocks. Using the class name is convention, not a requirement.

**Two rules:**
1. `<servlet-class>` must be the **fully-qualified name** — package included.
2. `<url-pattern>` must **start with `/`**.

### Option 2 — the annotation (modern)

```java
@WebServlet("/login")
public class LoginServlet extends HttpServlet {
    protected void doGet(...) { ... }
}
```

One line, right above the class. No XML at all. Requires Servlet 3.0+ (Tomcat 7+).

### Which should you use?

| | `web.xml` | `@WebServlet` |
|---|---|---|
| **Lines needed** | 8 lines of XML, in another file | **1 line**, above the class |
| **Find all mappings** | ✅ **Easy** — all listed in one file | Harder — scattered across source files |
| **Risk** | Name mismatch between the two blocks | Forgetting the leading `/` |
| **Needs** | Any servlet version | Servlet 3.0+ |

⚠️ **Never map the same servlet both ways.** Tomcat may refuse to start with a duplicate-mapping
error, and the message is not obvious.

Also note: `<welcome-file-list>` has **no annotation equivalent**, so `web.xml` never disappears
entirely.

### Putting the URL together

```text
   http://localhost:8080  /ServletBasics  /login
   ────────────────────   ──────────────  ──────
            │                    │           │
        the server        CONTEXT PATH   URL-PATTERN
                          (project name)  (from web.xml)
```

> Get either of the last two wrong and you get a **404**.

### Why teach `web.xml` first?

Because it makes the wiring **visible**. You can see, in one file, that a URL is deliberately
bound to a class — nothing is hidden.

Once that clicks, `@WebServlet` stops looking like magic and starts looking like a **shortcut**.
It's the same reason we teach JDBC before Spring Data.

> 🎓 **Teaching tip**
> Deliberately break the mapping in front of them: change `<url-pattern>` to `/logon`, restart,
> and hit `/login` → **404**. Then fix it. This makes the connection concrete and simultaneously
> teaches "404 = mapping problem", which is the diagnostic from chapter 9.
> Also stress **"restart Tomcat after editing web.xml"** here and again in the lab. People will
> forget, get a 404, and conclude their XML is wrong when it was fine.

> ✅ **Check yourself**
> **Q16.1** What joins the `<servlet>` block to the `<servlet-mapping>` block?
> **Q16.2** Full URL for a servlet mapped to `/product` in a project called `Shop`, on default Tomcat?

---

## 17. Project setup and structure

### Dynamic Web Project vs Java Project

In Eclipse these are **two different project types**, and a servlet only works in the web one.
Getting this wrong is where most people lose time on day one.

| | Java Project | **Dynamic Web Project** |
|---|---|---|
| **Icon** | A plain folder / **J** | A folder with a small **globe 🌐** badge |
| **Runs via** | `main()` — Run As → Java Application | A **server** — Run As → **Run on Server** |
| **Has `WebContent/`** | No | **Yes** — with `WEB-INF/` inside |
| **Has `web.xml`** | No | **Yes** (if you tick the box) |
| **Servlet API available?** | ❌ No — `HttpServlet` won't resolve | ✅ Yes — from the Tomcat runtime |
| **Produces** | A `.jar` | A `.war` — a deployable web archive |

**The two symptoms of picking wrong:**

1. `import javax.servlet.http.HttpServlet;` shows a red error — "cannot be resolved".
2. There is **no "Run on Server"** option in the right-click menu.

> Both mean you made a plain Java Project. **Delete it and start again** — retrofitting is more
> painful than recreating.

**Two boxes to tick when creating it:**

1. **Target Runtime** → your Tomcat. *This is what puts the Servlet API on your build path.*
2. On the last wizard page → **"Generate web.xml deployment descriptor"**. Easy to miss.

### The folder structure

```text
ServletBasics/
│
├── src/                          ← ALL your .java files
│   └── com/tcs/web/
│       └── LoginServlet.java
│
├── WebContent/                   ← the WEB ROOT: browser CAN reach things here
│   │
│   ├── index.html                ← reachable at /ServletBasics/index.html
│   │
│   └── WEB-INF/                  ← 🔒 PROTECTED: browser can NEVER reach these
│       ├── web.xml               ← the deployment descriptor
│       ├── lib/                  ← JARs your app needs (used in Part 2)
│       └── classes/              ← your compiled .class files (auto-generated)
│
└── build/                        ← Eclipse's compiler output (ignore it)
```

| Folder | Purpose |
|---|---|
| **`WebContent/`** | The web root. *(Maven projects call this `src/main/webapp` — same idea, different name.)* |
| **`WEB-INF/`** | **Deliberately unreachable** from the browser. The servlet spec *forbids* serving anything inside it. That's a **security feature** — config and JARs can't be downloaded by a visitor. |
| **`web.xml`** | The **deployment descriptor**. Tomcat reads it **at startup** to learn your servlets, their URLs, and the welcome file. |

**Try this in the lab:** browse to `http://localhost:8080/ServletBasics/WEB-INF/web.xml`.
You get a **404** even though the file exists. That's the protection working.

### The welcome file

What loads when the URL names no file?

```xml
<welcome-file-list>
    <welcome-file>index.html</welcome-file>
</welcome-file-list>
```

```text
   Request:  http://localhost:8080/ServletBasics/
                                                └── no filename!

   Tomcat:   "check the welcome list... index.html exists... serve that."
```

It serves the **first entry it can find**. Change it to `home.html` and you must actually *have*
a `home.html` — otherwise **404**, and it's a confusing one because the URL looks perfectly fine.

### ⚠️ Edited `web.xml`? Restart Tomcat.

The descriptor is read **once, at startup**.

> Add a mapping, reload the page without restarting → **404**, and a lot of confusion.
>
> **Change `web.xml` → restart the server.** Every time.

> 🎓 **Teaching tip**
> Walk through the project-creation wizard **on the projector, slowly**, and have everyone
> follow along before anyone writes code. Then do a **verification round**: "everyone check you
> have a globe icon and a `web.xml`; raise a hand if not." Fixing three people now takes two
> minutes; discovering it twenty minutes later derails the session.
> The `WEB-INF` 404 demo is worth doing live — it's memorable and teaches a real security
> principle.

> ✅ **Check yourself**
> **Q17.1** Why can't the browser fetch `WEB-INF/web.xml`?
> **Q17.2** You added a servlet mapping and still get 404. What did you probably forget?


---
---

# Part D — Writing the code

## 18. `doGet` line by line

Let's dissect the method you'll write in the lab. Every line has a job.

```java
protected void doGet(HttpServletRequest request,
                     HttpServletResponse response)
        throws ServletException, IOException {              // ← 1

    response.setContentType("text/html");                   // ← 2  BEFORE getWriter()
    PrintWriter out = response.getWriter();                 // ← 3

    String action = request.getParameter("action");         // ← 4

    if ("login".equals(action)) {                           // ← 5  null-safe order
        out.println("<h3>Logging you in...</h3>");          // ← 6
    }
}
```

| # | What it does and why |
|---|---|
| **1** | `protected` because we're **overriding** `HttpServlet.doGet`. The two exceptions are declared by the parent — you must keep them (or narrow them). Just let the IDE generate the signature. |
| **2** | Tells the browser the body is HTML. **Must come before `getWriter()`** — chapter 20 explains what happens otherwise. |
| **3** | Gets the pipe to the browser. `PrintWriter` is from `java.io` — `Ctrl+Shift+O` in Eclipse adds the import. |
| **4** | Reads one parameter. Returns a `String`, or **`null`** if that parameter wasn't sent at all. |
| **5** | Note the order — see below. |
| **6** | Writes the response body. This text becomes **part 4** of the HTTP response from chapter 8. |

### Line 5 deserves its own explanation

```java
if ("login".equals(action))     // ✅ CONSTANT FIRST — safe
if (action.equals("login"))     // ❌ VARIABLE FIRST — crashes if action is null
```

If `action` is `null` (nobody sent that parameter), the second form throws
`NullPointerException` → the user sees a **500** page.

The first form is fine, because `"login"` is never null and `equals(null)` simply returns `false`.

```text
   Someone visits  /login   with no parameters at all
                            │
                            ▼
              action = null
                            │
        ┌───────────────────┴────────────────────┐
        ▼                                        ▼
 "login".equals(null)                  null.equals("login")
        │                                        │
        ▼                                        ▼
     false                          💥 NullPointerException
   (clean message)                       (500 error page)
```

> **Build the habit now: constant first, always.** It costs nothing and prevents a whole class
> of crashes.

### ⚠️ GET vs POST must match your form, or you get a 405

`doGet` only answers **GET** requests. If your form says `method="post"`, Tomcat looks for
`doPost`, doesn't find it, and returns **405 Method Not Allowed**.

Two fixes:

```java
// Option A — change the form to method="get"

// Option B — add a doPost that simply forwards. Very common, very practical.
protected void doPost(HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException {
    doGet(request, response);
}
```

Option B means **one place for your logic** and it works with both methods. We use it in the lab.

> 🎓 **Teaching tip**
> Type this method out live rather than pasting it, narrating each line. Beginners learn a
> surprising amount from watching *where* the IDE complains and how you fix it
> (e.g. `Ctrl+Shift+O` for imports).
> The null-safety diagram is worth drawing. Then demo it: visit `/login` with no parameters
> using `action.equals(...)` → 500. Swap the order → clean message. Twenty seconds, permanent
> lesson.

> ✅ **Check yourself**
> **Q18.1** Why `"login".equals(action)` rather than `action.equals("login")`?
> **Q18.2** Your form is `method="post"` and you only wrote `doGet`. What status code do you get?

---

## 19. `PrintWriter` vs `System.out`

Both print. They print to **completely different places**. Mixing them up is the most common
"my page is blank" moment for beginners.

```text
   ┌─────────────────────────────────────────────────────────────────┐
   │                        YOUR SERVLET                             │
   │                                                                 │
   │   System.out.println("hello")        out.println("hello")       │
   │            │                                  │                 │
   └────────────┼──────────────────────────────────┼─────────────────┘
                │                                  │
                ▼                                  ▼
     ┌────────────────────┐            ┌────────────────────────┐
     │  ECLIPSE CONSOLE   │            │  HTTP RESPONSE BODY    │
     │  (Tomcat's log)    │            │        │               │
     │                    │            │        ▼               │
     │   FOR YOU 👨‍💻        │            │   THE BROWSER 🌐       │
     │   (debugging)      │            │   FOR THE USER         │
     └────────────────────┘            └────────────────────────┘
```

### Side by side

```java
// ❌ Goes to the CONSOLE. The user sees NOTHING — blank page.
System.out.println("<h3>Welcome</h3>");

// ✅ Goes to the BROWSER. The user sees: Welcome (as a heading)
PrintWriter out = response.getWriter();
out.println("<h3>Welcome</h3>");
```

### One sentence to keep them straight

> **`System.out` is for you. `out` (the `PrintWriter`) is for the user.**

If a page renders empty, your **first** check is whether you printed to the wrong one.

### `System.out` is not useless — it's your debugging channel

This is genuinely how you debug a servlet:

```java
protected void doGet(HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException {

    // trace line — leave this in while developing
    System.out.println("doGet called. action=" + request.getParameter("action")
                     + ", id=" + request.getParameter("id"));
    ...
}
```

Now every request prints a line to the console. This is how you answer *"did my method even
run?"* and *"what value actually arrived?"* — the two questions behind most servlet bugs.

### Where does the console live in a web app?

| Environment | `System.out` goes to |
|---|---|
| **Development** (Tomcat inside Eclipse) | Eclipse's **Console** view |
| **Production** (a real server) | A log file, e.g. `catalina.out` |

Same stream, different destination. *(This is also why production code uses a logging framework
instead of `System.out` — but that's a topic for another day.)*

> 🎓 **Teaching tip**
> Make everyone deliberately break this: change one `out.println` to `System.out.println`,
> reload, and see content vanish from the page and appear in the console. Ten seconds, and
> the distinction is permanent.
> Then have them **add and keep** the trace line above. Getting people into the habit of
> printing what actually arrived is one of the most useful things you can teach — it makes
> them self-sufficient debuggers.

> ✅ **Check yourself**
> **Q19.1** Your page loads but is completely blank, and your HTML is in the Eclipse console. What happened?
> **Q19.2** Is it wrong to use `System.out` in a servlet?

---

## 20. `setContentType` — the silent bug

You wrote perfect HTML. The page shows the **tags as literal text**. Nothing is wrong with your
Java — you just forgot to tell the browser what kind of content it's receiving.

### Without it

```java
PrintWriter out = response.getWriter();
out.println("<h3>Hi</h3>");
```

Browser shows, **literally**:

```text
<h3>Hi</h3>
```

The browser treated it as plain text. Tags became **characters**, not instructions.

### With it

```java
response.setContentType("text/html");
PrintWriter out = response.getWriter();
out.println("<h3>Hi</h3>");
```

Browser shows:

> ### Hi

Parsed as HTML. A real heading.

### ⚠️ Order matters — and this one fails silently

```java
// ✅ CORRECT
response.setContentType("text/html");        // 1. FIRST — always
PrintWriter out = response.getWriter();      // 2. THEN get the writer

// ❌ WRONG — silently ignored, NO error at all
PrintWriter out = response.getWriter();
response.setContentType("text/html");        // too late!
```

**Why?** Response headers are **committed** the moment you obtain the writer. After that you
cannot change them.

```text
   response.setContentType("text/html")   ──▶  sets a header  ──▶  ✅ works
   response.getWriter()                   ──▶  HEADERS ARE NOW LOCKED
   response.setContentType("text/html")   ──▶  ignored, no exception  ──▶ ❌ silent failure
```

> **This is the version that wastes people's time**, because the line is right there in the
> file and *looks* correct.

### Other content types you'll meet

| Content type | Used for |
|---|---|
| `text/html` | A web page — **today** |
| `text/plain` | Raw text |
| `application/json` | JSON — what a REST API returns |
| `application/pdf`, `image/png` | Binary downloads |

> When you later write `@RestController` in Spring Boot, it sets `application/json` **for you**.
> Same header, chosen automatically.

> 🎓 **Teaching tip**
> Have everyone reproduce **both** versions of this bug — the missing line *and* the misplaced
> line. The second one is the valuable lesson, because "it's there but it doesn't work" is far
> more disorienting than "it's missing".
> Sum it up with a rule they can chant: **"content type before writer."**

> ✅ **Check yourself**
> **Q20.1** Your page displays `<h3>Hi</h3>` as visible text. What's wrong?
> **Q20.2** Does calling `setContentType` after `getWriter()` throw an exception?

---

## 21. Reading form data

The bridge from an HTML form to your Java variables is **one method**, and it works off the
**`name` attribute** — not the label, not the id.

### The HTML you write

```html
<form action="login" method="get">

    <input type="text"     name="id" />
    <input type="password" name="pwd" />

    <input type="submit"   name="action" value="login" />
</form>
```

### The Java that reads it

```java
String id     = request.getParameter("id");
String pwd    = request.getParameter("pwd");
String action = request.getParameter("action");
```

### The connection

```text
   HTML                                  JAVA
   ────────────────────────────          ─────────────────────────────────
   <input name="id" />          ────▶    request.getParameter("id")
                 ──                                            ──
                  └───────── must match EXACTLY ────────────────┘
                             (including capitalisation)
```

> **`name="id"` in the HTML ⟷ `getParameter("id")` in the Java.** That is the entire contract.
> Get it wrong and you silently receive `null`.

### The four form attributes that matter

| Attribute | What it controls |
|---|---|
| `action="login"` | **Where** the request goes. Relative, so it becomes `/ServletBasics/login`. |
| `method="get"` | **Which servlet method** is called — `doGet`. Change to `post` → `doPost`. |
| `name="id"` | **The parameter name** — what `getParameter` looks for. |
| `type="password"` | Masks characters **on screen only**. The value still travels as plain text. |

### ⚠️ It returns `null`, and `null` is not an error

| Situation | `getParameter("email")` returns |
|---|---|
| Parameter **not sent at all** | **`null`** |
| Field was submitted but **left empty** | **`""`** (empty string) |

Two *different* cases — and both will crash you if you call a method on the result blindly.

The safe guard:

```java
String email = request.getParameter("email");

// null check FIRST, so the later calls can never throw (short-circuit &&)
if (email != null && !email.trim().isEmpty()) {
    // safe to use
}
```

### The submit-button trick

Look again at the submit button:

```html
<input type="submit" name="action" value="login" />
```

Because it has a `name`, it **sends `action=login`** along with the form. That's how one servlet
can tell **which button was pressed** — useful when a page has several.

It works, and many tutorials use it. But a **hidden field** is clearer:

```html
<input type="hidden" name="action" value="login" />
<input type="submit" value="Sign in" />          <!-- label is now independent -->
```

With a hidden field, the value the server reads doesn't depend on the button's **visible label**.
You can change "login" to "Sign in" without breaking the servlet.

> Part 1 uses the button trick; **Part 2 uses hidden fields** — deliberately, so you've seen both.

### Two relatives of `getParameter`

```java
// For checkbox groups / multi-selects — one name, several values
String[] hobbies = request.getParameterValues("hobbies");

// Every parameter name that arrived — great for debugging a mysterious null
Enumeration<String> names = request.getParameterNames();
```

> 🎓 **Teaching tip**
> The `name` ⟷ `getParameter` mismatch is *the* most common beginner bug, and the symptom is
> horrible: a silent `null` that later becomes a confusing `NumberFormatException`.
> **Demo it deliberately:** change `name="id"` to `name="userid"`, leave the Java as
> `getParameter("id")`, and let them watch it break. Then show how the console trace line from
> chapter 19 reveals it instantly (`id=null`). That connects debugging technique to a real bug.
> Lab 6's echo servlet, which lists every parameter that arrived, is the permanent fix for this
> class of problem — mention it here.

> ✅ **Check yourself**
> **Q21.1** Your `<input>` is `name="userId"` and you call `getParameter("userid")`. What do you get?
> **Q21.2** What's the difference between a parameter returning `null` and returning `""`?

---

## 22. Everything arrives as a String

HTTP is a **text** protocol. There are no ints, doubles or booleans on the wire — **only
characters**.

So `getParameter()` **always** returns a `String`, even for a field you think of as a number.
**Converting is your job.**

```java
// The request said:  action=login&id=123&pwd=Christi

String idText = request.getParameter("id");     // "123"  ← a String!

int id = Integer.parseInt(idText);              // 123    ← now a number

// Other conversions you'll need in Part 2:
double price  = Double.parseDouble(request.getParameter("price"));
int quantity  = Integer.parseInt(request.getParameter("quantity"));
```

```text
   ┌──────────┐   text over the wire   ┌──────────┐   parseInt()   ┌──────────┐
   │ BROWSER  │ ────────"123"────────▶ │ SERVLET  │ ─────────────▶ │   123    │
   │          │                        │  String  │                │   int    │
   └──────────┘                        └──────────┘                └──────────┘
                                                                   your job ↑
```

### ⚠️ Three ways this throws

All three produce the same exception — `NumberFormatException` — and therefore the same **500**
page:

| What the user did | What happens |
|---|---|
| Typed `abc` in a number box | `parseInt("abc")` → 💥 |
| Left the field **blank** | `parseInt("")` → 💥 |
| Parameter **missing entirely** | `parseInt(null)` → 💥 |

Unhandled, each shows the user a raw stack trace. **Never acceptable in real software.**

### The defensive version — this is what we write

```java
try {
    int id = Integer.parseInt(request.getParameter("id"));
    // ... use it ...

} catch (NumberFormatException e) {
    out.println("<h3><font color='red'>User ID must be a number.</font></h3>");
}
```

Now a user typing nonsense gets a **helpful message** instead of a stack trace.

### The habit to build

> **Every single value from a browser is untrusted text.**
> Parse it, validate it, and be ready for it to be garbage — because sooner or later someone
> *will* type letters into your number box.

*(Later, Spring Boot does this conversion and validation for you with `@RequestParam int id` and
`@Valid`. But it is doing exactly what you're about to write by hand.)*

> 🎓 **Teaching tip**
> Ask before explaining: *"the form has a number field. What type does `getParameter` return?"*
> Most people guess `int`. The surprise makes the answer stick.
> Then have them submit `abc` **without** the try/catch and look at the ugly 500 page. Then add
> the catch and submit again. The before/after contrast teaches error handling as a **user
> experience** issue, not a syntax rule — which is the more valuable framing.

> ✅ **Check yourself**
> **Q22.1** Why does `getParameter` return a `String` for a numeric field?
> **Q22.2** Name the three inputs that make `Integer.parseInt` throw.

---

## 23. The complete login servlet

Everything from Part D, assembled. This is the file you build in Lab 3.

```java
package com.tcs.web;

import java.io.IOException;
import java.io.PrintWriter;

// On Tomcat 10+ change these four to jakarta.servlet.*
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class LoginServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;

    // Constants, not per-request data — so fields are safe here (ch. 15).
    // Hardcoded on purpose: this is a teaching exercise, not real auth.
    // Real apps check a database and store only HASHED passwords.
    private static final int    VALID_ID  = 123;
    private static final String VALID_PWD = "Christi";

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        // 1. Tell the browser we're sending HTML. MUST come before getWriter().
        response.setContentType("text/html");

        // 2. This writer is the pipe to the browser (NOT System.out).
        PrintWriter out = response.getWriter();

        // 3. Which button was pressed? Our submit had name="action" value="login".
        String action = request.getParameter("action");

        out.println("<html><body>");
        out.println("<h2>Login result</h2>");

        // 4. Constant FIRST: safe even when action is null.
        if ("login".equals(action)) {

            // 5. Form data always arrives as String — even the numeric field.
            //    LOCAL variables: one per thread, therefore thread-safe.
            String idText = request.getParameter("id");
            String pwd    = request.getParameter("pwd");

            try {
                // 6. Convert it yourself. Throws if the user typed letters.
                int id = Integer.parseInt(idText);

                if (id == VALID_ID && VALID_PWD.equals(pwd)) {
                    out.println("<h3><font color='green'>Login successful. Welcome!</font></h3>");
                } else {
                    // Deliberately vague: never reveal WHICH one was wrong.
                    out.println("<h3><font color='red'>Invalid id or password.</font></h3>");
                }

            } catch (NumberFormatException e) {
                // 7. Without this catch, the user sees a raw 500 stack trace.
                out.println("<h3><font color='red'>User ID must be a number.</font></h3>");
            }

        } else {
            out.println("<h3><font color='red'>Unknown action: " + action + "</font></h3>");
        }

        out.println("<p><a href='index.html'>&laquo; Back to login</a></p>");
        out.println("</body></html>");
    }

    // Without this, a form using method="post" gets 405 Method Not Allowed.
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }
}
```

### The four behaviours it handles

| Input | Result |
|---|---|
| `id=123`, `pwd=Christi` | 🟢 **Login successful. Welcome!** |
| `id=999`, `pwd=wrong` | 🔴 **Invalid id or password.** |
| `id=abc` | 🔴 **User ID must be a number.** *(not a 500)* |
| no parameters at all | 🔴 **Unknown action: null** *(not a crash)* |

**Notice that all four are handled gracefully.** No input produces a stack trace. That's the
standard to hold yourself to.

### Two small professional touches worth pointing out

1. **`serialVersionUID`** — `HttpServlet` implements `Serializable`, so the compiler warns
   without it. It's boilerplate; let Eclipse generate it and move on.

2. **The vague error message** — "Invalid id **or** password" rather than "wrong password".
   Telling an attacker *which* half was correct helps them enumerate valid usernames. Real
   login pages are deliberately vague, and it's a nice security habit to introduce early.

> 🎓 **Teaching tip**
> Build this file **incrementally on screen**, not all at once:
> 1. Empty `doGet` with just `out.println("<h1>Hi</h1>")` → **run it**. It works!
> 2. Add `getParameter` and print the raw values → **run it**.
> 3. Add `parseInt` and the comparison → **run it**.
> 4. Add the `try/catch` → **run it** with `abc`.
>
> **Running after every step** is the single best technique for teaching this. It keeps
> everyone's code working, and when something breaks, the cause is the last three lines rather
> than sixty.

> ✅ **Check yourself**
> **Q23.1** Why is the error message "Invalid id or password" instead of "Wrong password"?
> **Q23.2** Which single line prevents a 500 page when the user types `abc` in the ID box?

---

## 24. Tracing one real request, end to end

Everything in this session, applied to a single click. The user types **123** and **Christi** and
presses login.

| # | What happens | The concept behind it |
|---|---|---|
| **1** | Browser collects the form fields and builds a URL | Form is `method="get"`, so values go in the **query string** (ch. 10) |
| **2** | Sends `GET /ServletBasics/login?action=login&id=123&pwd=Christi` | A **request line** + headers + blank line (ch. 7) |
| **3** | Tomcat, listening on **port 8080**, accepts the connection | The **web server's** job (ch. 3) |
| **4** | Parses the raw text into a request object | The **container** doing work you never write (ch. 12) |
| **5** | Matches `/login` → `com.tcs.web.LoginServlet` | **URL mapping** from `web.xml` (ch. 16) |
| **6** | First request ever? Creates **one instance**, calls `init()` | **Lifecycle** phase 1 — once only (ch. 14) |
| **7** | Calls `service()`, which sees "GET" and calls **your `doGet`** | `HttpServlet`'s dispatch ladder (ch. 13) |
| **8** | Your code sets the content type, then gets the writer | **Order matters** — headers commit on `getWriter()` (ch. 20) |
| **9** | `getParameter("id")` returns the **String** `"123"` | HTTP carries text only (ch. 22) |
| **10** | `Integer.parseInt` makes it an `int`; you compare and decide | Conversion is **your** job, and can throw (ch. 22) |
| **11** | `out.println("<h3>...</h3>")` writes into the response **body** | You produce **characters**, not widgets (ch. 5) |
| **12** | Tomcat wraps it with `200 OK` and headers, and sends it | **Response structure**, built for you (ch. 8) |
| **13** | Browser reads `Content-Type: text/html` and **renders** the tags | Why `setContentType` isn't optional (ch. 20) |
| **14** | Exchange over. Tomcat remembers **nothing**. | **Statelessness** — next click starts fresh (ch. 6) |

### If you can narrate those fourteen steps, you understand servlets

Not the syntax — the **flow**. Syntax you can look up; the flow is what lets you debug:

```text
   404?                    ──▶  step 5 failed   (mapping / URL)
   500?                    ──▶  step 10 threw   (your code)
   Tags shown as text?     ──▶  step 8 skipped  (setContentType)
   Blank page?             ──▶  step 11 went to the console instead
```

> 🎓 **Teaching tip**
> **Close the session with this table** and walk it aloud, pointing back at the diagram from
> chapter 5. Then run it as a quiz: *"I get a 404. Which step broke?"*
> Even better — have a volunteer narrate all fourteen steps from memory while the rest correct
> them. If they can do that, they've got it, and you'll know exactly what to revise before
> Part 2.


---
---

# Appendix A — Common mistakes and how to spot them

The seven that cost people an afternoon. **Read the symptom column first** — that's how you'll
meet them in real life.

| # | Symptom you see | Cause | Fix |
|---|---|---|---|
| 1 | `HttpServlet cannot be resolved`, and no "Run on Server" option | You created a **plain Java Project** | Delete it; create a **Dynamic Web Project** with a Tomcat target runtime |
| 2 | `The import jakarta.servlet cannot be resolved` | Wrong package for your Tomcat version | Tomcat 9 → `javax.servlet`. Tomcat 10+ → `jakarta.servlet` |
| 3 | Page shows `<h3>Hi</h3>` as **visible text** | `setContentType` missing, **or called after `getWriter()`** | Call it **before** `getWriter()` |
| 4 | Page is **blank**, HTML is in the Eclipse console | You printed with `System.out` instead of `out` | Use the `PrintWriter` for anything the user must see |
| 5 | **405 Method Not Allowed** | Form is `method="post"`, servlet only has `doGet` | Add `doPost` that calls `doGet` |
| 6 | A value is mysteriously `null`, then `NumberFormatException` | `name=""` in the HTML doesn't match `getParameter("...")` | Make them match **exactly**, capitalisation included |
| 7 | **404** even though the mapping looks right | You edited `web.xml` and **didn't restart Tomcat** | Restart the server. Every `web.xml` change needs it |

## The two-question debugging routine

Memorise this. It covers the large majority of what goes wrong:

```text
   ┌─────────────────────────────────────────────────────────────┐
   │                                                             │
   │   Got a 404?                                                │
   │      └─▶ Your URL is wrong. Check, in this order:            │
   │           1. project name in the URL                        │
   │           2. <url-pattern> in web.xml                       │
   │           3. did you restart Tomcat?                        │
   │                                                             │
   │   Got a 500?                                                │
   │      └─▶ Your code threw. Go to the Eclipse console and     │
   │          read the FIRST line of the stack trace,            │
   │          not the last.                                      │
   │                                                             │
   └─────────────────────────────────────────────────────────────┘
```

**Why the first line and not the last?** The first line names the actual exception and the line
number in *your* file. The last lines are deep inside Tomcat and tell you nothing useful.

---

# Appendix B — Glossary

| Term | Meaning |
|---|---|
| **Client** | The program making the request — a browser. |
| **Server** | The machine/software receiving requests and sending responses. |
| **Web server** | Software that speaks HTTP. Tomcat, Nginx, IIS. |
| **Application server** | A web server plus enterprise services (EJB, transactions). WildFly, WebLogic. |
| **Servlet** | A Java class that handles HTTP requests. Has no `main()`; the container calls it. |
| **Servlet container** | The part of Tomcat that loads, creates and calls your servlets. Also called a *web container*. Tomcat's is named **Catalina**. |
| **Tomcat** | Apache's web server + servlet container. The one that runs Java. |
| **HTTP** | HyperText Transfer Protocol — the text format of web requests and responses. |
| **Stateless** | Each request is independent; the server remembers nothing from the last one. |
| **Request line** | The first line of a request: method + path + version. |
| **Status line** | The first line of a response: version + status code. |
| **Header** | A `key: value` metadata line in a request or response. |
| **Body** | The payload of a request or response. Your HTML goes in the response body. |
| **Query string** | The `?key=value&key=value` part of a URL. |
| **Fragment** | The `#part` of a URL. **Never sent to the server.** |
| **Context path** | The first path segment — your project name, e.g. `/ServletBasics`. |
| **url-pattern** | The path that maps to a servlet, e.g. `/login`. Must start with `/`. |
| **Deployment descriptor** | `web.xml` — the file where servlets, mappings and the welcome file are declared. |
| **Welcome file** | The page served when a URL names no file. |
| **`WEB-INF`** | A protected folder the browser can never reach. Holds `web.xml`, `lib/`, `classes/`. |
| **Dynamic Web Project** | The Eclipse project type that can run servlets. Has the globe icon. |
| **WAR** | Web Archive — the deployable package a web project produces. |
| **Idempotent** | Doing it twice gives the same result as doing it once. GET is; POST isn't. |
| **Inversion of control** | You don't call the framework; the framework calls you. |
| **POJO** | Plain Old Java Object — a simple data class. *(Used heavily in Part 2.)* |
| **Session** | Server-side memory of a particular user across requests. *(Not covered in Part 1.)* |
| **Cookie** | A small value the server asks the browser to store and send back. |
| **JSESSIONID** | The cookie Tomcat uses to recognise a returning visitor. |

---

# Appendix C — Cheat sheet

## The servlet API

```java
// ===== The class =====
public class MyServlet extends HttpServlet { }

// ===== The methods the container calls =====
protected void doGet (HttpServletRequest req, HttpServletResponse res)
protected void doPost(HttpServletRequest req, HttpServletResponse res)

// ===== READING (request = incoming) =====
request.getParameter("id")           // one value, as String, or null
request.getParameterValues("tags")   // String[] — checkbox groups
request.getParameterNames()          // Enumeration<String> — everything that arrived
request.getMethod()                  // "GET" or "POST"
request.getHeader("Host")            // one request header
request.getRequestURI()              // "/ServletBasics/login"
request.getQueryString()             // "action=login&id=123"  (null for POST)

// ===== WRITING (response = outgoing) =====
response.setContentType("text/html");     // ALWAYS BEFORE getWriter()
PrintWriter out = response.getWriter();
out.println("<h1>Hello</h1>");
response.sendRedirect("index.html");      // sends a 302

// ===== MAPPING (pick ONE, never both) =====
// web.xml:  <servlet> + <servlet-mapping> joined by the same <servlet-name>
// or:       @WebServlet("/login")   above the class
```

## The lifecycle

```text
   init()      ── ONCE, on the first request ever
   doGet()     ── EVERY request        ← your code lives here
   destroy()   ── ONCE, at shutdown

   1 ── many ── 1

   ONE instance, MANY threads  →  per-request data in LOCALS, never fields
```

## The URL

```text
   http://localhost:8080/ServletBasics/login?action=login&id=123#top
   ─────  ─────────  ──── ────────────  ────  ──────────────────  ───
     1        2       3        4          5           6            7

   1 protocol   2 host   3 port   4 context path (project)
   5 url-pattern (servlet)   6 query string   7 fragment (never sent)
```

## GET vs POST

| | GET | POST |
|---|---|---|
| Data in | the URL | the body |
| Visible | yes | no |
| Idempotent | yes | no |
| Bookmarkable | yes | no |
| Method called | `doGet` | `doPost` |
| Use for | **reading** | **writing** |

**Security:** POST hides data from the URL. **Only HTTPS encrypts it.**

## Status codes

| Code | Meaning | First check |
|---|---|---|
| `200` | OK | — |
| `302` | Redirect | what `sendRedirect()` sends |
| `404` | Not Found | **your URL / url-pattern**, then restart Tomcat |
| `405` | Method Not Allowed | form method vs your servlet methods |
| `500` | Server Error | **the Eclipse console**, first line of the trace |

**4xx = the client's fault. 5xx = the server's fault.**

## Five habits to keep

1. `setContentType` **before** `getWriter()` — always.
2. `"literal".equals(variable)` — **never** `variable.equals("literal")`.
3. Wrap every `parseInt` / `parseDouble` in `try/catch`.
4. Per-request data in **local variables**, never instance fields.
5. Changed `web.xml`? **Restart Tomcat.**

---
---

# Appendix D — Teaching Guide

Everything below is for when **you** are the one at the front of the room.

## D.1 Suggested session plan

A comfortable pace for a **3-hour session** including the lab. Adjust to your batch.

| Time | Topic | Chapters | Delivery notes |
|---:|---|---|---|
| 0:00–0:10 | **Hook + agenda** | — | Ask "what happens when you type gmail.com?" Let them guess. |
| 0:10–0:25 | Web apps, static vs dynamic | 1–2 | Poster vs waiter analogy. Live: same URL, two browsers. |
| 0:25–0:35 | Web servers, Tomcat | 3 | Don't dwell. Drill the interview answer. |
| 0:35–0:45 | URL anatomy | 4 | Live: find a `?` in a real address bar. |
| 0:45–0:55 | The request journey | 5 | **Key diagram.** Live: View Page Source. |
| 0:55–1:15 | HTTP request & response, status codes | 6–9 | **Live: DevTools → Network tab.** |
| 1:15–1:30 | **GET vs POST** | 10 | Interview favourite. Be precise about "secure". |
| 1:30–1:40 | ☕ **Break** | | |
| 1:40–1:55 | What is a servlet, container, API family | 11–13 | **Confirm everyone's Tomcat version here.** |
| 1:55–2:10 | Lifecycle, one-instance-many-threads | 14–15 | **Live: print statements to prove 1-many-1.** |
| 2:10–2:20 | URL mapping, project structure | 16–17 | Walk the wizard on the projector. |
| 2:20–2:45 | **The code** — doGet, PrintWriter, contentType, getParameter | 18–22 | Type it live, incrementally, running after each step. |
| 2:45–2:55 | Complete servlet + request trace | 23–24 | Volunteer narrates the 14 steps. |
| 2:55–3:00 | Recap + what's coming in Part 2 | — | |

**If you only have 90 minutes:** cover chapters 1, 2, 5, 7, 10, 11, 14, 18–22 and set the rest as
reading. Do **not** cut chapter 10 (GET vs POST) or 15 (threads) — they're the highest-value ones.

## D.2 The five live demos that carry the session

Prepare these in advance; they do more work than any slide.

| # | Demo | Teaches | Time |
|---|---|---|---|
| 1 | **View Page Source** on any site | A web page is just text | 1 min |
| 2 | **DevTools → Network → Headers** | HTTP requests are real, not a teaching fiction | 3 min |
| 3 | **Password visible in the address bar** after a GET login | GET vs POST, `type="password"` is cosmetic | 2 min |
| 4 | **Lifecycle print statements** — hit refresh 5× | `init` once, `doGet` five times | 3 min |
| 5 | **Break it three ways** — remove `setContentType`; swap `out` for `System.out`; POST with no `doPost` | The three failure modes, recognised by sight | 5 min |

> Demo 3 is the crowd-pleaser. Demo 5 is the most *useful*. Do both.

## D.3 The analogies that work

| Concept | Analogy |
|---|---|
| Static vs dynamic | **Printed poster** vs **a waiter** |
| Port | A **flat number** in an apartment building (the IP is the building) |
| Stateless HTTP | A shop assistant with **total amnesia** — hence the numbered ticket (cookie) |
| The container | You're a **chef in a hotel kitchen** — you cook; the hotel handles guests, bookings, washing up |
| Inversion of control | **"Don't call us, we'll call you"** |
| One instance, many threads | **One waiter, one notepad, three tables** — vs a notepad per table |
| `System.out` vs `out` | A **private diary** vs a **letter you post** |

## D.4 Questions your associates *will* ask

Prepare these; they come up almost every time.

**"Why is there no `main` method? How does it run?"**
> The container has the `main`. Tomcat is a running Java program; your servlet is a class it
> loads and calls. You're writing a *part* of a program, not a whole one.

**"Is POST secure?"**
> No. POST hides data from the address bar. Anyone watching the network can still read the body.
> **Only HTTPS encrypts it.** POST + HTTP is not secure.

**"Why do we write HTML inside Java strings? It's horrible."**
> **Agree with them — it genuinely is.** That's exactly why JSP was invented, and later
> Thymeleaf and template engines. We do it by hand once so you understand what those tools are
> doing. You will not write production code this way.

**"Do I have to use `web.xml`? I've seen annotations."**
> Both work. `web.xml` shows all mappings in one place, which is why we start there.
> `@WebServlet` is one line and very common in modern code. Never use both for the same servlet.

**"Why did my change not take effect?"**
> If you changed **`web.xml`** → restart Tomcat. If you changed **Java** → Eclipse usually
> hot-reloads, but restart if in doubt. If you changed **HTML** → hard-refresh the browser
> (`Ctrl+Shift+R`).

**"What's `serialVersionUID` for?"**
> `HttpServlet` implements `Serializable`, so the compiler warns without it. It's boilerplate —
> let Eclipse generate it. It does not affect how your servlet behaves.

**"Why is one instance shared? Wouldn't one per user be safer?"**
> It would be safer but far slower and heavier — thousands of objects for thousands of users.
> One instance plus a thread pool is the performance trade-off. It's safe **as long as you keep
> per-request data in local variables.**

**"Can two people really overwrite each other's data?"**
> Yes — with instance fields. It's a real production bug, and it's nasty because it never
> reproduces when you test alone. That's why the rule matters.

**"When do we get to Spring Boot?"**
> After Part 2. And everything here maps directly: `doGet` → `@GetMapping`, `getParameter` →
> `@RequestParam`. Learning this makes Spring make sense instead of feeling like magic.

## D.5 What to emphasise vs what to skim

| ⭐ Emphasise — they'll use it constantly | ⏩ Skim — awareness is enough |
|---|---|
| The request journey (ch. 5) | The four non-Java web servers (ch. 3) |
| GET vs POST + the security nuance (ch. 10) | `Pragma`, `Expires`, cache headers (ch. 8) |
| Lifecycle 1-many-1 (ch. 14) | 1xx and 3xx status codes (ch. 9) |
| One instance, many threads (ch. 15) | `GenericServlet` details (ch. 13) |
| `setContentType` before `getWriter` (ch. 20) | `serialVersionUID` (ch. 23) |
| `name` ⟷ `getParameter` matching (ch. 21) | |
| Everything is a String (ch. 22) | |
| 404 vs 500 diagnosis (ch. 9, App. A) | |

## D.6 Before the session — a checklist

- [ ] **Confirm everyone's Tomcat version** and write it on the board. *(Saves the most time of anything on this list.)*
- [ ] Everyone has **Eclipse IDE for Enterprise Java** — not the plain Java edition.
- [ ] Everyone can create a project showing the **globe icon**.
- [ ] Port **8080** is free on the training machines.
- [ ] You have the five demos from D.2 ready in tabs.
- [ ] A finished, working `LoginServlet` is available to paste if someone falls badly behind.

## D.7 Signs it's going well / going badly

**Going well:** someone asks *"so is the container basically doing dependency injection?"* ·
someone spots the 405 cause before you say it · someone asks about hashing the password.

**Going badly — and what to do:**

| Sign | Fix |
|---|---|
| Half the room has red imports | Stop. Do a Tomcat-version round. Fix it for everyone before continuing. |
| Silence at "any questions?" | Ask a *specific* question instead: "Sunita, does GET put data in the URL or the body?" |
| People pasting code without reading | Switch to type-along mode and slow down. Ask *them* what the next line should be. |
| Nobody's page works | Stop teaching, start troubleshooting one machine on the projector. Others will recognise their own problem. |

---

# Appendix E — Answers to all Check-yourself questions

**Q1.1** The **server**. Your Java runs on the server; the browser only displays the result.
**Q1.2** Security and control. The browser is on the user's machine and can be tampered with —
exposing a database to it would let anyone read or destroy your data. The server also enforces
business rules the client can't be trusted with.

**Q2.1** The login **form** is static (a fixed `.html` file). The login **result** is dynamic —
it depends on what you typed.
**Q2.2** Anything personalised or live: a social feed, a search result, an inbox, a bank balance,
a train-times page.

**Q3.1** **No.** Nginx cannot run a Java class; it has no servlet container. It can only serve
files or forward requests to something that can (like Tomcat).
**Q3.2** A **web server with a servlet container**. It is not a full application server — no EJB
container, no full Java EE stack.

**Q4.1** `#total` — the fragment. The browser keeps it and uses it to scroll.
**Q4.2** Because `80` is the **default** port for `http`, so the browser adds it invisibly.
Tomcat listens on **8080**, which is not a default, so it must be written.

**Q5.1** Step **3** — the servlet container tried to match the URL to a servlet and found
nothing. Your code never ran.
**Q5.2** Step **4** — your Java code ran and threw an exception.

**Q6.1** **No.** Plain HTTP is strictly request–response; the server can only reply. Push
requires extra technology (WebSockets, or repeated polling).
**Q6.2** Each request is independent — the server remembers nothing from the previous one.

**Q7.1** The **request line**, as the query string after the `?`. GET has no body.
**Q7.2** It marks the boundary between headers and body, so the server knows where to stop
parsing headers.

**Q8.1** **`Content-Type`**. `text/html` → render the tags. `text/plain` → show them literally.
**Q8.2** **No** — Tomcat writes the status line and headers for you. You only write the body,
with `out.println`.

**Q9.1** Your **URL** (or your `url-pattern`). A 404 means your code was never reached.
**Q9.2** The **Eclipse console** — read the *first* line of the stack trace.

**Q10.1** **No.** POST only keeps data out of the URL; the body is still plain text. Only
**HTTPS** encrypts.
**Q10.2** A search is a **GET** — the whole request is one URL, so the URL alone can reproduce
it. A checkout is a **POST** — the data is in the body, which is not part of the URL, and
repeating it would charge you twice.
**Q10.3** `doPost`.

**Q11.1** `request` (`HttpServletRequest`).
**Q11.2** Because you never start it. The **container** creates it and calls its methods when a
matching request arrives — inversion of control.

**Q12.1** The **container**. It creates exactly one instance.
**Q12.2** You don't call the framework; the framework calls your code.

**Q13.1** `HttpServlet.service()` contains the if-ladder that dispatches to
`doGet`/`doPost`/etc. Overriding it breaks that dispatching. Override `doGet`/`doPost` instead.
**Q13.2** You used **`javax.servlet`** on Tomcat 10+, which needs **`jakarta.servlet`**. It
compiles but Tomcat doesn't recognise it as a servlet.

**Q14.1** `init()` runs **once**. `doGet()` runs **10 times**.
**Q14.2** **One.** One instance serves all requests, on many threads.

**Q15.1** It's an **instance field** on a single shared object, so all users' threads read and
write the same variable. One user can overwrite another's value mid-request.
**Q15.2** **Not dangerous.** It's `static final` — a constant, identical for everyone and never
modified. The rule is about *per-request* data.

**Q16.1** The identical **`<servlet-name>`** value in both blocks. It's just a nickname.
**Q16.2** `http://localhost:8080/Shop/product`

**Q17.1** The servlet specification **forbids** serving anything under `WEB-INF`. It's a
security feature — visitors must not be able to download your config or JARs.
**Q17.2** To **restart Tomcat**. `web.xml` is read only at startup.

**Q18.1** Because `action` may be `null`. `"login".equals(null)` returns `false` safely;
`null.equals("login")` throws `NullPointerException` → a 500 page.
**Q18.2** **405 Method Not Allowed.**

**Q19.1** You printed with **`System.out`** instead of the response's `PrintWriter`.
**Q19.2** Not at all — it's your **debugging channel**. Just never use it for content the user
needs to see. (In production, prefer a logging framework.)

**Q20.1** `setContentType("text/html")` is **missing**, or was called **after** `getWriter()`
(in which case it's silently ignored).
**Q20.2** **No** — and that's the problem. It fails **silently**, with no error at all.

**Q21.1** **`null`** — the names don't match, and matching is case-sensitive.
**Q21.2** `null` = the parameter **wasn't sent at all**. `""` = it **was** sent but the user left
the field **empty**. Two different situations.

**Q22.1** HTTP is a **text** protocol — only characters travel on the wire. There are no numeric
types to preserve, so everything arrives as a `String` and you convert it.
**Q22.2** Non-numeric text (`"abc"`), an **empty** string (`""`), and **`null`** (parameter
missing).

**Q23.1** Security. Telling an attacker *which* half was correct lets them confirm valid user
IDs. Real login pages are deliberately vague.
**Q23.2** The `catch (NumberFormatException e)` block around `Integer.parseInt`.

---

## Where to go next

**Part 2 — MVC Architecture & CRUD with JDBC** takes exactly this project and turns it into a
real application: five MVC packages, a Derby database, and a full product CRUD app — with the
servlet reduced to what a controller should actually be.

- `servlets-session2-theory-notes.md` — the written notes
- `servlets-session2-theory.html` — the slides
- `servlets-session2-lab.html` — the hands-on lab

**Keep your `ServletBasics` project.** Part 2 builds straight on top of it.

---

*Java Servlets Part 1 — Study notes & teaching guide · Purvam Prajapati, Faculty — AHD*
