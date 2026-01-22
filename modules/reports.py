from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from io import BytesIO
from datetime import datetime
import base64
import os
import jinja2
import modules.common as mc
import streamlit as st



def build_aforo_html(aforo, residues=None, title="Reporte de Aforos", fig_b64=None):
    """Render the aforos HTML using a Jinja2 template located in resources/templates/aforos.html."""
    residues = residues or {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Prepare data for template: include image data URIs and residues
    prepared = []
    aforo_id = aforo['id']
    if aforo_id < 10:
        aforo_id_str = f"00{aforo_id}"
    elif aforo_id < 100:
        aforo_id_str = f"0{aforo_id}"
    else:
        aforo_id_str = str(aforo_id)
    prepared.append({
        'id': aforo_id_str,
        'ciudad': aforo['sucursal']['ciudad'],
        'cliente': aforo['sucursal']['clients']['razon_social'],
        'sucursal': aforo['sucursal']['sucursal'],
        'direccion': aforo['sucursal']['direccion'],
        'barrio': aforo['sucursal']['barrio'],
        'correo': aforo['sucursal']['correo'],
        'cliente_nit': aforo['sucursal']['clients']['nit'],
        'sucursal_nit': aforo['sucursal']['nit'],
        'operario': aforo['users']['full_name'],
        'vehiculo_placa': aforo['vehiculo_placa'],
        'fecha': datetime.fromisoformat(aforo['created_at']).strftime("%Y-%m-%d"),
        'hora': datetime.fromisoformat(aforo['created_at']).strftime("%I:%M %p"),
        'observaciones': aforo['observaciones'] or '',
        'operario_cedula': aforo['users']['cedula'] or '',
        'latitud': aforo['latitude'] or '',
        'longitud': aforo['longitude'] or '',
        'nombre_firma': aforo['nombre_firma'] or '',
        'cedula_firma': aforo['cedula_firma'] or '',
        'evidencia_fachada': aforo['evidencia_fachada'],
        'evidencia_residuos': aforo['evidencia_residuos'],
        'firma': aforo['firma'],
        'residues': residues or [],
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


def generate_aforos_pdf(aforo, residues=None, title="Reporte de Aforos", fig_b64=None) -> bytes:
    """Generate PDF bytes from aforos list using WeasyPrint."""
    font_config = FontConfiguration()
    html_str = build_aforo_html(aforo, residues=residues, title=title, fig_b64=fig_b64)
    css_path = os.path.join(os.path.dirname(__file__), "..", "resources", "aforo.css")
    css_path = os.path.normpath(css_path)
    pdf_bytes = HTML(string=html_str).write_pdf(stylesheets=[CSS(filename=css_path, font_config=font_config)], font_config=font_config)
    return pdf_bytes
