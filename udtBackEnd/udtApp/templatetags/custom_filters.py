from django import template
import datetime

register = template.Library()

@register.filter
def get_item(obj, key):
    """Ritorna l'attributo dell'oggetto o chiave del dizionario, anche con underscore."""
    try:
        # Se l'oggetto è un dizionario, usa key per accedere al valore
        return obj[key]
    except (KeyError, TypeError):
        return None

@register.filter
def extract_type(value):
    if isinstance(value, str):
        return value.split('/')[-1]  # Restituisce l'ultima parte della stringa dopo il '/'
    return value

@register.filter
def format_timestamp(value):
    if isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    return value