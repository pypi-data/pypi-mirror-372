# Copyright (C) 2022-2025 J. Nathanael Philipp (jnphilipp) <nathanael@philipp.land>
#
# This file is part of django-html-utils.
#
# django-html-utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-html-utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-html-utils. If not, see <http://www.gnu.org/licenses/>.
"""DjangoHtmlUtils app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoHtmlConfigConfig(AppConfig):
    """DjangoHtmlConfig app config."""

    name = "django_html_utils"
    verbose_name = _("Django HTML Utils")
    verbose_name_plural = _("Django HTML Utils")
