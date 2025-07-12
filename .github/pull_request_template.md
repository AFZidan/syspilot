---
name: 🔄 Pull Request
about: Submit changes to SysPilot
title: '[TYPE](scope): Brief description of changes'
labels: ''
assignees: ''
---

## 📋 Pull Request Checklist

- [ ] **PR Title** follows [Conventional Commits](https://www.conventionalcommits.org/) format: `type(scope): description`
- [ ] **Code** follows project style guidelines (Black, isort, flake8)
- [ ] **Tests** are added/updated for new features or bug fixes
- [ ] **Documentation** is updated if needed
- [ ] **Breaking changes** are clearly documented
- [ ] **Self-review** of code has been performed
- [ ] **Linear history** is maintained (rebase instead of merge)

## 🎯 Type of Change

<!-- Mark with [x] the type that applies -->

- [ ] 🐛 **Bug fix** (non-breaking change which fixes an issue)
- [ ] ✨ **New feature** (non-breaking change which adds functionality)
- [ ] 💥 **Breaking change** (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 **Documentation** (documentation only changes)
- [ ] 🎨 **Style** (formatting, missing semi-colons, etc; no production code change)
- [ ] ♻️ **Refactoring** (refactoring production code, eg. renaming a variable)
- [ ] ⚡ **Performance** (changes that improve performance)
- [ ] 🧪 **Test** (adding missing tests, refactoring tests; no production code change)
- [ ] 🔧 **Chore** (updating grunt tasks etc; no production code change)
- [ ] 🚀 **CI/CD** (changes to CI/CD pipeline)

## 📖 Description

<!-- Provide a clear and comprehensive description of your changes -->

### Summary
<!-- Brief overview of what this PR accomplishes -->

### Motivation and Context
<!-- Why is this change required? What problem does it solve? -->
<!-- If it fixes an open issue, please link to the issue here: Fixes #123 -->

### Changes Made
<!-- Detailed list of changes made -->

- Change 1
- Change 2
- Change 3

## 🧪 Testing

<!-- Describe the tests that you ran to verify your changes -->

### Test Environment

- **OS**: <!-- e.g., Ubuntu 22.04, Windows 11, macOS 13 -->
- **Python Version**: <!-- e.g., 3.9.16 -->
- **Qt Version**: <!-- e.g., PyQt5 5.15.7 -->

### Test Cases
<!-- List the test cases you've run -->

- [ ] **Unit Tests**: All existing tests pass
- [ ] **Integration Tests**: Cross-platform functionality verified
- [ ] **Manual Testing**: GUI components work as expected
- [ ] **Performance Tests**: No significant performance degradation
- [ ] **Edge Cases**: Tested with invalid inputs and edge conditions

### Test Commands

```bash
# Commands used to test the changes
pytest tests/ -v
python main.py --cli --system-info
python main.py --gui  # Manual GUI testing
```

## 📸 Screenshots/Demo

<!-- If applicable, add screenshots or GIFs to help explain your changes -->
<!-- For UI changes, before/after screenshots are very helpful -->

### Before
<!-- Screenshot or description of the current behavior -->

### After
<!-- Screenshot or description of the new behavior -->

## 🔗 Related Issues

<!-- Link to related issues, discussions, or PRs -->

- Closes #<!-- issue number -->
- Related to #<!-- issue number -->
- Depends on #<!-- PR number -->

## 🚨 Breaking Changes

<!-- If this PR introduces breaking changes, describe them here -->
<!-- Include migration instructions for users -->

**Does this PR introduce breaking changes?**: <!-- Yes/No -->

<!-- If yes, describe: -->

- **What breaks**: Description of what functionality breaks
- **Why it was necessary**: Explanation of why the breaking change was required
- **Migration path**: Steps users need to take to migrate their setup

## 📝 Additional Notes

<!-- Any additional information that reviewers should know -->

### Deployment Notes
<!-- Any special deployment considerations -->

### Future Work
<!-- Any follow-up work that should be done -->

### Dependencies
<!-- Any new dependencies added or version changes -->

---

## 🔍 Reviewer Guidelines

### Focus Areas

Please pay special attention to:

- [ ] **Code Quality**: Adherence to project standards and best practices
- [ ] **Performance**: No unnecessary performance impact
- [ ] **Security**: No security vulnerabilities introduced
- [ ] **Cross-Platform**: Changes work on Linux, Windows, and macOS
- [ ] **Documentation**: Code is well-documented and self-explanatory
- [ ] **Tests**: Adequate test coverage for new/changed functionality

### Testing Checklist for Reviewers

- [ ] Pull and test the branch locally
- [ ] Verify all CI checks pass
- [ ] Test on multiple platforms if applicable
- [ ] Review code for potential security issues
- [ ] Check that documentation is accurate and complete

---

**By submitting this PR, I confirm that:**

- [ ] I have read and followed the [Contributing Guidelines](CONTRIBUTING.md)
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
