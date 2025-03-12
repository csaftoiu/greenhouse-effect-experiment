# CLAUDE.md - Guidance for Working with This Codebase

## Core Rules

You have two modes of operation:

1. Plan mode - You will work with the user to define a plan, you will gather all the information you need to make the changes but will not make any changes
2. Act mode - You will make changes to the codebase based on the plan

- You start in plan mode and will not move to act mode until the plan is approved by the user.
- You will print `# Mode: PLAN` when in plan mode and `# Mode: ACT` when in act mode at the beginning of each response.
- Unless the user explicity asks you to move to act mode, by typing `ACT` you will stay in plan mode.
- You will move back to plan mode after every response and when the user types `PLAN`.
- If the user asks you to take an action while in plan mode you will remind them that you are in plan mode and that they need to approve the plan first.
- When in plan mode always output the full updated plan in every response.

## Plan Mode Template
Use this template for plan mode:

"""
# Summary

# Assumptions

# References

- Files `dir/file`
- Libraries `http://library.com`
- Documentation `http://docs.com`

# Implementation Steps

1. First step (`dir/file`)

# Confidence Level

- **High/Medium/Low** confidence in X

# Questions

- bullet points of what, how, why, any questions that are not fully clear
- if all is clear then still include this section but write "No questions"
"""

## Self-Planning

- When you have questions that can be answered by looking at the code, take the next step and look at the code and generate the next step of the plan.

## Finalizing Action

- after an ACT step, ask user if ok to commit changes, if they say 'commit' then commit and push to git
- Don't include CLAUDE co-authors in commit messages
- git push after committing

## Dependencies
- Required packages: numpy, pandas, matplotlib, scipy
- All code runs with Python 3.6+

## Code Style Guidelines
- **Imports**: Group by standard library, third-party, then local imports
- **Naming**: Use snake_case for variables and functions
- **Comments**: Use block comments (#) for explaining logic, triple quotes for docstrings
- **Error handling**: Check file existence before loading, validate parameters
- **File organization**: Keep data in data/ subdirectories, code in Python files
- **Plotting**: Focus on publication-quality plotting with consistent styling
- **Path handling**: Use os.path for cross-platform compatibility

## Project Structure
- Each figure has its own directory with code and data
- Shared code should be extracted to utility functions
- Entry points use `if __name__ == "__main__"` pattern