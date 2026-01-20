from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from io import BytesIO
from datetime import datetime
import base64
import os
import jinja2
import modules.common as mc



def _img_tag_from_b64(b64_str, alt="image", max_width_px=400):
    if not b64_str:
        return ""
    # Ensure we have only the raw base64 body (strip data: prefix if present)
    if b64_str.startswith("data:"):
        # find comma
        idx = b64_str.find(",")
        if idx != -1:
            b64_body = b64_str[idx+1:]
        else:
            b64_body = b64_str
    else:
        b64_body = b64_str
    return f"<img src=\"data:image/png;base64,{b64_body}\" alt=\"{alt}\" style=\"max-width:{max_width_px}px;\" />"


def build_aforos_html(aforos, residues_map=None, title="Reporte de Aforos"):
    """Render the aforos HTML using a Jinja2 template located in resources/templates/aforos.html."""
    residues_map = residues_map or {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Prepare data for template: include image data URIs and residues
    prepared = []
    for a in (aforos or []):
        aforo_id = a.get('id')
        evidencia_fachada = a.get('evidencia_fachada')
        evidencia_residuos = a.get('evidencia_residuos')
        firma = a.get('firma')

        evidencia_fachada = _img_tag_from_b64(evidencia_fachada, alt='fachada') if evidencia_fachada else ''
        evidencia_residuos = _img_tag_from_b64(evidencia_residuos, alt='residuos') if evidencia_residuos else ''
        firma = _img_tag_from_b64(firma, alt='firma') if firma else ''

        prepared.append({
            'id': aforo_id,
            'created_at': a.get('created_at'),
            'sucursal_id': a.get('sucursal_id'),
            'vehiculo_placa': a.get('vehiculo_placa'),
            'operario_name': a.get('operario_name'),
            'observaciones': a.get('observaciones') or '',
            'nombre_firma': a.get('nombre_firma') or '',
            'cedula_firma': a.get('cedula_firma') or '',
            'evidencia_fachada': evidencia_fachada,
            'evidencia_residuos': evidencia_residuos,
            'firma': firma,
            'residues': residues_map.get(aforo_id) or [],
        })

    # Locate templates directory
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'resources', 'templates')
    templates_dir = os.path.normpath(templates_dir)
    loader = jinja2.FileSystemLoader(templates_dir)
    env = jinja2.Environment(loader=loader, autoescape=True)

    # Allow using images_html as safe HTML in template
    env.filters['safe_html'] = lambda v: jinja2.markup.Markup(v)
    # mc.img_to_b64 expects a file-like object; if a path is provided, try reading the file
    logo_b64 = mc.img_to_b64("./resources/Logo2.png")
    if not logo_b64:
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'logo.png')
            with open(os.path.normpath(logo_path), 'rb') as f:
                logo_b64 = base64.b64encode(f.read()).decode()
        except Exception:
            logo_b64 = None

    logo = _img_tag_from_b64(logo_b64, alt="Logo", max_width_px=100)

    try:
        template = env.get_template('aforos.html')
    except jinja2.exceptions.TemplateNotFound:
        # Fallback to minimal HTML if template missing
        return "<html><body><p>Template not found: resources/templates/aforos.html</p></body></html>"
    

    rendered = template.render(aforos=prepared, title=title, generated_at=now, logo=logo)
    return rendered


def generate_aforos_pdf(aforos, residues_map=None, title="Reporte de Aforos") -> bytes:
    """Generate PDF bytes from aforos list using WeasyPrint."""
    font_config = FontConfiguration()
    html_str = build_aforos_html(aforos, residues_map=residues_map, title=title)
    css_path = os.path.join(os.path.dirname(__file__), "..", "resources", "aforo.css")
    css_path = os.path.normpath(css_path)
    pdf_bytes = HTML(string=html_str).write_pdf(stylesheets=[CSS(filename=css_path, font_config=font_config)], font_config=font_config)
    return pdf_bytes
