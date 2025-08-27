"""Pythonic API for Datastar attributes in StarHTML."""

import json
import re
from re import Pattern
from typing import Any

from fastcore.xml import NotStr


class DatastarAttr:
    """Wrapper that enables flat API usage without ** unpacking."""

    def __init__(self, attrs):
        self.attrs = attrs

    def __repr__(self):
        return f"DatastarAttr({self.attrs})"


# ============================================================================
# Helper Functions & Expression Utilities
# ============================================================================


def t(template: str) -> str:
    """JavaScript template literal using Python f-string style."""
    return f"`{re.sub(r'{([^}]+)}', r'${\1}', template)}`"


def if_(condition: str | dict[str, str], *args, **kwargs) -> str:
    """CSS-aligned conditional matching if() function."""
    if len(args) == 2:
        return f"{condition} ? {_to_js_value(args[0])} : {_to_js_value(args[1])}"

    if kwargs:
        default = kwargs.pop("_", "null")
        result = _to_js_value(default)
        for pattern, value in reversed(kwargs.items()):
            check = (
                condition
                if pattern == "true"
                else f"!{condition}"
                if pattern == "false"
                else f"{condition} === {_to_js_value(pattern)}"
            )
            result = f"{check} ? {_to_js_value(value)} : {result}"
        return result

    if isinstance(condition, dict):
        conditions = [(c, v) for c, v in condition.items() if c != "_"]
        result = _to_js_value(condition.get("_", "null"))
        for cond, val in reversed(conditions):
            result = f"{cond} ? {_to_js_value(val)} : {result}"
        return result

    raise ValueError("if_ requires either 2 positional args or keyword args with conditions")


# ============================================================================
# Internal Utilities
# ============================================================================


def _make_comparison(op: str):
    def compare(signal: str, value: Any) -> str:
        sig = signal if signal.startswith("$") else f"${{{signal}}}"
        val = _to_js_value(value) if op == "===" else value
        return f"{sig} {op} {val}"

    return compare


equals = _make_comparison("===")
gt = _make_comparison(">")
lt = _make_comparison("<")
gte = _make_comparison(">=")
lte = _make_comparison("<=")


def _to_js_value(value: Any) -> str:  # noqa: PLR0911
    match value:
        case bool():
            return "true" if value else "false"
        case str() if value.startswith(("$", "`")):
            return value
        case str():
            return json.dumps(value)
        case int() | float():
            return str(value)
        case None:
            return "null"
        case dict() | list() | tuple():
            return json.dumps(value)
        case _:
            return json.dumps(str(value))


def _normalize_value(value: Any, wrap_strings: bool = False) -> Any:
    match value:
        case bool():
            return "true" if value else "false"
        case None:
            return "null"
        case int() | float():
            return value
        case str():
            return NotStr(value) if wrap_strings else value
        case dict() | list() | tuple():
            return json.dumps(value)
        case _:
            return str(value)


def _to_signal_value(value: Any) -> str:
    """Convert values for data-signals-* without over-quoting strings."""
    match value:
        case bool():
            return "true" if value else "false"
        case None:
            return "null"
        case int() | float():
            return str(value)
        case str():
            return " " if value == "" else value
        case dict() | list() | tuple():
            return json.dumps(value)
        case _:
            return str(value)


def _process_patterns(patterns: str | list[str | Pattern]) -> str | list[str]:
    if isinstance(patterns, str):
        return f"/{patterns}/"
    patterns = patterns if isinstance(patterns, list | tuple) else [patterns]
    result = [f"/{p.pattern}/" if hasattr(p, "pattern") else f"/{p}/" for p in patterns]
    return result[0] if len(result) == 1 else result


# ============================================================================
# Core Datastar Attributes
# ============================================================================


def ds_show(value: bool | str) -> DatastarAttr:
    return DatastarAttr({"data-show": _normalize_value(value)})


def ds_text(value: str) -> DatastarAttr:
    return DatastarAttr({"data-text": _normalize_value(value)})


def ds_bind(signal: str, case: str | None = None) -> DatastarAttr:
    if case:
        return DatastarAttr({f"data-bind-{signal}__case.{case}": True})
    return DatastarAttr({"data-bind": signal})


def ds_ref(name: str) -> DatastarAttr:
    return DatastarAttr({"data-ref": name})


def ds_indicator(name: str) -> DatastarAttr:
    return DatastarAttr({"data-indicator": name})


def ds_effect(expression: str) -> DatastarAttr:
    return DatastarAttr({"data-effect": NotStr(expression)})


def ds_computed(name: str, expression: str, case: str | None = None) -> DatastarAttr:
    key = f"data-computed-{name}" + (f"__case.{case}" if case else "")
    return DatastarAttr({key: expression})


# ============================================================================
# Conditional Attributes (class, style, attr)
# ============================================================================


def _make_attr_func(prefix: str):
    def attr_func(**kwargs) -> DatastarAttr:
        return DatastarAttr(
            {f"{prefix}-{name.replace('_', '-')}": _normalize_value(value) for name, value in kwargs.items()}
        )

    return attr_func


ds_class = _make_attr_func("data-class")
ds_style = _make_attr_func("data-style")
ds_attr = _make_attr_func("data-attr")


# ============================================================================
# Signals & State Management
# ============================================================================


def ds_signals(*args, **kwargs) -> DatastarAttr:
    ifmissing = kwargs.pop("ifmissing", None)
    signals = args[0] if args and isinstance(args[0], dict) else kwargs

    result = {}
    if ifmissing:
        result["data-signals__ifmissing"] = ifmissing

    for name, value in signals.items():
        result[f"data-signals-{name}"] = _to_signal_value(value)

    return DatastarAttr(result)


def ds_persist(*signals, include=None, exclude=None, session=False, key=None):
    attr_key = f"data-persist-{key}" if key else "data-persist" + ("__session" if session else "")
    value = (
        ",".join(signals)
        if signals
        else json.dumps({k: _process_patterns(v) for k, v in [("include", include), ("exclude", exclude)] if v})
        if include or exclude
        else None
    )
    return DatastarAttr({attr_key: value})


def ds_json_signals(show=True, include=None, exclude=None, terse=False):
    key = f"data-json-signals{'__terse' if terse else ''}"
    if show is False:
        value = "false"
    elif include or exclude:
        filters = [f"{k}: {_process_patterns(v)}" for k, v in [("include", include), ("exclude", exclude)] if v]
        value = f"{{{', '.join(filters)}}}"
    else:
        value = True
    return DatastarAttr({key: value})


# ============================================================================
# Event Handlers
# ============================================================================


def _build_event_key(base: str, modifiers: list[str], value_mods: dict[str, str]) -> str:
    modifier_parts = modifiers.copy()
    for name, value in value_mods.items():
        if value is True:
            modifier_parts.append(name)
        elif name in ("debounce", "throttle"):
            if match := re.search(r"(\d+)", str(value)):
                modifier_parts.append(f"{name}.{match.group(1)}ms")
        elif name == "duration":
            if match := re.search(r"(\d+)(ms|s)?", str(value)):
                num, unit = match.groups()
                modifier_parts.append(f"duration.{num}{'s' if unit == 's' else 'ms'}")
        else:
            modifier_parts.append(f"{name}.{value}")
    return f"{base}__{'.'.join(modifier_parts)}" if modifier_parts else base


def _create_event_handler(event_name: str):
    def handler(expression: str, *modifiers, **kwargs) -> DatastarAttr:
        key = _build_event_key(f"data-on-{event_name}", list(modifiers), kwargs)
        return DatastarAttr({key: NotStr(expression)})

    return handler


ds_on_click = _create_event_handler("click")
ds_on_input = _create_event_handler("input")
ds_on_change = _create_event_handler("change")
ds_on_submit = _create_event_handler("submit")
ds_on_keydown = _create_event_handler("keydown")
ds_on_keyup = _create_event_handler("keyup")
ds_on_focus = _create_event_handler("focus")
ds_on_blur = _create_event_handler("blur")
ds_on_scroll = _create_event_handler("scroll")
ds_on_resize = _create_event_handler("resize")
ds_on_load = _create_event_handler("load")
ds_on_interval = _create_event_handler("interval")
ds_on_intersect = _create_event_handler("intersect")

ds_on_mousedown = _create_event_handler("mousedown")
ds_on_mouseup = _create_event_handler("mouseup")
ds_on_mousemove = _create_event_handler("mousemove")
ds_on_mouseenter = _create_event_handler("mouseenter")
ds_on_mouseleave = _create_event_handler("mouseleave")
ds_on_mouseover = _create_event_handler("mouseover")
ds_on_mouseout = _create_event_handler("mouseout")
ds_on_contextmenu = _create_event_handler("contextmenu")
ds_on_dblclick = _create_event_handler("dblclick")
ds_on_wheel = _create_event_handler("wheel")

ds_on_touchstart = _create_event_handler("touchstart")
ds_on_touchmove = _create_event_handler("touchmove")
ds_on_touchend = _create_event_handler("touchend")
ds_on_touchcancel = _create_event_handler("touchcancel")

ds_on_dragstart = _create_event_handler("dragstart")
ds_on_drag = _create_event_handler("drag")
ds_on_dragenter = _create_event_handler("dragenter")
ds_on_dragover = _create_event_handler("dragover")
ds_on_dragleave = _create_event_handler("dragleave")
ds_on_drop = _create_event_handler("drop")
ds_on_dragend = _create_event_handler("dragend")

ds_on_reset = _create_event_handler("reset")
ds_on_select = _create_event_handler("select")
ds_on_invalid = _create_event_handler("invalid")

ds_on_pointerdown = _create_event_handler("pointerdown")
ds_on_pointerup = _create_event_handler("pointerup")
ds_on_pointermove = _create_event_handler("pointermove")
ds_on_pointerenter = _create_event_handler("pointerenter")
ds_on_pointerleave = _create_event_handler("pointerleave")

ds_on_canvas = _create_event_handler("canvas")

ds_on_toggle = _create_event_handler("toggle")
ds_on_beforetoggle = _create_event_handler("beforetoggle")

ds_on_copy = _create_event_handler("copy")
ds_on_cut = _create_event_handler("cut")
ds_on_paste = _create_event_handler("paste")

ds_on_animationstart = _create_event_handler("animationstart")
ds_on_animationend = _create_event_handler("animationend")
ds_on_animationiteration = _create_event_handler("animationiteration")
ds_on_animationcancel = _create_event_handler("animationcancel")

ds_on_transitionstart = _create_event_handler("transitionstart")
ds_on_transitionend = _create_event_handler("transitionend")
ds_on_transitionrun = _create_event_handler("transitionrun")
ds_on_transitioncancel = _create_event_handler("transitioncancel")

ds_on_play = _create_event_handler("play")
ds_on_pause = _create_event_handler("pause")
ds_on_ended = _create_event_handler("ended")
ds_on_volumechange = _create_event_handler("volumechange")
ds_on_timeupdate = _create_event_handler("timeupdate")
ds_on_canplay = _create_event_handler("canplay")
ds_on_canplaythrough = _create_event_handler("canplaythrough")
ds_on_loadedmetadata = _create_event_handler("loadedmetadata")
ds_on_progress = _create_event_handler("progress")

ds_on_online = _create_event_handler("online")
ds_on_offline = _create_event_handler("offline")

ds_on_error = _create_event_handler("error")
ds_on_message = _create_event_handler("message")
ds_on_storage = _create_event_handler("storage")
ds_on_popstate = _create_event_handler("popstate")
ds_on_hashchange = _create_event_handler("hashchange")
ds_on_beforeunload = _create_event_handler("beforeunload")
ds_on_unload = _create_event_handler("unload")
ds_on_visibilitychange = _create_event_handler("visibilitychange")

ds_on_fullscreenchange = _create_event_handler("fullscreenchange")
ds_on_fullscreenerror = _create_event_handler("fullscreenerror")

ds_on_orientationchange = _create_event_handler("orientationchange")


def ds_on(event: str, expression: str, *modifiers, **kwargs) -> DatastarAttr:
    key = _build_event_key(f"data-on-{event}", list(modifiers), kwargs)
    return DatastarAttr({key: NotStr(expression)})


# ============================================================================
# Custom Data Attributes
# ============================================================================


def ds_canvas_viewport(value: Any = True) -> DatastarAttr:
    return DatastarAttr({"data-canvas-viewport": value})


def ds_canvas_container(value: Any = True) -> DatastarAttr:
    return DatastarAttr({"data-canvas-container": value})


def ds_draggable(value: Any = True) -> DatastarAttr:
    return DatastarAttr({"data-draggable": value})


def ds_drop_zone(zone_id: str) -> DatastarAttr:
    return DatastarAttr({"data-drop-zone": zone_id})


# ============================================================================
# Datastar Action Plugins
# ============================================================================


CLIPBOARD_ACTION = """{
    type: 'action',
    name: 'clipboard',
    fn: ({ peek, mergePatch }, text, signal, timeout = 2000) => {
        navigator.clipboard.writeText(text).then(() => {
            if (signal) {
                peek(() => mergePatch({ [signal]: true }));
                setTimeout(() => peek(() => mergePatch({ [signal]: false })), timeout);
            }
        }).catch(() => {
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.cssText = 'position:fixed;left:-9999px';
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            if (signal) {
                peek(() => mergePatch({ [signal]: true }));
                setTimeout(() => peek(() => mergePatch({ [signal]: false })), timeout);
            }
        });
    }
}"""


def get_starhtml_action_plugins() -> list[dict]:
    return [{"type": "action", "name": "clipboard", "code": CLIPBOARD_ACTION}]


# ============================================================================
# Special Attributes
# ============================================================================


def ds_disabled(value: bool | str) -> DatastarAttr:
    return DatastarAttr({"data-disabled": _normalize_value(value)})


def ds_ignore(*modifiers) -> DatastarAttr:
    if "self" in modifiers:
        return DatastarAttr({"data-ignore__self": ""})
    return DatastarAttr({"data-ignore": ""})


def ds_preserve_attr(*attrs) -> DatastarAttr:
    return DatastarAttr({"data-preserve-attr": ",".join(attrs) if attrs else "*"})


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "t",
    "if_",
    "equals",
    "gt",
    "lt",
    "gte",
    "lte",
    "ds_show",
    "ds_text",
    "ds_bind",
    "ds_ref",
    "ds_indicator",
    "ds_effect",
    "ds_computed",
    "ds_class",
    "ds_style",
    "ds_attr",
    "ds_signals",
    "ds_persist",
    "ds_json_signals",
    "ds_on_click",
    "ds_on_input",
    "ds_on_change",
    "ds_on_submit",
    "ds_on_keydown",
    "ds_on_keyup",
    "ds_on_focus",
    "ds_on_blur",
    "ds_on_scroll",
    "ds_on_resize",
    "ds_on_load",
    "ds_on_interval",
    "ds_on_intersect",
    "ds_on_mousedown",
    "ds_on_mouseup",
    "ds_on_mousemove",
    "ds_on_mouseenter",
    "ds_on_mouseleave",
    "ds_on_mouseover",
    "ds_on_mouseout",
    "ds_on_contextmenu",
    "ds_on_dblclick",
    "ds_on_wheel",
    "ds_on_touchstart",
    "ds_on_touchmove",
    "ds_on_touchend",
    "ds_on_touchcancel",
    "ds_on_dragstart",
    "ds_on_drag",
    "ds_on_dragenter",
    "ds_on_dragover",
    "ds_on_dragleave",
    "ds_on_drop",
    "ds_on_dragend",
    "ds_on_reset",
    "ds_on_select",
    "ds_on_invalid",
    "ds_on_pointerdown",
    "ds_on_pointerup",
    "ds_on_pointermove",
    "ds_on_pointerenter",
    "ds_on_pointerleave",
    "ds_on",
    "ds_on_toggle",
    "ds_on_beforetoggle",
    "ds_on_copy",
    "ds_on_cut",
    "ds_on_paste",
    "ds_on_animationstart",
    "ds_on_animationend",
    "ds_on_animationiteration",
    "ds_on_animationcancel",
    "ds_on_transitionstart",
    "ds_on_transitionend",
    "ds_on_transitionrun",
    "ds_on_transitioncancel",
    "ds_on_play",
    "ds_on_pause",
    "ds_on_ended",
    "ds_on_volumechange",
    "ds_on_timeupdate",
    "ds_on_canplay",
    "ds_on_canplaythrough",
    "ds_on_loadedmetadata",
    "ds_on_progress",
    "ds_on_online",
    "ds_on_offline",
    "ds_on_error",
    "ds_on_message",
    "ds_on_storage",
    "ds_on_popstate",
    "ds_on_hashchange",
    "ds_on_beforeunload",
    "ds_on_unload",
    "ds_on_visibilitychange",
    "ds_on_fullscreenchange",
    "ds_on_fullscreenerror",
    "ds_on_orientationchange",
    "ds_disabled",
    "ds_ignore",
    "ds_preserve_attr",
    "ds_canvas_viewport",
    "ds_canvas_container",
    "ds_draggable",
    "ds_drop_zone",
    "ds_on_canvas",
]
