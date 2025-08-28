from dataclasses import dataclass

NamespaceName = str


@dataclass()
class NamespaceInfo:
    name: NamespaceName
    type: str = "unknown"

    def is_virtual(self) -> bool:
        return self.type == "virtual"

    def __str__(self) -> str:
        return self.name
