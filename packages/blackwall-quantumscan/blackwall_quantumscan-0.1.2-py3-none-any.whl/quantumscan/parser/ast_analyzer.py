from __future__ import annotations

import ast
from typing import Dict, List, Set, Tuple, Optional

from .models import Finding, FindingError, Severity

# Mapping from fully-qualified names to (algorithm, severity)
DIRECT_CALLS = {
    "hashlib.sha1": "SHA-1",
    "hashlib.md5": "MD5",
    "Crypto.Hash.SHA1.new": "SHA-1",
    "Crypto.Hash.MD5.new": "MD5",
}

RSA_PREFIXES = ["Crypto.PublicKey.RSA", "cryptography.hazmat.primitives.asymmetric.rsa", "OpenSSL.crypto"]
ECC_PREFIXES = ["cryptography.hazmat.primitives.asymmetric.ec", "ecdsa"]


def analyze_python_ast(source: str, path: str) -> tuple[List[Finding], List[FindingError]]:
    """Analyze Python AST and return findings with evidence strings."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:  # pragma: no cover - error path tested separately
        err = FindingError(path=path, code="syntax_error", message=str(e))
        return [], [err]

    analyzer = _Analyzer(path)
    analyzer.visit(tree)
    return analyzer.findings, []


class _Analyzer(ast.NodeVisitor):
    def __init__(
        self,
        path: str,
        *,
        depth: int = 0,
        collect_only: bool = False,
        alias_map: Optional[Dict[str, str]] = None,
        assign_map: Optional[Dict[str, str]] = None,
        func_algos: Optional[Dict[str, Set[Tuple[str, str, int]]]] = None,
    ):
        self.path = path
        self.depth = depth
        self.collect_only = collect_only
        self.alias_map: Dict[str, str] = alias_map or {}
        self.assign_map: Dict[str, str] = assign_map or {}
        self.func_algos: Dict[str, Set[Tuple[str, str, int]]] = func_algos or {}
        self.findings: List[Finding] = []
        self.algos_found: Set[Tuple[str, str, int]] = set()

    # --- utility -------------------------------------------------
    def _resolve_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            name = node.id
            if name in self.assign_map:
                return self.assign_map[name]
            return self.alias_map.get(name, name)
        if isinstance(node, ast.Attribute):
            base = self._resolve_name(node.value)
            if base is None:
                return None
            return f"{base}.{node.attr}"
        return None

    def _resolve_call(self, node: ast.Call, depth: int = 0) -> List[Tuple[str, str, int]]:
        name = self._resolve_name(node.func)
        if name is None:
            return []
        results: List[Tuple[str, str, int]] = []
        if name in DIRECT_CALLS:
            algo = DIRECT_CALLS[name]
            results.append((algo, name, 1))
        elif name == "hashlib.new" and node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                algo_name = arg.value.lower()
                if algo_name in {"sha1", "md5"}:
                    algo = "SHA-1" if algo_name == "sha1" else "MD5"
                    results.append((algo, "hashlib.new", 1))
        else:
            for prefix in RSA_PREFIXES:
                if name.startswith(prefix):
                    results.append(("RSA", name, 1))
                    break
            else:
                for prefix in ECC_PREFIXES:
                    if name.startswith(prefix):
                        results.append(("ECC", name, 1))
                        break
        if not results and name in self.func_algos and depth < 2:
            for algo, evidence, d in self.func_algos[name]:
                if depth + d <= 2:
                    results.append((algo, evidence, depth + d))
        return results

    def _add_finding(self, node: ast.AST, algo: str, evidence: str):
        severity = Severity.HIGH if algo in {"SHA-1", "MD5"} else Severity.MEDIUM
        self.findings.append(
            Finding(
                path=self.path,
                lineno=node.lineno,
                col_offset=node.col_offset,
                algorithm=algo,
                evidence=evidence,
                severity=severity,
            )
        )

    # --- visitors ------------------------------------------------
    def visit_Import(self, node: ast.Import) -> None:  # pragma: no cover - trivial
        for alias in node.names:
            self.alias_map[alias.asname or alias.name] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # pragma: no cover - trivial
        module = node.module or ""
        for alias in node.names:
            fq = f"{module}.{alias.name}" if module else alias.name
            self.alias_map[alias.asname or alias.name] = fq
            self.alias_map[alias.name] = fq

    def visit_Assign(self, node: ast.Assign) -> None:
        fq = self._resolve_name(node.value)
        if fq:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.assign_map[target.id] = fq
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        child = _Analyzer(
            self.path,
            depth=self.depth + 1,
            collect_only=True,
            alias_map=self.alias_map.copy(),
            assign_map=self.assign_map.copy(),
            func_algos=self.func_algos,
        )
        for stmt in node.body:
            child.visit(stmt)
        self.func_algos[node.name] = child.algos_found
        # no further traversal to avoid treating definition as call

    def visit_Call(self, node: ast.Call) -> None:
        for algo, evidence, depth in self._resolve_call(node, self.depth):
            if self.collect_only:
                self.algos_found.add((algo, evidence, depth))
            else:
                self._add_finding(node, algo, evidence)
        self.generic_visit(node)
