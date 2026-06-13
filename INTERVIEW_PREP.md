# Interview Prep: fullapi Project

**Project:** Production-ready FastAPI project generator with zero dependencies  
**Role:** Creator & Maintainer  
**Tech Stack:** Python 3.8+, FastAPI, SQLAlchemy, Docker, Terraform  
**Principles:** Security-first, stdlib-only, production-grade

This document covers programming concepts, design principles, and architectural decisions used in fullapi.

## Core Programming Concepts

### 1. Modular Architecture

**What we did:**
Split functionality into separate modules: `terraform_ops.py`, `docker_ops.py`, `scale_ops.py`, `templates/terraform.py`

**Why:**
- Single Responsibility Principle: Each module handles one domain
- Easier testing: Can test terraform operations without touching docker logic
- Maintainability: Bug in scaling doesn't affect terraform init
- Team scalability: Different developers can work on different modules

**Why not alternatives:**
- Not monolithic: All logic in one file becomes unmaintainable at scale
- Not microservices: Overkill for CLI tool, adds network complexity
- Not plugins: Too much abstraction for straightforward operations

### 2. Configuration Management with Dataclasses

**What we did:**
Used Python dataclass for `ProjectConfig` with typed fields

**Why:**
- Type safety: IDE autocomplete, catches typos at development time
- Default values: `instance_size = "small"` without boilerplate
- Immutability option: Can freeze if needed
- Auto-generated `__init__`, `__repr__`, `__eq__`

**Why not alternatives:**
- Not dict: No type hints, easy to misspell keys, no IDE support
- Not class with manual init: Too much boilerplate code
- Not Pydantic: External dependency, we want stdlib only
- Not NamedTuple: Dataclass more flexible, better defaults

### 3. Template Method Pattern

**What we did:**
String templating for Terraform files using Python f-strings and Template class

```python
def main_tf(project_name: str, cloud_provider: str, enable_database: bool):
    # Dynamic generation based on features
```

**Why:**
- Conditional generation: Include database module only if enabled
- DRY: Single source of truth for terraform structure
- Type-safe interpolation: Python string formatting
- Readable: Template stays close to final output

**Why not alternatives:**
- Not Jinja2: External dependency, overkill for simple interpolation
- Not file copying: Can't conditionally include modules
- Not JSON/YAML generation: Terraform uses HCL, not JSON
- Not hardcoded strings: Can't adapt to project features

### 4. Strategy Pattern for Cloud Providers

**What we did:**
Provider-specific logic selected at runtime

```python
def _get_provider_block(cloud_provider: str) -> str:
    if cloud_provider == "aws":
        return 'aws provider config'
    elif cloud_provider == "gcp":
        return 'gcp provider config'
```

**Why:**
- Open/Closed Principle: Easy to add new providers without modifying existing code
- Runtime polymorphism: Decision made based on user input
- Testable: Can test each provider independently
- Clear separation: AWS logic doesn't pollute GCP logic

**Why not alternatives:**
- Not inheritance: `AWSProvider(BaseProvider)` adds unnecessary classes
- Not factory classes: Overkill for simple string generation
- Not separate files per provider: Would need dynamic imports
- Not one giant if-else: Hard to maintain, but we use if-else at small scale

### 5. Command Pattern (CLI)

**What we did:**
Each CLI command maps to a handler function

```python
actions = {
    "init": terraform_init,
    "plan": terraform_plan,
    "apply": terraform_apply
}
exit_code = actions[args.action]()
```

**Why:**
- Decoupling: CLI parsing separate from business logic
- Testability: Can call `terraform_init()` directly in tests
- Extensibility: Add new commands without touching argparse logic
- Clear intent: Each function does one thing

**Why not alternatives:**
- Not giant if-else in main: Hard to test, poor separation
- Not classes per command: Overkill, adds boilerplate
- Not Click library: Want stdlib only, argparse sufficient
- Not custom parser: argparse handles complex cases well

### 6. Subprocess Management

**What we did:**
Wrapped `subprocess.run()` with error handling

```python
result = subprocess.run(command, cwd=terraform_dir, check=False, text=True)
return result.returncode
```

**Why:**
- Platform-agnostic: Works on Linux/Mac/Windows
- Stderr/stdout capture: Can parse terraform output
- Exit code handling: Proper error propagation
- Non-blocking by default: Can add timeout if needed

**Why not alternatives:**
- Not os.system(): Deprecated, no output capture, security issues
- Not shell=True: Command injection vulnerability
- Not asyncio: Terraform commands are synchronous, no benefit
- Not threading: Single command at a time, sequential is clearer

### 7. Path Handling with pathlib

**What we did:**
Used `pathlib.Path` instead of string concatenation

```python
terraform_dir = Path.cwd() / "terraform"
tfvars_path = terraform_dir / "terraform.tfvars"
```

**Why:**
- Cross-platform: Handles Windows vs Unix paths automatically
- Readable: `/` operator clearer than `os.path.join()`
- Type-safe: Path methods prevent common mistakes
- Integrated: `.exists()`, `.read_text()` built-in

**Why not alternatives:**
- Not string concatenation: Breaks on Windows, fragile
- Not os.path: More verbose, older API style
- Not relative paths: `Path.cwd()` makes intent explicit
- Not hardcoded absolute paths: Not portable across machines

### 8. Error Handling Strategy

**What we did:**
Return exit codes, print errors to stdout, minimal exceptions

```python
if not terraform_dir.exists():
    print(f"[ERROR] No terraform/ directory found")
    return 1
```

**Why:**
- Unix philosophy: Exit code 0 = success, non-zero = failure
- User-friendly: Errors printed immediately, not stack traces
- Composable: Can chain commands in shell scripts
- Debuggable: User sees exactly what went wrong

**Why not alternatives:**
- Not exceptions everywhere: CLI shouldn't crash with traceback
- Not silent failures: User must know what happened
- Not logging framework: Overkill for CLI, adds dependency
- Not stderr vs stdout: Keep it simple, all to stdout

### 9. Dependency Injection

**What we did:**
Pass `ProjectConfig` as parameter, not global state

```python
def scaffold_project(config: ProjectConfig):
    _generate_terraform_files(project_path, config)
```

**Why:**
- Testability: Can inject test config without globals
- Thread-safe: No shared mutable state
- Clear dependencies: Function signature shows what it needs
- Reusability: Same function works for any config

**Why not alternatives:**
- Not global variables: Hard to test, thread-unsafe
- Not singleton pattern: Overkill, adds complexity
- Not environment variables: Type-unsafe, hard to validate
- Not reading from disk each time: Inefficient, error-prone

### 10. Composition Over Inheritance

**What we did:**
`ProjectConfig` has fields, doesn't inherit from `BaseConfig`

**Why:**
- Flexibility: Can compose any combination of features
- Simplicity: No class hierarchy to understand
- Explicit: All fields visible in one place
- Pythonic: Dataclasses favor composition

**Why not alternatives:**
- Not inheritance: `FullConfig(BasicConfig)` creates rigid hierarchy
- Not mixins: Hard to reason about method resolution order
- Not abstract base classes: No polymorphism needed here
- Not metaclasses: Extreme overkill for configuration

### 11. Lazy Evaluation

**What we did:**
Generate terraform files only when requested, not on import

```python
if config.terraform:
    _generate_terraform_files(project_path, config)
```

**Why:**
- Performance: Don't generate unused files
- Resource efficiency: No wasted I/O operations
- Conditional logic: Users without terraform don't pay the cost
- Clear flow: Generation happens at decision point

**Why not alternatives:**
- Not eager generation: Wastes resources for unused features
- Not import-time execution: Slows down CLI startup
- Not caching: Files generated once, no need to cache
- Not generators: Overkill for file generation

### 12. Type Hints

**What we did:**
Added type annotations to all functions

```python
def main_tf(project_name: str, cloud_provider: str, enable_database: bool) -> str:
```

**Why:**
- Documentation: Function signature shows intent
- IDE support: Autocomplete, refactoring tools work better
- Type checking: mypy can catch bugs before runtime
- Maintainability: Future developers understand expectations

**Why not alternatives:**
- Not docstrings only: Types more precise than English
- Not runtime type checking: Performance overhead
- Not Pydantic models: External dependency
- Not no types: Loses modern Python benefits

### 13. Immutable Data Structures

**What we did:**
Dataclass fields assigned once, not mutated

**Why:**
- Predictability: Config doesn't change mid-execution
- Thread-safe: No race conditions
- Debugging: State doesn't mysteriously change
- Functional style: Easier to reason about

**Why not alternatives:**
- Not mutable globals: Race conditions, hard to debug
- Not property setters: Unnecessary complexity
- Not frozen dataclass: Need some flexibility during init
- Not NamedTuple: Dataclass more convenient

### 14. Separation of Concerns

**What we did:**
CLI parsing, business logic, file I/O in separate layers

**Why:**
- Testability: Can test terraform logic without CLI
- Reusability: `terraform_apply()` callable from Python code
- Clarity: Each layer has one responsibility
- Maintainability: Change CLI without touching core logic

**Why not alternatives:**
- Not MVC: Overkill for CLI tool
- Not hexagonal architecture: Too abstract for this scale
- Not everything in one function: Untestable, unmaintainable
- Not microservices: Network overhead for local CLI

### 15. Convention Over Configuration

**What we did:**
Sensible defaults (small instances, us-east-1, local state)

**Why:**
- User experience: Works out of box, customize if needed
- Low barrier to entry: New users get working config
- Opinionated: Guides users to good practices
- Pragmatic: 80% use case works without config

**Why not alternatives:**
- Not require everything: Overwhelming for new users
- Not zero defaults: Empty config breaks, bad UX
- Not config files first: CLI flags more discoverable
- Not environment-based: Explicit better than implicit

## Architecture Decisions

### Remote Modules vs Embedded Code

**Decision:** Reference remote modules in `~/.fullapi/terraform-modules/`

**Rationale:**
- DRY: One module implementation, N project references
- Updates: Fix bug once, all projects can upgrade
- Clean projects: 5 config files vs 50+ module files
- Standard practice: How Terraform modules are meant to be used

**Trade-off:** Requires internet on first init, but can cache locally

### Local State Default vs Remote State

**Decision:** Default to local `terraform.tfstate`, optional remote

**Rationale:**
- Simplicity: Zero setup for single developer
- No dependencies: No S3 bucket needed upfront
- Progressive disclosure: Advanced users can enable later
- Cost: Remote state has associated costs

**Trade-off:** Local state not suitable for teams, but that's documented

### argparse vs Click/Typer

**Decision:** Use stdlib argparse

**Rationale:**
- Zero dependencies: Core principle of fullapi
- Sufficient features: Subcommands, help text, validation
- Stable: Won't break with library updates
- Learning: Understanding argparse is valuable skill

**Trade-off:** More verbose than Click, but still manageable

### String Templates vs File Templates

**Decision:** Generate terraform files from Python strings

**Rationale:**
- Conditional logic: Easy to include/exclude modules
- Type-safe: Python catches syntax errors
- No extra files: Template logic in code
- Dynamic: Can compute values during generation

**Trade-off:** Harder to preview final template, but generated files are reviewable

### Multi-cloud in One Codebase vs Separate

**Decision:** All providers in same codebase with runtime selection

**Rationale:**
- Consistent interface: Same commands for all clouds
- Shared logic: Validation, prompts, error handling reused
- Easier maintenance: One place to update
- User experience: Don't need provider-specific CLI

**Trade-off:** Code more complex than single-provider, but manageable with if-else

### Exit Codes vs Exceptions

**Decision:** Return exit codes, print errors, minimal exceptions

**Rationale:**
- Unix convention: 0 success, non-zero failure
- Shell integration: `fullapi terraform apply && deploy.sh`
- User-friendly: No Python tracebacks for expected errors
- Debuggable: Error message explains what's wrong

**Trade-off:** Can't use exception-based flow control, but CLI shouldn't anyway

## Performance Considerations

### Why not asyncio for terraform commands

Terraform operations are:
- Synchronous by nature (state locking)
- Long-running (apply takes minutes)
- User needs to see output in real-time

Async adds complexity without benefit. Sequential is clearer and sufficient.

### Why not parallel module generation

File generation is I/O bound and fast (<100ms). Parallelizing would add:
- Threading complexity
- Race conditions on disk writes
- Harder debugging

Sequential is fast enough and much simpler.

### Why not cache terraform plans

Terraform plan output is:
- Large (can be MBs)
- Stale immediately if code/vars change
- Not reusable (user should regenerate)

Caching adds complexity for zero benefit. Users run plan when needed.

## Security Considerations

### Why subprocess.run with check=False

We want to capture exit codes and handle them ourselves:
- `check=True` raises exception on failure
- We need to print errors and return exit code
- CLI shouldn't crash with traceback

We validate exit codes and propagate to user.

### Why no shell=True

`shell=True` is a command injection vulnerability:
- User input could contain shell metacharacters
- Unintended commands could execute

We pass commands as lists: `["terraform", "init"]` not `"terraform init"`

### Why terraform.tfvars in .gitignore

Contains sensitive data:
- Database passwords
- API keys
- Resource identifiers

Never commit secrets to git. Example file shows format, real file is local.

### Why we validate file paths

Using Path.cwd() and explicit checks:
- Prevents directory traversal attacks
- Ensures we're in correct directory
- Fails fast with clear error

Security through validation and explicit paths.

## Testing Strategy

### Why integration tests over unit tests

Terraform feature is integration-heavy:
- File generation depends on config + templates
- CLI depends on argparse + handlers
- Full flow: prompt -> generate -> validate

Integration tests verify actual behavior users experience.

Unit tests would mock too much, testing mocks not reality.

### Why manual testing documented

Some operations require real cloud accounts:
- Terraform apply to AWS
- Docker push to ECR
- Scaling infrastructure

Automated tests would be expensive and slow. Manual smoke tests documented in test file.

## Design Principles Applied

### SOLID Principles

**1. Single Responsibility Principle (SRP)**
- Each module has one job: `terraform_ops.py` handles terraform, `docker_ops.py` handles docker
- `ProjectConfig` only stores configuration, doesn't generate files
- CLI parsing separated from business logic

**2. Open/Closed Principle (OCP)**
- Adding new cloud providers doesn't modify existing code
- New presets added via JSON without code changes
- Template system extensible without breaking existing templates

**3. Liskov Substitution Principle (LSP)**
- All database adapters (SQLite, PostgreSQL, MySQL) work through same interface
- Cloud providers interchangeable through strategy pattern

**4. Interface Segregation Principle (ISP)**
- Basic mode doesn't force auth/docker dependencies
- Users only install what they need
- CLI flags for granular feature selection

**5. Dependency Inversion Principle (DIP)**
- Depends on abstractions (ProjectConfig) not concrete implementations
- Functions receive config as parameter, not global state

### DRY (Don't Repeat Yourself)
- Template system: one source of truth for each file type
- Remote terraform modules: fix once, all projects benefit
- Requirements deduplication: single dependency list

### KISS (Keep It Simple, Stupid)
- Stdlib only: no external dependencies for CLI
- Simple if-else over complex factory patterns
- Flat directory structure, no deep nesting

### YAGNI (You Aren't Gonna Need It)
- No complex plugin system (not needed yet)
- No GUI (CLI sufficient)
- No database for CLI state (files sufficient)

### Security by Design
- AUTO-GENERATED SECRET_KEY in development
- ENFORCED SECRET_KEY in production
- NO WEAK DEFAULTS (CHANGE_ME placeholders)
- SQL injection warnings in generated code
- Connection pooling prevents resource exhaustion
- CORS locked to specific headers

### Fail Fast Principle
- Validate environment before generation
- Check file existence before operations
- Type hints catch errors at development time
- Production crashes without SECRET_KEY (by design)

### Convention Over Configuration
- Sensible defaults (small instances, common regions)
- Works out-of-box, customize if needed
- Opinionated choices guide users to best practices

---

## Advanced Programming Concepts

### 1. Metaprogramming with Templates
String interpolation for dynamic code generation
```python
CONFIG = '''from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
'''
```

### 2. Functional Programming Elements
- Immutable data structures (dataclasses)
- Pure functions (no side effects in templates)
- Higher-order functions (decorators, lru_cache)

### 3. Defensive Programming
- Input validation at boundaries
- Graceful error handling (exit codes not exceptions)
- Health checks with DB connectivity
- Type hints for compile-time safety

### 4. Resource Management
- Context managers for database sessions (`yield db`)
- Connection pooling (pool_size=20, max_overflow=10)
- Automatic connection recycling (every hour)

### 5. Concurrency Considerations
- Thread-safe through immutable config
- No shared mutable state
- Connection pooling for parallel requests

### 6. Performance Optimization
- Lazy loading (generate only what's needed)
- lru_cache for settings singleton
- Efficient file operations (pathlib)
- No premature optimization

---

## Interview Questions You Should Be Ready For

### Architecture & Design

**Q: Why build another FastAPI tool when others exist?**

A: Existing tools either have dependencies, limited features, or poor defaults. fullapi is zero-dependency, security-hardened, and production-ready. Covers auth, Docker, databases, cloud deployment in one tool.

**Q: Why zero dependencies for the CLI?**

A: Portability - works anywhere Python runs. No dependency hell. Faster installs. Users trust it won't break their environment. Generated projects can have dependencies, but CLI stays clean.

**Q: Explain the security fixes in v1.1.1**

A: Six critical fixes:
1. SECRET_KEY auto-generates (dev) or enforces (prod) - prevents weak defaults
2. Strong password placeholders - can't miss them
3. Python 3.12 datetime fix - forward compatibility
4. Connection pooling - prevents exhaustion under load
5. CORS header lockdown - removed wildcard vulnerability
6. SQL injection warnings - educates users

**Q: Why enforce SECRET_KEY in production but not development?**

A: Developer experience vs security trade-off. Development auto-generates so devs can start immediately. Production crashes intentionally - forcing explicit security. Better to fail early than deploy with weak secrets.

**Q: How does component addition detect database presence?**

A: Reads `.fullapi.json` config to check `database` field. If none, generates in-memory routers. If present, generates CRUD with SQLAlchemy. Smart adaptation based on project type.

**Q: Explain the connection pooling implementation**

A: SQLAlchemy engine with `pool_size=20` (persistent connections), `max_overflow=10` (burst capacity), `pool_pre_ping=True` (health checks), `pool_recycle=3600` (hourly refresh). Handles 30 concurrent requests, prevents stale connections, protects database.

**Q: Why dataclass over Pydantic for ProjectConfig?**

A: Zero dependencies principle. Dataclass is stdlib, sufficient for our needs. Pydantic great for generated projects (they can have dependencies), but CLI must stay dependency-free.

**Q: How would you add GraphQL support?**

A: Add `--graphql` flag, generate Strawberry/Graphene templates, include in requirements conditionally. Same pattern as existing features. Template method pattern makes it straightforward.

**Q: Why templates as Python strings instead of separate files?**

A: Conditional logic easier in Python. Type-safe interpolation. Single codebase. No file I/O during generation. Trade-off: less readable than files, but more flexible.

**Q: Explain the rate limiting limitation**

A: Current implementation uses in-memory storage (dict). Works single-instance but breaks with horizontal scaling. Solution: Redis-based rate limiting (planned v1.2.0). Trade-off accepted for v1.1 simplicity.

**Q: How do you handle breaking changes across versions?**

A: Semantic versioning. Major version for breaking changes. CHANGELOG documents all changes. Generated projects pinned to specific versions. Users control upgrades.

---

### Security Questions

**Q: What are the OWASP Top 10 vulnerabilities and how does fullapi address them?**

A:
1. **Injection**: SQLAlchemy ORM prevents SQL injection, warnings in CRUD
2. **Broken Authentication**: JWT with bcrypt, enforced SECRET_KEY
3. **Sensitive Data Exposure**: .env.example not committed, strong placeholders
4. **XML External Entities**: Not applicable (JSON API)
5. **Broken Access Control**: Generated auth scaffolding, user implements logic
6. **Security Misconfiguration**: Security headers by default, rate limiting
7. **XSS**: Pydantic validation, FastAPI auto-escaping
8. **Insecure Deserialization**: Pydantic validation layer
9. **Components with Known Vulnerabilities**: Pinned versions, regular updates
10. **Insufficient Logging**: Structured logging with rotation

**Q: How would you implement RBAC (Role-Based Access Control)?**

A: Add `roles` table, `user_roles` junction table, permission decorators:
```python
@require_role("admin")
async def admin_endpoint(): ...
```
Check role in dependency injection. Could be preset feature in v2.0.

**Q: Explain the SQL injection risk and mitigation**

A: Risk: User input in raw SQL (`f"SELECT * FROM users WHERE id={user_id}"`).  
Mitigation: SQLAlchemy ORM uses parameterized queries automatically. Warning comments educate users. Never use `.execute()` with f-strings.

**Q: Why CORS specific headers instead of wildcard?**

A: Wildcard (`*`) allows any header including sensitive ones (cookies, custom auth). Specific list (Content-Type, Authorization, X-Request-ID) only allows what's needed. Defense in depth.

**Q: How do you prevent DoS attacks?**

A: Rate limiting (100 req/60sec default), connection pooling (prevents DB exhaustion), request size limits (FastAPI default), timeout configurations. Planned: Redis-based distributed rate limiting.

---

### Scalability Questions

**Q: Can fullapi-generated apps scale horizontally?**

A: Yes, with caveats:
- ✅ Stateless design works with load balancers
- ✅ Database connection pooling handles concurrency
- ✅ Redis for session storage (not in-memory)
- ❌ In-memory rate limiting breaks (fix in v1.2.0)

**Q: What's the bottleneck in current design?**

A: In-memory rate limiting. Single instance only. Solution: Redis-based rate limiting with sliding window. Already have Redis support, just need to migrate rate limiter.

**Q: How would you implement caching?**

A: Decorator pattern with Redis backend:
```python
@cache(ttl=300)
async def expensive_query(id: int):
    return db.query(Model).get(id)
```
Cache key from function name + args. Invalidate on updates. Planned v1.2.0.

**Q: Explain database connection pooling strategy**

A: 20 persistent + 10 overflow = 30 total. Pre-ping checks health. Recycle every hour prevents stale connections. Max connections limited by DB server capacity. Monitor with `pool.size()`.

**Q: How would you add background job processing?**

A: Celery with Redis broker:
1. Add `--celery` flag
2. Generate worker.py, tasks.py
3. Include celery in requirements
4. Docker-compose adds celery service
Pattern fits existing architecture.

---

### Testing Questions

**Q: Why no test suite in the repository?**

A: `tests/` directory used for manual feature testing. Each test folder is a generated project verifying specific features. Pragmatic approach for CLI tool. Unit tests planned for v1.2.0.

**Q: How do you test generated projects?**

A: Generate project, verify structure, load Python modules, check for import errors. Integration tests verify full flow: `fullapi new -> pip install -> python -c "from main import app"`.

**Q: What would a proper test suite look like?**

A:
- Unit tests: template generation, config parsing
- Integration tests: full CLI commands, file generation
- Smoke tests: generated projects run without errors
- Security tests: validate no weak defaults
- Load tests: connection pooling under load

---

### Code Quality Questions

**Q: How do you ensure code quality without tests?**

A: 
- Type hints (mypy-compatible)
- Manual testing per feature in tests/
- Real-world usage (dogfooding)
- Security audits (v1.1.1 improvements)
- Code reviews (documented decisions)

**Q: Explain your commit message convention**

A: Conventional Commits:
- `fix:` bug fixes
- `feat:` new features
- `docs:` documentation
- `refactor:` code restructuring
- Under 50 chars, no Anthropic attribution

**Q: Why pathlib over os.path?**

A: Cross-platform, readable (`/` operator), type-safe, integrated methods (`.exists()`, `.read_text()`). Modern Python best practice. os.path is legacy API.

**Q: How would you refactor if this grew 10x?**

A: 
1. Plugin system for templates
2. Provider abstraction (ABC for clouds)
3. Proper test suite (pytest)
4. CLI framework (Click/Typer)
5. Separate packages per feature

But not premature - current design scales fine for now.

---

### Trade-offs & Decisions

**Q: Why not use Cookiecutter or similar?**

A: Cookiecutter is template-focused, not feature-aware. fullapi knows about databases, auth, Docker. Smart generation based on flags. More opinionated, less flexible. Better UX for FastAPI specifically.

**Q: What's the biggest technical debt?**

A: In-memory rate limiting. Acknowledged limitation, documented, planned fix in v1.2.0. Accepted trade-off for v1.1 simplicity.

**Q: Why Terraform instead of Pulumi/CDK?**

A: Terraform is industry standard, cloud-agnostic, declarative, huge ecosystem. Pulumi requires Go/TypeScript. CDK is AWS-only. Terraform works everywhere, most teams know it.

**Q: Would you rewrite in Go/Rust?**

A: No. Python is lingua franca of data/ML/API developers. Zero dependencies harder in Go/Rust. Distribution easier with Python (pip). Performance not a bottleneck for CLI.

---

## Behavioral Interview Prep

**Q: Why did you build fullapi?**

A: Noticed gap in FastAPI ecosystem - no production-grade project generator. Existing tools either too basic or wrong trade-offs. Built what I wished existed when starting FastAPI projects. Scratching own itch became useful for others.

**Q: Biggest challenge in v1.1.1?**

A: Balancing security with developer experience. Enforcing SECRET_KEY is breaking change but necessary. Solution: auto-generate in dev (good DX), enforce in prod (security). Fail fast prevents weak deployments.

**Q: How do you prioritize features?**

A: Security > scalability > convenience. P0 issues block production use. P1 issues limit scale. P2 issues improve experience. v1.1.1 fixed P0 security issues before adding features.

**Q: What would you do differently?**

A: Start with test suite. Manual testing works but automated would catch regressions faster. Trade-off: shipped faster without tests, paying tech debt now.

**Q: How do you handle user feedback?**

A: GitHub issues for bugs/features. Security issues fixed immediately. Features evaluated: does it fit zero-dependency principle? Is it production-critical? Can it be preset/plugin?

**Q: Why not use a framework like Serverless or Pulumi?**

A: Terraform is industry standard, widely known, has massive module ecosystem. Pulumi requires learning another tool. Serverless is AWS-specific. Terraform works across clouds and most teams already use it.

**Q: Why generate files instead of API calls to Terraform?**

A: Terraform is file-based by design. Users need to see and modify terraform files for their specific needs. Files are version-controlled, reviewable in PRs, and auditable. API would be a black box.

**Q: How would you add Azure support?**

A: Add Azure provider block to `_get_provider_block()`, add Azure regions to prompt, add Azure-specific resource types to modules. Pattern already supports it, just need Azure-specific details.

**Q: What if terraform binary is not installed?**

A: We check for `FileNotFoundError` and print helpful error with download link. User must install terraform, we don't bundle it (licensing, size, updates).

**Q: How do you handle terraform state conflicts?**

A: Default local state has no conflicts (single user). Remote state has locking (DynamoDB for S3). We recommend remote state for teams but don't enforce it.

**Q: Why not Kubernetes instead of ECS/Cloud Run?**

A: Kubernetes is overkill for most FastAPI apps. ECS Fargate, Cloud Run are simpler, cheaper, managed. Users needing K8s can write their own terraform modules.

**Q: How would you test the terraform generation without applying?**

A: `terraform validate` checks syntax, `terraform plan` shows what would be created. Integration test verifies files generate correctly and pass validation.

**Q: What about terraform module versioning?**

A: Modules reference `~/.fullapi/terraform-modules/` which can be versioned. Users can pin specific versions or use latest. We recommend pinning in production.

**Q: Why not generate terraform modules in each project?**

A: DRY violation, 50+ files per project, hard to update. Remote modules mean one fix updates all projects. Standard terraform practice.

**Q: How do you handle breaking changes in terraform?**

A: Pin terraform version `>= 1.0.0, < 2.0.0`. Provider versions also pinned `~> 5.0`. Users control when to upgrade, we test before releasing updates.
