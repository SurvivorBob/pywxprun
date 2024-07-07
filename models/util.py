from typing import Any, Optional, List

def dict_add(a: dict[Any, int | float], b: dict[Any, int | float]):
    keys = set(a.keys()) | set(b.keys())
    return {k: a.get(k, 0) + b.get(k, 0) for k in keys}

def dict_mul(a: dict[Any, int | float], n: int | float):
    return {k: a.get(k, 0) * n for k in a}

class TrieNode:
    def __init__(self):
        self.children = {}
        self.value: Optional[Any] = None

class PrefixTree:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, key: str, value: Any) -> None:
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.value = value

    def search(self, prefix: str) -> List[Any]:
        results = []

        def dfs(node: TrieNode, path: str):
            if node.value is not None:
                results.append(node.value)

            for child in node.children:
                dfs(node.children[child], path + child)

        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        dfs(node, prefix)
        return results