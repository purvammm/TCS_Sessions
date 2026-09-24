# WordGlow — AWS Build & Share Challenge Submission Pack

**Author:** Purvam Prajapati · Faculty, Ahmedabad
**Challenge:** Build & Share Challenge, AWS User Community @ TCS
**Submission deadline:** 30 September 2026 · **Community launch (presentation):** 9 October 2026, Chennai
**Chosen idea:** `WordGlow: The Karaoke Reader` (Dyslexia Accessibility) — themed idea, *not* bring-your-own

---

## 1. Why WordGlow is the right pick (read this before you submit)

Four of the five themed ideas (ClearCall, RouteWise, TriageCouncil, Guardian Watch) are the *same architecture* wearing different clothes: a Bedrock supervisor agent plus collaborator agents, a retrieval step, and trace logs. Expect the majority of submissions to cluster there, and expect them to look interchangeable on a review sheet — and to demo as a wall of text on stage.

WordGlow is the outlier, and that is an advantage on every axis that decides this:

| Axis | Why WordGlow wins |
|---|---|
| **Differentiation at review** | It is the only idea with a *hard, verifiable engineering problem* at its centre — millisecond word-level audio/text synchronisation. There is a right answer and a wrong answer, so a strong submission is visibly strong. |
| **Stage demo (9 Oct, Chennai)** | Photograph a real textbook page from the podium; ~20 seconds later the page is re-typeset and reads itself aloud with each word lighting up. That is a 90-second demo that lands with a non-technical audience instantly. The agent ideas cannot be demoed in 90 seconds. |
| **Single-builder feasibility** | Linear pipeline, six managed services, no multi-agent non-determinism to debug under time pressure. Realistically buildable and *polishable* by one person. |
| **Credits constraint** | The Amazon-only foundation model rule (Titan/Nova) hurts the reasoning-heavy agent ideas most, because their entire output quality is the model's reasoning. WordGlow's heavy lifting is Textract and Polly; Nova Lite/Micro is used for narrow, schema-constrained judgment calls, which is exactly what a small, cheap model is good at. Constraint becomes a design fit, not a handicap. |
| **"AI for good" credibility** | A child either can or cannot read the page. The benefit is immediate, personal and non-abstract — no speculative chain between the software and the good it does. |
| **Risk of looking naive** | Low. The reviewers' own bullet list ("applied deliberately rather than as a single cosmetic adjustment", "output text accurately matching the source") signals they have already seen shallow attempts. Section 5 below is engineered to answer exactly those two suspicions. |

**Decision: pick the themed WordGlow idea, answer "NA" for the bring-your-own field, and put all differentiation into the Solution Approach field.** Bring-your-own carries the extra burden of selling the problem itself; the themed track lets you spend every character proving you can *build* it.

---

## 2. Copy-paste answers for the registration form

> Forms: [Google Form](https://forms.gle/FZJxb75E4Bx5ZhX67) · [Microsoft Form](https://forms.cloud.microsoft/r/ZtEAx2XyLQ)

**Q1. Employee Name**
```
Purvam Prajapati
```

**Q2. Employee ID** — numbers only
```
<your 7-digit TCS employee ID, digits only, no letters or prefix>
```

**Q3. TCS Email ID** — must NOT be the `empid@tcs.com` format
```
<firstname.lastname@tcs.com — your named alias, not the numeric one>
```

**Q4. Work Location**
```
Ahmedabad
```
*(Confirm against your allocation record — write the location exactly as HR lists it, e.g. "Ahmedabad, Gujarat" or the specific campus name if that is the convention in your unit.)*

**Q5. Choose Your Idea**
```
WordGlow: The Karaoke Reader
```

**Q6. Bring your own idea description (max 2000 characters)**
```
NA
```

**Q7. Solution Approach Description** — use **Version A** below (**1,997 characters**, verified safe for a hidden 2000-char cap). If the field visibly accepts more, use **Version B** (**4,336 characters**).

### Version A — 1,997 characters (verified by character count)

```
WordGlow turns a phone photo of a page into a dyslexia-friendly, karaoke-narrated reader. A Step Functions pipeline:

1) Presigned S3 upload; Amazon Textract (DetectDocumentText + LAYOUT) extracts text with reading order.
2) Deterministic code rebuilds paragraphs, repairs hyphenated line-breaks, strips page furniture.
3) Amazon Nova Lite on Bedrock makes only bounded judgment calls - ranking candidate OCR corrections from a constrained list, choosing syntactic phrase boundaries, flagging hard words - returning strict JSON under Guardrails. It never rewrites content.
4) A typesetter applies a cited typography policy as versioned JSON: sans-serif, 1.5x leading, wider letter and word tracking (Zorzi, PNAS 2012), 45-60 character lines broken at phrase boundaries, off-white ground, left-aligned, bold-only emphasis, no italics. Dyslexia-specific fonts are opt-in, not default: their controlled evidence is weak, the spacing evidence strong.
5) Amazon Polly (neural, en-IN) synthesises from SSML in which we place our own <mark> before every token, so the returned speech marks give an exact token-to-millisecond map that survives Polly normalising "Dr." or "1947", the failure that breaks naive karaoke sync. The same chunk boundaries insert SSML breaks, so audio and visual chunking agree.
6) A fidelity gate computes word error rate between the Textract transcript and the rendered page, withholding pages above 0.5% WER or missing a mark.

A static CloudFront player: requestAnimationFrame binary-searches the marks array against audio.currentTime, so highlighting cannot drift. It dims inactive lines, allows tap-to-seek, and 0.6-1.25x speed. DynamoDB holds reader preferences; pages export as one offline HTML file for low-bandwidth schools.

Deliverable: three pages - a textbook page, a two-column worksheet, a school notice - with measured OCR WER, sync offset in ms, chunk-boundary agreement against a human, and cost per page. Amazon models only, so usage stays inside the credits.
```

### Version B — 4,336 characters (use only if the field accepts more than 2000)

```
WordGlow converts a photographed page into a dyslexia-friendly, karaoke-narrated reader, built as a serverless AWS pipeline. Three design commitments separate it from a cosmetic reformatter.

FIDELITY IS MEASURED, NOT CLAIMED. A child cannot detect a hallucinated word in their own homework, so no generative step is permitted to author text. The foundation model may only select from a constrained list of candidate corrections, and a final gate computes word error rate between the raw Textract transcript and the rendered page. Above 0.5% WER, or if any rendered token lacks a timing mark, the page is withheld and routed to a teacher review queue rather than shipped. Every page carries a verification report.

SYNCHRONISATION IS ANCHORED, NOT GUESSED. Naive karaoke readers split text on whitespace and pair token N with Polly speech mark N. This drifts the moment Polly normalises text: "Dr." becomes two spoken words, "1947" becomes four, an abbreviation collapses to one. WordGlow instead emits SSML with its own <mark name="t0147"/> tag before every token (between words, never mid-word, to avoid inserted pauses) and requests ssml, word and sentence speech mark types. Polly returns our identifiers with millisecond offsets, giving an exact, normalisation-proof token-to-time map. Because the neural engine supports custom tags and generative voices do not expose speech marks, the engine choice is a constraint, not a preference.

TYPOGRAPHY IS A CITED POLICY, NOT A STYLE TWEAK. Rules live in a versioned JSON ruleset, each with its source: sans-serif face; 1.5x leading; increased letter and word tracking (Zorzi et al., PNAS 2012, where extra-large letter spacing roughly doubled accuracy and raised speed over 20% in dyslexic children aged 8-14); 45-60 character measure; left-aligned, never justified; bold-only emphasis, no italics; warm off-white ground at WCAG AA contrast. Specialised dyslexia fonts are offered as a toggle but are not the default, because the controlled evidence for them is weak (Wery and Diliberto, 2017) while the spacing evidence is strong - the honest position, and the one that answers "deliberately rather than cosmetically".

PIPELINE. Presigned S3 upload triggers a Step Functions workflow: Textract DetectDocumentText with LAYOUT for text, reading order and geometry; a deterministic structurer that rebuilds paragraphs, repairs hyphenated line breaks, removes headers and page numbers, and preserves lists and headings; a Bedrock step on Amazon Nova Lite under Guardrails, called three times with strict JSON schemas, to rank OCR corrections, pick syntactic phrase boundaries, and flag tier-2 vocabulary for an optional side glossary that never replaces source text; a typesetter that applies the policy and breaks lines at those phrase boundaries; a Polly neural synthesis step producing both MP3 and speech marks from marked-up SSML, where the same chunk boundaries also place SSML breaks so auditory and visual chunking agree; and the fidelity gate. Artefacts land in S3, state and preferences in DynamoDB, traces in CloudWatch and X-Ray.

PLAYER. A static S3 and CloudFront page. requestAnimationFrame binary-searches the marks array against audio.currentTime, so highlighting cannot drift the way setTimeout chains do; times divide by playbackRate for 0.6-1.25x pitch-preserved slowdown. The current word is highlighted, non-active lines dimmed to a focus line, and tapping any word seeks the audio to it, making the sync bidirectional. Keyboard-only operation, prefers-reduced-motion support, and a one-file offline HTML export for low-bandwidth schools.

PRIVACY. Photographed schoolwork can carry a child's name, so uploads carry a 24-hour S3 lifecycle expiry, a DynamoDB TTL, and a flag-and-mask option for detected names, in line with DPDP Act 2023 expectations for children's data.

EVIDENCE. The build ships with three real pages - a Std-5 English textbook page, a two-column worksheet with boxed questions, and a school notice - and a metrics table: OCR WER per page, mean and worst-case sync offset in milliseconds against hand annotation, chunk-boundary agreement with a human annotator, end-to-end latency, and cost per page (about one cent). Models used are Amazon's own Nova family only; no third-party foundation models, so all usage stays within the provided credits.
```

---

## 3. The problem, framed the way a reviewer will respect

Specific Learning Disability is a recognised disability under India's **Rights of Persons with Disabilities Act, 2016**, and prevalence estimates for SLD among Indian school children commonly fall in the **5–15%** band depending on study and screening instrument. In a 40-child classroom that is realistically two to six children.

The lived failure is mundane and daily:

- The textbook is a fixed artefact. Its 10pt type, tight leading, justified columns and 90-character lines cannot be changed by the child, the parent or the teacher.
- Accommodations that do exist (a human reader, a scribe, extra time) are rationed to examinations. **Homework on a Tuesday night has no accommodation.**
- Existing help is either a plain screen reader — audio with no visual anchor, so the child never practises print — or a "dyslexia font" plugin that only works on web pages the child was already able to open, never on the physical page in front of them.

Reading-while-listening with the spoken word visually anchored is the specific intervention that keeps the child's eyes on print instead of replacing print. **WordGlow's contribution is that it starts from a photograph** — the actual object the child is stuck on — and it does so without editing what the page says.

---

## 4. Architecture

```
  Parent / teacher phone                      Static reader (S3 + CloudFront)
        │  photo                                      ▲  reader.json + mp3 + marks.json
        ▼                                             │
  ┌───────────────┐   presigned PUT    ┌──────────────┴───────────┐
  │ API Gateway   │ ─────────────────► │  S3  ingest/ → output/   │
  │  + Lambda     │                    └──────────┬───────────────┘
  └───────────────┘                               │ ObjectCreated (EventBridge)
                                                  ▼
                            ┌──────────────────────────────────────────────┐
                            │        AWS Step Functions  (Standard)        │
                            ├──────────────────────────────────────────────┤
   ①  OCR                   │ Textract DetectDocumentText + LAYOUT         │
                            │   → words, lines, reading order, geometry    │
   ②  Structure (deterministic) │ paragraphs, de-hyphenate, strip furniture│
   ③  Judgment (Bedrock)    │ Amazon Nova Lite ×3, strict JSON, Guardrails │
                            │   a. rank OCR correction candidates          │
                            │   b. choose syntactic phrase boundaries      │
                            │   c. flag hard words → side glossary         │
   ④  Typeset               │ apply typography-policy.json → reader.json   │
   ⑤  Speak                 │ build SSML with <mark> per token →           │
                            │ Polly neural ×2  → page.mp3 + marks.json     │
   ⑥  Fidelity gate         │ WER(Textract, rendered) ≤ 0.5%  AND          │
                            │ every token has a mark  → else REVIEW queue  │
                            └───────────────┬──────────────────────────────┘
                                            ▼
                    DynamoDB  documents · pages · reader-prefs · review-queue
                    CloudWatch Logs + X-Ray traces across every state
```

### Stage detail

| # | Stage | Service | What it actually does |
|---|---|---|---|
| ① | OCR | **Amazon Textract** | `DetectDocumentText` for printed pages; `AnalyzeDocument` with `LAYOUT` where columns, headings or boxed questions need reading-order recovery. Returns per-word confidence and bounding boxes — both are used downstream. |
| ② | Structure | Lambda (Python) | Pure deterministic code, no model: joins lines into paragraphs using geometry, repairs `pro-` / `gramme` hyphenated breaks against a dictionary check, drops running headers and page numbers by position, keeps list and heading roles from LAYOUT blocks. |
| ③ | Judgment | **Bedrock — Amazon Nova Lite** (Micro for the cheap calls) | Three narrow, schema-bound calls. The model never sees a "rewrite this" instruction: it *selects* among candidates, *marks* boundaries, and *labels* vocabulary. Bedrock Guardrails plus a deterministic post-check reject any response that alters token content. |
| ④ | Typeset | Lambda | Loads `typography-policy.v1.json`, emits `reader.json`: `{blocks:[{role, lines:[[{id,text}]]}]}` — lines already broken at the phrase boundaries from ③, respecting the character-measure rule. |
| ⑤ | Speak | **Amazon Polly**, neural engine, `en-IN` | Two calls on identical SSML: one `OutputFormat=mp3`, one `OutputFormat=json` with `SpeechMarkTypes=[ssml, word, sentence]`. SSML carries `<mark name="tNNNN"/>` before each token and `<break>` at chunk boundaries. |
| ⑥ | Verify | Lambda | Normalising WER between the Textract transcript and the rendered reader text; coverage check that every token id appears in `marks.json`; writes `verification.json`. Failure routes the page to a human review queue instead of publishing. |

**Frontend:** plain HTML/CSS/JS on S3 behind CloudFront — the same self-contained-HTML discipline used throughout this repository, so there is no build toolchain to fail on demo day.

---

## 5. The three hard problems, and the answers that win the review

The reviewers' bullet list contains two tells: *"applied deliberately rather than as a single cosmetic adjustment"* and *"with the output text accurately matching the source."* They have seen shallow versions of this. Each of the following exists to close one of those doors.

### 5.1 Word-level sync that does not drift — self-anchored SSML marks

**The naive approach, which nearly everyone will submit:** split the display text on whitespace, request `word` speech marks, pair token *N* with mark *N*.

**Why it breaks:** Polly speaks normalised text, not your tokens.

| Display token | Spoken as | Marks produced |
|---|---|---|
| `Dr.` | "Doctor" | 1 |
| `1947` | "nineteen forty-seven" | 2–4 |
| `12.5 km` | "twelve point five kilometres" | 4–5 |
| `don't` | "dont" | 1 |

One such token on the page and every subsequent highlight is offset by one word — visible, and fatal on stage.

**WordGlow's answer:** emit SSML where *we* place the anchors.

```xml
<speak>
  <prosody rate="92%">
    <mark name="t0001"/>The <mark name="t0002"/>monsoon <mark name="t0003"/>winds
    <break time="250ms"/>
    <mark name="t0004"/>reach <mark name="t0005"/>Kerala <mark name="t0006"/>in
    <mark name="t0007"/>June<mark name="t0008"/>.
  </prosody>
</speak>
```

Polly returns *our* identifiers with millisecond offsets, so the mapping is exact regardless of how the text was normalised. Two documented constraints shape this and are worth stating in the writeup because they prove first-hand knowledge:

- The custom `<mark>` tag is supported by the **standard, neural and long-form** engines; **generative voices do not expose speech marks at all** ([Polly docs — custom tag](https://docs.aws.amazon.com/polly/latest/dg/custom-tag.html)). Neural `en-IN` is therefore the correct engine, not merely a preference.
- Marks must sit **between words, never inside one**, or an unintended pause can be introduced ([AWS re:Post](https://repost.aws/questions/QUp-ry1Z-cT-Cu7jkplQmkOg/polly-mark-tag-changes-the-pronunciation)). The SSML builder enforces this.

**Player side:** never chain `setTimeout`. Each animation frame, binary-search the sorted marks array against `audio.currentTime * 1000 * playbackRate`. Drift becomes structurally impossible; scrubbing and tap-to-seek work for free because the map is bidirectional.

### 5.2 Fidelity that is measured, not asserted

Hallucinating a word into a dyslexic child's homework is the one unrecoverable failure: the child, by definition, cannot audit it.

- **No generative authoring.** Nova is never asked to produce text. For corrections it receives the OCR token, its confidence, and a small candidate list built deterministically (confusion pairs such as `rn/m`, `l/1`, `O/0`, plus dictionary neighbours) and must return a choice plus confidence. Anything outside the candidate list is rejected by code, not by trust.
- **A gate with a number.** Normalised WER between the Textract transcript and the final rendered text, thresholded at **0.5%**, plus 100% timing-mark coverage. Fail → the page goes to a review queue, not to a child.
- **A visible artefact.** Each page ships `verification.json`. On stage, showing a page the system *refused* to publish is more persuasive than three that worked.

### 5.3 Typography as a cited, versioned policy

The rules live in `typography-policy.v1.json`, each with a source, and the UI can show the rationale. This is the direct answer to "not a single cosmetic adjustment".

| Rule | Value | Grounding |
|---|---|---|
| Letter tracking | +0.08–0.12em, user-adjustable | [Zorzi et al., PNAS 2012](https://www.pnas.org/doi/10.1073/pnas.1205566109) — extra-large letter spacing roughly **doubled accuracy** and raised reading speed **>20%** in dyslexic children aged 8–14; the group × spacing interaction was significant, i.e. the benefit is dyslexia-specific |
| Word spacing | ≥ 3.5× letter spacing | Dyslexia style-guide convention (British Dyslexia Association guidance); prevents words fusing once tracking is increased |
| Line height | 1.5× type size | Standard accessible-typography guidance; reduces line-transition loss |
| Measure | 45–60 characters | Shorter lines reduce return-sweep errors; combined with chunking below |
| Alignment | Left, never justified | Justification creates irregular word-space "rivers" that disrupt tracking |
| Emphasis | **Bold only** | Italics and underline degrade letterform recognition |
| Ground | Warm off-white (`#FFFDF5`), tint selectable | Reduces glare; tint offered as preference, **not** claimed as therapy (Irlen-style overlay evidence is contested) |
| Chunking | Break at syntactic phrase boundaries; chunk = one focus unit | Phrase-cued / chunked-text evidence is **mixed** — some studies show comprehension gains, others no effect. So it is **on by default but toggleable, and measured** in the evaluation |
| Dyslexia-specific font | Offered, **not** default | [Wery & Diliberto, 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5629233/) found OpenDyslexic gave no rate or accuracy advantage over Arial or Times New Roman. Defaulting to it would be exactly the cosmetic gesture the brief warns against |

**Include the honest lines about mixed and negative evidence.** A submission that says "we default to the intervention with strong controlled evidence and make the popular-but-unproven one an opt-in toggle" reads as the work of someone who read the literature. That is rare in a hackathon field, and it is cheap to say truthfully.

**One coupling worth calling out:** the chunk boundaries chosen in stage ③ drive *both* the visual line breaks *and* the `<break>` placement in the SSML. Eye and ear are chunked identically. Most implementations chunk the text and let the audio run flat.

---

## 6. Requirement traceability — their bullets, your build

| Reviewer expectation | Where it is satisfied | Evidence you can show |
|---|---|---|
| Accepts a photographed/scanned page and extracts text accurately | Presigned S3 upload → Textract; ⑥ fidelity gate enforces accuracy | Phone photo taken live; `verification.json` WER per page |
| Performs an OCR step | Stage ① — Textract `DetectDocumentText` / `AnalyzeDocument` + `LAYOUT` | Raw Textract JSON alongside output |
| Reformats using established dyslexia-friendly typography, deliberately not cosmetically | Stage ④ against `typography-policy.v1.json`, every rule sourced (§5.3) | Side-by-side before/after; the policy file with citations; the "default is spacing, not a dyslexia font" argument |
| TTS with precise word-level timing driving the sync | Stage ⑤ — Polly neural, self-anchored SSML `<mark>` + `ssml`/`word` speech marks | `marks.json`; measured sync offset in ms against hand annotation |
| Foundation model supports judgment calls such as chunking | Stage ③ — Amazon Nova Lite, three schema-bound calls under Guardrails | Prompt + JSON response logs; chunk-boundary agreement vs. human annotator |
| Works end to end on 2–3 sample pages, output text matching source | Three prepared pages (§7) | Metrics table; live run of a fourth, unseen page |

---

## 7. Evaluation set and metrics

Three deliberately different pages, chosen so that each breaks a different naive assumption:

1. **Std-5 English textbook page** — flowing prose, an inset illustration with a caption, a running header. *Tests:* reading order, furniture removal, hyphenated line breaks.
2. **Maths/EVS worksheet** — two columns, numbered boxed questions, blank answer ruled lines, `12.5 km` style tokens. *Tests:* LAYOUT reading order, list preservation, and exactly the normalisation case that destroys naive sync.
3. **School notice / circular** — a date line, a dense single paragraph, a signature block, mild page skew from a handheld photo. *Tests:* skew tolerance, `Dr.`-style abbreviations, date normalisation.

Reported for every page:

| Metric | Target | How measured |
|---|---|---|
| OCR word error rate | ≤ 0.5% | Normalised WER vs. a hand-keyed ground-truth transcript |
| Timing-mark coverage | 100% | Every rendered token id present in `marks.json` |
| Sync offset, mean / worst case | ≤ 80 ms / ≤ 200 ms | Hand-annotate word onsets in Audacity for 30 sampled words; compare to mark times |
| Chunk-boundary agreement | ≥ 80% F1 | Nova's boundaries vs. a human annotator's phrase boundaries |
| End-to-end latency | ≤ 25 s for one page | Step Functions execution duration |
| Cost per page | ≈ ₹1 / \$0.01 | Cost Explorer with resource tags |

A metrics table beats adjectives. Almost nobody will bring one.

---

## 8. Cost — comfortably inside the credits

Per page of roughly 350 words / 2,000 characters (us-east-1 list prices; re-verify at build time):

| Component | Basis | Per page |
|---|---|---|
| Textract `DetectDocumentText` | ≈ \$1.50 / 1,000 pages ([pricing](https://aws.amazon.com/textract/pricing/)) | \$0.0015 |
| Bedrock — Amazon Nova Lite | ≈ \$0.06 / M input, \$0.24 / M output tokens; ~4K in, 1K out across 3 calls | ≈ \$0.0005 |
| Polly neural | \$16 / M characters; 2 calls (audio + marks) | ≈ \$0.032 |
| Step Functions, Lambda, S3, DynamoDB, API Gateway, CloudFront | negligible at demo volume | < \$0.001 |
| **Total** | | **≈ \$0.035 / page** |

Even 2,000 pages of development and testing lands near **\$70**. The dominant line is Polly, and the marks call can reuse a cached synthesis during iteration, roughly halving it.

**Credits compliance:** the only foundation model is **Amazon Nova** (Bedrock-native); Titan Text Embeddings only if a future retrieval feature is added. **No third-party Bedrock models are used anywhere in the pipeline**, so nothing falls outside the credit scope. Say this explicitly in the form — the note's prominence in the brief suggests past submissions ignored it.

---

## 9. Build plan once shortlisted

| Stage | Work | Exit criterion |
|---|---|---|
| **A — Spike the risk first** | Polly SSML `<mark>` round-trip: 300 words → MP3 + marks → a crude HTML highlighter | A word highlights on cue. *If this fails, everything downstream is worthless — so do it on day one.* |
| **B — Ingest + OCR** | Presigned upload, Textract, deterministic structurer, ground-truth transcripts for the 3 pages | WER measured and under target on all three |
| **C — Typography policy** | Write `typography-policy.v1.json` with citations; typesetter Lambda; before/after renderer | Side-by-side view of all three pages |
| **D — Nova judgment calls** | Three schema-bound prompts, Guardrails, deterministic rejection of any content-altering response | Chunk-boundary F1 vs. human annotation |
| **E — Player polish** | rAF + binary search, focus-line dimming, tap-to-seek, speed control, keyboard access, `prefers-reduced-motion` | Measured sync offset within target |
| **F — Fidelity gate + review queue** | WER + coverage gate, `verification.json`, deliberate failure case | One page correctly *refused* |
| **G — Offline export & demo prep** | Single-file HTML bundle; 90-second script; pre-baked fallback artefacts on the laptop | Full rehearsal with Wi-Fi switched off |

Sequencing note: **Stage A is the whole project's load-bearing wall.** Do not build UI before the marks round-trip works.

---

## 10. Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Venue Wi-Fi fails during the live demo | Fatal on stage | Pre-baked artefacts for 3 pages served from `localhost`; live capture is the *encore*, not the demo |
| Polly inserts pauses around `<mark>` | Unnatural, jerky narration | Marks strictly between tokens; A/B listen against unmarked synthesis; documented re:Post caveat |
| Handheld photo skew degrades OCR | Poor WER | Client-side deskew/crop guide before upload; Textract geometry used to detect skew and prompt a retake |
| Nova returns an off-schema or content-altering response | Fidelity breach | JSON-schema validation + candidate-list whitelist + WER gate; three independent layers, none relying on model goodwill |
| Chunking makes reading *worse* for some readers | Harm, not help | Toggleable, honestly reported as mixed-evidence, measured in the evaluation |
| Scope creep (multi-language, handwriting, a mobile app) | Nothing finished | Explicit non-goals below; printed English pages only for v1 |
| Child's name in a photographed worksheet | Privacy | 24-hour S3 lifecycle expiry, DynamoDB TTL, optional name masking, no training on uploads; framed against **DPDP Act 2023** expectations for children's data |

---

## 11. Non-goals (state them — it signals judgment)

- Not a diagnostic or screening tool for dyslexia. It reformats and narrates; it never assesses the child.
- No handwriting recognition in v1 — printed pages only.
- No paraphrasing, simplification or summarising of the source text. Hard words get a *side* glossary; the sentence the teacher wrote stays the sentence the child reads.
- English only for v1; the architecture allows other Polly-supported languages, but sync quality must be measured per language before claiming it.

---

## 12. The 90-second stage demo (9 Oct, Chennai)

1. **0:00** Hold up a real Std-5 textbook page. *"Two to six children in a forty-child classroom cannot read this page — not because they can't read, but because of how it is set."*
2. **0:10** Photograph it. Upload.
3. **0:15** While it processes, show the before/after typography split and name one grounded rule: *"letter spacing — this one roughly doubled reading accuracy in a PNAS study of dyslexic children."*
4. **0:35** Audio plays. Words light up in time. **Say nothing for eight seconds and let the room watch.**
5. **0:50** Tap a word mid-paragraph — audio jumps there. *"The sync is a map, not a timer."*
6. **1:05** Show `verification.json`: 0.0% WER. Then show the page the system **refused** to publish. *"It would rather hand a page back to a teacher than guess a word in a child's homework."*
7. **1:20** Close on the offline export. *"One HTML file. It works in a school with no bandwidth."*

Beat six is what people remember. A system that knows when to stop reads as engineering, not as a demo.

---

## 13. References

- [Amazon Polly — Speech marks](https://docs.aws.amazon.com/polly/latest/dg/speechmarks.html) and [custom `<mark>` tag support by engine](https://docs.aws.amazon.com/polly/latest/dg/custom-tag.html) — confirms `<mark>` works on standard/neural/long-form and that generative voices do not expose speech marks
- [AWS re:Post — `<mark>` placement and unintended pauses](https://repost.aws/questions/QUp-ry1Z-cT-Cu7jkplQmkOg/polly-mark-tag-changes-the-pronunciation)
- [Amazon Textract pricing](https://aws.amazon.com/textract/pricing/) · [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- Zorzi, M. et al. (2012). *Extra-large letter spacing improves reading in dyslexia.* PNAS — [paper](https://www.pnas.org/doi/10.1073/pnas.1205566109), [authors' reply on effect size and group interaction](https://www.pnas.org/doi/10.1073/pnas.1213265109)
- Wery, J. & Diliberto, J. (2017). *The effect of a specialized dyslexia font, OpenDyslexic, on reading rate and accuracy* — [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5629233/)
- [Letter spacing and coloured overlays in adult dyslexia](https://pubmed.ncbi.nlm.nih.gov/27629067/) — spacing helps speed generally and accuracy in dyslexic readers
- Phrase-cued / chunked text: [ERIC ED313689](http://files.eric.ed.gov/fulltext/ED313689.pdf) (facilitative for readers still developing syntactic sensitivity) and [ERIC ED029763](http://files.eric.ed.gov/fulltext/ED029763.pdf) (no significant difference) — the basis for treating chunking as toggleable and measured
- Rights of Persons with Disabilities Act, 2016 (India) — SLD as a recognised disability; Digital Personal Data Protection Act, 2023 — children's data

*Source material was paraphrased and condensed; figures should be re-verified against the linked primary sources before quoting them in a live presentation. Content was rephrased for compliance with licensing restrictions.*
