# billing/templatetags/extra_filters.py

from django import template
from decimal import Decimal

# ✅ ONE register at the top - never repeat this line!
register = template.Library()


# ══════════════════════════════════════════
#  LENGTH FILTER
# ══════════════════════════════════════════

@register.filter(name="length_is")
def length_is(value, expected_length):
    try:
        return len(value) == int(expected_length)
    except Exception:
        return False


# ══════════════════════════════════════════
#  INDIAN CURRENCY FILTERS
# ══════════════════════════════════════════

@register.filter(name='indian_currency')
def indian_currency(value):
    """
    Format number in Indian currency format.
    1234567.89 → 12,34,567.89
    """
    try:
        value = Decimal(str(value))

        is_negative = value < 0
        value = abs(value)

        str_value = f"{value:.2f}"
        integer_part, decimal_part = str_value.split('.')

        if len(integer_part) <= 3:
            formatted = integer_part
        else:
            last_three = integer_part[-3:]
            remaining  = integer_part[:-3]

            groups = []
            while len(remaining) > 2:
                groups.append(remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                groups.append(remaining)

            groups.reverse()
            formatted = ','.join(groups) + ',' + last_three

        result = f"{formatted}.{decimal_part}"
        return f"-{result}" if is_negative else result

    except Exception:
        return str(value)


@register.filter(name='indian_currency_symbol')
def indian_currency_symbol(value):
    """Returns ₹1,23,456.78"""
    return f"₹{indian_currency(value)}"


@register.filter(name='indian_number')
def indian_number(value):
    """
    Format without decimal places.
    1234567 → 12,34,567
    """
    try:
        value = int(float(str(value)))
        is_negative = value < 0
        value = abs(value)

        str_value = str(value)

        if len(str_value) <= 3:
            formatted = str_value
        else:
            last_three = str_value[-3:]
            remaining  = str_value[:-3]

            groups = []
            while len(remaining) > 2:
                groups.append(remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                groups.append(remaining)

            groups.reverse()
            formatted = ','.join(groups) + ',' + last_three

        return f"-{formatted}" if is_negative else formatted

    except (ValueError, TypeError):
        return str(value)


# ══════════════════════════════════════════
#  HUMANIZE FILTERS
# ══════════════════════════════════════════

@register.filter(name="humanize_views")
def humanize_views(value):
    try:
        value = int(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}k"
        return str(value)
    except Exception:
        return value


# ══════════════════════════════════════════
#  DICTIONARY FILTER
# ══════════════════════════════════════════

@register.filter
def get_item(dictionary, key):
    """Usage: {{ my_dict|get_item:key }}"""
    return dictionary.get(key)