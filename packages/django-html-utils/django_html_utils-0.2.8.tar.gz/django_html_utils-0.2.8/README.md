# django-html-utils app

HTML utils app for django.

![Linting & Tests](https://github.com/jnphilipp/django-html-utils/actions/workflows/tests.yml/badge.svg)
[![pypi Version](https://img.shields.io/pypi/v/django-html-utils.svg?logo=pypi&logoColor=white)](https://pypi.org/project/django-html-utils/)


## Included versions

* [Bootstrap](https://github.com/twbs/bootstrap) (bundle): 5.3.8
* [Font-Awesome](https://github.com/FortAwesome/Font-Awesome): 7.0.0
* [jQuery](https://github.com/jquery/jquery): 3.7.1
* [jQuery UI](https://github.com/jquery/jquery-ui): 1.14.1
* [Select2](https://github.com/select2/select2): 4.0.13


## Usage

### Basics

Load with `{% load django_html_utils %}` and include CSS/JS with:

```html
<head>
  {% django_html_utils_css %}
  {% django_html_utils_js %}
</head>
```


### Font-Awesome

To add a Font-Awesome icon use `{% fa "icon-name" %}`. Additional options are `tag`, for the tag to use, defaults to `span` and `icon_type`, for the icon type, defaults to `solid`.

For example:

```html
{% fa "upload" %}
```

resolves to:
```html
<span class="fa-solid fa-upload"></span>
```


### iFrame modal

Simple modal with an iFrame, designed for usage with forms.

Add modal with `{% iframe_form_modal %}`, with options:
* **iframe_min_height**: set minimum height of iframe, defaults to None
* **iframe_max_height**: set maximum height of iframe, defaults to None
* **static_backdrop**: if the backdrop of the model should be static, defaults to `True`
* **submit_button_text**: the text of the submit button, when `None` no text will be displayed, defaults to `None`
* **fa_icon_name**: the Font-Awesome icon name on the submit button
* **fa_tag**: the Font-Awesome tag to use, defaults to `span`
* **fa_icon_type**: the icon type, defaults to `solid`

Open link with:
```html
<a href="{% url SOME_FORM %}" title="{% trans "Modal title" %}" data-bs-toggle="modal" data-bs-target="#iframeFormModal">open modal form</a>
```

The URL will be loaded in the iFrame and the title will be set as the modal title.
