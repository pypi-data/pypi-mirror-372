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
"""DjangoHtmlUtils tests."""

from django import forms
from django.template import Context, Template
from django.test import TestCase


class DjangoHtmlUtilsTestCase(TestCase):
    def render_template(self, string, context: dict = {}) -> str:
        context = Context(context)
        return Template(string).render(context)

    def test_load_css_js(self) -> None:
        rendered = self.render_template(
            "{% load django_html_utils %}{% django_html_utils_css %}"
        )
        self.assertEqual(
            rendered,
            '\n\n<link rel="stylesheet" media="all" href="/static/css/bootstrap.min.css'
            '"/>\n<link rel="stylesheet" media="all" href="/static/css/django-bootstrap'
            '5.css"/>\n<link rel="stylesheet" media="all" href="/static/css/jquery-ui.m'
            'in.css"/>\n<link rel="stylesheet" media="all" href="/static/css/jquery-ui.'
            'structure.min.css"/>\n<link rel="stylesheet" media="all" href="/static/css'
            '/jquery-ui.theme.min.css"/>\n<link rel="stylesheet" media="all" href="/sta'
            'tic/css/select2.min.css"/>\n<link rel="stylesheet" media="all" href="'
            '/static/css/fontawesome.min.css"/>\n<link rel="stylesheet" media="all" '
            'href="/static/css/brands.min.css"/>\n<link rel="stylesheet" media="all" '
            'href="/static/css/regular.min.css"/>\n<link rel="stylesheet" media="all" '
            'href="/static/css/solid.min.css"/>\n',
        )

        rendered = self.render_template(
            "{% load django_html_utils %}{% django_html_utils_js %}"
        )
        self.assertEqual(
            rendered,
            '\n\n<script type="text/javascript" src="/static/js/jquery.min.js"></script'
            '>\n<script type="text/javascript" src="/static/js/jquery-ui.min.js"></scri'
            'pt>\n<script type="text/javascript" src="/static/js/bootstrap.bundle.min.j'
            's"></script>\n<script type="text/javascript" src="/static/js/select2.min.j'
            's"></script>\n<script type="text/javascript" src="/static/js/btn-toggle.js'
            '"></script>\n<script type="text/javascript">\n    $(function () {\n       '
            " $('[data-toggle=\"tooltip\"]').tooltip();\n    });\n</script>\n",
        )

    def test_form(self) -> None:
        class SimpleForm(forms.Form):
            name = forms.CharField(max_length=100)

        rendered = self.render_template(
            "{% load django_html_utils %}{% form form=form %}",
            context={"form": SimpleForm()},
        )
        self.assertRegex(
            rendered,
            r'^\s*<form\s*action="" method="post"\s*>\s*<div class="row mb-3">\s*<label'
            + r' class="col-sm-3 col-form-label required" for="id_name">Name:</label>'
            + r'\s*<div class="col-sm-9">\s*<input type="text" name="name" '
            + r'maxlength="100" class="form-control" autocomplete="off" required '
            + r'id="id_name">\s*</div>\s*</div>\s*<div class="row">\s*<div class="'
            + r'offset-sm-3 col-sm-9">\s*<button class="btn btn-primary" type="submit">'
            + r"\s*Submit\s*</button>\s*</div>\s*</div>\s*</form>\s*$",
        )

    def test_iframeformmodal(self) -> None:
        rendered = self.render_template(
            "{% load django_html_utils %}{% iframe_form_modal %}"
        )
        self.assertEqual(
            rendered,
            '\n\n<script type="text/javascript">\n    $(function() {\n        $("a.ifra'
            'meFormModal").modal({\n            show: false\n        });\n        $("#i'
            'frameFormModal").on("show.bs.modal", function(e) {\n            $("#iframe'
            'FormModalLabel").html(e.relatedTarget.title);\n            $("#iframeFormM'
            'odalIframe").attr("src", e.relatedTarget.href);\n        });\n\n        fu'
            "nction sleep(ms) {\n            return new Promise(resolve => setTimeout(r"
            'esolve, ms));\n        }\n\n        let iframe = document.getElementById("'
            'iframeFormModalIframe");\n        iframe.addEventListener("load", async (e'
            "vent) => {\n            try {\n                while ( true ) {\n         "
            "           if ( iframe.contentWindow.document.body.scrollHeight === 0 ) {"
            "\n                        await sleep(100);\n                    } else {"
            "\n                        iframe.style.height = iframe.contentWindow.docum"
            'ent.body.scrollHeight + "px";\n                        break;\n           '
            "         }\n                }\n            } catch (error) {\n            "
            '    console.log("Error:", error);\n            }\n        });\n    });\n</'
            'script>\n<div class="modal fade" id="iframeFormModal" tabindex="-1" role="'
            'dialog" aria-labelledby="iframeFormModalLabel" aria-hidden="true" data-bs-'
            'backdrop="static">\n    <div class="modal-dialog modal-xl modal-dialog-cen'
            'tered modal-dialog-scrollable" role="document">\n        <div class="modal'
            '-content">\n            <div class="modal-header">\n                <h5 cl'
            'ass="modal-title" id="iframeFormModalLabel"></h5>\n                <button'
            ' type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cance'
            'l"></button>\n            </div>\n            <div class="modal-body" styl'
            'e="padding-left: 0; padding-right: 0;">\n                <iframe id="ifram'
            'eFormModalIframe" name="iframeFormModalIframe" frameborder="0" style="widt'
            'h: 100%;  "></iframe>\n            </div>\n            <div class="modal-'
            'footer">\n                <button type="button" class="btn btn-secondary" '
            'data-bs-dismiss="modal">Cancel</button>\n                <button id="ifram'
            'eFormModalSubmit" type="submit" class="btn" onclick="window.frames[\'ifram'
            "eFormModalIframe'].document.forms[0].submit();\"> </button>\n            "
            "</div>\n        </div>\n    </div>\n</div>\n",
        )
        rendered = self.render_template(
            "{% load django_html_utils %}{% iframe_form_modal "
            + 'iframe_min_height="500px" %}'
        )
        self.assertEqual(
            rendered,
            '\n\n<script type="text/javascript">\n    $(function() {\n        $("a.ifra'
            'meFormModal").modal({\n            show: false\n        });\n        $("#i'
            'frameFormModal").on("show.bs.modal", function(e) {\n            $("#iframe'
            'FormModalLabel").html(e.relatedTarget.title);\n            $("#iframeFormM'
            'odalIframe").attr("src", e.relatedTarget.href);\n        });\n\n        fu'
            "nction sleep(ms) {\n            return new Promise(resolve => setTimeout(r"
            'esolve, ms));\n        }\n\n        let iframe = document.getElementById("'
            'iframeFormModalIframe");\n        iframe.addEventListener("load", async (e'
            "vent) => {\n            try {\n                while ( true ) {\n         "
            "           if ( iframe.contentWindow.document.body.scrollHeight === 0 ) {"
            "\n                        await sleep(100);\n                    } else {"
            "\n                        iframe.style.height = iframe.contentWindow.docum"
            'ent.body.scrollHeight + "px";\n                        break;\n           '
            "         }\n                }\n            } catch (error) {\n            "
            '    console.log("Error:", error);\n            }\n        });\n    });\n</'
            'script>\n<div class="modal fade" id="iframeFormModal" tabindex="-1" role="'
            'dialog" aria-labelledby="iframeFormModalLabel" aria-hidden="true" data-bs-'
            'backdrop="static">\n    <div class="modal-dialog modal-xl modal-dialog-cen'
            'tered modal-dialog-scrollable" role="document">\n        <div class="modal'
            '-content">\n            <div class="modal-header">\n                <h5 cl'
            'ass="modal-title" id="iframeFormModalLabel"></h5>\n                <button'
            ' type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cance'
            'l"></button>\n            </div>\n            <div class="modal-body" styl'
            'e="padding-left: 0; padding-right: 0;">\n                <iframe id="ifram'
            'eFormModalIframe" name="iframeFormModalIframe" frameborder="0" style="widt'
            'h: 100%; min-height: 500px; "></iframe>\n            </div>\n            <'
            'div class="modal-footer">\n                <button type="button" class="bt'
            'n btn-secondary" data-bs-dismiss="modal">Cancel</button>\n                '
            '<button id="iframeFormModalSubmit" type="submit" class="btn" onclick="wind'
            "ow.frames['iframeFormModalIframe'].document.forms[0].submit();\"> </button"
            ">\n            </div>\n        </div>\n    </div>\n</div>\n",
        )
        rendered = self.render_template(
            '{% load django_html_utils %}{% iframe_form_modal iframe_min_height="400px"'
            + ' iframe_max_height="800px" %}'
        )
        self.assertEqual(
            rendered,
            '\n\n<script type="text/javascript">\n    $(function() {\n        $("a.ifra'
            'meFormModal").modal({\n            show: false\n        });\n        $("#i'
            'frameFormModal").on("show.bs.modal", function(e) {\n            $("#iframe'
            'FormModalLabel").html(e.relatedTarget.title);\n            $("#iframeFormM'
            'odalIframe").attr("src", e.relatedTarget.href);\n        });\n\n        fu'
            "nction sleep(ms) {\n            return new Promise(resolve => setTimeout(r"
            'esolve, ms));\n        }\n\n        let iframe = document.getElementById("'
            'iframeFormModalIframe");\n        iframe.addEventListener("load", async (e'
            "vent) => {\n            try {\n                while ( true ) {\n         "
            "           if ( iframe.contentWindow.document.body.scrollHeight === 0 ) {"
            "\n                        await sleep(100);\n                    } else {"
            "\n                        iframe.style.height = iframe.contentWindow.docum"
            'ent.body.scrollHeight + "px";\n                        break;\n           '
            "         }\n                }\n            } catch (error) {\n            "
            '    console.log("Error:", error);\n            }\n        });\n    });\n</'
            'script>\n<div class="modal fade" id="iframeFormModal" tabindex="-1" role="'
            'dialog" aria-labelledby="iframeFormModalLabel" aria-hidden="true" data-bs-'
            'backdrop="static">\n    <div class="modal-dialog modal-xl modal-dialog-cen'
            'tered modal-dialog-scrollable" role="document">\n        <div class="modal'
            '-content">\n            <div class="modal-header">\n                <h5 cl'
            'ass="modal-title" id="iframeFormModalLabel"></h5>\n                <button'
            ' type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cance'
            'l"></button>\n            </div>\n            <div class="modal-body" styl'
            'e="padding-left: 0; padding-right: 0;">\n                <iframe id="ifram'
            'eFormModalIframe" name="iframeFormModalIframe" frameborder="0" style="widt'
            'h: 100%; min-height: 400px; max-height: 800px;"></iframe>\n            </d'
            'iv>\n            <div class="modal-footer">\n                <button type='
            '"button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>'
            '\n                <button id="iframeFormModalSubmit" type="submit" class="'
            "btn\" onclick=\"window.frames['iframeFormModalIframe'].document.forms[0].s"
            'ubmit();"> </button>\n            </div>\n        </div>\n    </div>\n'
            "</div>\n",
        )
        rendered = self.render_template(
            '{% load django_html_utils %}{% iframe_form_modal iframe_min_height="400px"'
            + ' iframe_max_height="800px" submit_button_text="Save" '
            + 'fa_icon_name="floppy-disk" %}'
        )
        self.assertEqual(
            rendered,
            '\n\n<script type="text/javascript">\n    $(function() {\n        $("a.ifra'
            'meFormModal").modal({\n            show: false\n        });\n        $("#i'
            'frameFormModal").on("show.bs.modal", function(e) {\n            $("#iframe'
            'FormModalLabel").html(e.relatedTarget.title);\n            $("#iframeFormM'
            'odalIframe").attr("src", e.relatedTarget.href);\n        });\n\n        fu'
            "nction sleep(ms) {\n            return new Promise(resolve => setTimeout(r"
            'esolve, ms));\n        }\n\n        let iframe = document.getElementById("'
            'iframeFormModalIframe");\n        iframe.addEventListener("load", async (e'
            "vent) => {\n            try {\n                while ( true ) {\n         "
            "           if ( iframe.contentWindow.document.body.scrollHeight === 0 ) {"
            "\n                        await sleep(100);\n                    } else {"
            "\n                        iframe.style.height = iframe.contentWindow.docum"
            'ent.body.scrollHeight + "px";\n                        break;\n           '
            "         }\n                }\n            } catch (error) {\n            "
            '    console.log("Error:", error);\n            }\n        });\n    });\n</'
            'script>\n<div class="modal fade" id="iframeFormModal" tabindex="-1" role="'
            'dialog" aria-labelledby="iframeFormModalLabel" aria-hidden="true" data-bs-'
            'backdrop="static">\n    <div class="modal-dialog modal-xl modal-dialog-cen'
            'tered modal-dialog-scrollable" role="document">\n        <div class="modal'
            '-content">\n            <div class="modal-header">\n                <h5 cl'
            'ass="modal-title" id="iframeFormModalLabel"></h5>\n                <button'
            ' type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cance'
            'l"></button>\n            </div>\n            <div class="modal-body" styl'
            'e="padding-left: 0; padding-right: 0;">\n                <iframe id="ifram'
            'eFormModalIframe" name="iframeFormModalIframe" frameborder="0" style="widt'
            'h: 100%; min-height: 400px; max-height: 800px;"></iframe>\n            </d'
            'iv>\n            <div class="modal-footer">\n                <button type='
            '"button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>'
            '\n                <button id="iframeFormModalSubmit" type="submit" class="'
            "btn\" onclick=\"window.frames['iframeFormModalIframe'].document.forms[0].s"
            'ubmit();"><span class="fa-solid fa-floppy-disk"></span> Save</button>\n'
            "            </div>\n        </div>\n    </div>\n</div>\n",
        )

    def test_fa(self) -> None:
        rendered = self.render_template('{% load django_html_utils %}{% fa "search" %}')
        self.assertEqual(rendered, '<span class="fa-solid fa-search"></span>')

        rendered = self.render_template(
            '{% load django_html_utils %}{% fa "search" tag="i" %}'
        )
        self.assertEqual(rendered, '<i class="fa-solid fa-search"></i>')

        rendered = self.render_template(
            '{% load django_html_utils %}{% fa "search" icon_type="regular" %}'
        )
        self.assertEqual(rendered, '<span class="fa-regular fa-search"></span>')

        rendered = self.render_template(
            '{% load django_html_utils %}{% fa "search" icon_type="regular" tag="i" %}'
        )
        self.assertEqual(rendered, '<i class="fa-regular fa-search"></i>')
