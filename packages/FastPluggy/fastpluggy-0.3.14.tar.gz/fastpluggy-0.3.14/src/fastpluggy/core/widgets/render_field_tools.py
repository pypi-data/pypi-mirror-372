from datetime import datetime, timezone
from enum import Enum


class RenderFieldTools:

    @staticmethod
    def render_http_verb_badges(verbs):
        """
        Render a list of HTTP verbs as HTML <span> badges with background
        colors according to the mapping:

          GET       → blue
          POST      → green
          PUT       → orange
          DELETE    → red
          PATCH     → yellow
          WEBSOCKET → purple (with special styling)
          HEAD      → gray
          OPTIONS   → gray
          TRACE     → gray

        Any unrecognized verb also falls back to gray.
        """
        # 1. define your color map
        color_map = {
            'GET': 'blue',
            'POST': 'green',
            'PUT': 'orange',
            'DELETE': 'red',
            'PATCH': 'yellow',
            'WEBSOCKET': 'purple',
        }

        # 2. build badges
        badges = []
        for raw in verbs:
            verb = raw.upper()
            color = color_map.get(verb, 'gray')
            # inline style for background + ensure text is readable
            badge = f'<span class="badge badge-outline text-{color}">{verb}</span>'
            badges.append(badge)

        # 3. return one HTML string you can drop into your page
        return ' '.join(badges)

    @staticmethod
    def render_enum(value):
        if isinstance(value, Enum):
            label = value.name.title()
            badge_class = value.badge_class if value.badge_class else 'badge-success'
            return f'<span class="badge {badge_class}">{label}</span>'
        return value

    @staticmethod
    def render_boolean(value):
        return '<span class="badge bg-green">Yes</span>' if value else '<span class="badge bg-red">No</span>'

    @staticmethod
    def render_icon(value):
        return f'<i class="{value}"></i>'

    @staticmethod
    def render_datetime(value):
        return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else ""
