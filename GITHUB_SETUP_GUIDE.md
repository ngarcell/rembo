# GitHub Repository Setup Guide

## 🚀 Step 1: Create Repository

1. **Go to**: https://github.com/new
2. **Repository name**: `rembo`
3. **Description**: `Matatu Fleet Management System - A comprehensive platform for managing matatu fleets, bookings, and operations in Kenya built with BMAD methodology`
4. **Visibility**: Public ✅
5. **Initialize**: Leave all checkboxes unchecked ❌
6. **Click**: "Create repository"

## 📤 Step 2: Push Code

After creating the repository, run:

```bash
# This will push all our code to GitHub
git push -u origin main
```

## 🛡️ Step 3: Configure Branch Protection Rules

### Main Branch Protection

1. **Go to**: `https://github.com/ngarcell/rembo/settings/branches`
2. **Click**: "Add rule"
3. **Branch name pattern**: `main`

### Protection Settings

#### ✅ **Require a pull request before merging**
- **Required approving reviews**: 1
- **Dismiss stale PR approvals when new commits are pushed**: ✅
- **Require review from code owners**: ✅ (if CODEOWNERS file exists)
- **Restrict pushes that create files larger than 100MB**: ✅

#### ✅ **Require status checks to pass before merging**
- **Require branches to be up to date before merging**: ✅
- **Status checks to require**:
  - `test-auth-service`
  - `security-scan`
  - `docker-build`
  - `integration-tests`

#### ✅ **Require conversation resolution before merging**

#### ✅ **Require signed commits**

#### ✅ **Require linear history**

#### ✅ **Include administrators**
- Enforce all configured restrictions for administrators

#### ❌ **Allow force pushes**
- Nobody should be able to force push to main

#### ❌ **Allow deletions**
- Nobody should be able to delete the main branch

### Development Branch Protection (Optional)

If you plan to use a `develop` branch:

1. **Create develop branch**:
   ```bash
   git checkout -b develop
   git push -u origin develop
   ```

2. **Set up protection** with similar rules but:
   - **Required approving reviews**: 1
   - **Allow force pushes**: ✅ (for maintainers only)
   - Less strict than main branch

## ⚙️ Step 4: Repository Settings

### General Settings

1. **Go to**: `https://github.com/ngarcell/rembo/settings`

#### Features
- **Wikis**: ✅ Enable
- **Issues**: ✅ Enable
- **Sponsorships**: ✅ Enable (optional)
- **Preserve this repository**: ✅ Enable
- **Discussions**: ✅ Enable

#### Pull Requests
- **Allow merge commits**: ✅
- **Allow squash merging**: ✅
- **Allow rebase merging**: ✅
- **Always suggest updating pull request branches**: ✅
- **Allow auto-merge**: ✅
- **Automatically delete head branches**: ✅

#### Archives
- **Include Git LFS objects in archives**: ✅

### Security Settings

1. **Go to**: `https://github.com/ngarcell/rembo/settings/security_analysis`

#### Security Features
- **Dependency graph**: ✅ Enable
- **Dependabot alerts**: ✅ Enable
- **Dependabot security updates**: ✅ Enable
- **Code scanning**: ✅ Enable (GitHub Actions will handle this)
- **Secret scanning**: ✅ Enable

## 🔐 Step 5: Secrets Configuration

### Repository Secrets

1. **Go to**: `https://github.com/ngarcell/rembo/settings/secrets/actions`
2. **Add the following secrets** (when you have real values):

```
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Redis
REDIS_URL=redis://host:port

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# SMS Service (Africa's Talking)
AFRICAS_TALKING_USERNAME=your-username
AFRICAS_TALKING_API_KEY=your-api-key
AFRICAS_TALKING_SENDER_ID=your-sender-id

# Docker Registry (if using private registry)
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password

# Deployment (if using cloud services)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
DIGITAL_OCEAN_TOKEN=your-do-token
```

## 📋 Step 6: Create CODEOWNERS File

Create `.github/CODEOWNERS`:

```
# Global owners
* @ngarcell

# Backend services
backend/ @ngarcell
backend/services/auth/ @ngarcell

# Infrastructure
docker-compose.yml @ngarcell
.github/ @ngarcell
infrastructure/ @ngarcell

# Documentation
docs/ @ngarcell
README.md @ngarcell
CONTRIBUTING.md @ngarcell

# BMAD Framework
.bmad-core/ @ngarcell
```

## 🏷️ Step 7: Create Labels

### Bug Labels
- `bug` - Something isn't working (red)
- `critical` - Critical bug that needs immediate attention (dark red)
- `security` - Security-related issue (red)

### Feature Labels
- `enhancement` - New feature or request (green)
- `feature` - New feature implementation (green)
- `improvement` - Enhancement to existing feature (light green)

### Priority Labels
- `priority: high` - High priority (red)
- `priority: medium` - Medium priority (yellow)
- `priority: low` - Low priority (green)

### Component Labels
- `auth` - Authentication service (blue)
- `fleet` - Fleet management (blue)
- `booking` - Booking system (blue)
- `payment` - Payment processing (blue)
- `gps` - GPS tracking (blue)
- `frontend` - Frontend/UI (purple)
- `backend` - Backend services (purple)
- `database` - Database related (orange)
- `infrastructure` - Infrastructure/DevOps (orange)

### Process Labels
- `needs-review` - Needs code review (yellow)
- `work-in-progress` - Work in progress (yellow)
- `blocked` - Blocked by external dependency (red)
- `duplicate` - Duplicate issue (gray)
- `wontfix` - Won't fix (gray)
- `help-wanted` - Help wanted (green)
- `good-first-issue` - Good for newcomers (green)

## 🔄 Step 8: Set Up Automated Workflows

The repository already includes:

### CI/CD Pipeline (`.github/workflows/ci.yml`)
- ✅ Unit tests for all services
- ✅ Security scanning
- ✅ Docker builds
- ✅ Integration tests
- ✅ Automated deployments

### Issue Templates
- ✅ Bug report template
- ✅ Feature request template

### Pull Request Template
- ✅ Comprehensive PR checklist
- ✅ BMAD methodology compliance
- ✅ Security and testing requirements

## 🎯 Step 9: Initial Project Board (Optional)

1. **Go to**: `https://github.com/ngarcell/rembo/projects`
2. **Create new project**: "Rembo Development"
3. **Add columns**:
   - 📋 Backlog
   - 🔄 In Progress
   - 👀 In Review
   - ✅ Done
   - 🚀 Released

## 📊 Step 10: Enable Insights

1. **Go to**: `https://github.com/ngarcell/rembo/pulse`
2. **Review**: Community standards
3. **Add missing items**:
   - ✅ Description
   - ✅ README
   - ✅ Code of conduct
   - ✅ Contributing guidelines
   - ✅ License
   - ✅ Issue templates
   - ✅ Pull request template

## ✅ Verification Checklist

After setup, verify:

- [ ] Repository created and code pushed
- [ ] Branch protection rules configured
- [ ] CI/CD pipeline running
- [ ] Security features enabled
- [ ] Labels created
- [ ] CODEOWNERS file added
- [ ] Secrets configured (when available)
- [ ] Issue templates working
- [ ] PR template working
- [ ] Community standards met

## 🚀 Next Steps

1. **Create first issue**: Use the bug report or feature request template
2. **Create development branch**: `git checkout -b develop && git push -u origin develop`
3. **Set up project board**: Organize your work
4. **Invite collaborators**: Add team members
5. **Configure notifications**: Set up email/Slack notifications
6. **Set up monitoring**: Add status badges to README

## 📞 Support

If you encounter any issues:
1. Check GitHub's documentation
2. Review the repository settings
3. Test the CI/CD pipeline
4. Verify branch protection rules are working

---

**🎉 Your repository is now enterprise-ready with best practices implemented!**
