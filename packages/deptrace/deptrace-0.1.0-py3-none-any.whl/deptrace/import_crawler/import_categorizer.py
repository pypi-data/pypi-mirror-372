from importlib.util import find_spec
from pathlib import Path
from typing import Set, Dict, List
from deptrace.logging import get_logger

logger = get_logger(__name__)


class ImportCategorizer:
    def __init__(
        self, stdlib_paths: Set[str], site_packages_paths: Set[Path]
    ) -> None:
        self.stdlib_paths = stdlib_paths
        self.site_packages_paths = site_packages_paths
        self.system_imports: Set[str] = set()
        self.third_party_imports: Set[str] = set()
        self.local_imports: Set[str] = set()

    def categorize_import(self, module_name: str) -> None:
        """Categorize an import into system, third-party, or local."""
        try:
            # The find_spec function returns a spec (ModuleSpec object), which has an origin attribute.
            # The origin attribute is a string that describes the origin of the module.
            # For file-based modules, the origin is the path to the module.
            # For built-in and frozen modules, the origin is "built-in" or "frozen".
            spec = find_spec(module_name)
            if spec and spec.origin:
                origin_str: str = spec.origin
                is_builtin = origin_str == "built-in" or origin_str == "frozen"
                is_stdlib = any(origin_str.startswith(p) for p in self.stdlib_paths)
                if is_builtin or is_stdlib:
                    self.system_imports.add(module_name)
                    return

                # Check if it's in site-packages
                module_path = Path(origin_str).resolve()
                is_third_party = any(
                    str(module_path).startswith(str(site_pkg))
                    for site_pkg in self.site_packages_paths
                )
                if is_third_party:
                    self.third_party_imports.add(module_name)
                    return
        except (ImportError, AttributeError):
            pass

        # If find_spec fails or returns None/no origin, try searching site-packages directly
        base_module = module_name.split(".")[0]  # Get the root package name
        for site_pkg in self.site_packages_paths:
            potential_locations = [
                site_pkg / base_module,  # As a directory/package
                site_pkg / f"{base_module}.py",  # As a .py file
                site_pkg / f"{base_module}.pyi",  # As a .pyi file
                site_pkg / f"{base_module}.so",  # As a compiled module
            ]
            if any(loc.exists() for loc in potential_locations):
                self.third_party_imports.add(module_name)
                return

        # If not system or third-party, assume it's local
        self.local_imports.add(module_name)

    def get_unresolved_imports(self) -> Dict[str, List[str]]:
        """Returns unresolved imports as a dictionary for JSON output."""
        result = {}

        if self.local_imports:
            result["local_imports"] = sorted(list(self.local_imports))

        if self.system_imports:
            result["system_imports"] = sorted(list(self.system_imports))

        if self.third_party_imports:
            result["third_party_imports"] = sorted(list(self.third_party_imports))

        return result
