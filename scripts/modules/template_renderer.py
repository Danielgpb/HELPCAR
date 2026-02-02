"""
Module: Template Renderer
Description: Remplace les variables dans les templates HTML
Principe KISS & DRY - Simple find/replace avec dictionnaire
Version 2.0: Ajout support Jinja2 pour templates avancés
"""

from pathlib import Path
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateRenderer:
    """Moteur de rendu de templates simple et efficace (v2.0 - Jinja2 support)"""

    def __init__(self, templates_dir):
        """
        Initialise le renderer

        Args:
            templates_dir (str): Chemin vers le dossier templates/
        """
        self.templates_dir = Path(templates_dir)
        self.components_dir = self.templates_dir / 'components'
        self.pages_dir = self.templates_dir / 'pages'
        self.cache = {}

        # Jinja2 Environment pour templates avancés
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def load_template(self, template_path):
        """
        Charge un template depuis un fichier

        Args:
            template_path (str): Chemin relatif depuis templates/
                Exemple: 'pages/service.html' ou 'components/header.html'

        Returns:
            str: Contenu du template
        """
        full_path = self.templates_dir / template_path

        # Cache pour éviter de relire le même fichier
        if str(full_path) in self.cache:
            return self.cache[str(full_path)]

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.cache[str(full_path)] = content
            return content

    def load_component(self, component_name):
        """
        Charge un composant depuis components/

        Args:
            component_name (str): Nom du composant (ex: 'header', 'footer', 'sidebar-service')

        Returns:
            str: HTML du composant
        """
        return self.load_template(f'components/{component_name}.html')

    def render(self, template_content, variables):
        """
        Remplace toutes les variables {{VAR}} dans le template (simple find/replace)

        Args:
            template_content (str): Contenu du template avec {{VARIABLES}}
            variables (dict): Dictionnaire des variables à remplacer
                Exemple: {"TITLE": "Mon titre", "H1": "Mon H1"}

        Returns:
            str: Template avec toutes les variables remplacées
        """
        rendered = template_content

        for key, value in variables.items():
            # Remplace {{KEY}} par la valeur
            # Gère None en remplaçant par chaîne vide
            if value is None:
                value = ''

            rendered = rendered.replace(f'{{{{{key}}}}}', str(value))

        return rendered

    def render_jinja2(self, template_path, context):
        """
        Rend un template avec Jinja2 (support boucles, conditions, filtres)

        Args:
            template_path (str): Chemin relatif du template depuis templates/
                Exemple: 'components/etapes-items.html'
            context (dict): Contexte de variables pour Jinja2
                Exemple: {'etapes': [...], 'path_prefix': '../'}

        Returns:
            str: HTML rendu avec Jinja2
        """
        template = self.jinja_env.get_template(template_path)
        return template.render(**context)

    def render_with_components(self, template_path, variables):
        """
        Rend un template en chargeant automatiquement les composants

        Les composants sont détectés via {{COMPONENT_nom}}
        Exemple: {{COMPONENT_HEADER}} charge components/header.html

        Args:
            template_path (str): Chemin du template principal
            variables (dict): Variables à remplacer

        Returns:
            str: HTML complet avec composants intégrés
        """
        # Charge le template principal
        template = self.load_template(template_path)

        # Détecte et remplace les composants {{COMPONENT_NOM}}
        component_pattern = r'\{\{COMPONENT_([A-Z_]+)\}\}'
        components_found = re.findall(component_pattern, template)

        for component_key in components_found:
            # Convertit COMPONENT_HEADER en 'header'
            component_name = component_key.lower().replace('_', '-')

            try:
                component_html = self.load_component(component_name)
                # Remplace le placeholder
                template = template.replace(f'{{{{COMPONENT_{component_key}}}}}', component_html)
            except FileNotFoundError:
                print(f"⚠️  Warning: Component '{component_name}' not found")
                template = template.replace(f'{{{{COMPONENT_{component_key}}}}}', f'<!-- Component {component_name} not found -->')

        # Remplace les variables
        return self.render(template, variables)

    def render_list_items(self, items, item_template):
        """
        Rend une liste d'items avec un template répété

        Args:
            items (list): Liste d'objets (dict)
            item_template (str): Template pour 1 item
                Exemple: "<li><a href='{{url}}'>{{text}}</a></li>"

        Returns:
            str: HTML de tous les items concaténés
        """
        rendered_items = []

        for item in items:
            rendered_items.append(self.render(item_template, item))

        return '\n'.join(rendered_items)

    def build_sidebar_links(self, links):
        """
        Construit une liste de liens pour la sidebar

        Args:
            links (list): Liste de dict avec 'text' et 'url'
                Exemple: [{"text": "Service 1", "url": "/service-1/"}, ...]

        Returns:
            str: HTML des liens <li><a>...</a></li>
        """
        template = '<li><a href="{{url}}">{{text}}</a></li>'
        return self.render_list_items(links, template)

    def check_missing_variables(self, rendered_html):
        """
        Vérifie s'il reste des variables non remplacées

        Args:
            rendered_html (str): HTML après rendu

        Returns:
            list: Liste des variables manquantes (ex: ['TITLE', 'H1'])
        """
        pattern = r'\{\{([A-Z_0-9]+)\}\}'
        missing = re.findall(pattern, rendered_html)
        return list(set(missing))  # Unique

    def minify_html(self, html):
        """
        Minifie le HTML (supprime espaces superflus, commentaires)

        Args:
            html (str): HTML à minifier

        Returns:
            str: HTML minifié
        """
        # Supprime les commentaires HTML (sauf ceux pour IE)
        html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)

        # Supprime les espaces multiples
        html = re.sub(r'\s+', ' ', html)

        # Supprime espaces entre tags
        html = re.sub(r'>\s+<', '><', html)

        return html.strip()


# Exemple d'utilisation
if __name__ == '__main__':
    renderer = TemplateRenderer('../templates')

    # Test 1: Rendu simple
    template = "<h1>{{TITLE}}</h1><p>{{CONTENT}}</p>"
    result = renderer.render(template, {
        "TITLE": "Mon Titre",
        "CONTENT": "Mon contenu"
    })
    print("✅ Test rendu simple:")
    print(result)
    print()

    # Test 2: Chargement composant
    try:
        header = renderer.load_component('header')
        print(f"✅ Header chargé: {len(header)} caractères")
    except FileNotFoundError:
        print("⚠️  Header non trouvé")
    print()

    # Test 3: Build sidebar links
    links = [
        {"text": "Service 1", "url": "/service-1/"},
        {"text": "Service 2", "url": "/service-2/"}
    ]
    sidebar_html = renderer.build_sidebar_links(links)
    print("✅ Sidebar links:")
    print(sidebar_html)
    print()

    # Test 4: Check missing variables
    html = "<h1>{{TITLE}}</h1><p>{{MISSING}}</p>"
    rendered = renderer.render(html, {"TITLE": "OK"})
    missing = renderer.check_missing_variables(rendered)
    print(f"✅ Variables manquantes: {missing}")
