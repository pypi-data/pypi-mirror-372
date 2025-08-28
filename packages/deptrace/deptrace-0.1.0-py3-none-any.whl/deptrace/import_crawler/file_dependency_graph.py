from dataclasses import dataclass
from typing import Dict, Set, List, Optional
from .file_info import FileInfo
from .import_categorizer import ImportCategorizer

@dataclass
class FileDependencyGraph:
    """Represents a dependency graph of Python modules."""

    dependencies: Dict[FileInfo, Set[FileInfo]]
    import_categorizer: ImportCategorizer

    def __init__(self, import_categorizer: Optional[ImportCategorizer] = None) -> None:
        self.dependencies = {}
        if import_categorizer:
            self.import_categorizer = import_categorizer

    def add_dependency(self, source: FileInfo, target: FileInfo) -> None:
        """Add a dependency from source to target module."""
        self.dependencies.setdefault(source, set()).add(target)
        # Ensure target exists in graph even if it has no dependencies
        self.dependencies.setdefault(target, set())

    def __getitem__(self, key: FileInfo) -> Set[FileInfo]:
        """Allow dictionary-style access to dependencies."""
        return self.dependencies[key]

    def __setitem__(self, key: FileInfo, value: Set[FileInfo]) -> None:
        """Allow dictionary-style assignment of dependencies."""
        self.dependencies[key] = value

    def __contains__(self, key: str) -> bool:
        """Allow 'in' operator to check if a module path is in the graph."""
        return any(str(k) == key for k in self.dependencies)

    def get_imports(self, file_path: str) -> List[str]:
        """Get a list of all files imported by the given file."""
        # Find the FileInfo matching this file path
        for source, targets in self.dependencies.items():
            if str(source.full_path) == file_path:
                return [str(target.full_path) for target in targets]
        return []

    def get_all_files(self) -> List[str]:
        """Get a list of all files in the dependency graph."""
        all_files = set()
        for source in self.dependencies:
            all_files.add(str(source.full_path))
            for target in self.dependencies[source]:
                all_files.add(str(target.full_path))
        return list(all_files)

    def imports(self, source_file: str, target_file: str) -> bool:
        """Check if source_file directly imports target_file."""
        for source, targets in self.dependencies.items():
            if str(source.full_path) == source_file:
                for target in targets:
                    if str(target.full_path) == target_file:
                        return True
        return False

    def imported_by(self, target_file: str, source_file: str) -> bool:
        """Check if target_file is directly imported by source_file."""
        return self.imports(source_file, target_file)

    def has_transitive_dependency(self, source_file: str, target_file: str) -> bool:
        """Check if source_file directly or indirectly imports target_file."""
        visited = set()

        def dfs(current: str) -> bool:
            if current == target_file:
                return True

            if current in visited:
                return False

            visited.add(current)

            for source, targets in self.dependencies.items():
                if str(source.full_path) == current:
                    for target in targets:
                        target_path = str(target.full_path)
                        if dfs(target_path):
                            return True
            return False

        return dfs(source_file)

    def to_json(self) -> Dict[str, Dict[str, list[str]]]:
        """
        Convert the dependency graph to a JSON-serializable dictionary.

        Returns:
            A dictionary with file paths as keys and their import information as values.
            Each value contains 'imports' and 'imported_by' lists.
        """
        json_graph: Dict[str, Dict[str, list[str]]] = {}

        # First pass: Create nodes and add imports
        for source, targets in self.dependencies.items():
            source_path = str(source)
            if source_path not in json_graph:
                json_graph[source_path] = {"imports": [], "imported_by": []}

            json_graph[source_path]["imports"] = sorted(
                [str(target) for target in targets]
            )

        # Second pass: Build imported_by relationships
        for source, targets in self.dependencies.items():
            for target in targets:
                target_path = str(target)
                json_graph[target_path]["imported_by"].append(str(source))

        # Sort imported_by lists for consistency
        for node in json_graph.values():
            node["imported_by"].sort()

        return json_graph
