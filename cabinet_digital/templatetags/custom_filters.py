from django import template
import re

register = template.Library()

@register.filter
def first_sentence(value):
    # Split the text by sentence-ending punctuation followed by a space or end of string
    sentences = re.split(r'(?<=[.!?])\s+|\Z', value)
    # Return the first sentence if there is one, otherwise return the whole text
    return sentences[0] if sentences else value
