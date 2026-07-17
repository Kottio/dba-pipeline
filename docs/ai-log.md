# AI log — working with AI on this project

One honest entry per phase, minimum: one interaction that worked well, one that failed or needed correction. This is teaching material on the "AI does syntax, humans own semantics" discipline — the failures are the most valuable entries.

Workflow: Tom writes raw notes in `Notetaking.md` → Claude formats them here.

## Phase 0 — 2026-07-17

**Task given to AI:** plan the pipeline (research, architecture, build plan) and scaffold the repo (Claude, Cowork session).

**What it did well:**
- Planning: market research with sources; the DuckLake-vs-Postgres discussion surfaced the concurrency argument.
- Repo created with a sensible folder structure for GitHub.

**Where it went wrong / what the human had to correct:**
- Created many files the owner didn't understand: `.sqlfluff`, a `docker-compose.yml` already written before Phase 1 even started, `.github/workflows/ci.yml` created without explanation or discussion.
- Too many decisions taken upfront, instead of evolving step by step with the builder.
- The scaffold was *complete* but not *understood* — and an unexplained file is technical debt for a learning project.

**Correction applied:** delete the not-yet-understood files and let the project grow organically. Each file comes back only when its phase needs it, explained first, understood before committed.

**Applied by Tom (same day):**
- Deleted `docker-compose.yml`, the GitHub workflow, and the pre-written dependencies in `pyproject.toml` — each returns when its phase needs it.
- Deleted Claude's `.git` entirely (it was littered with stale lock files — the remote bridge can't delete git's temp files) and re-initialized it himself. New rule: **git runs only on the owner's machine**; the AI proposes commands, the human executes.
- Confirmed the local-first order: everything proven locally → GitHub → droplet last, to optimize cost.
- Brought the project plan into the repo to guide the work.

**Lesson:** an AI will happily build the whole house on day one. The human's job is pacing: nothing enters the repo that its owner can't explain. "AI does syntax, humans own semantics" also means humans own the *rhythm*.

> Note originale (FR) : « Création de beaucoup de fichiers que je ne comprends pas (…) Trop de décisions prises sans évolution au fur et à mesure. Je vais demander à Claude ce que sont ces fichiers et les supprimer pour que le projet grandisse organiquement. »
