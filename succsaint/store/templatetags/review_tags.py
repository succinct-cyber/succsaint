from django import template

register = template.Library()

@register.filter
def star_class(rating, position):
    """
    Returns the FontAwesome star class suffix for a given star position.
    
    Usage: {{ review.rating|star_class:1 }}
    Returns: '' (full), '-half-o' (half), or '-o' (empty)
    
    position = 1 to 5 (which star we're rendering)
    rating   = the actual rating value (e.g. 3.5)
    """
    rating = float(rating)   # ensure it's a float regardless of DB field type

    full_threshold = position        # e.g. position 3 needs rating >= 3 for full
    half_threshold = position - 0.5  # e.g. position 3 needs rating == 2.5 for half

    if rating >= full_threshold:
        return ''           # full star → "fa fa-star"
    elif rating == half_threshold:
        return '-half-o'    # half star → "fa fa-star-half-o"
    else:
        return '-o'         # empty star → "fa fa-star-o"