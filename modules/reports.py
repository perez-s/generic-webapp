from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from io import BytesIO
from datetime import datetime
import base64
import os
import jinja2
import modules.common as mc
import streamlit as st



def build_aforos_html(aforos, residues_map=None, title="Reporte de Aforos", fig_b64=None):
    """Render the aforos HTML using a Jinja2 template located in resources/templates/aforos.html."""
    residues_map = residues_map or {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Prepare data for template: include image data URIs and residues
    prepared = []
    for a in (aforos or []):
        aforo_id = a.get('id')
        if aforo_id < 10:
            aforo_id_str = f"00{aforo_id}"
        elif aforo_id < 100:
            aforo_id_str = f"0{aforo_id}"
        else:
            aforo_id_str = str(aforo_id)
        evidencia_fachada = a.get('evidencia_fachada')
        evidencia_residuos = a.get('evidencia_residuos')
        firma = a.get('firma')
        print(aforo_id)
        prepared.append({
            'id': aforo_id_str,
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
            'map_figure': fig_b64
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
    try:
        template = env.get_template('aforos.html')
    except jinja2.exceptions.TemplateNotFound:
        # Fallback to minimal HTML if template missing
        return "<html><body><p>Template not found: resources/templates/aforos.html</p></body></html>"
    

    rendered = template.render(aforos=prepared, title=title, generated_at=now, logo=logo_b64)
    return rendered


def generate_aforos_pdf(aforos, residues_map=None, title="Reporte de Aforos", fig_b64=None) -> bytes:
    """Generate PDF bytes from aforos list using WeasyPrint."""
    font_config = FontConfiguration()
    html_str = build_aforos_html(aforos, residues_map=residues_map, title=title, fig_b64=fig_b64)
    css_path = os.path.join(os.path.dirname(__file__), "..", "resources", "aforo.css")
    css_path = os.path.normpath(css_path)
    pdf_bytes = HTML(string=html_str).write_pdf(stylesheets=[CSS(filename=css_path, font_config=font_config)], font_config=font_config)
    return pdf_bytes
