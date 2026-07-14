"""Calculator CGI application."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from html import escape

from .common import CgiResult, html_document, parse_form, run_main


_SYMBOLS = {"add": "+", "sub": "−", "mul": "×", "div": "÷"}


def _format_decimal(value: Decimal) -> str:
    if value == value.to_integral():
        return str(value.quantize(Decimal(1)))
    return format(value.normalize(), "f")


def run(environ: dict[str, str], body: bytes) -> CgiResult:
    try:
        values = parse_form(environ, body)
        operation = values.get("op", "")
        if operation not in _SYMBOLS:
            raise ValueError("请选择有效的运算符")
        left = Decimal(values.get("a", ""))
        right = Decimal(values.get("b", ""))
        if not left.is_finite() or not right.is_finite():
            raise ValueError("请输入有限数字")
        if operation == "add":
            answer = left + right
        elif operation == "sub":
            answer = left - right
        elif operation == "mul":
            answer = left * right
        else:
            if right == 0:
                raise ValueError("除数不能为 0")
            answer = left / right
    except (InvalidOperation, ValueError) as exc:
        message = escape(str(exc) or "请输入有效数字")
        return CgiResult(
            400,
            {"Content-Type": "text/html; charset=utf-8"},
            html_document("计算错误", f"<h1>计算错误</h1><p>{message}</p>"),
        )

    expression = (
        f"{escape(_format_decimal(left))} {escape(_SYMBOLS[operation])} "
        f"{escape(_format_decimal(right))} = <strong>{escape(_format_decimal(answer))}</strong>"
    )
    return CgiResult(
        200,
        {"Content-Type": "text/html; charset=utf-8"},
        html_document("计算结果", f"<h1>计算结果</h1><p class='result'>{expression}</p>"),
    )


def main() -> int:
    return run_main(run)


if __name__ == "__main__":
    raise SystemExit(main())
