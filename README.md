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

## How to set up in your project

You need an existing SFDX project (a repo with `sfdx-project.json` and `force-app/`) and:

- [Claude Code](https://claude.com/claude-code)
- [sf CLI](https://developer.salesforce.com/tools/salesforcecli)
- [uv](https://docs.astral.sh/uv/), which runs the MCP server with the right Python, nothing to install by hand
- the [Superpowers](https://github.com/obra/superpowers) plugin, whose skills some agents use: run `/plugin install superpowers@claude-plugins-official` in Claude Code

### 1. Copy the files into your project

Work on a branch, so you can try it and throw it away.

```bash
cd path/to/your-sfdx-project
git switch -c chore/claude-agents
git clone --depth 1 https://github.com/WessimH/w-corp-agents.git /tmp/w-corp-agents
cp -R /tmp/w-corp-agents/.claude /tmp/w-corp-agents/tools .
cp /tmp/w-corp-agents/.mcp.json /tmp/w-corp-agents/.env.example .
cp -n /tmp/w-corp-agents/CLAUDE.md .
```

Already have some of these files? Merge by hand instead of overwriting:

- `CLAUDE.md`: `cp -n` above skips it. Paste the sections you want (at least *Salesforce*, *Frugality* and *Milestone flow*) into yours.
- `.claude/settings.json`: merge the `allow`, `ask` and `deny` lists into yours. These lists are the guardrails, do not skip them.
- `.mcp.json`: add the `sf-mcp` entry next to your other servers.

Then add to your `.gitignore`:

```
.env
notes/
.claude/settings.local.json
```

### 2. Point it at your dev sandbox

```bash
cp .env.example .env
```

Set `SF_TARGET_ORG` in `.env` to the alias of the sandbox the agents may use, and write the same alias in the *Configuration* section of `CLAUDE.md`. Then log in to that sandbox yourself (agents are not allowed to):

```bash
sf org login web -a my-dev-sandbox --instance-url https://test.salesforce.com
```

Only log in to orgs you are fine with the agents reading. Never log in to production on this machine under that alias.

### 3. Start Claude Code with the variable loaded

Claude Code does not read `.env` by itself:

```bash
set -a; source .env; set +a; claude
```

On first start, Claude Code asks whether to enable the project MCP server `sf-mcp`: accept.

### 4. Check that it works

In that new session, ask:

```
Which agents and sf-mcp tools do you see? Then describe the Account object with sf-mcp.
```

Expected: 12 agents, 4 tools (`describe_object`, `soql`, `retrieve`, `validate_deploy`), and a short list of Account fields. If you get "Run: sf org login web -a ...", step 2 is not done.

### 5. Use it on a real milestone

Paste a milestone and name the note:

```
New milestone: <paste the text>. Run po-ba. Note: notes/Milestone - <name>.md
```

Then follow the *Milestone flow* in `CLAUDE.md`: answer po-ba's questions with your manager, call scrum-master, and let each task run with only the agents it names.

### Optional

- **CI**: copy `templates/ci.yml` to `.github/workflows/ci.yml` for static analysis and a check-only deploy on every pull request. It needs a GitHub secret `SFDX_AUTH_URL_DEV` from a dedicated integration user with minimal rights, never your own account.
- **Hosted Salesforce MCP**: if one is connected in Claude, deny it in `.claude/settings.local.json` (`"deny": ["mcp__<its-id>"]`) so agents cannot write through it.
- **Obsidian**: replace `notes/` with the path of your vault in `CLAUDE.md` to read the notes there.

## Tests

```bash
cd tools/sf-mcp && uv run --python 3.12 --with "mcp>=2,<3" --with pytest pytest -q
```

## Easter eggs

The team was built by Wessim, a former apprentice. Start a new chat and it will introduce itself. Mention the IR (internal requests) and see what happens.

## License

MIT
