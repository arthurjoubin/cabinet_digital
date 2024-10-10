from django import template
import markdown as md
from markdownx.utils import markdownify

register = template.Library()

@register.filter
def markdown_filter(text):
    return md.markdown(text)

@register.filter
def markdown(text):
    # Convert markdown to HTML using markdownify
    return markdownify(text)


