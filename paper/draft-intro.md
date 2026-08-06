# Draft: Introduction Sections (IEEE ISCAS — Education Track)

> Scope of this draft: **problem statement**, **prior work**, **motivation**, and **contributions**. Methods / evaluation to follow once experiments are defined.
>
> **Positioning:** the artifact is a **reusable open-source platform** (engine + content contract + authoring path + planned question→video skill). It is designed to plug into the [Digital Design and Verification (DDV) open learning platform](https://universal-verification-methodology.github.io/learning/) (guided labs, tools shelf, browser HDL simulation, courses map). **Digital foundations** is the ISCAS use case and reference content pack—not the product boundary. Adopters `git clone` / `git pull`, replace module question banks, and run the same quest UX for other topics.
>
> **Status honesty:** the adaptive blind-quest runtime and authoring path are in progress; **question-to-video stem generation** (skill that turns a bank item into a short explainer video with an embedded circuit/figure image) is a planned core integrity feature—not yet complete. This draft treats it as a first-class contribution of the overall system.

### Title candidates (pick one)

1. An Open-Source Adaptive Quiz Challenge Platform for Integrity-Aware Learning: A Digital Circuits Case Study
2. Blind Adaptive Quizzing Against Generative-AI Shortcuts: An Open Platform Demonstrated in Digital Circuits Education
3. A Content-Agnostic Open-Source Quiz Challenge Engine for Circuits and Systems Education Under Generative AI
4. Friction-Oriented Online Assessment for STEM Courses: An Open Adaptive Quest Platform with a Digital Foundations Use Case
5. Reusable Blind-Quest Assessment for Module-Based Learning: Open-Source Design and Digital Circuits Demonstration
6. Video-Stem Adaptive Quizzing for Anti-AI Assessment: An Open Platform Integrated with Digital Design Learning
7. From Text Banks to Video Stems: An Open Quiz Challenge Platform for Circuits Education Under Generative AI

> **Selected title:** *(none yet — replace this line when chosen)*

---

## 1. Problem Statement

Web-based quizzes are widely used across STEM courses because they scale, support hybrid and self-paced study, and give instructors modular coverage of a syllabus. In circuits and systems education, they often sit beside labs and tools—as on the [DDV open learning platform](https://universal-verification-methodology.github.io/learning/), which already offers guided labs, a shared tools shelf, browser HDL simulation, and a courses map. Two pressures undermine quiz value today.

**Assessment integrity under generative AI.** Large language models (LLMs) can answer many textbook-style, **copy-pasteable text** items in seconds. When a quiz shows the full stem as selectable HTML text, reveals correctness immediately, exposes a fixed module path, or imposes no meaningful time pressure, a student can copy the question into a chat agent, obtain an answer, and progress without engaging the concept. Conventional LMS quizzes and lightweight self-checks were designed for answer-key sharing and search engines; they are poorly matched to conversational AI.

**Copy-to-AI is the dominant casual attack.** Surveillance and LLM-output detectors are brittle and harmful to learning experience. A more practical lever is to **change the stem medium**: present the question primarily as a short **video that narrates the prompt and shows a circuit (or other figure) on screen**, so there is no clean text block to select and paste. This does not stop screenshots or multimodal models, but it raises the cost of the common workflow—copy from the page → paste into an AI agent—while keeping assessment inside the same browser learning ecosystem.

**Learning experience vs. integrity trade-off.** Hard proctoring worsens anxiety and accessibility; open formative quizzes with instant feedback invite AI-assisted completion. Educators need formats that (i) keep students in an interactive loop, (ii) raise the cost of casual AI use without claiming perfect prevention, (iii) return rich post-attempt analytics, and (iv) **reuse existing course modules and media conventions** rather than forcing a separate exam silo.

**Platform gap.** Integrity-oriented tools are often course-specific, closed, or LMS-locked. Instructors who want challenge-style quizzes—and especially **video stems at bank scale**—cannot easily reuse an engine or generate media from JSON items. The open problem is: *how to provide an open, content-agnostic adaptive quiz challenge, integrated with an existing open learning platform, that educators adopt by replacing module banks and (via a skill) converting items into video stems that explain the question with circuit imagery—improving engagement while increasing friction against copy-to-AI—with a digital circuits demonstration for ISCAS and a documented path for other domains.*

---

## 2. Prior Work

Prior art falls into several strands relevant to online assessment and circuits education (our demonstration domain).

**Open learning platforms and CAS tutoring.** Web platforms for digital design and verification literacy (labs, tools, simulation) improve practice and access—exemplified by client-side open learning sites such as the [DDV platform](https://universal-verification-methodology.github.io/learning/). Circuit tutors and topology-randomized practice systems improve scaffolding. Challenge-based digital courses have appeared at ISCAS. These efforts strengthen *delivery and practice*; they rarely ship a separable **blind quest** layer plus a **bank→video** authoring skill aimed at generative-AI paste resistance.

**Integrity via problem uniqueness and remote labs.** Remote-lab and AI-immunity work assigns unique circuits or measured responses so fabricated answers fail instructor checks. Topology randomization reduces answer sharing. Strong for lab authenticity; less a drop-in quiz + video-stem pipeline for module taxonomies shared with an open learning site.

**Multimedia and video in assessment.** Instructional video is common for *teaching*; using **per-item stem videos** (prompt narration + on-screen schematic) as the primary assessment channel—to deny easy text copy—is less standardized, especially when coupled with automated conversion from structured question JSON and download-friction playback in-browser.

**Adaptive testing and mastery learning.** CAT and quest-style clearance adjust length and difficulty. Few lightweight open runtimes combine hidden randomized modules, silent grading, bounded per-difficulty clearance, timed items, **video stems**, and post-quest analytics as one integrity-aware package instructors can retarget by editing content packs.

**AI detection and proctoring.** Complementary but not our focus: we prioritize **friction during the attempt** (non-text stems, timing, no mid-quest key) and **learning after the quest**.

**Gap.** We do not find a published open stack that jointly offers (1) a reusable blind adaptive quiz engine, (2) integration path into an open CAS learning platform (labs/tools/courses), (3) a documented content-replacement workflow for new topics, (4) a **question-to-video skill** that produces explainer stems with circuit/figure imagery to impede copy-to-AI, and (5) report-only feedback with telemetry, certificates, and optional leaderboards—demonstrated on digital foundations for ISCAS.

*(Citation placeholders — replace with formal IEEE references before submission.)*

---

## 3. Motivation

Five observations motivate this work.

1. **We already have an open learning home.** The challenge layer should **tap** the [DDV learning platform](https://universal-verification-methodology.github.io/learning/)—same course/module ids, quiz schema affinity, media URL conventions, and eventual merge under the platform’s challenge entry point—so students move from labs/tools into a quest without a disconnected exam site.

2. **Text stems are the weak link under generative AI.** Timing and deferred feedback help, but selectable HTML prompts remain trivial to paste. **Video stems** that *explain the question* (audio/on-screen text briefly) while showing a **circuit or figure** force visual attention and break one-click copy. Residual risk (screen capture, multimodal LLMs) must stay explicit.

3. **Video at bank scale needs a skill, not hand-editing alone.** Challenge banks are large (e.g., tens of items per difficulty). A **Cursor/agent skill** (and/or scripted pipeline) that converts structured items → short videos (narration + circuit image composite) is what makes integrity-oriented media maintainable when adopters replace questions for new modules or topics.

4. **Immediate correctness feedback helps AI more than struggling learners in a multi-module quest.** Silent grading during the run and a full analytical report afterward preserve challenge continuity and yield a learning artifact.

5. **Adoption should be content replacement (+ optional media generation), not a rewrite.** Clone/pull, edit banks, run the skill for video stems, serve or merge into the learning platform—matching how open educational resources are reused across STEM, with circuits as the ISCAS showcase.

Together, these motivate an open-source adaptive quiz challenge platform—**content-agnostic**, **DDV-integrated**, with **question→video** as a planned first-class anti-copy mechanism—demonstrated on digital foundations for ISCAS.

---

## 4. Contributions

This paper and the accompanying open-source repository aim to make the following contributions:

1. **Open platform framing.** Generative-AI pressure on module-mapped quizzes as a *learning-experience + integrity* co-design problem; a **reusable challenge runtime** under a clear content contract, not a single-course quiz site.

2. **Integration with the DDV open learning platform.** Align course/module identifiers and quiz-item schema with the live [Digital Design and Verification learning platform](https://universal-verification-methodology.github.io/learning/); design for merge into the platform’s challenge path so labs (immediate formative feedback) and the blind quest (report-only) coexist.

3. **Blind adaptive quest architecture (course-agnostic).** Randomized hidden module order; within-module **easy → medium → hard** clearance (**one correct** to clear, **≤10 unique attempts**, banks sized to avoid repeats); silent grading (`report_only`).

4. **Anti-AI friction stack (honest residual risk).**
   - **Planned / in progress — question-to-video skill:** convert bank items into short stem videos that **explain the question** and **embed a circuit (or topic figure) image**, so students cannot trivially select-and-copy the prompt into an AI agent; playback with download friction (no easy save-as); captions retained for accessibility where feasible.
   - **Shipped / prototype — session friction:** difficulty-dependent time limits, timeouts as incorrect, timers that keep counting when the tab is hidden, dwell-to-lock selection, media policy flags.

5. **Post-quest learning loop.** Session telemetry and an analytical report (metrics, module breakdowns, explanations, attempt-path visualization).

6. **Incentives and privacy-aware results pipeline.** Optional certificate claim with consent, server-side archival, masked leaderboard with composite benchmark score.

7. **ISCAS use case + adopter path.** Digital foundations pack (radix, K-maps, setup/hold) as the circuits demonstration; [authoring instructions](../docs/AUTHORING.md) so others replace banks for other topics and (when the skill lands) regenerate video stems for the new items.

---

## 5. Planned work: question → video skill (detail for Methods later)

| Step | Intent |
|------|--------|
| Input | Item JSON (`prompt`, choices, optional figure/circuit asset or generation hint) |
| Compose | On-screen layout: circuit/figure + concise question wording (possibly burned in briefly or spoken only) |
| Narrate | Short voiceover that **states/explains the question** (not the answer) |
| Encode | Per-item `media.type: "video"` stem referenced from the bank |
| Serve | Challenge player plays video in-quest; discourage download; timer runs as configured |
| Adopter UX | After editing banks, run the skill (or batch script) before publishing a quest |

**Design principle:** deny the default copy-paste path; do **not** claim immunity to screen recording or multimodal models.

**Accessibility:** prefer captions/subtitles; avoid relying on video-only information that cannot be perceived another way when institutional policy requires it (document trade-offs in the paper).

---

## Notes for the next drafting pass

- **Claims to keep honest:** friction / deterrence via video stems + timing + deferred feedback; not “prevents all AI use.” Mark video skill as **planned** until implemented.
- **ISCAS fit:** education track + tie-in to open CAS learning tools; DDV platform as the living integration target.
- **Paper artifacts:** learning site URL, challenge repo, `docs/AUTHORING.md`, skill spec / demo clip (question video with circuit image), before/after (text stem vs video stem) figure.
- **Evaluation ideas:** (a) time/success to copy-paste attack on text vs video stems; (b) circuits pilot on DDV users; (c) adopter authors a new pack and runs the video skill; (d) accessibility review.
- **Figures to plan:** (a) DDV ↔ challenge integration; (b) bank → skill → video → quest pipeline; (c) clearance state machine; (d) sample stem frame (circuit on screen); (e) report UI.

---

## System snapshot (for author reference; trim in final paper)

| Aspect | Status / behavior |
|--------|-------------------|
| Learning home | [DDV platform](https://universal-verification-methodology.github.io/learning/) — labs, tools, simulator, courses |
| Challenge runtime | Static HTML/JS; `content/<course_id>/`; merge-ready with DDV |
| Demo pack | `learn_digital` — radix, K-map, setup/hold |
| Bank (demo) | 90 items/module (30×3 difficulties) — largely **text** today |
| Video stems + question→video skill | Skill scaffolded (`.cursor/skills/question-video/`); batch render + player wiring still in progress |
| Clearance | 1 correct / difficulty; ≤10 unique attempts |
| Feedback | Report only after quest |
| Timing defaults | 30 / 45 / 60 s by difficulty |
| After quest | Report + optional certificate + leaderboard |
| Adopter action | Replace banks per AUTHORING; later run video skill per item/bank |
