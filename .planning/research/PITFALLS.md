# Pitfalls Research

**Domain:** Repo-local LLM wiki skills for coding agents
**Researched:** 2026-05-12
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Putting the wiki in the wrong directory

**What goes wrong:**
The skill initializes `.llm-wiki/` in a multi-repo parent workspace instead of the actual project repo.

**Why it happens:**
Agents use the current working directory instead of the git root, or assume a parent folder is the project.

**How to avoid:**
Always resolve `git rev-parse --show-toplevel` and show the target root in the result. Fail clearly outside a git repo unless the user explicitly chooses a repo.

**Warning signs:**
The initialized folder has sibling project repos, no package manifest, or no meaningful code files.

**Phase to address:**
Phase 1.

---

### Pitfall 2: Wiki becomes a task log

**What goes wrong:**
`.llm-wiki/` accumulates todos, execution status, checkpoints, raw logs, and temporary planning artifacts.

**Why it happens:**
Agents want one memory layer and copy everything into it.

**How to avoid:**
Write strict AGENTS rules and raw policy. Make promotion happen only after validated non-trivial work.

**Warning signs:**
Pages mention active branch status, current sprint progress, unvalidated debugging hypotheses, or "next action" task lists.

**Phase to address:**
Phase 1 for policy, Phase 3 for promotion workflow.

---

### Pitfall 3: Unsafe raw source tracking

**What goes wrong:**
Secrets, tokens, customer data, full logs, database exports, or huge generated dumps get committed under `.llm-wiki/raw/`.

**Why it happens:**
Raw source capture is treated as a dumping ground.

**How to avoid:**
Track only curated, de-secreted raw sources. Add lint patterns for secret-looking content and oversized raw files.

**Warning signs:**
Raw files contain `.env`-like keys, JWTs, API tokens, credentials, production logs, or large machine-generated payloads.

**Phase to address:**
Phase 1.

---

### Pitfall 4: AGENTS.md patch clobbers existing instructions

**What goes wrong:**
The skill overwrites NotebookLM guidance, workflow contracts, or repo-specific agent rules.

**Why it happens:**
Patch logic rewrites the whole file or inserts unbounded prose.

**How to avoid:**
Use marker-bounded sections or precise insertion rules. Test against a fixture with an existing NotebookLM section.

**Warning signs:**
Diff shows unrelated AGENTS content moved, reformatted, or deleted.

**Phase to address:**
Phase 2.

---

### Pitfall 5: Stale wiki overrides current code

**What goes wrong:**
Agents trust `.llm-wiki/` over current implementation and make wrong architecture/debug decisions.

**Why it happens:**
The wiki is framed as source of truth instead of compiled context.

**How to avoid:**
Every wiki and AGENTS template must state: repo code wins when it disagrees with wiki notes. Lint should flag stale pages and likely contradictions.

**Warning signs:**
Agents quote wiki claims without checking code for current implementation details.

**Phase to address:**
Phase 1 for rules, Phase 2 or 3 for contradiction lint.

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Embed all templates in `SKILL.md` | Faster first draft | Hard to maintain and test | Only for very short template snippets |
| LLM-only lint | Less code | Inconsistent results and missed deterministic errors | Never for broken links, index gaps, secret patterns |
| Unmarked AGENTS insertion | Simple edit | Duplicate sections and merge conflicts | Never |
| No tests for idempotency | Saves time | Init reruns can damage repos | Never |
| Broad automatic ingest | Looks helpful | Unsafe commits and noisy wiki | Never in v1 |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Tracking secrets in raw files | Credential leak through git | Secret-looking pattern lint and explicit raw policy |
| Copying customer data into summaries | Privacy breach | Ban private customer data and require de-secreted summaries |
| Storing full production logs | Secret leakage and repo bloat | Store distilled runbooks or incident summaries only |
| Auto-patching AGENTS without diff discipline | Behavior changes across agents | Bounded patching and idempotency tests |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Too many commands too early | Skill feels heavy | Start with init and lint MVP |
| Vague lint output | User cannot act | Output specific files, warnings, and suggested fixes |
| Query answers without citations | User cannot trust synthesis | Require `[[wikilink]]` citations |
| Init overwrites hand-written notes | User loses trust | Never overwrite existing notes; report existing files |

## "Looks Done But Isn't" Checklist

- [ ] **Init:** Often missing rerun idempotency - verify by running twice in a fixture.
- [ ] **Git tracking:** Often missed because generated files are ignored - verify `git status` shows `.llm-wiki/`.
- [ ] **Raw policy:** Often documented but not enforced - verify lint flags secret-looking raw files.
- [ ] **AGENTS patch:** Often works only on empty files - verify against NotebookLM and existing instruction sections.
- [ ] **Query:** Often answers from chat memory - verify it reads `.llm-wiki/index.md` and appends `log.md`.
- [ ] **Lint:** Often checks only broken links - verify missing index entries, raw file size, and secret patterns.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong directory wiki | MEDIUM | Move `.llm-wiki/` to correct git root, update git history if already committed |
| Unsafe raw source committed | HIGH | Remove file, rotate secrets if needed, rewrite history when necessary |
| AGENTS clobber | MEDIUM | Restore from git, reapply marker-bounded patch |
| Wiki/task state mixing | MEDIUM | Move task state back to `.planning/` or workflow system, keep durable summary only |
| Stale wiki claim | LOW | Update page with provenance and add lint warning pattern if recurring |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Wrong directory wiki | Phase 1 | Clean test repo and multi-repo fixture root detection |
| Unsafe raw source tracking | Phase 1 | Secret-looking raw file fixture triggers lint |
| Wiki as task log | Phase 1 | Template and AGENTS rules define durable boundary |
| AGENTS clobber | Phase 2 | Fixture preserves existing NotebookLM section |
| Stale wiki overrides code | Phase 2 or 3 | Lint warns and templates state repo wins |

## Sources

- User-provided test plan and agent rules
- `projects/vault-llm-wiki/usage`
- `skills/vault-ingest/SKILL`
- `skills/vault-lint/SKILL`
- `projects/vault-llm-wiki/summaries/zaid-karpathy-second-brain-agent-memory-2026-04-29`

---
*Pitfalls research for: repo-local LLM wiki skills*
*Researched: 2026-05-12*
