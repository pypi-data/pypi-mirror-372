import warnings
from typing import Mapping, Any, Optional, Iterable

from nestify.recursive_processor import RecursiveProcessor


class Nestify(RecursiveProcessor):
    """
    将字典中带“点号路径”的键（如 'a.b.c'）展开为嵌套结构：
      {'a.b.c': 1} -> {'a': {'b': {'c': 1}}}

    冲突策略：
      - forbid_mixed:  当同一键位上出现 dict 与 非 dict 混合时抛错（默认）
      - merge_dicts:   两个 dict 合并（键冲突时发出警告，并以新值覆盖旧值）
      - overwrite:     非 dict 直接覆盖，并发出警告
    """

    def __init__(
        self,
        separator: str = ".",
        conflict_policy: str = "forbid_mixed",
        iterable_types: Optional[Iterable[type]] = None,
    ):
        super().__init__(iterable_types=iterable_types)
        if not separator:
            raise ValueError("separator must be a non-empty string")
        if conflict_policy not in {"forbid_mixed", "merge_dicts", "overwrite"}:
            raise ValueError("conflict_policy must be one of: 'forbid_mixed', 'merge_dicts', 'overwrite'")
        self.separator = separator
        self.conflict_policy = conflict_policy

    # --- 覆盖叶子处理：叶子如果还是 dict，也要继续展开 ---
    def process_leaf(self, x: Any) -> Any:
        if isinstance(x, dict):
            return self.process_dict(x)
        return x

    # --- 核心：将一条路径插入到目标 dict 中 ---
    def _insert_path(self, dest: dict, parts: list[str], value: Any) -> None:
        """
        将 value 按路径 parts（如 ['a', 'b', 'c']）插入到 dest 中。
        途中会自动创建缺失的子 dict，并根据冲突策略处理终点冲突。
        """
        node = dest
        # 走到最后一层之前，保证每层都是 dict
        for i, p in enumerate(parts[:-1]):
            if p not in node:
                node[p] = {}
            node = node[p]
            if not isinstance(node, dict):
                path_str = self.separator.join(parts[: i + 1])
                raise ValueError(
                    f"Path conflict at '{path_str}': expected a dict at this level but found {type(node).__name__}."
                )

        leaf_key = parts[-1]
        if leaf_key not in node:
            node[leaf_key] = value
            return

        # 已存在，触发冲突处理
        existing = node[leaf_key]
        self._resolve_conflict(node, leaf_key, existing, value, parts)

    def _resolve_conflict(
        self,
        parent: dict,
        key: str,
        old: Any,
        new: Any,
        full_path: list[str],
    ) -> None:
        """按策略处理同一位置的冲突。"""
        path_str = self.separator.join(full_path)

        old_is_dict = isinstance(old, dict)
        new_is_dict = isinstance(new, dict)

        # 禁止 dict 与 非 dict 混合
        if self.conflict_policy == "forbid_mixed":
            if old_is_dict != new_is_dict:
                raise ValueError(
                    f"Type mismatch at '{path_str}': cannot merge dict with non-dict "
                    f"(existing={type(old).__name__}, new={type(new).__name__})."
                )
            if old_is_dict and new_is_dict:
                # dict-merge（保留策略：新值覆盖旧值，冲突键告警）
                self._merge_dicts_in_place(old, new, path_str)
            else:
                # 非 dict 同名：直接覆盖并告警
                warnings.warn(
                    f"Overwriting non-dict value at '{path_str}'. Old={old!r}, New={new!r}",
                    RuntimeWarning,
                )
                parent[key] = new
            return

        # 允许 dict 合并
        if self.conflict_policy == "merge_dicts":
            if old_is_dict and new_is_dict:
                self._merge_dicts_in_place(old, new, path_str)
            elif old_is_dict != new_is_dict:
                # 混合类型，也允许覆盖并警告
                warnings.warn(
                    f"Merging mixed types at '{path_str}' (dict vs non-dict). Overwriting existing value.",
                    RuntimeWarning,
                )
                parent[key] = new
            else:
                # 非 dict 同名：覆盖并警告
                warnings.warn(
                    f"Overwriting non-dict value at '{path_str}'. Old={old!r}, New={new!r}",
                    RuntimeWarning,
                )
                parent[key] = new
            return

        # 全量覆盖策略
        if self.conflict_policy == "overwrite":
            if old_is_dict and new_is_dict:
                # 合并比直接替换更稳妥，也能尽可能保留旧内容
                self._merge_dicts_in_place(old, new, path_str)
            else:
                if old != new:
                    warnings.warn(
                        f"Overwriting value at '{path_str}'. Old={old!r}, New={new!r}",
                        RuntimeWarning,
                    )
                parent[key] = new
            return

        # 兜底（理论上不会到这）
        raise RuntimeError("Unknown conflict policy.")

    def _merge_dicts_in_place(self, target: dict, incoming: dict, path_str: str) -> None:
        """就地合并两个 dict，键冲突时以 incoming 覆盖 target，并发出警告。"""
        overlap = set(target).intersection(incoming)
        if overlap:
            warnings.warn(
                f"Key overlap while merging dicts at '{path_str}': {sorted(overlap)}. "
                f"Incoming values will overwrite existing ones.",
                RuntimeWarning,
            )
        for k, v in incoming.items():
            # 对于深层 dict 冲突，进行递归合并
            if isinstance(target.get(k), dict) and isinstance(v, dict):
                self._merge_dicts_in_place(target[k], v, f"{path_str}.{k}")
            else:
                target[k] = v

    # --- 覆盖：对 dict 的处理，执行“点号展开” ---
    def process_dict(self, d: Mapping[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for raw_key, raw_value in d.items():
            value = self.process(raw_value)  # 先递归处理值
            # 仅当 key 是字符串且包含分隔符时才展开
            if isinstance(raw_key, str) and self.separator in raw_key:
                parts = [p for p in raw_key.split(self.separator) if p != ""]
                if not parts:
                    warnings.warn(f"Empty path derived from key {raw_key!r}. Skipped.", RuntimeWarning)
                    continue
                self._insert_path(out, parts, value)
            else:
                # 普通键，直接写入（若冲突，按策略处理）
                if raw_key in out:
                    self._resolve_conflict(out, raw_key, out[raw_key], value, [str(raw_key)])
                else:
                    out[raw_key] = value
        return out


def nestify(d: Any, separator: str = ".", conflict_policy: str = "forbid_mixed") -> dict[str, Any]:
    return Nestify(separator=separator, conflict_policy=conflict_policy).process(d)
