from django import template

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """
    Template filter to lookup a value in a dictionary by key.

    Usage: {{ dictionary|lookup:key }}
    """
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None


@register.filter
def get_type(value):
    """
    Template filter to get the type of a value.

    Usage: {{ value|get_type }}
    """
    return type(value).__name__


@register.filter
def is_list(value):
    """
    Template filter to check if a value is a list.

    Usage: {{ value|is_list }}
    """
    return isinstance(value, list)


@register.filter
def is_dict(value):
    """
    Template filter to check if a value is a dictionary.

    Usage: {{ value|is_dict }}
    """
    return isinstance(value, dict)


@register.filter
def format_setting_value(value):
    """
    Template filter to format setting values for display.

    Usage: {{ value|format_setting_value }}
    """
    if isinstance(value, bool):
        return 'True' if value else 'False'
    elif isinstance(value, (list, tuple)):
        return f"[{', '.join(map(str, value))}]"
    elif isinstance(value, dict):
        return f"{{ {', '.join(f'{k}: {v}' for k, v in value.items())} }}"
    elif isinstance(value, str) and len(value) > 100:
        return f"{value[:100]}..."
    else:
        return str(value)
