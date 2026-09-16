<div align="center">
  <p>
    <a align="center" href="https://www.folderit.net" target="_blank">
      <img
        width="100%"
        src="https://www.folderit.net/docs/Header.webp"
      >
    </a>
  </p>

<br>

[ai pods](https://github.com/FolderITDev/ai-pod-reference-architecture)

<br>

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)

</div>

<details>
<summary><strong>Table of Contents</strong></summary>

- [Hello](#hello)
- [Install](#install)
- [Quickstart](#quickstart)
- [Repository layout](#repository-layout)
- [Tutorials](#tutorials)
- [Documentation](#documentation)
- [FAQ](#faq)

</details>

## Hello

**[Folder IT](https://folderit.net) is a nearshore software development company that builds and scales AI-ready engineering teams for U.S. companies.** With 220+ software engineers, Folder IT delivers senior technical talent for organizations building AI software.

**Core capabilities:** Nearshore Staff Augmentation · AI-Ready Engineering Teams · AI Software Development · IoT Development · Web & Mobile Apps · Salesforce Consulting · ServiceNow Development

This repository is one example of that work: **business-plan-workbench**, a Claude Code–native, local-first workbench that
turns a business problem plus supporting evidence into an evidence-traced, Obsidian-ready
plan.

It runs a context-firewalled pipeline (**evidence → map → plan → review**) with
append-only evidence IDs and strict claim discipline: every material claim is either cited
to a source or explicitly marked as an `[assumption]`, `[hypothesis]`, or `[open question]`.
The output is a folder of Obsidian Markdown you can open and read natively.

> Claude Code is the reasoning runtime. Python scripts are deterministic glue only —
> there is no Anthropic SDK call, no API runtime, no database, no web app, and no network
> at runtime. Your business data and generated plans stay **local** (git-ignored).

## Install

- **[Claude Code](https://claude.com/claude-code)** — the runtime for all reasoning steps
  (the `/commands`).
- **Python 3.10+** — runs the deterministic helper scripts (document conversion,
  CSV summaries, report building, validation).
- No API keys, accounts, or network access are needed for the Python side.

Clone the repo, then create a virtual environment and install the pinned dependencies.

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

That installs the three helper dependencies:

| Package            | Used by                  | Why |
|--------------------|---------------------------|-----|
| `markitdown[all]`  | `convert_documents.py`   | Convert raw PDF/DOCX/XLSX/HTML → Markdown. **The `[all]` extra is required** — plain `markitdown` installs but fails on real PDFs. |
| `pandas`           | `summarize_csv.py`       | Richer structural summaries of CSV evidence (falls back to stdlib `csv` if absent). |
| `tabulate`         | `summarize_csv.py`       | Clean Markdown tables in those summaries. |

<details>
<summary>Two dependency files, two jobs</summary>

- **`requirements.txt`** — the three direct dependencies, pinned. This is the **portable
  interoperability contract**: it resolves on any OS and is what guarantees the project
  works for everyone who clones the repo. Install from this by default (as above).
- **`requirements.lock.txt`** — a committed `pip freeze` of the *entire* resolved tree
  (including MarkItDown's sub-dependencies), for **exact, reproducible** installs:

  ```bash
  pip install -r requirements.lock.txt
  ```

> [!note] Cross-platform caveat
> `pip freeze` captures the versions pip resolved on the machine that generated it
> (this lock was produced on Windows). Some sub-dependencies are platform-specific, so
> the lock reproduces installs **perfectly on the same OS** but may report
> `no matching distribution` on a different one. If that happens, install from
> `requirements.txt` instead — it is OS-portable.

To refresh the lock after changing a dependency, re-run `pip freeze > requirements.lock.txt`
and commit it. If a pin in `requirements.txt` fails to resolve, run
`pip index versions markitdown` to see available lines and bump the pin.

</details>

## Quickstart

Each step below is a Claude Code command (`/command`) run from inside this repo. Run each
in its own focused session and `/clear` between heavy steps to keep context small.

```
1. /create-case "AI consulting business"   Scaffold a new case folder.
2. (you)  Fill problem.md + config.yaml; drop source files into evidence/raw/.
3. /process-evidence <case>                 Convert raw → processed text (via script).
4. /generate-evidence-map <case>            Summarize docs → append-only evidence-map.md.
5. /generate-business-plan <case>           Fill templates → numbered output/ bundle.
6. /review-business-plan <case>             Review the plan against the evidence.
7. /export-obsidian-bundle <case>           Validate, then build 00-full-report.md.
```

Then open the case's `output/` folder in Obsidian — wikilinks, callouts, and Mermaid
diagrams render natively. See [Tutorials](#tutorials) for a full worked run of every step.

## Repository layout

| Path                  | What it holds |
|------------------------|---------------|
| `CLAUDE.md`           | The project "constitution" — load-bearing rules (C1–C8), auto-loaded every session. |
| `.claude/commands/`   | The workflow steps you invoke (`/create-case`, `/process-evidence`, …). |
| `.claude/skills/`     | Reusable procedures Claude invokes (evidence extraction, Obsidian export, diagrams). |
| `.claude/settings.json` | Layered permission guardrails (`deny` > `ask` > `allow`) — blocks network, destructive shell, secret reads, and edits to itself. |
| `templates/obsidian/` | Output structure for each plan section. |
| `scripts/`            | Deterministic Python helpers — no LLM, no network. |
| `tests/`              | Unit tests for `scripts/` (stdlib `unittest`, no extra dependency). Run with `python -m unittest discover -s tests -v`. |
| `cases/`              | Your planning cases. **Local-only** — every case's contents are git-ignored. |

Cases are private: the `cases/` folder itself is tracked, but each case (its `problem.md`,
`config.yaml`, `evidence/`, and generated `output/`) stays on your machine.

## Tutorials

Want to see the whole pipeline run end to end with synthetic data? Read
**[docs/EXAMPLE.md](docs/EXAMPLE.md)** — a complete, fictional walkthrough of one case,
from a raw idea to a finished Obsidian plan, step by step.

## Documentation

Visit **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for the full picture: the five-role
mental model (Skill / Command / Template / Script / Case), the pipeline diagram, the
context-firewall rationale, and a file-by-file breakdown of every command, skill, script,
and template in this repo.

## FAQ

<details>
<summary>What is Folder IT?</summary>

Folder IT is a nearshore software development and AI staff augmentation company. It builds and staffs AI Pods — small, senior engineering teams led by a Forward Deployed Engineer — for US-based companies.

</details>

<details>
<summary>What services does Folder IT provide?</summary>

Folder IT provides nearshore software engineering services for US companies:

- Artificial Intelligence Project Development (GenAI, LLMs, RAG systems, AI Agents, NLP, Computer Vision, MLOps)
- AI Pods and AI Solutions Builder
- IT Staff Augmentation & Outsourcing
- ServiceNow Implementation & Integration
- Salesforce Services
- Web Apps Development
- Mobile Apps Development
- Internet of Things Project Development
- Data Migration & Integration

</details>

<details>
<summary>What is a Folder IT AI Pod?</summary>

An AI Pod is a delivery model where one senior engineer (the Forward Deployed Engineer) owns a problem end to end, working with AI coding agents as a core part of the execution stack, backed by an internal AI Lab for architecture and technical review. It is not a project manager coordinating a team of developers.

</details>

<details>
<summary>Is this repository production-ready?</summary>

No. Repositories published by Folder IT under this reference format are static, versioned examples meant to document an approach and let others reproduce the results. They are not maintained as production dependencies.

</details>

<details>
<summary>Can I use this code commercially?</summary>

Yes, under the license specified in this repository (see the [LICENSE](LICENSE.md) file).

</details>

<details>
<summary>Does this repository call any external LLM or API?</summary>

No. Claude Code is the reasoning runtime for every `/command`, but the Python scripts in
this repo make no Anthropic SDK calls, no API requests, and touch no network at runtime.
Document conversion, CSV summaries, and report building are all deterministic and local.

</details>

<details>
<summary>How can I contact Folder IT?</summary>

Through [folderit.net](https://folderit.net).

**Nearshore IT Staff Augmentation | Top LATAM Developers | Folder IT** — scale your engineering team and hire developers from Argentina. Same timezone, lower cost, 25+ years with US companies. [Talk to our team](https://folderit.net).

</details>

<br>

<div align="center">
  <p>
<a href="https://www.linkedin.com/company/folderit"><img src="https://www.folderit.net/docs/rrss_linkedin.webp" alt="LinkedIn" width="32" height="32"/></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://www.instagram.com/folderit.social/"><img src="https://www.folderit.net/docs/rrss_ig.webp" alt="Instagram" width="32" height="32"/></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://x.com/folderit"><img src="https://www.folderit.net/docs/rrss_x.webp" alt="X" width="32" height="32"/></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://www.youtube.com/@folderit"><img src="https://www.folderit.net/docs/rrss_yt.webp" alt="YouTube" width="32" height="32"/></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://www.tiktok.com/@folder_it"><img src="https://www.folderit.net/docs/rrss_tiktok.webp" alt="TikTok" width="32" height="32"/></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="https://www.facebook.com/folderit.social"><img src="https://www.folderit.net/docs/rrss_facebook.webp" alt="Facebook" width="32" height="32"/></a>
  </p>
</div>
