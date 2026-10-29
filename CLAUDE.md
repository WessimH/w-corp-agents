# Salesforce repo — rules for Claude and its agents

Solo Salesforce admin. Work arrives as milestones with no tasks. The manager expects questions for context and real challenge from the AI.

## Configuration (edit these two lines)

- Dev sandbox alias: `my-dev-sandbox` (also set in `.mcp.json` as `SF_TARGET_ORG`).
- Notes folder: `notes/` (git-ignored). Point it to an Obsidian vault if you use one.

## Working rules

1. Think before acting. Assume nothing, voice doubts, lay out trade-offs.
2. The minimum that solves the problem. Nothing speculative. If 50 lines do, not 200.
3. Touch only what is needed. Clean up only your own mess.
4. Define the success criterion before starting, then loop until it is verified.

## How to talk to me

- Answer or next action first. No preamble.
- Numbered steps, five points max per list.
- One concrete next step at the end.
- End with a **Mechanism** block of two or three lines: what was done, why, with which command.

## Salesforce

- One org only: the dev sandbox above. Never target another.
- Reads: the home-made `sf-mcp` tools. Everything else: sf CLI. Never a hosted Salesforce MCP.
- Real deployment (`sf project deploy start`) only after a green check-only deploy and a click from the user.
- Pre-prod and prod: DevOps Center, by a human. No agent touches them.

## Frugality: an agent works only when useful

By default, no agent. Questions, simple reads and small fixes: the main Claude alone.

| Agent | Trigger |
|---|---|
| po-ba | New milestone pasted, or unclear need. |
| scrum-master | Validated stories to turn into tasks. |
| architect | New object or relationship, sharing change, multi-object automation. |
| org-analyst | Need for the org's state, missing from the repo. |
| dpo | GDPR or personal-data access policy to define (before design). |
| builder | Ready task (DoR passed) that needs metadata. |
| qa | Before any deployment to the dev sandbox. |
| security | Diff touching PS, PSG, profiles, FLS, sharing or personal data. |
| simplicity-guard | Diff with code, a script, or a Flow of more than a few elements. |
| release-manager | Work item ready to promote. |
| devops | CI change or failure. |
| tech-writer | Task reached the Definition of Done. One pass. |

On a task, the `scrum-master` has named the agents. No other is called. When delegating, always give the agent the exact path of the milestone note.

## Milestone flow

1. Milestone pasted → `po-ba`: stories, acceptance criteria, questions for the manager.
2. The user asks the questions and pastes the answers.
3. `scrum-master`: tasks, agents per task, estimates, labels, issue-tracker and DevOps Center blocks.
4. Each task: only the named agents work.
5. Definition of Done: QA green, no open veto, UAT script written, docs up to date.

## Notes

- Working note: `notes/Milestone - <name>.md`. Each agent writes only in its own `## <agent-name>` section.
- A dated log `notes/Journal.md` gets one entry per new context (milestone pasted, manager answer, decision).
