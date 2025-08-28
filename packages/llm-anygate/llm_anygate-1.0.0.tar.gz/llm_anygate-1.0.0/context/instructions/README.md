# Instructions and Prompt Templates

## Purpose

This directory contains reusable prompt snippets, command templates, and standardized instructions for AI assistants working on the LLM AnyGate project. These ensure consistency across different development sessions and AI interactions.

## Contents

Store here:
- Reusable AI prompt templates
- Command sequences for common operations
- Code generation templates
- Review and testing instructions
- Deployment procedures
- Git workflow commands

## Naming Conventions

- `prompt-[task].md` - AI prompt templates
- `command-[operation].md` - Command sequences
- `snippet-[pattern].md` - Code snippet templates
- `template-[document-type].md` - Document templates
- `workflow-[process].md` - Multi-step procedures

## Example Documents

### For LLM AnyGate project:
- `prompt-provider-implementation.md` - Template for creating new providers
- `command-release-process.md` - Commands for releasing to PyPI
- `snippet-error-handling.md` - Standard error handling patterns
- `template-provider-tests.md` - Test file template for providers
- `workflow-add-provider.md` - Complete workflow for adding providers
- `prompt-code-review.md` - AI code review instructions

## Document Template

```markdown
# [Instruction/Template Name]

## HEADER
- **Purpose**: [What this instruction achieves]
- **Status**: [active/deprecated]
- **Date**: [YYYY-MM-DD]
- **Dependencies**: [Required context or tools]
- **Target**: [AI assistants, developers]

## Usage Context
[When and why to use this instruction]

## Instruction/Template

[For prompts:]
```
You are working on the LLM AnyGate project. Your task is to...

Requirements:
1. [Requirement 1]
2. [Requirement 2]

Constraints:
- [Constraint 1]
- [Constraint 2]
```

[For commands:]
```bash
# Step 1: [Description]
command1

# Step 2: [Description]
command2
```

## Parameters
- `[param1]`: [Description of what to replace]
- `[param2]`: [Description of what to replace]

## Expected Output
[What the result should look like]

## Related
- [Links to related instructions]
```

## Best Practices

1. Make instructions clear and unambiguous
2. Include parameter placeholders with clear descriptions
3. Test instructions before documenting
4. Version significant changes
5. Include examples of successful outputs
6. Document any prerequisites or setup required