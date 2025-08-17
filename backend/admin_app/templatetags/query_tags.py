"""
Custom template tags for building and modifying URL query strings 

Provides the `update_query` tag to dunamically preserve existing GET parameters
while updating or removing specific parameters (e.g. filters, sorting options)

Will help keep URLs clean and consistent across pages, filtering, and sorting
No manual reconstructing of query strings in templates.

Usage example in templates: 
    {% load query_tags %}
    <a href="?{% update_query request sort='cwa_desc' %}">Sort by CWA ↓<a/>  
"""
from django import template 
from urllib.parse import urlencode 

# Create new template library instance to register custom tags
register = template.Library()

@register.simple_tag(takes_context=True)
def update_query(context, **kwargs):
    """
    Template tag to update URL query parameters dynamically 

    Args: 
        context: Template context, passed with 'takes_context=True'.
        **kwargs: Key-value pairs of query paramters to add/update/remove. 
            To remove a parameter, pass value as None 

    Returns:
        URL-encoded query string with updated parameters
    """
    # Get current request object 
    request = context['request']

    # Mutable copy of params
    query_params = request.GET.copy()

    # Update/Remove parameters based on args
    for key, value in kwargs.items():
        if value is None:
            # Remove it if None was passed
            query_params.pop(key, None)
        else: 
            # Set or update the parameter value 
            query_params[key] = value

    # Return encoded query string 
    return query_params.urlencode()