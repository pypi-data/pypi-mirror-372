from functools import cached_property
from pathlib import Path
from typing import Callable, Optional

from jinja2 import Environment, FileSystemLoader
from loguru import logger as log
from starlette.responses import HTMLResponse
from toomanyconfigs import CWD
from toomanyconfigs.cwd import CWDNamespace
import traceback

from .css_body import base, typography
from .css_animations import particle_anims, entrance, interactive, loading
from .css_background import gradients, particles
from .css_buttons import primary, variants, effects
from .css_components import status, forms, icons
from .css_containers import cards, modals
from .css_layout import containers, grid
from .css_utilities import spacing, text, visibility, responsive
from .css_vars import css_vars
from .css_documentation import generate_css_documentation
from .html_render_error import render_error as html_render_error
from .html_header import header
from .js_core import search_handler
from .js_documentation import generate_js_documentation

file_structure = {
    "templates": {
        "html": {
            "header.html": header,
            "render_error.html": f"{html_render_error}",
            "content": {

            }
        },
        "js": {
            "1-core": {
                "search_handler.js": search_handler
            },
        },
        "css": {
            "vars.css": css_vars,
            "1-body": {
                "base.css": base,
                "typography.css": typography
            },
            "2-background": {
                "gradients.css": gradients,
                "particles.css": particles,
            },
            "3-layout": {
                "containers.css": containers,
                "grid.css": grid
            },
            "4-containers": {
                "cards.css": cards,
                "modals.css": modals,
            },
            "5-components": {
                "icons.css": icons,
                "forms.css": forms,
                "status.css": status
            },
            "6-buttons": {
                "primary.css": primary,
                "variants.css": variants,
                "effects.css": effects
            },
            "7-utilities": {
                "spacing.css": spacing,
                "text.css": text,
                "visibility.css": visibility,
                "responsive.css": responsive
            },
            "8-animations": {
                "entrance.css": entrance,
                "interactive.css": interactive,
                "loading.css": loading,
                "particle_anims.css": particle_anims
            },
        }
    }
}


class FastJ2(CWD, Environment):
    templates: CWDNamespace

    def __init__(
        self,
        *cwd_args,
        error_method: Optional[Callable[[Exception, str, dict], HTMLResponse]] = None,
        cwd: Path = Path.cwd(),
    ):
        CWD.__init__(
            self,
            file_structure,
            *cwd_args,
            path=cwd
        )
        Environment.__init__(
            self,
            loader=FileSystemLoader(Path(self.templates._path))  # type: ignore
        )
        self.error_method = error_method or self.render_error
        log.success(f"{self}: Successfully initialized FastJ2 Templater for FastAPI with params:\n  - path={self.cwd}\n  - cwd_args={cwd_args}\n  - error_method={self.error_method}")
        self.safe_render = self.render
        self.server_context = {
            "fastj2_app_name": self.__class__.__name__
        }
        self.client_context = {
        }
        _ = self.app_js
        _ = self.app_css


    def __repr__(self):
        return f"[FastJ2.{self.cwd.name}]"

    @cached_property
    def _concatenated_files(self):
        """Concatenate CSS and JS files ordinally based on sorted files, then sorted subfolders"""

        def _concatenate_directory(directory_path: Path, file_extensions: list) -> str:
            """Helper to concatenate files in a directory with ordinal sorting"""
            content = []

            if not directory_path.exists():
                return ""

            # Get all items (files and directories) and sort them
            items = sorted(directory_path.iterdir(), key=lambda x: x.name)

            for item in items:
                if item.is_file() and any(item.name.endswith(ext) for ext in file_extensions):
                    try:
                        content.append(item.read_text(encoding='utf-8'))
                        log.debug(f"{self}: Added file {item.name}")
                    except Exception as e:
                        log.warning(f"{self}: Could not read {item.name}: {e}")
                elif item.is_dir():
                    # Recursively process subdirectories
                    subdirectory_content = _concatenate_directory(item, file_extensions)
                    if subdirectory_content:
                        content.append(subdirectory_content)
                        log.debug(f"{self}: Added subdirectory {item.name}")

            return "\n\n".join(content)

        # Concatenate CSS files
        css_dir = Path(self.templates._path) / "css"
        css = _concatenate_directory(css_dir, ['.css'])

        # Concatenate JS files
        js_dir = Path(self.templates._path) / "js"
        js = _concatenate_directory(js_dir, ['.js'])

        log.success(
            f"{self}: Files concatenated - CSS: {len(css)} chars, JS: {len(js)} chars")

        return css, js

    @cached_property
    def app_js(self) -> str:
        """Get concatenated JavaScript content"""
        generate_js_documentation(self.cwd / "templates" / "js")
        _ , js = self._concatenated_files
        path = self.cwd / "templates" / "app.js"
        path.write_text(js)
        return js

    @cached_property
    def app_css(self) -> str:
        """Get concatenated CSS content"""
        generate_css_documentation(self.cwd / "templates" / "css")
        css, _ = self._concatenated_files
        path = self.cwd / "templates" / "app.css"
        path.touch(exist_ok=True)
        path.write_text(css)
        return css

    def render_error(self, e: Exception, template_name: str, context: dict) -> HTMLResponse:
        """Default error handler for template rendering failures"""
        context_info = ""
        for key, value in context.items():
            try:
                if isinstance(value, (dict, list)):
                    context_info += f"<p><strong>{key}:</strong> {len(value)} items</p>\n"
                else:
                    context_info += f"<p><strong>{key}:</strong> {str(value)[:100]}...</p>\n"
            except Exception as e:
                log.warning(f"{self}: Exception in context truncation: {e}... Skipping...")
                continue

        template = self.get_template("html/render_error.html")
        rendered_html = template.render(
            template_name = template_name,
            e = e,
            traceback = traceback.format_exc(),
            context_info = context_info
        )
        return HTMLResponse(rendered_html, status_code=500)

    def render(self, template_name: str, header: bool = True, css: bool = True, js: bool = True, **context) -> HTMLResponse:
        """
        Safely render a template with comprehensive error handling and fallback.

        Args:
            template_name: Name of the template file to render
            header: determines whether to include the header from templates/html/header.html
            css: determines whether to include app.css
            js: determines whether to include app.js
            **context: Template context variables

        Returns:
            HTMLResponse with rendered template or fallback HTML
        """
        try:
            template = self.get_template(f"html/content/{template_name}")
            log.debug(f"{self}: About to render template: {template_name}")
            full_context = {
                **self.server_context,
                **self.client_context,
                **context,
                "fastj2_css": css,
                "fastj2_js": js
            }
            log.debug(f"{self}: Loading context:\n   - context={full_context}")
            rendered_html = template.render(**full_context)
            if header:
                header = self.get_template("html/header.html")
                rendered_header = header.render(**full_context)
                rendered_html = f"{rendered_header}\n{rendered_html}"
            final = f"""
<!DOCTYPE html>
<html lang="en">
{rendered_html}
</html>
"""
            log.debug(f"{self}: Template {template_name} rendered successfully:")
            print(f"{final[:280]}...")
            return HTMLResponse(final)

        except Exception as e:
            import traceback
            full_traceback = traceback.format_exc()
            for each in context:
                try:
                    val = context[each]
                    context[each] = f"{val[:100]} ..."
                except Exception as e2:
                    log.warning(f"{self}: Error in context truncation: {e2}... Skipping...")
                    continue
            log.error(f"{self}: Exception rendering template '{template_name}': {type(e).__name__}: {e}\n{full_traceback}\nTemplate context: {context}")
            return self.error_method(e, template_name, context)