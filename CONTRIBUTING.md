# Contributing to Rembo

Thank you for your interest in contributing to Rembo! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git
- Node.js 18+ (for frontend development)

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/rembo.git`
3. Create a development branch: `git checkout -b feature/your-feature-name`
4. Set up the development environment: `docker-compose up -d`

## 🏗️ BMAD Development Methodology

This project follows the **BMAD METHOD™** (Agentic Agile Driven Development). Please familiarize yourself with the methodology:

### Development Workflow
1. **Planning Phase**: Create detailed PRD and architecture documents
2. **SM Agent**: Transform plans into detailed development stories
3. **Dev Agent**: Implement features following the stories
4. **QA Agent**: Review and approve implementations
5. **Deployment**: Deploy to development/staging/production

### Story-Driven Development
- All features must have corresponding stories in `docs/stories/`
- Stories should contain complete context and acceptance criteria
- Follow the story template in `.bmad-core/templates/story-tmpl.yaml`

## 📝 Code Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting: `black backend/services/`
- Use flake8 for linting: `flake8 backend/services/`
- Use mypy for type checking: `mypy backend/services/`

### API Development
- Follow FastAPI best practices
- Use Pydantic models for request/response validation
- Include comprehensive docstrings
- Implement proper error handling
- Add unit tests for all endpoints

### Database
- Use Alembic for database migrations
- Follow PostgreSQL naming conventions
- Include proper indexes and constraints
- Document schema changes

## 🧪 Testing

### Unit Tests
- Write tests for all new functionality
- Maintain minimum 80% code coverage
- Use pytest for Python tests
- Place tests in `tests/` directories within each service

### Integration Tests
- Test API endpoints end-to-end
- Test database interactions
- Test external service integrations
- Use Docker Compose for test environments

### Running Tests
```bash
# Unit tests for auth service
cd backend/services/auth
python -m pytest tests/ -v

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Coverage report
python -m pytest --cov=app --cov-report=html tests/
```

## 📋 Pull Request Process

### Before Submitting
1. Ensure all tests pass
2. Update documentation if needed
3. Add/update unit tests for new functionality
4. Follow the commit message format
5. Rebase your branch on the latest main

### Commit Message Format
```
type(scope): brief description

Detailed description of changes made.

- List specific changes
- Reference issue numbers if applicable

Closes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### PR Requirements
- [ ] All CI checks pass
- [ ] Code coverage maintained/improved
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] BMAD story created/updated
- [ ] Breaking changes documented

## 🔍 Code Review Guidelines

### For Reviewers
- Check code quality and adherence to standards
- Verify test coverage and functionality
- Ensure BMAD methodology compliance
- Review security implications
- Check performance impact

### For Contributors
- Respond to feedback promptly
- Make requested changes in separate commits
- Update PR description if scope changes
- Be open to suggestions and improvements

## 🐛 Bug Reports

### Before Reporting
- Check existing issues for duplicates
- Verify the bug in the latest version
- Gather relevant information

### Bug Report Template
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.11.5]
- Docker version: [e.g., 20.10.21]

**Additional Context**
Screenshots, logs, or other relevant information
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Mockups, examples, or references
```

## 📚 Documentation

### Types of Documentation
- **API Documentation**: Auto-generated from code
- **User Guides**: Step-by-step instructions
- **Developer Docs**: Technical implementation details
- **Architecture Docs**: System design and decisions

### Documentation Standards
- Use clear, concise language
- Include code examples
- Keep documentation up-to-date
- Use proper markdown formatting

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code review and collaboration

## 🏷️ Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers bumped
- [ ] Release notes prepared
- [ ] Security review completed

## 📞 Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Request review from maintainers

Thank you for contributing to Rembo! 🚀
