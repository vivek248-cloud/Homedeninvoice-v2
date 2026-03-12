from django import template

register = template.Library()

@register.filter(name="pdf_wrap")
def pdf_wrap(text):
    if not text:
        return ""

    text = str(text)
    width = 34   # chars per line (adjust if needed)

    return "<br>".join(
        text[i:i+width] for i in range(0, len(text), width)
    )
