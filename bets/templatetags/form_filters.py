# In your app directory, create these files:

# First, ensure you have a templatetags directory
# myapp/
#   ├── templatetags/
#   │   ├── __init__.py
#   │   └── form_filters.py

# myapp/templatetags/__init__.py
# Leave this file empty (just creates the package)

# myapp/templatetags/form_filters.py
from django import template
from django import forms

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Adds CSS class to form fields
    
    Usage in template:
    {{ form.field|add_class:"my-class" }}
    """
    if not isinstance(value, forms.BoundField):
        return value

    # Get existing classes or create an empty string
    css_classes = value.field.widget.attrs.get('class', '')
    
    # Combine existing classes with new classes
    if css_classes:
        css_classes = f"{css_classes} {arg}"
    else:
        css_classes = arg
    
    # Create a new widget with updated classes
    new_widget = value.field.widget.__class__(
        value.field.widget.attrs.copy()
    )
    new_widget.attrs['class'] = css_classes
    
    # Render the field with new widget
    return value.as_widget(widget=new_widget)