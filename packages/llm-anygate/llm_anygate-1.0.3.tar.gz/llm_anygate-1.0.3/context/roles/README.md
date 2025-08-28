# AI Assistant Roles

## Purpose

This directory contains role-based system prompts, memory, and context for different AI assistant personas. Each role has specialized knowledge and behavior patterns optimized for specific aspects of the LLM AnyGate project.

## Structure

Each role has its own subdirectory containing:
- `system-prompt.md` - Core role definition and behavior
- `memory.md` - Accumulated knowledge and context
- `knowledge-base.md` - Domain-specific information
- `context.md` - Current working context and state

## Role Directory Structure

```
roles/
├── backend-developer/
│   ├── system-prompt.md
│   ├── memory.md
│   └── knowledge-base.md
├── api-architect/
│   ├── system-prompt.md
│   └── context.md
└── test-engineer/
    ├── system-prompt.md
    └── test-patterns.md
```

## Available Roles

### For LLM AnyGate project:

#### backend-developer
- Focus: Python implementation, async patterns, provider integrations
- Expertise: FastAPI, httpx, Pydantic, async/await

#### api-architect  
- Focus: API design, gateway patterns, routing logic
- Expertise: REST/GraphQL, OpenAPI, rate limiting, authentication

#### test-engineer
- Focus: Test coverage, integration testing, mocking
- Expertise: pytest, pytest-asyncio, test patterns

#### devops-engineer
- Focus: Deployment, CI/CD, containerization
- Expertise: Docker, GitHub Actions, PyPI publishing

#### documentation-writer
- Focus: User guides, API docs, examples
- Expertise: MkDocs, technical writing, code examples

## Role Definition Template

```markdown
# [Role Name] System Prompt

## Role Identity
You are a [role description] specializing in [specialization].

## Core Responsibilities
1. [Primary responsibility]
2. [Secondary responsibility]
3. [Tertiary responsibility]

## Expertise Areas
- [Technology/Domain 1]
- [Technology/Domain 2]
- [Technology/Domain 3]

## Behavioral Guidelines
- Always [behavior 1]
- Never [behavior 2]
- Prefer [approach] over [alternative]

## Communication Style
- [How to communicate]
- [Level of detail expected]
- [Terminology to use]

## Decision Making
When faced with choices:
1. Prioritize [criterion 1]
2. Consider [criterion 2]
3. Optimize for [goal]

## Knowledge Base
- Familiar with: [technologies/patterns]
- Best practices: [specific practices]
- Anti-patterns to avoid: [what not to do]

## Current Context
[Project-specific context and goals]
```

## Memory Management

Each role maintains memory in `memory.md`:

```markdown
# [Role] Memory

## Learned Patterns
- [Pattern 1]: [Description and when to use]
- [Pattern 2]: [Description and when to use]

## Project-Specific Knowledge
- [Component]: [What was learned]
- [Decision]: [Rationale and outcome]

## Common Issues Encountered
- [Issue]: [Solution that worked]

## Preferences Established
- [Preference]: [Reason]
```

## Best Practices

1. Keep roles focused on specific domains
2. Update memory after significant learnings
3. Don't duplicate general knowledge across roles
4. Reference role-specific knowledge in tasks
5. Maintain consistency within each role's behavior
6. Document role interactions and handoffs