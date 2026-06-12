"""Project health check (fullapi doctor)."""

import re
from pathlib import Path

from fullapi.colors import (
    ICON_CHECK, ICON_CROSS, ICON_WARNING,
    success, error, warning, info, bold
)
from fullapi.metadata import read_metadata


def run_doctor() -> None:
    """Run project health checks."""
    print()
    print(f"  {bold('Project Health Check')}")
    print()

    metadata = read_metadata()
    passed = 0
    failed = 0
    warnings = 0

    # Check 1: main.py exists
    if Path("main.py").exists():
        _pass("main.py exists")
        passed += 1
    else:
        _fail("main.py not found — not a valid fullapi project")
        failed += 1
        _summary(passed, failed, warnings)
        return

    # Check 2: .fullapi.json exists
    if metadata:
        _pass(f".fullapi.json found (v{metadata.get('version', '?')})")
        passed += 1
    else:
        _warn(".fullapi.json missing — project may have been created with older fullapi")
        warnings += 1

    # Check 3: requirements.txt exists
    if Path("requirements.txt").exists():
        _pass("requirements.txt exists")
        passed += 1
    else:
        _fail("requirements.txt missing")
        failed += 1

    # Check 4: routers directory
    if Path("routers").is_dir():
        _pass("routers/ directory exists")
        passed += 1
    else:
        _fail("routers/ directory missing")
        failed += 1

    # Check 5: router imports match files
    main_content = Path("main.py").read_text()
    router_files = list(Path("routers").glob("*.py")) if Path("routers").is_dir() else []
    router_names = [f.stem for f in router_files if f.stem != "__init__"]

    imported_routers = _extract_router_imports(main_content)

    for name in router_names:
        if name == "health":
            continue
        if name not in imported_routers:
            _warn(f"routers/{name}.py exists but not imported in main.py")
            warnings += 1

    for name in imported_routers:
        if name not in router_names and name != "health":
            _fail(f"main.py imports router '{name}' but routers/{name}.py not found")
            failed += 1

    if not (set(router_names) - set(imported_routers) - {"health"}) and not (set(imported_routers) - set(router_names)):
        _pass("all routers properly imported")
        passed += 1

    # Check 6: database consistency
    if metadata and metadata.get("database", "none") != "none":
        db_checks = ["db/session.py", "models", "crud"]
        for path in db_checks:
            if Path(path).exists():
                _pass(f"{path} exists (database: {metadata['database']})")
                passed += 1
            else:
                _fail(f"{path} missing — project configured with database '{metadata['database']}'")
                failed += 1
    elif Path("db").is_dir():
        _pass("db/ directory exists")
        passed += 1

    # Check 7: auth consistency
    if metadata and metadata.get("auth"):
        if Path("core/security.py").exists():
            _pass("core/security.py exists (auth enabled)")
            passed += 1
        else:
            _fail("core/security.py missing — project configured with auth")
            failed += 1

    # Check 8: docker consistency
    if metadata and metadata.get("docker"):
        for f in ["Dockerfile", "docker-compose.yml"]:
            if Path(f).exists():
                _pass(f"{f} exists")
                passed += 1
            else:
                _fail(f"{f} missing — project configured with docker")
                failed += 1

    # Check 9: requirements covers key imports
    if Path("requirements.txt").exists():
        req_content = Path("requirements.txt").read_text().lower()
        if "fastapi" in req_content:
            _pass("fastapi in requirements.txt")
            passed += 1
        else:
            _fail("fastapi not in requirements.txt")
            failed += 1

        if metadata and metadata.get("database", "none") != "none":
            if "sqlalchemy" in req_content:
                _pass("sqlalchemy in requirements.txt")
                passed += 1
            else:
                _fail("sqlalchemy missing from requirements.txt")
                failed += 1

    # Check 10: redis consistency
    if metadata and metadata.get("redis"):
        if Path("core/redis_config.py").exists():
            _pass("redis config exists")
            passed += 1
        else:
            _fail("core/redis_config.py missing — project configured with redis")
            failed += 1

    _summary(passed, failed, warnings)


def _extract_router_imports(content: str) -> list:
    """Extract router names imported in main.py."""
    names = []
    for match in re.finditer(r"from routers[.\s]+import\s+(.+)", content):
        imports = match.group(1)
        names.extend([n.strip().split(" ")[0] for n in imports.split(",")])
    for match in re.finditer(r"from routers\.(\w+)\s+import", content):
        names.append(match.group(1))
    return names


def _pass(msg: str):
    print(f"  {ICON_CHECK}  {msg}")


def _fail(msg: str):
    print(f"  {ICON_CROSS}  {error(msg)}")


def _warn(msg: str):
    print(f"  {ICON_WARNING}  {warning(msg)}")


def _summary(passed: int, failed: int, warnings: int):
    print()
    parts = []
    if passed:
        parts.append(success(f"{passed} passed"))
    if failed:
        parts.append(error(f"{failed} failed"))
    if warnings:
        parts.append(warning(f"{warnings} warnings"))
    print(f"  {bold('Result:')} {', '.join(parts)}")
    print()
    if failed == 0:
        print(f"  {success('Project looks healthy!')}")
    else:
        print(f"  {info('Run')} fullapi doctor {info('after fixing issues to re-check')}")
    print()
