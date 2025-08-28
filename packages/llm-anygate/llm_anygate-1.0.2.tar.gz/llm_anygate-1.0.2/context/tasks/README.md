# Task Management

## Purpose

This directory organizes current and planned work items for the LLM AnyGate project. Tasks are categorized by type to help prioritize and track different kinds of development work.

## Structure

```
tasks/
├── features/    # New functionality to be added
├── fixes/       # Bug fixes and issue resolutions
├── refactor/    # Code improvement without changing behavior
└── tests/       # Testing tasks and coverage improvements
```

## Task Categories

### features/
New functionality, enhancements, and feature requests
- User-facing features
- API endpoints
- New provider integrations
- Configuration options

### fixes/
Bug fixes, issue resolutions, and corrections
- Reported bugs
- Performance issues
- Security vulnerabilities
- Documentation errors

### refactor/
Code quality improvements without changing functionality
- Code cleanup
- Performance optimizations
- Architecture improvements
- Technical debt reduction

### tests/
Testing-related tasks
- Unit test creation
- Integration test development
- Test coverage improvements
- Test infrastructure setup

## Task File Format

Each task should follow this template:

```markdown
# Task: [Brief Title]

## HEADER
- **Purpose**: [What this task accomplishes]
- **Status**: [pending/in-progress/completed/blocked]
- **Date**: [YYYY-MM-DD]
- **Dependencies**: [What must be done first]
- **Target**: [AI assistants, developers]

## Description
[Detailed description of what needs to be done]

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests pass

## Implementation Notes
[Any helpful context or approach suggestions]

## Related
- Links to design docs
- Related tasks
- Relevant code files
```

## Naming Conventions

- `task-[verb]-[object].md` - Standard task format
- `epic-[feature-name].md` - Large features with subtasks
- `bug-[issue-number].md` - Bug fixes linked to issues
- `goal.md` - Overall goal for a directory

## Priority Indicators

Use prefixes for priority:
- `P0-` Critical, blocking
- `P1-` High priority
- `P2-` Normal priority
- `P3-` Low priority

Example: `P1-task-implement-rate-limiting.md`

## Task Lifecycle

1. **Creation**: Task identified and documented
2. **Assignment**: Task assigned or picked up
3. **In Progress**: Active development
4. **Review**: Code review or testing
5. **Completed**: Merged and deployed
6. **Archived**: Move to `completed/` subdirectory

## Best Practices

1. One task per file for clarity
2. Break large tasks into subtasks
3. Link dependencies explicitly
4. Update status as work progresses
5. Include time estimates when known
6. Reference issue numbers from GitHub