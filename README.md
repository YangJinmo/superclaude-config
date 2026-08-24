# SuperClaude Config

My personal [Claude Code](https://claude.com/product/claude-code) configuration, built on top of the [SuperClaude Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework). This is what actually loads into every Claude Code session I run — not a demo, my day-to-day setup.

## What this is

`CLAUDE.md` is the entry point Claude Code reads on startup. It imports every file in this repo, which together define:

- **Behavioral modes** — switch how Claude approaches a task depending on context
- **MCP server routing rules** — which tool to reach for and when
- **Core principles and rules** — engineering standards Claude follows across every session

## Behavioral Modes

| File | Mode | Purpose |
|---|---|---|
| [MODE_Brainstorming.md](MODE_Brainstorming.md) | Brainstorming | Socratic discovery for vague/early-stage requests |
| [MODE_Task_Management.md](MODE_Task_Management.md) | Task Management | Hierarchical planning with persistent memory for multi-step work |
| [MODE_Orchestration.md](MODE_Orchestration.md) | Orchestration | Picks the right tool/MCP server per task, manages resource load |
| [MODE_Introspection.md](MODE_Introspection.md) | Introspection | Meta-cognitive self-review after errors or complex decisions |
| [MODE_DeepResearch.md](MODE_DeepResearch.md) | Deep Research | Evidence-based, cited, multi-source investigation |
| [MODE_Token_Efficiency.md](MODE_Token_Efficiency.md) | Token Efficiency | Symbol-compressed communication under context pressure |
| [MODE_Business_Panel.md](MODE_Business_Panel.md) | Business Panel | Multi-expert business-strategy analysis (discussion/debate/Socratic) |

## MCP Server Routing

Each `MCP_*.md` file documents when Claude should reach for that server over the alternatives — e.g. Context7 for official library docs, Sequential for multi-step reasoning, Serena for symbol-level code navigation, Playwright for real browser testing, Morphllm for bulk pattern edits, Tavily for live web research.

## Core Rules & Principles

- [`RULES.md`](RULES.md) — session workflow, git safety, scope discipline, workspace hygiene, professional-honesty guardrails
- [`PRINCIPLES.md`](PRINCIPLES.md) — SOLID, DRY/KISS/YAGNI, evidence-based decision-making
- [`FLAGS.md`](FLAGS.md) — manual flags for overriding auto-detected mode/depth/MCP selection
- [`RESEARCH_CONFIG.md`](RESEARCH_CONFIG.md) — defaults for the deep-research workflow (parallelism, source credibility tiers, confidence thresholds)

## Business Panel

[`MODE_Business_Panel.md`](MODE_Business_Panel.md), [`BUSINESS_PANEL_EXAMPLES.md`](BUSINESS_PANEL_EXAMPLES.md), and [`BUSINESS_SYMBOLS.md`](BUSINESS_SYMBOLS.md) configure a multi-expert business-strategy panel (Christensen, Porter, Drucker, Godin, Kim & Mauborgne, Collins, Taleb, Meadows, Doumont) that can run in discussion, debate, or Socratic mode — used for evaluating product/strategy decisions from multiple frameworks at once instead of a single generic take.

## Skills

Custom Claude Code [Skills](https://code.claude.com/docs/en/skills) I use day-to-day, invoked as slash commands (e.g. `/tubeinfo <url>`) or triggered automatically when the request matches.

| Skill | Purpose |
|---|---|
| [Skills/tubeinfo](Skills/tubeinfo/SKILL.md) | Summarizes a YouTube video (channel info, view/like/comment counts, chapters, full transcript) via the TubeAlfred MCP server |
| [Skills/app-mockup](Skills/app-mockup/SKILL.md) | Composites app screenshots into iPhone/Galaxy device mockup frames (Dynamic Island/notch/punch-hole, status bar, home indicator/nav bar handling) as a single transparent-background image |

## Usage

Drop these files in `~/.claude/` (global) or `.claude/` (per-project) and reference them from your own `CLAUDE.md` via `@filename.md` imports, same as this repo's [`CLAUDE.md`](CLAUDE.md) does. Skills go in `~/.claude/skills/<name>/SKILL.md` (global) or `.claude/skills/` (per-project).

## Built with

[PartMoney](https://github.com/YangJinmo/PartMoney) — a Clean Architecture SwiftUI app — was designed, tested, and CI'd entirely through Claude Code running this configuration.
