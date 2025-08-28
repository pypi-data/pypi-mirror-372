import ast
from typing import Any


def extract_import_aliases(tree: ast.AST) -> dict[str, str]:
    """Extract import aliases from the AST."""
    import_aliases = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Track 'from module import name' statements
            for alias in node.names:
                imported_name = alias.name
                local_name = alias.asname if alias.asname else imported_name
                import_aliases[local_name] = imported_name
        elif isinstance(node, ast.Import):
            # Track 'import module' statements
            for alias in node.names:
                module_name = alias.name
                local_name = alias.asname if alias.asname else module_name
                import_aliases[local_name] = module_name
    
    return import_aliases


def analyze_call_tree(source_code: str, target_function_name: str) -> dict[str, Any]:
    """
    Analyze Python source code to find all calls to a target function.

    Args:
        source_code: The Python source code to analyze
        target_function_name: Name of the target function to trace

    Returns:
        A dictionary with the call tree structure containing:
        - target_function: The name of the target function
        - direct_callers: List of functions that directly call the target
    """
    tree = ast.parse(source_code)
    
    # Extract import aliases for this file
    import_aliases = extract_import_aliases(tree)

    # Build a map of function definitions
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    functions[f"{node.name}.{item.name}"] = item

    # Find direct callers of the target function
    direct_callers = []

    for func_name, func_node in functions.items():
        call_sites = []

        # Walk through the function body to find calls
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                # Check if this is a call to our target function
                func_expr = node.func
                called_func_name = None
                
                if isinstance(func_expr, ast.Name):
                    # Direct function call: func() or renamed_func()
                    local_name = func_expr.id
                    
                    # Check if this is an aliased import
                    if local_name in import_aliases:
                        # This is an imported function, possibly renamed
                        actual_name = import_aliases[local_name]
                        if actual_name == target_function_name:
                            called_func_name = target_function_name
                    elif local_name == target_function_name:
                        # Direct call without import alias
                        called_func_name = target_function_name
                        
                elif isinstance(func_expr, ast.Attribute):
                    # Module.function call: module.func()
                    if func_expr.attr == target_function_name:
                        called_func_name = target_function_name
                
                if called_func_name == target_function_name:
                        # Extract arguments
                        positional = []
                        for arg in node.args:
                            positional.append(ast.unparse(arg))

                        keyword = {}
                        for kw in node.keywords:
                            keyword[kw.arg] = ast.unparse(kw.value)

                        # Determine context (simplified for now)
                        context = "direct"

                        call_sites.append(
                            {
                                "line": node.lineno,
                                "arguments": {
                                    "positional": positional,
                                    "keyword": keyword,
                                    "context": context,
                                },
                            }
                        )

        if call_sites:
            # For now, just track the direct callers without recursion
            direct_callers.append(
                {
                    "name": func_name.split(".")[-1] if "." in func_name else func_name,
                    "file": "example.py",
                    "call_sites": call_sites,
                    "callers": [],  # Will implement recursive caller tracking later
                }
            )

    return {"target_function": target_function_name, "direct_callers": direct_callers}
