from django import template
import re

register = template.Library()

@register.filter
def first_sentence(value):
    # Split the text by sentence-ending punctuation followed by a space or end of string
    sentences = re.split(r'(?<=[.!?])\s+|\Z', value)
    # Return the first sentence if there is one, otherwise return the whole text
    return sentences[0] if sentences else value

@register.filter
def after_first_sentence(value):
    # Split the text by sentence-ending punctuation followed by a space or end of string
    sentences = re.split(r'(?<=[.!?])\s+|\Z', value)
    # Return everything after the first sentence, or an empty string if there's only one sentence
    return ' '.join(sentences[1:]) if len(sentences) > 1 else ''
