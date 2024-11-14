from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Multiplies the given value by the argument.

    Args:
        value (float or int): The first number to be multiplied.
        arg (float or int): The second number to multiply with.

    Returns:
        float: The result of multiplying value by arg.
        str: Returns an empty string if value or arg cannot be converted to a float.
        
    Raises:
        ValueError: If either value or arg cannot be converted to float.
        TypeError: If either value or arg is not of a compatible type.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
