"""
ASK AI chatbot for Sphinx.

(c) 2024 - present Biel.ai
This code is licensed under MIT license (see LICENSE.md for details).
"""

__version__ = "0.1.6"

from sphinx.application import Sphinx

class BielExtension:
    DEFAULT_OPTIONS = {
        # biel-button
        'project': None,
        'button_position': 'bottom-right',
        'button_text': 'Ask AI',
        'button_style': "dark",
        'custom_font': None,
        'hide_icon': None,
        'ai_icon': None,
        'hide_avatars': None,
        'version': 'latest',
        'api_key': None,

        # biel-bot
        'disable_input': None,
        'email': None,
        'expand_modal': None,
        'hide_close_button': None,
        'hide_expand_button': None,
        'hide_refresh_button': None,
        'hide_feedback': None,
        'modal_position': None,
        'show_terms_modal': None,

        # biel-bot text
        'error_message_4_0_3': None,
        'error_message_4_0_4': None,
        'error_message_default': None,
        'footer_text': None,
        'header_title': 'Biel.ai chatbot',
        'input_placeholder_text': None,
        'send_button_text': None,
        'sources_text': None,
        'suggested_questions': None,
        'suggested_questions_title': None,
        'terms_checkbox_text': None,
        'terms_description': None,
        'terms_title': None,
        'welcome_message': None,
    }

    def __init__(self, app: Sphinx):
        self.app = app
        self.setup_options()
        self.setup_events()

    @staticmethod
    def snake_to_kebab(string):
        """Convert snake_case string to kebab-case."""
        return string.replace('_', '-')

    def inject_biel_scripts(self, app, pagename, templatename, context, doctree):
        version = getattr(app.config, "biel_version", self.DEFAULT_OPTIONS['version'])
        biel_js_module = f'''
            <script type="module" src="https://cdn.jsdelivr.net/npm/biel-search@{version}/dist/biel-search/biel-search.esm.js"></script>
        '''

        # Add Biel JS module to body
        context.setdefault('body', '')
        context['body'] += biel_js_module

        if getattr(app.config, "biel_button_position", None) != "default":
            attribute_pairs = [
                f'bielBtn.setAttribute("{self.snake_to_kebab(key)}", "{getattr(app.config, f"biel_{key}")}");'
                for key in self.DEFAULT_OPTIONS.keys() if getattr(app.config, f"biel_{key}") is not None
            ]
            set_attributes_script = "\n                    ".join(attribute_pairs)
            
            button_text = getattr(app.config, "biel_button_text", self.DEFAULT_OPTIONS['button_text'])

            biel_script = f'''
                <script>
                    window.addEventListener('DOMContentLoaded', (event) => {{
                        let bielBtn = document.createElement("biel-button");
                        bielBtn.innerHTML = "{button_text}";
                        {set_attributes_script}
                        document.body.appendChild(bielBtn);
                    }});
                </script>
            '''
            context['body'] += biel_script

    def setup_options(self):
        for key in self.DEFAULT_OPTIONS.keys():
            self.app.add_config_value(f'biel_{key}', self.DEFAULT_OPTIONS[key], 'html')

    def setup_events(self):
        version = getattr(self.app.config, "biel_version", self.DEFAULT_OPTIONS["version"])
        self.app.add_css_file(f'https://cdn.jsdelivr.net/npm/biel-search@{version}/dist/biel-search/biel-search.css')
        self.app.connect('html-page-context', self.inject_biel_scripts)


def setup(app: Sphinx):
    extension = BielExtension(app)
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
