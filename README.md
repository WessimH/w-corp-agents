# W Corp Agents

A team of 12 Claude Code agents for a Salesforce admin who works alone.

Milestones usually arrive as one vague line. A big company would turn that line into stories, tasks, a design, tests, a security review and a release plan, with a different person for each. These agents play those roles. They do not make decisions for you: they prepare the work, ask the questions your manager expects, and push back on weak ideas.

## The team

| Agent | Real-world role | Called when | Model |
|---|---|---|---|
| `po-ba` | Product Owner / Business Analyst | A milestone arrives or a need is unclear | sonnet |
| `scrum-master` | Scrum Master | Stories are validated and must become tasks (with estimates and labels) | sonnet |
| `architect` | Solution architect | New object, sharing change, multi-object automation | opus |
| `org-analyst` | Analyst admin (read-only) | You need the real state of the org | haiku |
| `dpo` | Data Protection Officer | Who may access personal data, why, and for how long | opus |
| `builder` | Configurator admin | A ready task needs metadata | sonnet |
| `qa` | Tester | Before and after each deployment to the sandbox | sonnet |
| `security` | Security officer (veto) | A diff touches access or personal data | opus |
| `simplicity-guard` | Reviewer (veto) | A diff contains code, a script or a large Flow | sonnet |
| `release-manager` | Release manager | A work item is ready for DevOps Center | haiku |
| `devops` | DevOps | The CI changes or fails | sonnet |
| `tech-writer` | Technical writer | A task is done and must be documented | sonnet |

Cheap models read, mid-range models build, the most capable model takes the risky decisions.

## How it works

1. You paste a milestone. Claude hands it to `po-ba`, which writes stories, acceptance criteria and questions for your manager in a Markdown note.
2. You ask the questions and paste the answers.
3. `scrum-master` splits the stories into tasks of one day max, each with an estimate, a priority, labels, and the list of agents it needs.
4. For each task, only those agents work. `security` and `simplicity-guard` answer `VETO` or `OK`; a task with an open veto is not done.
5. A human promotes to pre-prod and prod through DevOps Center. No agent ever does.

All agents share one note per milestone. Each writes only in its own `## <agent>` section, so you can read the whole story in one place, for example in Obsidian.

## Guardrails

- **One org.** Agents only see one dev sandbox. `sf org login` and `sf org display` are denied in `.claude/settings.json`, so an agent cannot connect elsewhere or read a token.
- **A click for anything that writes.** Real deployments, retrieves (they overwrite local files), data changes and anonymous Apex all ask for your approval.
- **Frugality.** By default no agent runs. Questions and small fixes stay with the main Claude.

The filtering relies on command shapes. It is not bulletproof: the real barrier is that only the dev sandbox is authenticated on your machine.

## Home-made Salesforce MCP

`tools/sf-mcp/` is a small Python MCP server that wraps sf CLI. It exposes four tools: `describe_object`, `soql`, `retrieve` and `validate_deploy`. It keeps only what matters: describing `Account` returns name, label, type and required flag for each field instead of thousands of lines of JSON. No paid service, no extra login.

## Setup

Requirements: [Claude Code](https://claude.com/claude-code), [sf CLI](https://developer.salesforce.com/tools/salesforcecli), [uv](https://docs.astral.sh/uv/), and the [Superpowers](https://github.com/obra/superpowers) plugin (some agents use its skills).

1. Copy `.claude/`, `tools/`, `.mcp.json` and `CLAUDE.md` into your SFDX project.
2. Copy `.env.example` to `.env` and set `SF_TARGET_ORG` to your dev sandbox alias. Load it before starting Claude Code: `set -a; source .env; set +a`.
3. Log in once, yourself:

   ```bash
   sf org login web -a my-dev-sandbox --instance-url https://test.salesforce.com
   ```

4. Start a new Claude Code session in the project (agents load at startup) and ask: "Which agents and sf-mcp tools do you see?"
5. Optional: copy `templates/ci.yml` to `.github/workflows/` for static analysis and a check-only deploy on every pull request. It needs a `SFDX_AUTH_URL_DEV` secret from a dedicated integration user.

If you also have a hosted Salesforce MCP connected, deny it in `.claude/settings.local.json` so agents cannot write through it.

## Tests

```bash
cd tools/sf-mcp && uv run --python 3.12 --with "mcp>=2,<3" --with pytest pytest -q
```

## Easter eggs

The team was built by Wessim, a former apprentice. Start a new chat and it will introduce itself. Mention the IR (internal requests) and see what happens.

## License

MIT
