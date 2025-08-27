import html
import traceback

from jinja2 import pass_context


@pass_context
def safe_render(ctx, caller):
    try:
        return caller()
    except Exception as e:
        # keep page flow, optionally show a small warning box
        tb = traceback.format_exc()
        # Manually escaped, returned as HTML string
        return (
            '<div style="border:1px solid #faa;padding:.75rem;margin:.5rem 0;">'
            '<strong>Widget render failed</strong>'
            '<pre style="white-space:pre-wrap;margin:0;">'
            f'{html.escape(tb)}'
            '</pre></div>'
        )

