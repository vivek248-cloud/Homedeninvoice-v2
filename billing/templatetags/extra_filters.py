from django import template

register = template.Library()


@register.filter(name="length_is")
def length_is(value, expected_length):
    try:
        return len(value) == int(expected_length)
    except:
        return False


@register.filter(name="indian_currency")
def indian_currency(value):
    try:
        value = int(float(value))
        s = str(value)

        if len(s) <= 3:
            return s

        last3 = s[-3:]
        rest = s[:-3]

        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]

        if rest:
            parts.insert(0, rest)

        return ",".join(parts) + "," + last3
    except:
        return value


@register.filter(name="humanize_views")
def humanize_views(value):
    try:
        value = int(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}k"
        return str(value)
    except:
        return value