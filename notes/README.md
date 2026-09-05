# Spring Boot — Study Notes

Written-out study notes for the four Spring Boot theory sessions, by **Purvam Prajapati** (Faculty, AHD).

The HTML files in the repository root are **slide decks** and **lab sheets** — built for presenting and for following along at a keyboard. These Markdown files are the same material written as **prose you can learn from**, and then **teach from**.

---

## Start here

| # | Session | Notes | Slides | Lab |
|---|---|---|---|---|
| 1 | **Spring Boot Foundations** | 📄 [session-1](session-1-spring-boot-foundations.md) | [`springboot-session1-theory.html`](../springboot-session1-theory.html) | [`springboot-session1-lab.html`](../springboot-session1-lab.html) |
| 2 | **REST APIs & Web Services** | 📄 [session-2](session-2-rest-apis.md) | [`springboot-session2-theory.html`](../springboot-session2-theory.html) | [`springboot-session2-lab.html`](../springboot-session2-lab.html) |
| 3 | **Databases, DTOs & Exception Handling** | 📄 [session-3](session-3-data-jpa-dtos-exceptions.md) | [`springboot-session3-theory.html`](../springboot-session3-theory.html) | [`springboot-session3-lab.html`](../springboot-session3-lab.html) |
| 4 | **Microservices with Spring Cloud** | 📄 [session-4](session-4-microservices-spring-cloud.md) | [`springboot-session4-theory.html`](../springboot-session4-theory.html) | [`springboot-session4-lab.html`](../springboot-session4-lab.html) |

**Read them in order.** Each session removes a constraint the next one relies on — Session 2's *statelessness* and Session 3's *shared database* are exactly what make Session 4's load balancing possible.

---

## What's in each file

Every file follows the same shape, so you always know where to look:

| Section | What it's for |
|---|---|
| **How to use this file** | Reading order, and where to jump if you're preparing to teach |
| **What you'll be able to do** | The concrete outcomes for that session |
| **Numbered parts** | The material itself — plain English first, jargon second |
| **Recap and self-test** | A one-page summary, cheat sheets, and click-to-reveal questions |
| **Glossary** | Every term defined in one line |
| **Teaching this session** | ⭐ Timing plan, the demos that matter, and the questions your associates will actually ask |

### Notation used throughout

| Marker | Meaning |
|---|---|
| 💡 **Idea** | The plain-English concept, before any jargon |
| 📖 **The word for it** | The official term, once you understand the idea |
| 🔬 **Try it** | A hands-on experiment — these are where understanding sticks |
| ⚠️ **Trap** | A mistake beginners genuinely make |
| 🎓 **Teach this** | A note for when you're the one explaining it |

---

## If you're learning this for the first time

1. **Read one session per sitting**, in order. Don't skip Part 1 of Session 1 even if you know Java — it defines four words the rest of the series leans on.
2. **Do the 🔬 Try it experiments.** Especially the *break-it-on-purpose* ones. Deliberately causing an error and reading the message teaches more than any explanation.
3. **Use the self-test at the end.** The answers are hidden behind click-to-reveal toggles. If you can't answer out loud, re-read that part.
4. **Then do the lab** for that session before moving on.

## If you're preparing to teach

1. **Read the whole session end to end first**, then go to **Teaching this session** at the bottom.
2. That section gives you a **minute-by-minute timing plan**, the **three or four demos that matter most**, an **emphasis guide** (what to dwell on, what to skim), and the **questions your associates will actually ask** — with answers.
3. **Run the demos yourself before the session.** They're chosen because they convert abstract ideas into things people can see.

---

## The single most important thing in these notes

> ## 🔑 The Golden Rule
> **Every class you create must live in the same package as the main class, or in a sub-package of it.**

Break it and Spring never finds your class. The app starts with **no error at all**, and every request returns a **404 Whitelabel Error Page**.

This is the #1 cause of lost time for beginners, and it has a subtle root cause: **Spring Initializr builds your package name by joining Group + Artifact and stripping hyphens**, so the two fields you type produce a third value you didn't type.

| Group you type | Artifact you type | Package you actually get |
|---|---|---|
| `com.tcs.training` | `demo` | `com.tcs.training.demo` |
| `com.tcs.training` | `student-api` | `com.tcs.training.studentapi` ⚠️ |
| `com.tcs.training` | `eureka-server` | `com.tcs.training.eurekaserver` ⚠️ |

**The five-second check:** open the main class, read line 1. Whatever the `package` line says **is** your base package — regardless of what you expected.

It's covered in full in [Session 1, Part 5](session-1-spring-boot-foundations.md#part-5--the-entry-point-and-the-golden-rule).

---

## Base packages used by the labs

Each session uses a fresh project. Note them down as you go:

| Session | Group | Artifact | Base package |
|---|---|---|---|
| 1 | `com.tcs.training` | `demo` | `com.tcs.training.demo` |
| 2 | `com.tcs.training` | `students` | `com.tcs.training.students` |
| 3 | `com.tcs.training` | `posts` | `com.tcs.training.posts` |
| 4 | `com.tcs.training` | `eureka-server` | `com.tcs.training.eurekaserver` |
| 4 | `com.tcs.training` | `student-ms` | `com.tcs.training.studentms` |
| 4 | `com.tcs.training` | `customer-ms` | `com.tcs.training.customerms` |
| 4 | `com.tcs.training` | `api-gateway` | `com.tcs.training.apigateway` |

---

## A note on the diagrams

These files use [Mermaid](https://mermaid.js.org/) diagrams, which **GitHub renders automatically** — you'll see real flowcharts and sequence diagrams, not code blocks.

If you're reading in an editor that doesn't support Mermaid, the surrounding prose always explains the same thing in words, so nothing is lost.

---

*Spring Boot Training Series · Presenter: **Purvam Prajapati**, Faculty — AHD*
