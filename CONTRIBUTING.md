# Contributing to AnswerDeck

Thank you for interest in contributing! This document provides guidelines for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Test your changes
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request

## Development Setup

See [DEVELOPER.md](docs/DEVELOPER.md) for detailed setup instructions.

## Code Style

### Python
- Format with `black`
- Sort imports with `isort`
- Lint with `flake8`
- Type hints with `mypy`

```bash
black src tests
isort src tests
flake8 src tests
mypy src
```

### TypeScript/JavaScript
- Follow React best practices
- Use TypeScript for type safety
- Format with Prettier (configured)

## Testing

All code changes must include tests:

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Check coverage
open htmlcov/index.html
```

## Commit Messages

Follow conventional commits:

```
type(scope): subject

body

footer
```

Types: feat, fix, docs, style, refactor, test, chore

**Examples:**
```
feat(chat): add streaming responses
fix(search): handle empty queries gracefully
docs(api): update endpoint documentation
test(embeddings): add comprehensive unit tests
```

## Pull Requests

1. **Title**: Clear, descriptive, follows conventions
2. **Description**: What changed and why
3. **Tests**: Include test coverage
4. **Documentation**: Update if needed
5. **Review**: Respond to feedback promptly

## Issues

### Reporting Bugs
- Describe the bug clearly
- Include steps to reproduce
- Provide example code/screenshots
- Note your environment

### Requesting Features
- Describe the use case
- Explain the benefit
- Suggest implementation if applicable

## Areas for Contribution

- **Documentation**: Improve docs, examples
- **Tests**: Add more test coverage
- **Features**: New functionality
- **Performance**: Optimize code
- **Bug Fixes**: Fix existing issues
- **UI/UX**: Frontend improvements

## Review Process

1. Automated checks must pass
2. Code review from maintainers
3. Address feedback
4. Final approval and merge

## Documentation

Update documentation for:
- API changes
- New features
- Configuration changes
- Architecture updates

## Version Control

- `master`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches

## Performance

When optimizing:
- Measure before and after
- Document performance impact
- Consider trade-offs

## Security

- Don't commit secrets
- Use environment variables
- Follow security best practices
- Report security issues privately

## Questions?

Feel free to:
- Open an issue for questions
- Check existing discussions
- Ask in PR comments

## License

By contributing, you agree your code will be under the MIT License.

Thank you for contributing to AnswerDeck! 🙏
