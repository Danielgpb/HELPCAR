#!/usr/bin/env python3
"""
BRUXELLES CAR DEPANNAGE - Générateur de Pages HTML Statiques v4.1
Description: Script principal pour générer toutes les pages du site
Architecture: Modulaire KISS & DRY - Source unique Schema.org
Auteur: Claude Code
Date: 2025-12-17
Version: 4.1 - Refactoring: Contenu externalisé + Templates Jinja2
"""

import argparse
import sys
import json
import shutil
from pathlib import Path

# Import des modules
sys.path.append(str(Path(__file__).parent / 'modules'))

from data_loader import DataLoader
from template_renderer import TemplateRenderer
from css_generator import CSSGenerator
from content_builder import ContentBuilder
from breadcrumb_builder import BreadcrumbBuilder
from card_builder import CardBuilder
from sidebar_builder import SidebarBuilder
from icons import get_icon

# Modules de refactoring #6 - Extraction fonctionnelle
from modules import page_builder, grid_builder, html_builder
from modules.service_icons import get_service_icon


class SiteGenerator:
    """Générateur principal du site statique (multilingue) v3.0"""

    # ==========================================
    # CONFIGURATION - Constantes centralisées
    # ==========================================

    # Fichiers CSS à copier vers build/
    CSS_FILES = ['main.css', 'shared.css', 'service.css', 'commune.css', 'dropdown.css', 'fonts.css', 'carousel.css', 'accessibility.css', 'language-selector.css']

    # Fichiers JavaScript à copier vers build/
    JS_FILES = ['carousel.js', 'whatsapp-smart.js', 'language-selector.js']

    # Fichiers logo à copier à la racine de images/
    LOGO_ROOT_FILES = ['logo.webp', 'logo.png']

    # Dossiers d'images simples (fichiers uniquement, pas de sous-dossiers)
    IMAGE_FOLDERS_SIMPLE = {
        'icons': 'icônes',
        'hero': 'images hero',
        'logo': 'images logo',
        'services': 'images services',
        'communes': 'images communes'
    }

    # Dossiers d'images de pages
    IMAGE_FOLDERS_PAGES = ['zones-index', 'tarif', 'contact', 'a-propos',
                           'services-index', 'service', 'mentions-legales', 'politique-confidentialite']

    # Extensions d'images supportées
    IMAGE_EXTENSIONS = ['.webp', '.jpg', '.jpeg', '.png', '.svg', '.gif']

    def __init__(self, base_path='.', lang='fr', verbose=True):
        """
        Initialise le générateur v4.0

        Args:
            base_path (str): Chemin vers la racine du projet
            lang (str): Code langue ('fr', 'en', 'nl')
            verbose (bool): Afficher les logs détaillés
        """
        self.base_path = Path(base_path)
        self.lang = lang
        self.verbose = verbose
        # FR génère à la racine de build/, autres langues dans build/{lang}/
        if lang == 'fr':
            self.build_dir = self.base_path / 'build'
        else:
            self.build_dir = self.base_path / 'build' / lang

        # Initialisation des modules
        self.log(f"📦 Chargement des modules v4.0 ({lang.upper()})...")

        # DataLoader v4.0 - Source unique Schema.org
        self.loader = DataLoader(base_path, lang=lang)

        # SchemaBuilder accessible via loader
        self.schema_builder = self.loader.schema_builder

        # Template renderer
        self.renderer = TemplateRenderer(self.base_path / 'templates')

        # Chargements
        self.ui_translations = self.loader.load_ui_translations()
        self.variables = self.load_variables()

        # Injecter les URLs des services et communes selon la langue (FR ou EN)
        self.inject_service_urls_for_lang()
        self.inject_commune_urls_for_lang()

        self.images_alt = self.load_images_alt()
        self.images_dimensions = self.load_images_dimensions()

        # Validation URLs centralisées (Option A+)
        self.validate_urls_consistency()

        # ContentBuilder v4.1 - Génère HTML depuis templates Jinja2
        self.content_builder = ContentBuilder(self.base_path, lang=lang, template_renderer=self.renderer)

        # BreadcrumbBuilder v4.1 - Génère breadcrumbs depuis templates
        components_translations = self.content_builder.components_translations
        self.breadcrumb_builder = BreadcrumbBuilder(self.base_path, lang=lang, template_renderer=self.renderer, translations=components_translations)

        # CardBuilder v4.1 - Génère cartes services depuis templates
        self.card_builder = CardBuilder(self.base_path, lang=lang, template_renderer=self.renderer, icon_getter=self._get_service_icon)

        # SidebarBuilder v4.1 - Génère sidebars avec rotation
        self.sidebar_builder = SidebarBuilder(self.base_path, lang=lang, data_loader=self.loader)

        self.log(f"✅ Générateur v4.1 initialisé (Lang: {lang}) - Tous les builders activés")

    def log(self, message):
        """Affiche un message si verbose activé"""
        if self.verbose:
            print(message)

    # ==========================================
    # MULTILINGUAL SUPPORT - Helper Methods
    # ==========================================

    def _get_lang_prefix(self):
        """
        Retourne le préfixe de langue pour les URLs

        Returns:
            str: '' pour FR (version de base), '/en' pour EN, '/nl' pour NL
        """
        if self.lang == 'fr':
            return ''  # Pas de préfixe pour FR (version de base)
        else:
            return f'/{self.lang}'  # /en pour anglais, /nl pour néerlandais

    def _get_path_prefix(self, level='subpage'):
        """
        Retourne PATH_PREFIX selon la langue et le niveau de page

        Args:
            level: 'base' pour homepage, 'subpage' pour pages dans /services/, /zones/, etc.

        Returns:
            str: PATH_PREFIX approprié

        Examples:
            FR homepage: '' (assets dans build/)
            FR subpage: '../' (remonter à build/)
            EN homepage: '' (assets dans build/en/)
            EN subpage: '../' (remonter à build/en/)

        Note: Chaque version de langue a ses assets copiés localement dans son dossier
        """
        # Même logique pour toutes les langues car assets copiés localement
        if level == 'base':
            return ''  # Homepage: assets dans le même dossier
        else:
            return '../'  # Subpages: un niveau up

    def _get_page_content_filename(self, page_type):
        """
        Retourne le nom du fichier de contenu selon la langue et le type de page

        Args:
            page_type: 'tarifs', 'zones-index', 'a-propos', 'mentions-legales', 'politique-confidentialite'

        Returns:
            str: Nom du fichier de contenu approprié

        Examples:
            FR: 'tarifs' → 'tarifs.json'
            EN: 'tarifs' → 'pricing.json'
        """
        # Mapping des noms de fichiers par langue
        filename_mapping = {
            'tarifs': {
                'fr': 'tarifs.json',
                'en': 'pricing.json'
            },
            'zones-index': {
                'fr': 'zones-index.json',
                'en': 'zones-index.json'
            },
            'a-propos': {
                'fr': 'a-propos.json',
                'en': 'about-us.json'
            },
            'mentions-legales': {
                'fr': 'mentions-legales.json',
                'en': 'legal-notice.json'
            },
            'politique-confidentialite': {
                'fr': 'politique-confidentialite.json',
                'en': 'privacy-policy.json'
            }
        }

        return filename_mapping.get(page_type, {}).get(self.lang, f'{page_type}.json')

    def _get_page_save_path(self, page_type):
        """
        Retourne le chemin de sauvegarde selon la langue et le type de page

        Args:
            page_type: 'tarifs', 'zones', 'a-propos', 'mentions-legales', 'politique-confidentialite'

        Returns:
            str: Chemin de sauvegarde approprié (ex: 'pricing/index.html' pour EN)

        Examples:
            FR: 'tarifs' → 'tarifs/index.html'
            EN: 'tarifs' → 'pricing/index.html'
        """
        # Mapping des chemins de sauvegarde par langue
        path_mapping = {
            'tarifs': {
                'fr': 'tarifs/index.html',
                'en': 'pricing/index.html'
            },
            'zones': {
                'fr': 'zones/index.html',
                'en': 'areas/index.html'
            },
            'a-propos': {
                'fr': 'a-propos/index.html',
                'en': 'about-us/index.html'
            },
            'mentions-legales': {
                'fr': 'mentions-legales/index.html',
                'en': 'legal-notice/index.html'
            },
            'politique-confidentialite': {
                'fr': 'politique-confidentialite/index.html',
                'en': 'privacy-policy/index.html'
            }
        }

        return path_mapping.get(page_type, {}).get(self.lang, f'{page_type}/index.html')

    def _get_language_variables(self, level='base'):
        """
        Génère les variables pour le sélecteur de langue, système multilingue et header traduit

        Args:
            level: 'base' pour homepage, 'subpage' pour pages dans sous-dossiers

        Returns:
            dict: Variables de langue (CURRENT_LANG, LANG_PREFIX, LANG_URL_*, LANG_ACTIVE_*, HEADER_*)
        """
        lang_upper = self.lang.upper()

        # URLs de langue pour le sélecteur (chemins relatifs adaptés au niveau)
        if self.lang == 'fr':
            # Version française (base: build/)
            if level == 'base':
                # build/index.html → build/en/index.html
                lang_url_fr = './'
                lang_url_en = 'en/'
                lang_url_nl = 'nl/'
            else:
                # build/service/index.html → build/en/service/index.html
                lang_url_fr = './'
                lang_url_en = '../en/'  # Remonter puis entrer dans /en/
                lang_url_nl = '../nl/'
        elif self.lang == 'en':
            # Version anglaise (build/en/)
            if level == 'base':
                # build/en/index.html → build/index.html
                lang_url_fr = '../'
                lang_url_en = './'
                lang_url_nl = '../nl/'
            else:
                # build/en/service/index.html → build/service/index.html
                lang_url_fr = '../../'  # Remonter de 2 niveaux
                lang_url_en = './'
                lang_url_nl = '../../nl/'
        else:  # nl
            # Version néerlandaise (build/nl/)
            if level == 'base':
                lang_url_fr = '../'
                lang_url_en = '../en/'
                lang_url_nl = './'
            else:
                lang_url_fr = '../../'
                lang_url_en = '../../en/'
                lang_url_nl = './'

        lang_vars = {
            'CURRENT_LANG': lang_upper,
            'LANG_PREFIX': self._get_lang_prefix(),
            'LANG_URL_FR': lang_url_fr,
            'LANG_URL_EN': lang_url_en,
            'LANG_URL_NL': lang_url_nl,
            'LANG_ACTIVE_FR': 'active' if self.lang == 'fr' else '',
            'LANG_ACTIVE_EN': 'active' if self.lang == 'en' else '',
            'LANG_ACTIVE_NL': 'active' if self.lang == 'nl' else '',
        }

        # Ajouter les variables header traduites
        lang_vars.update(self._get_header_variables())

        # URLs des pages statiques (dépendent de la langue)
        path_prefix = self._get_path_prefix(level)
        if self.lang == 'en':
            lang_vars['ZONES_INDEX_URL'] = f'{path_prefix}areas/index.html'
            lang_vars['TARIFS_INDEX_URL'] = f'{path_prefix}pricing/index.html'
        else:  # fr (ou nl dans le futur)
            lang_vars['ZONES_INDEX_URL'] = f'{path_prefix}zones/index.html'
            lang_vars['TARIFS_INDEX_URL'] = f'{path_prefix}tarifs/index.html'

        return lang_vars

    def _generate_hreflang_urls(self, page_type, slug=''):
        """
        Génère les URLs hreflang pour une page (SEO multilingue)

        Args:
            page_type: 'homepage', 'service', 'location', 'services-index', etc.
            slug: Slug de la page (pour services/locations)

        Returns:
            dict: Variables hreflang (HREFLANG_FR, HREFLANG_EN, HREFLANG_NL, HREFLANG_X_DEFAULT)
        """
        base_url = "https://www.bruxelles-car-depannage.be"

        # Construire les URLs selon le type de page
        if page_type == 'homepage':
            url_fr = f"{base_url}/"
            url_en = f"{base_url}/en/"
            url_nl = f"{base_url}/nl/"

        elif page_type == 'services-index':
            url_fr = f"{base_url}/services/"
            url_en = f"{base_url}/en/services/"
            url_nl = f"{base_url}/nl/services/"

        elif page_type == 'zones-index':
            url_fr = f"{base_url}/zones/"
            url_en = f"{base_url}/en/zones/"
            url_nl = f"{base_url}/nl/zones/"

        elif page_type == 'service':
            # Pour l'instant, on utilise le même slug (sera amélioré quand services EN seront traduits)
            url_fr = f"{base_url}/{slug}/"
            url_en = f"{base_url}/en/{slug}/"
            url_nl = f"{base_url}/nl/{slug}/"

        elif page_type == 'location':
            # Les slugs locations restent identiques
            url_fr = f"{base_url}/{slug}/"
            url_en = f"{base_url}/en/{slug}/"
            url_nl = f"{base_url}/nl/{slug}/"

        elif page_type in ['tarifs', 'pricing', 'contact', 'a-propos', 'about-us', 'mentions-legales', 'legal-notice', 'politique-confidentialite', 'privacy-policy']:
            # Pages statiques - mapper les slugs
            page_slugs_map = {
                'tarifs': {'fr': 'tarifs', 'en': 'pricing', 'nl': 'prijzen'},
                'pricing': {'fr': 'tarifs', 'en': 'pricing', 'nl': 'prijzen'},
                'contact': {'fr': 'contact', 'en': 'contact', 'nl': 'contact'},
                'a-propos': {'fr': 'a-propos', 'en': 'about-us', 'nl': 'over-ons'},
                'about-us': {'fr': 'a-propos', 'en': 'about-us', 'nl': 'over-ons'},
                'mentions-legales': {'fr': 'mentions-legales', 'en': 'legal-notice', 'nl': 'juridische-kennisgeving'},
                'legal-notice': {'fr': 'mentions-legales', 'en': 'legal-notice', 'nl': 'juridische-kennisgeving'},
                'politique-confidentialite': {'fr': 'politique-confidentialite', 'en': 'privacy-policy', 'nl': 'privacybeleid'},
                'privacy-policy': {'fr': 'politique-confidentialite', 'en': 'privacy-policy', 'nl': 'privacybeleid'}
            }

            slugs = page_slugs_map.get(page_type, {'fr': page_type, 'en': page_type, 'nl': page_type})
            url_fr = f"{base_url}/{slugs['fr']}/"
            url_en = f"{base_url}/en/{slugs['en']}/"
            url_nl = f"{base_url}/nl/{slugs['nl']}/"

        else:
            # Fallback - homepage
            url_fr = f"{base_url}/"
            url_en = f"{base_url}/en/"
            url_nl = f"{base_url}/nl/"

        return {
            'HREFLANG_FR': url_fr,
            'HREFLANG_EN': url_en,
            'HREFLANG_NL': url_nl,
            'HREFLANG_X_DEFAULT': url_fr  # FR est la version par défaut
        }

    def _get_header_variables(self):
        """
        Extrait les variables de traduction pour le header depuis ui_translations

        Returns:
            dict: Variables HEADER_* pour le template header.html
        """
        header_translations = self.ui_translations.get('header', {})

        # Remplacer {{count}} dans les templates
        nombre_services = self.variables.get('stats', {}).get('nombre_services', 22)
        nombre_communes = self.variables.get('stats', {}).get('nombre_communes', 34)

        view_all_services = header_translations.get('view_all_services', 'Voir tous les services ({{count}}) →')
        view_all_services = view_all_services.replace('{{count}}', str(nombre_services))

        view_all_zones = header_translations.get('view_all_zones', 'Voir toutes les zones ({{count}}) →')
        view_all_zones = view_all_zones.replace('{{count}}', str(nombre_communes))

        return {
            'HEADER_SERVICES_MENU': header_translations.get('services_menu', 'Nos Services'),
            'HEADER_ZONES_MENU': header_translations.get('zones_menu', 'Zones d\'Intervention'),
            'HEADER_TARIFS': header_translations.get('tarifs', 'Tarifs'),
            'HEADER_CONTACT': header_translations.get('contact', 'Contact'),
            'HEADER_PHONE_CALL': header_translations.get('phone_call', 'Appelez-nous'),
            'HEADER_PHONE_24_7': header_translations.get('phone_24_7', '24/7'),
            'HEADER_MOBILE_MENU_OPEN': header_translations.get('mobile_menu_open', 'Ouvrir le menu'),
            'HEADER_MOBILE_CALL_NOW': header_translations.get('mobile_call_now', 'Appelez Maintenant'),
            'HEADER_VIEW_ALL_SERVICES': view_all_services,
            'HEADER_VIEW_ALL_ZONES': view_all_zones,
            'HEADER_SERVICE_TOWING': header_translations.get('service_towing', 'Remorquage de voitures'),
            'HEADER_SERVICE_BATTERY': header_translations.get('service_battery', 'Dépannage batterie'),
            'HEADER_SERVICE_TIRE': header_translations.get('service_tire', 'Réparation pneu'),
            'HEADER_SERVICE_FUEL': header_translations.get('service_fuel', 'Panne d\'essence'),
            'HEADER_SERVICE_DOOR': header_translations.get('service_door', 'Ouverture de porte'),
            'HEADER_SERVICE_MOTO': header_translations.get('service_moto', 'Remorquage de motos'),
            'HEADER_LANG_SELECT': header_translations.get('lang_select', 'Sélectionner la langue')
        }

    def _load_json_safe(self, file_path, default=None, description="fichier JSON"):
        """
        Charge un fichier JSON de manière sécurisée avec gestion d'erreurs

        Args:
            file_path (Path): Chemin vers le fichier JSON
            default: Valeur par défaut en cas d'erreur (None ou {})
            description (str): Description du fichier pour les logs

        Returns:
            dict/list: Contenu JSON ou valeur par défaut
        """
        if default is None:
            default = {}

        if not file_path.exists():
            if self.verbose:
                self.log(f"⚠️  {description} introuvable: {file_path}")
            return default

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON dans {file_path}: {e}")
            return default
        except Exception as e:
            print(f"❌ Erreur lecture {description}: {e}")
            return default

    def _get_svg_icon(self, icon_name):
        """
        Retourne le SVG inline pour un nom d'icône donné
        Délègue au module icons centralisé

        Args:
            icon_name (str): Nom de l'icône (ex: 'map-pin', 'battery', 'parking')

        Returns:
            str: Code SVG inline
        """
        return get_icon(icon_name, variant='standard')

    def _build_quartiers_html(self, quartiers):
        """
        Génère le HTML pour la section quartiers (v4.3 - Jinja2)

        Args:
            quartiers (list): Liste des quartiers avec icon, nom, description

        Returns:
            str: HTML de la grille de quartiers
        """
        if not quartiers:
            return ''

        # Préparer les données pour le template
        quartiers_data = []
        for quartier in quartiers:
            icon_svg = self._get_svg_icon(quartier.get('icon', 'map-pin'))
            nom = self.replace_variables_in_content(quartier.get('nom', ''), {})
            description = self.replace_variables_in_content(quartier.get('description', ''), {})

            quartiers_data.append({
                'icon_svg': icon_svg,
                'nom': nom,
                'description': description
            })

        return self.renderer.render_jinja2('components/quartiers-grid.html', {
            'quartiers': quartiers_data
        })

    def _build_parkings_html(self, parkings_data):
        """
        Génère le HTML pour la section parkings (v4.3 - Jinja2)

        Args:
            parkings_data (dict): Données de la section parkings

        Returns:
            str: HTML de la section parkings ou chaîne vide si non affiché
        """
        if not parkings_data.get('afficher', False):
            return ''

        # Préparer les données pour le template
        parkings_list = []
        for parking in parkings_data.get('parkings', []):
            icon_svg = self._get_svg_icon(parking.get('icon', 'parking'))
            nom = self.replace_variables_in_content(parking.get('nom', ''), {})

            parkings_list.append({
                'icon_svg': icon_svg,
                'nom': nom
            })

        return self.renderer.render_jinja2('components/parkings-section.html', {
            'h3': self.replace_variables_in_content(parkings_data.get('h3', ''), {}),
            'intro': self.replace_variables_in_content(parkings_data.get('intro', ''), {}),
            'parkings': parkings_list,
            'conclusion': self.replace_variables_in_content(parkings_data.get('conclusion', ''), {})
        })

    def _get_category_class(self, titre):
        """
        Retourne la classe CSS de couleur selon le titre de la catégorie

        Args:
            titre (str): Titre de la catégorie

        Returns:
            str: Classe CSS (ex: 'cat-batterie', 'cat-pneus', etc.)
        """
        titre_lower = titre.lower()

        # JAUNE - Pannes classiques (Batterie + Pneus)
        if 'batterie' in titre_lower or 'pneu' in titre_lower or 'roue' in titre_lower:
            return 'cat-jaune'

        # ORANGE - Assistance rapide (Carburant + Accès)
        elif ('carburant' in titre_lower or 'essence' in titre_lower or 'siphonnage' in titre_lower or
              'accès' in titre_lower or 'ouverture' in titre_lower or 'porte' in titre_lower or 'clé' in titre_lower):
            return 'cat-orange'

        # ROUGE - Urgences critiques (Remorquage + Urgences)
        elif 'remorquage' in titre_lower or 'urgence' in titre_lower or 'accident' in titre_lower:
            return 'cat-rouge'

        else:
            return 'cat-rouge'  # Par défaut : rouge

    def _build_services_categories_html(self, categories, path_prefix='../'):
        """
        Génère le HTML pour les services groupés par catégories (v4.3 - Jinja2)

        Args:
            categories (list): Liste des catégories avec services
            path_prefix (str): Préfixe de chemin relatif

        Returns:
            str: HTML des services par catégories
        """
        if not categories:
            return ''

        # Préparer les données pour le template
        categories_data = []

        for category in categories:
            icon_svg = self._get_svg_icon(category.get('icon', 'car'))
            titre = self.replace_variables_in_content(category.get('titre', ''), {})
            category_class = self._get_category_class(titre)

            # Préparer les services de cette catégorie
            services_list = []
            for service in category.get('services', []):
                # Résoudre l'URL
                url_var = service.get('url_var', '')
                if url_var:
                    slug = self.resolve_variable_path(
                        self.variables.get('template_variables', {}).get(url_var, ''),
                        self.variables
                    )
                else:
                    slug = service.get('slug', '')

                service_url = f'{path_prefix}{slug}/index.html' if slug else '#'

                services_list.append({
                    'nom': self.replace_variables_in_content(service.get('nom', ''), {}),
                    'description': self.replace_variables_in_content(service.get('description', ''), {}),
                    'url': service_url
                })

            categories_data.append({
                'icon_svg': icon_svg,
                'titre': titre,
                'class_attr': f' {category_class}' if category_class else '',
                'services': services_list
            })

        return self.renderer.render_jinja2('components/services-categories.html', {
            'categories': categories_data,
            'path_prefix': path_prefix
        })

    def _build_faq_locale_html(self, faq_data):
        """
        Génère le HTML pour la FAQ locale (v4.3 - Jinja2)

        Args:
            faq_data (dict): Données de la FAQ avec h2 et questions

        Returns:
            str: HTML de la FAQ
        """
        if not faq_data or not faq_data.get('questions'):
            return ''

        # Préparer les questions pour le template
        questions_list = []
        for q in faq_data.get('questions', []):
            questions_list.append({
                'question': self.replace_variables_in_content(q.get('question', ''), {}),
                'reponse': self.replace_variables_in_content(q.get('reponse', ''), {})
            })

        return self.renderer.render_jinja2('components/faq-locale.html', {
            'h2': faq_data.get('h2', 'Questions fréquentes'),
            'questions': questions_list
        })

    def _load_page_seo(self, page_name):
        """
        Charge les données SEO d'une page depuis content/fr/pages/{page_name}.json

        Args:
            page_name (str): Nom de la page (ex: 'tarifs', 'contact', 'services-index')

        Returns:
            dict: Données SEO (meta_title, h1, h2, meta_description) ou dict vide
        """
        content_file = self.base_path / 'content' / self.lang / 'pages' / f'{page_name}.json'
        data = self._load_json_safe(content_file, default={}, description=f"SEO page {page_name}")
        return data.get('seo', {})

    def _get_commune_image(self, slug):
        """
        Récupère le chemin de l'image d'une commune (supporte .jpg et .jpeg)

        Args:
            slug (str): Slug de la commune (ex: 'depannage-ixelles')

        Returns:
            str: Chemin relatif vers l'image
        """
        # Retirer le préfixe 'depannage-' du slug
        commune_slug = slug.replace('depannage-', '')

        # Essayer .jpg d'abord
        jpg_path = self.base_path / 'images' / 'communes' / f'commune-{commune_slug}.jpg'
        if jpg_path.exists():
            return f"../images/communes/commune-{commune_slug}.jpg"

        # Essayer .jpeg
        jpeg_path = self.base_path / 'images' / 'communes' / f'commune-{commune_slug}.jpeg'
        if jpeg_path.exists():
            return f"../images/communes/commune-{commune_slug}.jpeg"

        # Image par défaut si non trouvée
        return f"../images/communes/commune-{commune_slug}.jpg"

    def _get_service_icon(self, slug, relative_path='../'):
        """
        Récupère le chemin de l'icône d'un service (supporte .png, .jpg, .jpeg, .svg)

        Args:
            slug (str): Slug du service (ex: 'remorquage-voitures-bruxelles' ou 'car-towing-brussels')
            relative_path (str): Chemin relatif (../ pour pages, '' pour racine)

        Returns:
            str: Chemin relatif vers l'icône ou emoji par défaut
        """
        # Mapping des slugs EN vers les noms d'icônes (FR)
        en_to_fr_icon_mapping = {
            'car-towing': 'remorquage-voiture',
            'battery-breakdown': 'depannage-batterie',
            'tire-repair': 'reparation-pneu',
            'tyre-repair': 'reparation-pneu',  # UK spelling
            'out-of-fuel': 'panne-essence',
            'fuel-delivery': 'fourniture-carburant',
            'car-door-unlocking': 'ouverture-porte-voiture',
            'motorcycle-towing': 'remorquage-motos',
            'van-breakdown': 'depannage-camionnette',
            'scrap-car-removal': 'enlevement-epave',
            'underground-carpark-breakdown': 'depannage-parking-souterrain',
            'stuck-car': 'voiture-embourbee',
            'stuck-car-recovery': 'voiture-embourbee',  # Alternative slug
            'battery-replacement': 'remplacement-batterie',
            'wrong-fuel-draining': 'siphonnage-reservoir',
            'spare-wheel-installation': 'placement-roue-secours',
            'spare-wheel-fitting': 'placement-roue-secours',  # Alternative slug
            'towing-from-pound': 'sortie-fourriere',
            'pound-release': 'sortie-fourriere',  # Alternative slug
            'electric-car-breakdown': 'depannage-voiture-electrique',
            'accident-towing': 'depannage-accident',
            'car-breakdown': 'depannage-voiture',
            'special-vehicle-towing': 'remorquage-vehicules-speciaux',
            'engine-breakdown': 'panne-moteur',
            'local-road-transport': 'transport-routier-local',
            'long-distance-road-transport': 'transport-routier-longue-distance'
        }

        # Retirer le suffixe '-bruxelles' ou '-brussels' du slug
        service_slug = slug.replace('-bruxelles', '').replace('-brussels', '')

        # Si c'est un slug anglais, utiliser le mapping
        if service_slug in en_to_fr_icon_mapping:
            service_slug = en_to_fr_icon_mapping[service_slug]

        # Tester les différents formats (PNG en priorité pour transparence)
        for ext in ['.png', '.webp', '.svg', '.jpg', '.jpeg']:
            icon_path = self.base_path / 'images' / 'icons' / f'{service_slug}{ext}'
            if icon_path.exists():
                return f"{relative_path}images/icons/{service_slug}{ext}"

        # Retourner emoji par défaut si icône non trouvée
        return None

    def load_service_content(self, service_slug):
        """
        Charge le contenu d'un service depuis content/fr/services/{slug}.json

        Args:
            service_slug (str): Slug du service

        Returns:
            dict: Contenu du service (hero, sections, cta)
        """
        content_path = self.base_path / 'content' / self.lang / 'services' / f'{service_slug}.json'

        if not content_path.exists():
            self.log(f"⚠️  Contenu introuvable : {content_path}")
            return {
                'hero': {'h1': '', 'badges': []},
                'sections': [],
                'cta': {}
            }

        with open(content_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        return content

    def build_hero_badges(self, badge_ids):
        """
        Convertit les IDs de badges en HTML (v4.1 - utilise ContentBuilder)

        Args:
            badge_ids (list): Liste des IDs de badges (ex: ['intervention_rapide', 'disponible_24_7'])

        Returns:
            str: HTML des badges
        """
        return self.content_builder.build_hero_badges(badge_ids)

    def build_faq_section(self, faq_data):
        """
        Construit le HTML de la section FAQ (v4.1 - utilise ContentBuilder + template Jinja2)

        Args:
            faq_data (list): Liste de dict avec 'question' et 'answer'

        Returns:
            str: HTML de la section FAQ
        """
        return self.content_builder.build_faq_section(faq_data)

    def replace_variables_in_content(self, content, variables):
        """
        Remplace les variables dynamiques dans le contenu HTML

        Args:
            content (str): Contenu HTML avec variables {{VAR}}
            variables (dict): Dictionnaire des variables

        Returns:
            str: Contenu avec variables remplacées
        """
        # Récupérer le mapping des variables depuis config/variables.json
        template_variables = self.variables.get('template_variables', {})

        # Construire le dictionnaire de remplacement en résolvant les chemins
        replacements = {}

        # D'abord, ajouter les variables depuis template_variables (priorité basse)
        for var_name, var_path in template_variables.items():
            # Résoudre le chemin en dot-notation
            resolved_value = self.resolve_variable_path(var_path, self.variables)
            replacements[var_name] = resolved_value

        # Ensuite, écraser avec les variables passées en paramètre (priorité haute)
        # Cela permet aux valeurs calculées dynamiquement de remplacer les valeurs statiques
        for key, value in variables.items():
            replacements[key] = value

        # Remplacer toutes les variables {{VAR}} dans le contenu
        result = content
        for var_name, var_value in replacements.items():
            result = result.replace(f'{{{{{var_name}}}}}', str(var_value))

        return result

    def load_variables(self):
        """Charge les variables centralisées depuis config/variables.json - Source unique v2.0"""
        variables_path = self.base_path / 'config' / 'variables.json'

        variables = self._load_json_safe(
            variables_path,
            default={},
            description="variables.json"
        )

        if variables:
            self.log(f"✅ Variables chargées depuis {variables_path} v{variables.get('version', '1.0')}")

        return variables

    def inject_service_urls_for_lang(self):
        """
        Injecte les URLs des services selon la langue actuelle dans self.variables['urls']['services']

        Les clés (REMORQUAGE_VOITURE, BATTERIE, etc.) restent les mêmes pour toutes les langues,
        mais les slugs sont traduits (remorquage-voiture-bruxelles -> car-towing-brussels)
        """
        # Mapping ID -> KEY (basé sur l'ordre dans services-fr.json)
        # Les IDs sont les mêmes pour toutes les langues
        ID_TO_KEY = {
            1: 'REMORQUAGE_VOITURE',
            2: 'BATTERIE',
            4: 'PNEU',
            5: 'FOURNITURE_CARBURANT',
            6: 'REMORQUAGE_MOTO',
            7: 'REMORQUAGE_SPECIAUX',
            8: 'REMPLACEMENT_BATTERIE',
            9: 'TRANSPORT_LOCAL',
            10: 'TRANSPORT_LONGUE_DISTANCE',
            11: 'OUVERTURE_PORTE',
            12: 'PANNE_ESSENCE',
            13: 'ROUE_SECOURS',
            14: 'PARKING_SOUTERRAIN',
            15: 'VOITURE_EMBOURBEE',
            16: 'SIPHONNAGE',
            17: 'EPAVE',
            18: 'PANNE_MOTEUR',
            19: 'SORTIE_FOURRIERE',
            20: 'VOITURE_ELECTRIQUE',
            21: 'ACCIDENT',
            23: 'DEPANNAGE_VOITURE',
            24: 'CAMIONNETTE'
        }

        # Charger les services dans la langue actuelle
        services = self.loader.load_services()

        # S'assurer que la structure urls.services existe
        if 'urls' not in self.variables:
            self.variables['urls'] = {}
        if 'services' not in self.variables['urls']:
            self.variables['urls']['services'] = {}

        # Injecter les slugs traduits
        for service in services:
            service_id = service.get('id')
            service_slug = service.get('slug', '')

            if service_id in ID_TO_KEY:
                key = ID_TO_KEY[service_id]
                self.variables['urls']['services'][key] = service_slug

    def inject_commune_urls_for_lang(self):
        """
        Injecte les URLs des communes selon la langue actuelle dans self.variables['urls']['communes']

        Les clés (AUDERGHEM, BRUXELLES_VILLE, etc.) restent les mêmes pour toutes les langues,
        mais les slugs sont traduits (depannage-voiture-auderghem -> car-breakdown-auderghem)
        """
        # Mapping ID -> KEY (basé sur les noms des communes)
        ID_TO_KEY = {
            2: 'AUDERGHEM',
            4: 'BRUXELLES_VILLE',
            5: 'ETTERBEEK',
            6: 'EVERE',
            7: 'FOREST',
            9: 'IXELLES',
            13: 'SAINT_GILLES',
            14: 'SAINT_JOSSE_TEN_NOODE',
            15: 'SCHAERBEEK',
            16: 'UCCLE',
            17: 'WATERMAEL_BOITSFORT',
            18: 'WOLUWE_SAINT_LAMBERT',
            19: 'WOLUWE_SAINT_PIERRE',
            20: 'ZAVENTEM',
            21: 'VILVOORDE',
            22: 'MACHELEN',
            23: 'GRIMBERGEN',
            26: 'KRAAINEM',
            27: 'WEZEMBEEK_OPPEM',
            28: 'TERVUREN',
            29: 'OVERIJSE',
            30: 'HOEILAART',
            31: 'LA_HULPE',
            32: 'WATERLOO',
            33: 'BRAINE_L_ALLEUD',
            34: 'RHODE_SAINT_GENESE',
            37: 'DROGENBOS',
            39: 'MEISE',
            40: 'RIXENSART',
            41: 'WAVRE',
            42: 'LASNE',
            43: 'OTTIGNIES',
            44: 'LOUVAIN_LA_NEUVE',
            45: 'DIEGEM'
        }

        # Charger les communes dans la langue actuelle
        communes = self.loader.load_communes(active_only=True)

        # S'assurer que la structure urls.communes existe
        if 'urls' not in self.variables:
            self.variables['urls'] = {}
        if 'communes' not in self.variables['urls']:
            self.variables['urls']['communes'] = {}

        # Injecter les slugs traduits
        for commune in communes:
            commune_id = commune.get('id')
            commune_slug = commune.get('slug', '')

            if commune_id in ID_TO_KEY:
                key = ID_TO_KEY[commune_id]
                self.variables['urls']['communes'][key] = commune_slug

    def load_images_alt(self):
        """Charge les descriptions alt des images depuis content/{lang}/images-alt.json"""
        images_alt_file = self.base_path / 'content' / self.lang / 'images-alt.json'
        data = self._load_json_safe(images_alt_file, default={}, description="images-alt.json")

        if data:
            self.log(f"✅ Descriptions alt chargées depuis {images_alt_file.name}")

        return data

    def load_images_dimensions(self):
        """Charge les dimensions des images depuis content/{lang}/images-dimensions.json"""
        dimensions_file = self.base_path / 'content' / self.lang / 'images-dimensions.json'
        data = self._load_json_safe(dimensions_file, default={}, description="images-dimensions.json")

        if data:
            self.log(f"✅ Dimensions images chargées ({data.get('total_images', 0)} images)")

        return data.get('images', {})

    def get_image_dimensions_attrs(self, image_path):
        """
        Retourne les attributs width/height pour une image

        Args:
            image_path (str): Chemin relatif de l'image depuis images/ (ex: 'logo.webp' ou 'homepage/hero/image.webp')

        Returns:
            str: Attributs HTML width et height (ex: 'width="1200" height="800"') ou '' si non trouvé
        """
        # Normaliser le chemin (enlever 'images/' si présent)
        clean_path = image_path.replace('images/', '')

        dims = self.images_dimensions.get(clean_path)
        if dims and 'width' in dims and 'height' in dims:
            return f'width="{dims["width"]}" height="{dims["height"]}"'
        return ''

    def validate_urls_consistency(self):
        """
        Valide que les URLs dans variables.json correspondent aux slugs dans locations-fr.json et services-fr.json

        Returns:
            bool: True si validation OK, False si erreurs détectées
        """
        errors = []
        warnings = []

        # Charger les URLs depuis variables.json
        urls_communes = self.variables.get('urls', {}).get('communes', {})
        urls_services = self.variables.get('urls', {}).get('services', {})

        if not urls_communes or not urls_services:
            self.log("⚠️  Section 'urls' manquante dans config/variables.json")
            return True  # Pas d'erreur bloquante si section absente

        # Charger les slugs depuis les fichiers sources
        locations_data = self.loader.load_communes(active_only=True)
        services_data = self.loader.load_services()

        # Créer des maps nom→slug depuis les sources
        location_slugs = {loc['name'].upper().replace('-', '_').replace(' ', '_').replace("'", '_'): loc['slug']
                         for loc in locations_data}
        service_slugs = {svc['slug']: svc['slug'] for svc in services_data}

        # Valider les communes
        for commune_name, url_slug in urls_communes.items():
            if commune_name in location_slugs:
                source_slug = location_slugs[commune_name]
                if url_slug != source_slug:
                    errors.append(
                        f"❌ ERREUR Commune '{commune_name}':\n"
                        f"   - variables.json: '{url_slug}'\n"
                        f"   - locations-fr.json: '{source_slug}'\n"
                        f"   → Corrigez config/variables.json ligne 'urls.communes.{commune_name}'"
                    )

        # Valider les services
        for service_name, url_slug in urls_services.items():
            if url_slug not in service_slugs:
                warnings.append(
                    f"⚠️  Service '{service_name}' URL '{url_slug}' introuvable dans services-fr.json"
                )

        # Afficher les résultats
        if errors:
            self.log("\n" + "="*60)
            self.log("❌ VALIDATION URLs ÉCHOUÉE - INCOHÉRENCES DÉTECTÉES")
            self.log("="*60)
            for error in errors:
                self.log(error)
            self.log("="*60 + "\n")
            return False

        if warnings:
            self.log("\n⚠️  Avertissements validation URLs:")
            for warning in warnings:
                self.log(warning)

        self.log(f"✅ Validation URLs: {len(urls_communes)} communes + {len(urls_services)} services OK")
        return True

    def inject_template_variables(self, variables):
        """
        Injecte toutes les template_variables dans le dictionnaire de variables d'une page

        Args:
            variables (dict): Dictionnaire de variables existant

        Returns:
            dict: Dictionnaire enrichi avec toutes les template_variables
        """
        template_variables = self.variables.get('template_variables', {})

        # Pour chaque mapping de variable dans template_variables
        for var_name, var_path in template_variables.items():
            # Ne pas écraser si la variable existe déjà
            if var_name not in variables:
                # Résoudre le chemin en dot-notation
                resolved_value = self.resolve_variable_path(var_path, self.variables)
                variables[var_name] = resolved_value

        return variables

    def resolve_variable_path(self, path, data):
        """
        Résout un chemin en dot-notation dans un dictionnaire

        Args:
            path (str): Chemin en dot-notation (ex: "pricing.remorquage.voiture_courte_distance.display")
            data (dict): Dictionnaire source

        Returns:
            str: Valeur résolue ou chaîne vide
        """
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return ''

        return str(value) if value is not None else ''

    def ensure_build_dir(self):
        """Crée le dossier /build/ s'il n'existe pas"""
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.log(f"📁 Dossier build: {self.build_dir}")

    def build_service_page(self, service_data):
        """Wrapper vers page_builder.build_service_page() - Refactoring #6"""
        return page_builder.build_service_page(self, service_data)

    def build_commune_services_cards(self, limit=6, commune_id=1, path_prefix='../'):
        """Wrapper vers grid_builder.build_commune_services_cards() - Refactoring #6"""
        return grid_builder.build_commune_services_cards(self, limit, commune_id, path_prefix)

    def build_commune_why_cards(self):
        """Wrapper vers grid_builder.build_commune_why_cards() - Refactoring #6"""
        return grid_builder.build_commune_why_cards(self)

    def build_communes_voisines_tags(self, commune_slug, limit=5, path_prefix='../'):
        """Wrapper vers grid_builder.build_communes_voisines_tags() - Refactoring #6"""
        return grid_builder.build_communes_voisines_tags(self, commune_slug, limit, path_prefix)

    def build_commune_page(self, commune_data):
        """Wrapper vers page_builder.build_commune_page() - Refactoring #6"""
        return page_builder.build_commune_page(self, commune_data)

    def get_hero_variables(self, homepage_ui):
        """
        Génère les variables pour Hero V2 à partir des données UI

        Args:
            homepage_ui (dict): Variables UI homepage

        Returns:
            dict: Variables Hero V2 pour le template
        """
        hero_data = homepage_ui.get('hero', {})

        variables = {
            'HERO_H1': hero_data.get('h1', ''),
            'HERO_H2': hero_data.get('h2', ''),
            'HERO_H2_CTA': hero_data.get('h2_cta', ''),
            'HERO_CTA_TEXT': hero_data.get('cta_text', 'Appelez maintenant'),
            'HERO_CTA_PHONE': hero_data.get('cta_phone', '0479 89 00 89'),
            'HERO_CTA_PHONE_BADGE': hero_data.get('cta_phone_badge', 'URGENCE'),
            'HERO_CTA_WHATSAPP': hero_data.get('cta_whatsapp', 'Devis WhatsApp'),
            'HERO_CTA_WHATSAPP_BADGE': hero_data.get('cta_whatsapp_badge', 'RAPIDE'),
            'HERO_DISPONIBLE': hero_data.get('disponible', 'Disponible maintenant'),
            'HERO_DEVIS': hero_data.get('devis', 'Devis gratuit'),
            'HERO_BADGE_DISPONIBILITE': hero_data.get('badge_disponibilite', ''),
        }

        # Générer le carrousel hero principal - Scanner automatiquement les images
        hero_images_folder = self.base_path / 'images' / 'homepage' / 'hero'
        all_hero_images = []
        processed_stems = set()  # Pour éviter les doublons .jpg/.webp

        if hero_images_folder.exists():
            # Scanner tous les fichiers image dans le dossier
            for img_file in sorted(hero_images_folder.glob('*')):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp'] and not img_file.name.startswith('.'):
                    # Éviter les doublons si .jpg et .webp existent
                    if img_file.stem not in processed_stems:
                        processed_stems.add(img_file.stem)

                        # Utiliser l'extension réelle du fichier
                        real_filename = img_file.name

                        # Récupérer le alt depuis images-alt.json ou utiliser un fallback
                        alt_text = self.images_alt.get('homepage', {}).get('hero', {}).get(img_file.stem)
                        if not alt_text:
                            alt_text = f"Service de dépannage automobile à Bruxelles 24h/24"

                        all_hero_images.append({
                            "image": real_filename,
                            "alt": alt_text
                        })

        # Fallback si aucune image trouvée
        if not all_hero_images:
            all_hero_images = [
                {"image": "remorquage.webp", "alt": "Service de remorquage voiture Bruxelles"}
            ]

        # Générer le HTML du carrousel principal
        carousel_html = self._build_hero_carousel_main(all_hero_images)
        variables['HERO_CAROUSEL_MAIN'] = carousel_html

        return variables

    def _build_hero_carousel_main(self, images_data):
        """
        Construit le HTML du carrousel hero principal (un seul grand carrousel)
        Les dots sont générés automatiquement par carousel.js

        Args:
            images_data (list): Liste des images [{image: 'xxx.webp', alt: 'xxx'}]

        Returns:
            str: HTML des images du carrousel
        """
        if not images_data or len(images_data) == 0:
            return ''

        carousel_parts = []

        # Générer chaque image avec data-carousel-item
        for idx, img_data in enumerate(images_data):
            image_filename = img_data.get('image', '')
            image_alt = img_data.get('alt', '')
            loading = 'eager' if idx == 0 else 'lazy'
            fetchpriority_attr = 'fetchpriority="high"' if idx == 0 else ''

            # DIMENSIONS FIXES COHÉRENTES pour éviter CLS
            # Toutes les images hero DOIVENT avoir les MÊMES dimensions (ratio 4:3)
            # Le conteneur a aspect-ratio:4/3, les images doivent avoir width/height cohérents
            # Utiliser 800x600 pour toutes (ratio 4:3 parfait)
            dims_attrs = 'width="800" height="600"'

            # HTML de l'image (avec data-carousel-item pour carousel.js)
            carousel_parts.append(
                f'<img src="images/homepage/hero/{image_filename}" '
                f'alt="{image_alt}" '
                f'{dims_attrs} '
                f'class="hero-carousel-image" '
                f'data-carousel-item '
                f'loading="{loading}" '
                f'{fetchpriority_attr}>'
            )

        return '\n        '.join(carousel_parts)

    def _build_simple_carousel(self, images_data, image_folder, path_prefix='../'):
        """
        Construit un carrousel simple réutilisable pour toutes les pages

        Args:
            images_data (list): Liste des images [{image: 'xxx.webp', alt: 'xxx'}]
            image_folder (str): Nom du dossier d'images (zones, tarif, contact)
            path_prefix (str): Préfixe de chemin ('../' pour sous-répertoires, '' pour racine)

        Returns:
            str: HTML du carrousel complet
        """
        if not images_data or len(images_data) == 0:
            # Retourner image par défaut si pas de carousel
            return f'<img src="{path_prefix}images/hero/{image_folder}.webp" alt="Image" loading="eager">'

        carousel_parts = []

        # Générer chaque image avec data-carousel-item
        # Les dots sont générés automatiquement par carousel.js
        for idx, img_data in enumerate(images_data):
            image_filename = img_data.get('image', '')
            image_alt = img_data.get('alt', '')
            loading = 'eager' if idx == 0 else 'lazy'
            fetchpriority_attr = 'fetchpriority="high"' if idx == 0 else ''

            # Récupérer les dimensions
            dims_attrs = self.get_image_dimensions_attrs(f'{image_folder}/{image_filename}')

            # HTML de l'image (avec data-carousel-item pour carousel.js)
            carousel_parts.append(
                f'<img src="{path_prefix}images/{image_folder}/{image_filename}" '
                f'alt="{image_alt}" '
                f'{dims_attrs} '
                f'class="hero-carousel-image" '
                f'data-carousel-item '
                f'loading="{loading}" '
                f'{fetchpriority_attr}>'
            )

        carousel_images_html = '\n          '.join(carousel_parts)

        # Construire le HTML complet du carousel (Version 2.0 avec attributs data-*)
        carousel_html = f'''<div class="hero-carousel-simple">
  <div class="hero-carousel-simple-main" data-carousel data-autoplay="5000" data-loop="true" data-pause-on-hover="true">
    <div class="hero-carousel-track" data-carousel-track>
      {carousel_images_html}
    </div>

    <!-- Contrôles carrousel -->
    <button class="hero-carousel-prev" data-carousel-prev aria-label="Image précédente">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </button>
    <button class="hero-carousel-next" data-carousel-next aria-label="Image suivante">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 18 15 12 9 6"></polyline>
      </svg>
    </button>

    <!-- Dots navigation (générés automatiquement par carousel.js) -->
    <div class="hero-carousel-dots" data-carousel-dots></div>
  </div>
</div>'''

        return carousel_html

    def build_homepage(self):
        """Wrapper vers page_builder.build_homepage() - Refactoring #6"""
        return page_builder.build_homepage(self)

    def build_comment_ca_marche_section(self, homepage_ui):
        """Construit les étapes de Comment ça marche (v4.2 - Jinja2)"""
        section_comment = homepage_ui.get('section_comment_ca_marche', {})
        etapes = section_comment.get('etapes', [])

        return self.renderer.render_jinja2('components/etapes-items.html', {
            'etapes': etapes
        })

    def build_reviews_carousel(self, section_avis, variables):
        """Génère le carousel d'avis depuis les données JSON (v4.2 - Jinja2)"""
        avis_list = section_avis.get('avis', [])
        aria_labels = section_avis.get('aria_labels', {})

        return self.renderer.render_jinja2('components/reviews-carousel.html', {
            'avis_list': avis_list,
            'aria_prev': aria_labels.get('btn_prev', 'Avis précédent'),
            'aria_next': aria_labels.get('btn_next', 'Avis suivant'),
            'aria_dot_prefix': aria_labels.get('dot_prefix', 'Aller à l\'avis')
        })

    def build_faq_items(self, section_faq, variables):
        """Génère les items FAQ depuis les données JSON (v4.2 - Jinja2)"""
        questions = section_faq.get('questions', [])

        return self.renderer.render_jinja2('components/faq-items.html', {
            'questions': questions,
            'variables': variables
        })

    def build_zones_tags(self, limit=12, path_prefix=''):
        """Wrapper vers grid_builder.build_zones_tags() - Refactoring #6"""
        return grid_builder.build_zones_tags(self, limit, path_prefix)

    def build_communes_grid(self, path_prefix='../'):
        """Wrapper vers grid_builder.build_communes_grid() - Refactoring #6"""
        return grid_builder.build_communes_grid(self, path_prefix)

    def build_footer_communes_links(self, limit=6, path_prefix=''):
        """Wrapper vers grid_builder.build_footer_communes_links() - Refactoring #6"""
        return grid_builder.build_footer_communes_links(self, limit, path_prefix)

    def add_footer_variables(self, variables):
        """
        Ajoute les variables dynamiques du footer (communes + services + nombre + traductions UI)

        Args:
            variables (dict): Dictionnaire des variables à enrichir

        Returns:
            dict: Variables enrichies
        """
        communes = self.loader.load_communes()
        services = self.loader.load_services()
        path_prefix = variables.get('PATH_PREFIX', '')

        # Variables dynamiques footer
        variables['FOOTER_COMMUNES'] = self.build_footer_communes_links(6, path_prefix)
        variables['NOMBRE_COMMUNES'] = len(communes)
        variables['NOMBRE_SERVICES'] = len(services)
        variables['COMPANY_NAME'] = self.variables.get('company', {}).get('name_full', 'Bruxelles Car Depannage srl')
        variables['GOOGLE_REVIEWS'] = self.variables.get('google', {}).get('reviews_count', '200')
        variables['GOOGLE_RATING'] = self.variables.get('google', {}).get('rating', '4.9')
        variables['GOOGLE_MY_BUSINESS_URL'] = self.variables.get('google', {}).get('my_business_url', '#')
        variables['GOOGLE_ANALYTICS_ID'] = self.variables.get('google', {}).get('analytics_id', '')
        variables['FACEBOOK_URL'] = self.variables.get('social', {}).get('facebook_url', '#')
        variables['INSTAGRAM_URL'] = self.variables.get('social', {}).get('instagram_url', '#')

        # URLs des pages légales et zones (dynamiques selon langue)
        pages_slugs = {
            'about': {'fr': 'a-propos', 'en': 'about-us', 'nl': 'over-ons'},
            'legal': {'fr': 'mentions-legales', 'en': 'legal-notice', 'nl': 'juridische-kennisgeving'},
            'privacy': {'fr': 'politique-confidentialite', 'en': 'privacy-policy', 'nl': 'privacybeleid'},
            'zones': {'fr': 'zones', 'en': 'areas', 'nl': 'zones'}
        }
        lang = self.lang if self.lang in ['fr', 'en', 'nl'] else 'fr'
        variables['URL_ABOUT'] = pages_slugs['about'][lang]
        variables['URL_LEGAL'] = pages_slugs['legal'][lang]
        variables['URL_PRIVACY'] = pages_slugs['privacy'][lang]
        variables['URL_ZONES'] = pages_slugs['zones'][lang]

        # Traductions footer depuis ui.json
        footer_ui = self.ui_translations.get('footer', {})
        variables['FOOTER_DESCRIPTION'] = footer_ui.get('description', '')
        variables['FOOTER_SOCIAL_TITLE'] = footer_ui.get('social_title', 'Restons connectés')
        variables['FOOTER_SERVICES_TITLE'] = footer_ui.get('services_title', 'Nos Services')
        variables['FOOTER_SERVICES_ALL'] = footer_ui.get('services_all', 'Tous les services')
        variables['FOOTER_INFO_TITLE'] = footer_ui.get('info_title', 'Informations')
        variables['FOOTER_INFO_ABOUT'] = footer_ui.get('info_about', 'À propos de nous')
        variables['FOOTER_INFO_LEGAL'] = footer_ui.get('info_legal', 'Mentions Légales')
        variables['FOOTER_INFO_PRIVACY'] = footer_ui.get('info_privacy', 'Confidentialité')
        variables['FOOTER_ZONES_TITLE'] = footer_ui.get('zones_title', 'Zones d\'Intervention')
        variables['FOOTER_ZONES_ALL'] = footer_ui.get('zones_all', 'Voir toutes les communes')
        variables['FOOTER_REVIEWS_TITLE'] = footer_ui.get('reviews_title', 'Votre Avis Compte')
        variables['FOOTER_REVIEWS_DESCRIPTION'] = footer_ui.get('reviews_description', '')
        variables['FOOTER_REVIEWS_COUNT'] = footer_ui.get('reviews_count', 'avis clients')
        variables['FOOTER_COPYRIGHT'] = footer_ui.get('copyright', 'Tous droits réservés')
        variables['FOOTER_TAGLINE'] = footer_ui.get('tagline', 'Dépannage automobile professionnel 24h/24')

        return variables

    def build_sidebar_services_for_commune(self, commune_id, limit=6):
        """
        Construit les liens services pour sidebar commune avec rotation basée sur l'ID commune

        Args:
            commune_id (int): ID de la commune (pour rotation circulaire)
            limit (int): Nombre de services à afficher

        Returns:
            str: HTML des liens services
        """
        services = self.loader.load_services()

        # Trier par priorité
        services_sorted = sorted(services, key=lambda x: x.get('priority', 999))

        # Rotation circulaire avec multiplicateur premier (5) pour meilleure distribution
        start_index = ((commune_id - 1) * 5) % len(services_sorted)

        selected_services = []
        for i in range(limit):
            service_index = (start_index + i) % len(services_sorted)
            selected_services.append(services_sorted[service_index])

        links = []
        for service in selected_services:
            links.append({
                'text': service['name'],
                'url': f"../{service['slug']}/index.html"
            })

        return self.renderer.build_sidebar_links(links)

    def format_phone_number(self, phone):
        """
        Formate un numéro de téléphone avec des espaces
        Ex: "0479890089" -> "0479 89 00 89"

        Args:
            phone (str): Numéro de téléphone brut

        Returns:
            str: Numéro formaté avec espaces
        """
        # Enlever tous les espaces et caractères non-numériques
        phone_clean = ''.join(filter(str.isdigit, str(phone)))

        # Format belge: 0XXX XX XX XX (10 chiffres)
        if len(phone_clean) == 10 and phone_clean.startswith('0'):
            return f"{phone_clean[0:4]} {phone_clean[4:6]} {phone_clean[6:8]} {phone_clean[8:10]}"

        # Format international: +32 XXX XX XX XX (9 chiffres après +32)
        elif len(phone_clean) == 11 and phone_clean.startswith('32'):
            return f"+{phone_clean[0:2]} {phone_clean[2:5]} {phone_clean[5:7]} {phone_clean[7:9]} {phone_clean[9:11]}"

        # Retourner le numéro tel quel si format non reconnu
        return phone

    def build_sidebar_services_links(self, limit=6, current_service_id=None, current_category=None):
        """
        Construit les liens services pour la sidebar (v4.1 - utilise SidebarBuilder)

        Args:
            limit (int): Nombre de services à afficher
            current_service_id (int): ID du service actuel (à exclure)
            current_category (str): Catégorie du service actuel

        Returns:
            str: HTML des liens
        """
        return self.sidebar_builder.build_sidebar_services_links(limit, current_service_id, current_category, self.renderer)

    def build_zones_intervention_9_communes(self, current_service_id=1, path_prefix='../'):
        """Wrapper vers grid_builder.build_zones_intervention_9_communes() - Refactoring #6"""
        return grid_builder.build_zones_intervention_9_communes(self, current_service_id, path_prefix)

    def build_sidebar_communes_links(self, limit=5, current_service_id=None):
        """
        Construit les liens communes pour sidebar (v4.1 - utilise SidebarBuilder)

        Args:
            limit (int): Nombre de communes à afficher
            current_service_id (int): ID du service actuel (pour rotation)

        Returns:
            str: HTML des liens
        """
        return self.sidebar_builder.build_sidebar_communes_links(limit, current_service_id, self.renderer)

    def build_sidebar_voisines_links(self, commune_slug):
        """
        Construit les liens communes voisines (v4.1 - utilise SidebarBuilder)

        Args:
            commune_slug (str): Slug de la commune actuelle

        Returns:
            str: HTML des liens voisines
        """
        return self.sidebar_builder.build_sidebar_voisines_links(commune_slug, self.renderer)

    def build_services_grid(self, services, path_prefix=''):
        """Wrapper vers grid_builder.build_services_grid() - Refactoring #6"""
        return grid_builder.build_services_grid(self, services, path_prefix)

    def save_page(self, html, filename):
        """
        Sauvegarde une page HTML dans /build/

        Args:
            html (str): Contenu HTML
            filename (str): Nom du fichier (ex: 'depannage-batterie-bruxelles.html')
        """
        filepath = self.build_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    def generate_all_services(self):
        """Génère toutes les pages services (22 pages)"""
        self.log("\n🔧 === GÉNÉRATION PAGES SERVICES ===")
        services = self.loader.load_services()

        for service in services:
            html = self.build_service_page(service)
            self.save_page(html, f"{service['slug']}/index.html")

        self.log(f"✅ {len(services)} pages services générées")

    def generate_all_communes(self):
        """Génère toutes les pages communes"""
        self.log("\n📍 === GÉNÉRATION PAGES COMMUNES ===")
        communes = self.loader.load_communes()

        for commune in communes:
            html = self.build_commune_page(commune)
            self.save_page(html, f"{commune['slug']}/index.html")

        self.log(f"✅ {len(communes)} pages communes générées")

    def generate_homepage(self):
        """Génère la homepage"""
        html = self.build_homepage()
        self.save_page(html, 'index.html')
        self.log("✅ Homepage générée")

    def generate_zones_index(self):
        """Génère la page index des zones"""
        self.log("\n🗺️  === GÉNÉRATION PAGE ZONES INDEX ===")

        # Charger le contenu depuis JSON
        filename = self._get_page_content_filename('zones-index')
        content_path = self.base_path / 'content' / self.lang / 'pages' / filename
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except FileNotFoundError:
            self.log(f"⚠️  Fichier zones-index.json introuvable: {content_path}")
            content = {}

        # Récupération des données depuis variables.json
        domain = self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

        # Variables de base
        variables = {
            'PATH_PREFIX': self._get_path_prefix('subpage'),  # Dynamique selon langue
            'CANONICAL_URL': f"{domain}/zones/",
            'TELEPHONE': self.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
            'TELEPHONE_HREF': self.variables.get('contact', {}).get('phone_local', '0479890089'),
            'GOOGLE_RATING': self.variables.get('google', {}).get('rating', '4.9'),
            'GOOGLE_REVIEWS': self.variables.get('google', {}).get('reviews_count', '190'),
            'GOOGLE_MY_BUSINESS_URL': self.variables.get('google', {}).get('my_business_url', '#'),
            'YEARS_EXPERIENCE_PLUS': self.variables.get('company', {}).get('years_experience_plus', '+10'),
            'NOMBRE_COMMUNES': self.variables.get('stats', {}).get('nombre_communes', '35'),
        }

        # Meta tags
        variables['META_TITLE'] = content.get('meta_title', 'Zones d\'Intervention Dépannage Bruxelles')
        variables['META_DESCRIPTION'] = content.get('meta_description', '')

        # Open Graph (avec remplacement {{NOMBRE_COMMUNES}})
        og = content.get('open_graph', {})
        og_title = og.get('title', variables['META_TITLE'])
        variables['OG_TITLE'] = og_title.replace('{{NOMBRE_COMMUNES}}', variables['NOMBRE_COMMUNES'])
        variables['OG_DESCRIPTION'] = og.get('description', variables['META_DESCRIPTION'])
        # Carrousel Open Graph (2 images)
        variables['OG_IMAGE_1'] = f"{domain}/images/og/helpcar-depannage-bruxelles.jpg"
        variables['OG_IMAGE_2'] = f"{domain}/images/og/helpcar-depannage-bruxelles.jpg"

        # Hero
        hero = content.get('hero', {})
        variables['HERO_H1'] = hero.get('h1', 'Zones d\'Intervention')
        variables['HERO_H2'] = hero.get('h2', 'Intervention rapide 24h/24')
        variables['HERO_IMAGE_ALT'] = hero.get('image_alt', 'Zones d\'intervention')

        # WhatsApp button text
        cta_translations = self.ui_translations.get('cta', {})
        variables['HERO_WHATSAPP_TEXT'] = cta_translations.get('devis_whatsapp', 'Devis WhatsApp')

        # Carousel zones - Scanner automatiquement les images
        zones_images_folder = self.base_path / 'images' / 'zones-index'
        zones_images = []
        processed_zones_stems = set()

        if zones_images_folder.exists():
            for img_file in sorted(zones_images_folder.glob('*')):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp'] and not img_file.name.startswith('.') and img_file.name != 'README.md':
                    # Éviter les doublons .jpg/.webp
                    if img_file.stem not in processed_zones_stems:
                        processed_zones_stems.add(img_file.stem)

                        # Récupérer le alt depuis images-alt.json ou utiliser un fallback
                        alt_text = self.images_alt.get('zones-index', {}).get('hero', {}).get(img_file.stem)
                        if not alt_text:
                            # Fallback si pas trouvé
                            alt_text = self.images_alt.get('zones-index', {}).get('hero', {}).get('default', 'Zones d\'intervention de Bruxelles Car Depannage')

                        # Utiliser l'extension réelle du fichier
                        zones_images.append({
                            "image": img_file.name,
                            "alt": alt_text
                        })
        variables['ZONES_CAROUSEL'] = self._build_simple_carousel(zones_images, 'zones-index', '../')

        # Section couverture
        couverture = content.get('section_couverture', {})
        variables['COUVERTURE_LABEL'] = couverture.get('section_label', 'Couverture complète')
        variables['COUVERTURE_TITLE'] = couverture.get('section_title', 'Toute la région couverte')

        # Générer paragraphes couverture avec remplacement variables
        paragraphes_html = ''
        for p in couverture.get('paragraphes', []):
            p = p.replace('{{YEARS_EXPERIENCE_PLUS}}', variables['YEARS_EXPERIENCE_PLUS'])
            p = p.replace('{{GOOGLE_RATING}}', variables['GOOGLE_RATING'])
            p = p.replace('{{GOOGLE_REVIEWS}}', variables['GOOGLE_REVIEWS'])
            margin = 'margin-bottom: 1.5rem;' if p != couverture.get('paragraphes', [])[-1] else 'margin-bottom: 2rem;'
            paragraphes_html += f'<p style="{margin} font-size: 1.1rem; line-height: 1.7;">{p}</p>\n'
        variables['COUVERTURE_PARAGRAPHES'] = paragraphes_html

        # Section services
        services = content.get('section_services', {})
        variables['SERVICES_LABEL'] = services.get('section_label', 'Partout dans la région')
        variables['SERVICES_TITLE'] = services.get('section_title', 'Tous nos services')
        variables['SERVICES_DESCRIPTION'] = services.get('section_description', '')
        variables['SERVICES_CTA'] = services.get('cta_text', 'Voir tous nos services →')

        # Générer cartes services
        services_html = ''
        path_prefix = variables['PATH_PREFIX']  # Définir path_prefix depuis variables
        for service in services.get('services', []):
            nom = service.get('nom', '')
            description = service.get('description', '')
            icon = service.get('icon', 'default.png')

            # Résoudre url_var depuis variables.json (v5.2.0+)
            url_var = service.get('url_var', '')
            if url_var:
                # Résoudre la variable URL depuis template_variables
                slug = self.resolve_variable_path(
                    self.variables.get('template_variables', {}).get(url_var, ''),
                    self.variables
                )
            else:
                # Fallback : ancien système avec slug
                slug = service.get('slug', '')

            # Construire l'URL (relative si url_var, sinon slug brut)
            if url_var and slug:
                service_url = f'{path_prefix}{slug}/index.html'
            elif slug:
                service_url = slug
            else:
                service_url = '#'

            icon_svg = get_service_icon(slug)
            services_html += f'''<a href="{service_url}" class="service-card" style="display: flex; align-items: flex-start; gap: 1rem; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-decoration: none; transition: transform 0.3s, box-shadow 0.3s;">
            <div style="width: 48px; height: 48px; background: rgba(249, 115, 22, 0.08); border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              {icon_svg}
            </div>
            <div style="text-align: left;">
              <h3 style="margin: 0 0 0.5rem 0; color: #1E3A8A; font-size: 1.1rem; font-weight: 700;">{nom}</h3>
              <p style="margin: 0; color: #666; font-size: 0.95rem; line-height: 1.5;">{description}</p>
            </div>
          </a>
          '''
        variables['SERVICES_CARDS'] = services_html

        # Section communes
        communes = content.get('section_communes', {})
        communes_label = communes.get('section_label', '{{NOMBRE_COMMUNES}} communes')
        variables['COMMUNES_LABEL'] = communes_label.replace('{{NOMBRE_COMMUNES}}', variables['NOMBRE_COMMUNES'])
        variables['COMMUNES_TITLE'] = communes.get('section_title', 'Liste complète des zones')
        variables['COMMUNES_DESCRIPTION'] = communes.get('section_description', '')
        variables['COMMUNES_CARDS'] = self.build_communes_grid(path_prefix)

        # Section axes routiers
        axes = content.get('section_axes_routiers', {})
        variables['AXES_LABEL'] = axes.get('section_label', 'Partout sur la route')
        variables['AXES_TITLE'] = axes.get('section_title', 'Grands axes routiers')

        # Générer liste axes
        axes_html = ''
        for axe in axes.get('axes', []):
            emoji = axe.get('emoji', '🛣️')
            nom = axe.get('nom', '')
            description = axe.get('description', '')
            axes_html += f'''<li style="padding-left: 2rem; position: relative;">
              <span style="position: absolute; left: 0; color: #1E3A8A; font-size: 1.2rem;">{emoji}</span>
              <strong>{nom}</strong> – {description}
            </li>
            '''
        variables['AXES_LISTE'] = axes_html

        # Note autoroute avec remplacement {{TELEPHONE}}
        note = axes.get('note_autoroute', '')
        variables['AXES_NOTE'] = note.replace('{{TELEPHONE}}', variables['TELEPHONE'])

        # Section pourquoi nous
        pourquoi = content.get('section_pourquoi_nous', {})
        variables['POURQUOI_LABEL'] = pourquoi.get('section_label', 'Notre engagement')
        variables['POURQUOI_TITLE'] = pourquoi.get('section_title', 'Pourquoi nous choisir ?')

        # Générer liste avantages
        avantages_html = ''
        for idx, avantage in enumerate(pourquoi.get('avantages', [])):
            texte = avantage.get('texte', '')
            texte = texte.replace('{{GOOGLE_RATING}}', variables['GOOGLE_RATING'])
            texte = texte.replace('{{GOOGLE_REVIEWS}}', variables['GOOGLE_REVIEWS'])
            with_star = avantage.get('with_star', False)
            with_link = avantage.get('with_link', False)
            margin = 'margin-bottom: 1rem;' if idx < len(pourquoi.get('avantages', [])) - 1 else 'margin-bottom: 0;'

            if with_star and with_link:
                # Texte selon langue
                most_recommended_text = "– The most recommended in Brussels" if self.lang == 'en' else "– Le plus recommandé de Bruxelles"
                avantages_html += f'''<li style="{margin}">
              <span style="color: #10B981; font-weight: bold; font-size: 1.2rem; margin-right: 0.5rem;">✓</span>
              <svg class="star-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#FFC107" style="vertical-align: middle; margin-right: 4px;"><path d="M12 .587l3.668 7.568 8.332 1.151-6.064 5.828 1.48 8.279-7.416-3.967-7.417 3.967 1.481-8.279-6.064-5.828 8.332-1.151z"/></svg>
              <a href="{variables['GOOGLE_MY_BUSINESS_URL']}" target="_blank" rel="noopener noreferrer" style="color: #F97316; font-weight: 600; text-decoration: none;">{texte}</a> {most_recommended_text}
            </li>
            '''
            else:
                avantages_html += f'''<li style="{margin}">
              <span style="color: #10B981; font-weight: bold; font-size: 1.2rem; margin-right: 0.5rem;">✓</span>
              {texte}
            </li>
            '''
        variables['POURQUOI_AVANTAGES'] = avantages_html

        # FAQ
        faq = content.get('faq', {})
        variables['FAQ_LABEL'] = faq.get('section_label', 'FAQ')
        variables['FAQ_TITLE'] = faq.get('section_title', 'Questions Fréquentes')

        # Générer items FAQ
        faq_html = ''
        for q in faq.get('questions', []):
            question = q.get('question', '')
            reponse = q.get('reponse', '')
            reponse = reponse.replace('{{TELEPHONE}}', variables['TELEPHONE'])
            faq_html += f'''<div class="faq-item">
            <h3 class="faq-question">{question}</h3>
            <div class="faq-answer">
              <p>{reponse}</p>
            </div>
          </div>

          '''
        variables['FAQ_ITEMS'] = faq_html

        # CTA Final
        cta = content.get('cta_final', {})
        variables['CTA_FINAL_TITRE'] = cta.get('titre', 'En panne dans votre commune ?')
        variables['CTA_FINAL_SUBTITLE'] = cta.get('subtitle', '')
        variables['CTA_FINAL_BUTTON'] = cta.get('button', 'Appeler maintenant')

        # Schema.org
        homepage_schema = self.schema_builder.build_homepage_schema()
        variables['SCHEMA_ORG_LOCALBUSINESS'] = self.schema_builder.to_json_ld(homepage_schema)

        # Footer et Breadcrumb
        self.add_footer_variables(variables)
        variables['BREADCRUMB_ITEMS'] = self.build_breadcrumb_items('zones-index', '', variables['PATH_PREFIX'])

        # Injecter toutes les template_variables (URLs, pricing, etc.)
        variables = self.inject_template_variables(variables)

        # Aria labels
        aria_labels = self.ui_translations.get('aria_labels', {})
        variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

        # MULTILINGUAL: Ajouter variables de langue et hreflang
        variables.update(self._get_language_variables("subpage"))
        hreflang_vars = self._generate_hreflang_urls('zones-index')
        variables.update(hreflang_vars)

        # Rendre le composant hreflang
        hreflang_html = self.renderer.render('components/hreflang.html', hreflang_vars)
        variables['COMPONENT_HREFLANG'] = hreflang_html

        # Rendu
        html = self.renderer.render_with_components('pages/zones-index.html', variables)
        save_path = self._get_page_save_path('zones')
        self.save_page(html, save_path)
        self.log("✅ Page zones index générée")

    def build_services_cards_compact(self, services, path_prefix='../'):
        """Wrapper vers grid_builder.build_services_cards_compact() - Refactoring #6"""
        return grid_builder.build_services_cards_compact(self, services, path_prefix)

    def build_breadcrumb_items(self, breadcrumb_type, name='', path_prefix='../'):
        """
        Génère les items du breadcrumb (v4.1 - utilise BreadcrumbBuilder)

        Args:
            breadcrumb_type (str): Type de breadcrumb ('service', 'commune', 'contact', etc.)
            name (str): Nom de la page actuelle (optionnel)
            path_prefix (str): Préfixe de chemin pour les liens

        Returns:
            str: HTML des items du breadcrumb
        """
        return self.breadcrumb_builder.build_breadcrumb_items(breadcrumb_type, name, path_prefix)

    def generate_services_index(self):
        """Génère la page index des services avec nouveau design V4"""
        self.log("\n🔧 === GÉNÉRATION PAGE SERVICES INDEX ===")

        # Récupération des données depuis variables.json
        domain = self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

        # Charger le contenu de la page depuis JSON
        content_path = self.base_path / 'content' / self.lang / 'pages' / 'services-index.json'

        if content_path.exists():
            with open(content_path, 'r', encoding='utf-8') as f:
                page_content = json.load(f)
        else:
            # Contenu par défaut si le fichier n'existe pas
            page_content = {
                'hero': {'title': 'Nos Services', 'subtitle': '{{SERVICES_TOTAL}} services disponibles'},
                'section': {'label': 'Nos Services', 'title': 'Services', 'description': ''},
                'categories': {},
                'toggle': {},
                'cta': {'title': 'Besoin d\'aide ?', 'subtitle': 'Contactez-nous'}
            }

        # Charger tous les services
        all_services = self.loader.load_services()

        # Séparer par catégorie (selon la langue)
        if self.lang == 'en':
            category_towing = 'Towing'
            category_breakdown = 'Breakdown'
        else:  # FR par défaut
            category_towing = 'Remorquage'
            category_breakdown = 'Dépannage'

        services_remorquage = [s for s in all_services if s.get('category') == category_towing]
        services_depannage = [s for s in all_services if s.get('category') == category_breakdown]

        # Variables de base
        variables = {
            'LANG_CODE': 'en' if self.lang == 'en' else 'fr-BE',
            'PATH_PREFIX': self._get_path_prefix('subpage'),  # Dynamique selon langue
            'CANONICAL_URL': f"{domain}/services/",
            'TELEPHONE': self.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
            'TELEPHONE_HREF': self.variables.get('contact', {}).get('phone_local', '0479890089'),
            'GOOGLE_RATING': self.variables.get('google', {}).get('rating', '4.9'),
            'GOOGLE_REVIEWS': self.variables.get('google', {}).get('reviews_count', '190'),
            'GOOGLE_MY_BUSINESS_URL': self.variables.get('google', {}).get('my_business_url', '#'),
            'FACEBOOK_URL': self.variables.get('social', {}).get('facebook_url', '#'),
            'INSTAGRAM_URL': self.variables.get('social', {}).get('instagram_url', '#'),
            # Carrousel Open Graph (2 images)
            'OG_IMAGE_1': f"{domain}/images/og/helpcar-depannage-bruxelles.jpg",
            'OG_IMAGE_2': f"{domain}/images/og/helpcar-depannage-bruxelles.jpg",
            # Stats calculés dynamiquement (selon langue et catégories)
            'SERVICES_TOTAL': str(len(all_services)),
            'SERVICES_REMORQUAGE': str(len(services_remorquage)),
            'SERVICES_DEPANNAGE': str(len(services_depannage)),
            'LOCATIONS_TOTAL': str(self.variables.get('stats', {}).get('locations_total', 35)),
            'LOCATIONS_BRUXELLES': str(self.variables.get('stats', {}).get('locations_bruxelles', 19)),
            'LOCATIONS_PERIPHERIE': str(self.variables.get('stats', {}).get('locations_peripherie', 16)),
        }

        # Ajouter données SEO depuis JSON et remplacer les variables
        variables['META_TITLE'] = self.replace_variables_in_content(page_content.get('meta_title', 'Nos Services - Bruxelles Car Dépannage'), variables)
        variables['META_DESCRIPTION'] = self.replace_variables_in_content(page_content.get('meta_description', 'Découvrez nos services de dépannage'), variables)
        variables['OG_TITLE'] = self.replace_variables_in_content(page_content.get('og_title', 'Nos Services - Bruxelles Car Dépannage'), variables)
        variables['OG_DESCRIPTION'] = self.replace_variables_in_content(page_content.get('og_description', variables['META_DESCRIPTION']), variables)

        # Hero variables
        hero = page_content.get('hero', {})
        variables['HERO_H1'] = self.replace_variables_in_content(hero.get('h1', 'Nos Services'), variables)
        variables['HERO_SUBTITLE'] = self.replace_variables_in_content(hero.get('subtitle', 'Services de dépannage'), variables)

        # Categories variables
        categories = page_content.get('categories', {})

        remorquage = categories.get('remorquage', {})
        variables['CATEGORY_REMORQUAGE_NAME'] = self.replace_variables_in_content(remorquage.get('name', 'Remorquage'), variables)
        variables['CATEGORY_REMORQUAGE_COUNT'] = self.replace_variables_in_content(remorquage.get('count', f'{len(services_remorquage)} services'), variables)
        variables['CATEGORY_REMORQUAGE_TAGLINE'] = self.replace_variables_in_content(remorquage.get('tagline', ''), variables)
        variables['CATEGORY_REMORQUAGE_DESC'] = self.replace_variables_in_content(remorquage.get('description', ''), variables)
        variables['CATEGORY_REMORQUAGE_IMG_ALT'] = self.replace_variables_in_content(remorquage.get('image_alt', 'Service de Remorquage'), variables)
        variables['CATEGORY_REMORQUAGE_ARIA'] = self.replace_variables_in_content(remorquage.get('aria_label', 'Voir les services de remorquage'), variables)
        variables['CATEGORY_REMORQUAGE_CTA'] = self.replace_variables_in_content(remorquage.get('cta_text', 'Voir les services →'), variables)

        depannage = categories.get('depannage', {})
        variables['CATEGORY_DEPANNAGE_NAME'] = self.replace_variables_in_content(depannage.get('name', 'Dépannage'), variables)
        variables['CATEGORY_DEPANNAGE_COUNT'] = self.replace_variables_in_content(depannage.get('count', f'{len(services_depannage)} services'), variables)
        variables['CATEGORY_DEPANNAGE_TAGLINE'] = self.replace_variables_in_content(depannage.get('tagline', ''), variables)
        variables['CATEGORY_DEPANNAGE_DESC'] = self.replace_variables_in_content(depannage.get('description', ''), variables)
        variables['CATEGORY_DEPANNAGE_IMG_ALT'] = self.replace_variables_in_content(depannage.get('image_alt', 'Service de Dépannage'), variables)
        variables['CATEGORY_DEPANNAGE_ARIA'] = self.replace_variables_in_content(depannage.get('aria_label', 'Voir les services de dépannage'), variables)
        variables['CATEGORY_DEPANNAGE_CTA'] = self.replace_variables_in_content(depannage.get('cta_text', 'Voir les services →'), variables)

        # Intro section
        intro = page_content.get('intro', {})
        variables['INTRO_H2'] = self.replace_variables_in_content(intro.get('h2', 'Nos Services'), variables)
        intro_paras = intro.get('paragraphes', [])
        intro_html = ''
        for para in intro_paras:
            # Remplacer TOUTES les variables
            para_replaced = self.replace_variables_in_content(para, variables)
            intro_html += f'<p>{para_replaced}</p>\n        '
        variables['INTRO_PARAGRAPHES'] = intro_html.strip()

        # Toggle variables
        toggle = page_content.get('toggle', {})
        variables['TOGGLE_TOUS_LABEL'] = self.replace_variables_in_content(toggle.get('tous', {}).get('label', 'Tous les services'), variables)
        variables['TOGGLE_TOUS_COUNT'] = self.replace_variables_in_content(str(toggle.get('tous', {}).get('count', len(all_services))), variables)
        variables['TOGGLE_REMORQUAGE_LABEL'] = self.replace_variables_in_content(toggle.get('remorquage', {}).get('label', 'Remorquage'), variables)
        variables['TOGGLE_REMORQUAGE_COUNT'] = self.replace_variables_in_content(str(toggle.get('remorquage', {}).get('count', len(services_remorquage))), variables)
        variables['TOGGLE_DEPANNAGE_LABEL'] = self.replace_variables_in_content(toggle.get('depannage', {}).get('label', 'Dépannage'), variables)
        variables['TOGGLE_DEPANNAGE_COUNT'] = self.replace_variables_in_content(str(toggle.get('depannage', {}).get('count', len(services_depannage))), variables)

        # Services cards par catégorie
        variables['SERVICES_ALL_CARDS'] = self.build_services_cards_compact(all_services, variables['PATH_PREFIX'])
        variables['SERVICES_REMORQUAGE_CARDS'] = self.build_services_cards_compact(services_remorquage, variables['PATH_PREFIX'])
        variables['SERVICES_DEPANNAGE_CARDS'] = self.build_services_cards_compact(services_depannage, variables['PATH_PREFIX'])

        # Injecter toutes les template_variables (URLs, pricing, NOMBRE_COMMUNES, etc.) AVANT de construire les sections
        variables = self.inject_template_variables(variables)

        # Section "Pourquoi nous choisir"
        pourquoi = page_content.get('pourquoi', {})
        variables['POURQUOI_H2'] = self.replace_variables_in_content(pourquoi.get('h2', 'Pourquoi nous choisir ?'), variables)
        pourquoi_cards_html = ''
        for card in pourquoi.get('cards', []):
            icon = card.get('icon', '✓')
            titre = self.replace_variables_in_content(card.get('titre', ''), variables)
            description = self.replace_variables_in_content(card.get('description', ''), variables)
            pourquoi_cards_html += f'''
          <!-- Card -->
          <div class="why-us-card">
            <div class="why-us-icon">{icon}</div>
            <h3>{titre}</h3>
            <p>{description}</p>
          </div>
'''
        variables['POURQUOI_CARDS'] = pourquoi_cards_html.strip()

        # Section FAQ
        faq = page_content.get('faq', {})
        variables['FAQ_H2'] = self.replace_variables_in_content(faq.get('h2', 'Questions fréquentes'), variables)
        faq_items_html = ''
        for item in faq.get('items', []):
            question = self.replace_variables_in_content(item.get('question', ''), variables)
            answer = self.replace_variables_in_content(item.get('answer', ''), variables)
            faq_items_html += f'''
          <!-- FAQ Item -->
          <div class="faq-item">
            <h3 class="faq-question">{question}</h3>
            <div class="faq-answer">
              <p>{answer}</p>
            </div>
          </div>
'''
        variables['FAQ_ITEMS'] = faq_items_html.strip()

        # Section Zones
        zones = page_content.get('zones', {})
        variables['ZONES_H2'] = self.replace_variables_in_content(zones.get('h2', 'Nos zones d\'intervention'), variables)
        variables['ZONES_DESCRIPTION'] = self.replace_variables_in_content(zones.get('description', ''), variables)
        variables['ZONES_CTA_TEXT'] = self.replace_variables_in_content(zones.get('cta_text', 'Voir toutes nos zones'), variables)

        # CTA Final
        cta_final = page_content.get('cta_final', {})
        variables['CTA_TITLE'] = cta_final.get('titre', 'Besoin d\'aide ?')
        variables['CTA_SUBTITLE'] = cta_final.get('subtitle', 'Contactez-nous maintenant')

        # Schema.org
        homepage_schema = self.schema_builder.build_homepage_schema()
        variables['SCHEMA_ORG_LOCALBUSINESS'] = self.schema_builder.to_json_ld(homepage_schema)

        # Ajouter les variables du footer (communes dynamiques)
        self.add_footer_variables(variables)

        # Breadcrumb
        variables['BREADCRUMB_ITEMS'] = self.build_breadcrumb_items('services-index', '', variables['PATH_PREFIX'])

        # Aria labels
        aria_labels = self.ui_translations.get('aria_labels', {})
        variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

        # MULTILINGUAL: Ajouter variables de langue et hreflang
        variables.update(self._get_language_variables("subpage"))
        hreflang_vars = self._generate_hreflang_urls('services-index')
        variables.update(hreflang_vars)

        # Rendre le composant hreflang
        hreflang_html = self.renderer.render('components/hreflang.html', hreflang_vars)
        variables['COMPONENT_HREFLANG'] = hreflang_html

        # Rendu
        html = self.renderer.render_with_components('pages/services-index.html', variables)

        # Sauvegarder dans /services/index.html
        self.save_page(html, 'services/index.html')
        self.log(f"✅ Page services index générée ({len(all_services)} services : {len(services_remorquage)} remorquage + {len(services_depannage)} dépannage)")

    def copy_css_files(self):
        """Copie tous les fichiers CSS depuis public/css/ vers build/{lang}/public/css/"""
        source_css_dir = self.base_path / 'public' / 'css'
        dest_css_dir = self.build_dir / 'public' / 'css'

        # Créer le dossier de destination
        dest_css_dir.mkdir(parents=True, exist_ok=True)

        # Copier tous les fichiers CSS (variables.css est maintenant inline dans main.css)
        for css_file in self.CSS_FILES:
            source_file = source_css_dir / css_file
            if source_file.exists():
                dest_file = dest_css_dir / css_file
                shutil.copy2(source_file, dest_file)
                if self.verbose:
                    self.log(f"   📄 Copié: {css_file}")

        if self.verbose:
            self.log("✅ Fichiers CSS copiés vers build")

        # DÉSACTIVÉ : Fonts système utilisées (pas de fonts custom)
        # Performance : LCP optimisé, 0 requête HTTP pour les fonts
        # if self.verbose:
        #     self.log("⚡ Fonts système utilisées (pas de copie nécessaire)")

        # Copier les fichiers JavaScript
        source_js_dir = self.base_path / 'public' / 'js'
        dest_js_dir = self.build_dir / 'public' / 'js'

        # Créer le dossier de destination
        dest_js_dir.mkdir(parents=True, exist_ok=True)

        # Copier tous les fichiers JS
        for js_file in self.JS_FILES:
            source_file = source_js_dir / js_file
            if source_file.exists():
                dest_file = dest_js_dir / js_file
                shutil.copy2(source_file, dest_file)
                if self.verbose:
                    self.log(f"   📄 Copié: {js_file}")

        if self.verbose:
            self.log("✅ Fichiers JS copiés vers build")

        # Copier les fichiers de configuration WhatsApp V5
        source_config_dir = self.base_path / 'config' / 'whatsapp-v5'
        dest_config_dir = self.build_dir / 'public' / 'config' / 'whatsapp-v5'

        if source_config_dir.exists():
            dest_config_dir.mkdir(parents=True, exist_ok=True)

            # Copier tous les fichiers JSON de langue
            for json_file in source_config_dir.glob('*.json'):
                dest_file = dest_config_dir / json_file.name
                shutil.copy2(json_file, dest_file)
                if self.verbose:
                    self.log(f"   📄 Copié: config/whatsapp-v5/{json_file.name}")

            if self.verbose:
                self.log("✅ Configurations WhatsApp V5 copiées vers build")

        # Copier les favicons
        source_logo_dir = self.base_path / 'images' / 'logo'

        # Copier favicon.webp
        favicon_webp_source = source_logo_dir / 'logo.webp'
        if favicon_webp_source.exists():
            shutil.copy2(favicon_webp_source, self.build_dir / 'favicon.webp')
            if self.verbose:
                self.log("   📄 Copié: favicon.webp")

        # Copier favicon.ico optimisé
        favicon_ico_source = source_logo_dir / 'favicon.ico'
        if favicon_ico_source.exists():
            shutil.copy2(favicon_ico_source, self.build_dir / 'favicon.ico')
            if self.verbose:
                self.log("   📄 Copié: favicon.ico (optimisé)")

        if self.verbose:
            self.log("✅ Favicons copiés vers build")

        # Copier le fichier _redirects pour Netlify
        redirects_source = self.base_path / '_redirects'
        if redirects_source.exists():
            shutil.copy2(redirects_source, self.build_dir / '_redirects')
            if self.verbose:
                self.log("   📄 Copié: _redirects (Netlify)")
                self.log("✅ Fichier _redirects copié vers build")

    def _copy_folder(self, source_path, dest_path, description=None, recursive=False):
        """
        Méthode utilitaire pour copier un dossier avec logging

        Args:
            source_path (Path): Chemin source
            dest_path (Path): Chemin destination
            description (str): Description pour le log (optionnel)
            recursive (bool): Si True, copie récursive des sous-dossiers

        Returns:
            int: Nombre de fichiers/dossiers copiés
        """
        if not source_path.exists():
            return 0

        # Créer le dossier de destination
        dest_path.mkdir(parents=True, exist_ok=True)

        count = 0
        if recursive:
            # Copie récursive de sous-dossiers
            for item in source_path.iterdir():
                if item.is_dir():
                    dest_item = dest_path / item.name
                    if dest_item.exists():
                        shutil.rmtree(dest_item)
                    shutil.copytree(item, dest_item)
                    count += 1
        else:
            # Copie simple de fichiers
            for file_path in source_path.glob('*'):
                if file_path.is_file():
                    shutil.copy2(file_path, dest_path / file_path.name)
                    count += 1

        if self.verbose and description and count > 0:
            self.log(f"✅ {count} {description} copiés vers {dest_path.relative_to(self.build_dir)}/")

        return count

    def _copy_main_logo_to_root(self):
        """
        Copie le logo principal (bruxelles-car-depannage-logo.webp) vers la racine
        du dossier images/ sous le nom logo.webp pour compatibilité avec header.html
        """
        logo_source = self.build_dir / 'images' / 'logo' / 'bruxelles-car-depannage-logo.webp'
        logo_dest = self.build_dir / 'images' / 'logo.webp'

        if logo_source.exists():
            shutil.copy2(logo_source, logo_dest)
            if self.verbose:
                self.log(f"✅ Logo copié vers {logo_dest.relative_to(self.base_path)}")
        else:
            self.log(f"⚠️  Logo source introuvable: {logo_source}")

    def copy_images(self):
        """
        Optimise et copie toutes les images depuis images/ vers build/{lang}/images/
        Appelle le script optimize_images.py pour :
        - Compression JPEG/PNG
        - Conversion WebP
        - Génération alt texts automatiques
        - Calcul dimensions (width/height)
        """
        import subprocess

        source_images_dir = self.base_path / 'images'
        dest_images_dir = self.build_dir / 'images'

        if not source_images_dir.exists():
            self.log("⚠️  Dossier images/ introuvable, images non copiées")
            return

        # Si la langue est 'fr', utiliser le script d'optimisation
        # Pour les autres langues, copier simplement depuis build/fr/images/
        if self.lang == 'fr':
            # Appeler le script d'optimisation pour FR
            optimize_script = self.base_path / 'scripts' / 'optimize_images.py'

            if optimize_script.exists():
                try:
                    # Lancer l'optimisation en mode silencieux si verbose=False
                    args = ['python3', str(optimize_script)]
                    if not self.verbose:
                        args.append('--quiet')

                    result = subprocess.run(args, capture_output=not self.verbose, text=True)

                    if result.returncode == 0:
                        if self.verbose:
                            self.log("✅ Images optimisées et copiées vers build")
                    else:
                        self.log(f"⚠️  Erreur lors de l'optimisation des images")
                        if result.stderr:
                            self.log(f"   {result.stderr}")

                except Exception as e:
                    self.log(f"⚠️  Erreur lors de l'optimisation: {e}")
            else:
                # Fallback : copier directement les images sans optimisation
                self.log("⚠️  Script optimize_images.py introuvable, copie directe des images")
                dest_images_dir.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source_images_dir, dest_images_dir, dirs_exist_ok=True)
                if self.verbose:
                    self.log("✅ Images copiées directement vers build (sans optimisation)")
        else:
            # Pour les autres langues (EN, NL), copier depuis build/images/ (images FR)
            fr_images_dir = self.base_path / 'build' / 'images'

            if fr_images_dir.exists():
                # Créer le dossier de destination
                dest_images_dir.mkdir(parents=True, exist_ok=True)

                # Copier récursivement tous les fichiers et dossiers
                shutil.copytree(fr_images_dir, dest_images_dir, dirs_exist_ok=True)

                if self.verbose:
                    self.log(f"✅ Images copiées depuis build/images/ vers build/{self.lang}/images/")
            else:
                self.log(f"⚠️  Dossier build/images/ introuvable. Générez d'abord le site FR.")

        # Copier le logo principal à la racine du dossier images pour compatibilité avec header.html
        self._copy_main_logo_to_root()

    def optimize_images(self):
        """
        Optimise automatiquement toutes les images copiées
        Convertit JPG/PNG en WebP avec compression
        """
        import subprocess

        optimize_script = self.base_path / 'scripts' / 'optimize_images.py'

        if not optimize_script.exists():
            self.log("⚠️  Script optimize_images.py introuvable, images non optimisées")
            return

        try:
            # Exécute le script d'optimisation en mode silencieux
            result = subprocess.run(
                ['python3', str(optimize_script)],
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                check=True
            )

            # Affiche uniquement le résumé (dernières lignes)
            output_lines = result.stdout.strip().split('\n')

            # Trouve la section "RÉSULTATS"
            for i, line in enumerate(output_lines):
                if '📊 RÉSULTATS' in line:
                    # Affiche le résumé
                    for summary_line in output_lines[i:]:
                        if summary_line.strip():
                            self.log(summary_line)
                    break

        except subprocess.CalledProcessError as e:
            self.log(f"❌ Erreur lors de l'optimisation des images: {e}")
            if self.verbose and e.stderr:
                self.log(f"   {e.stderr}")
        except Exception as e:
            self.log(f"❌ Erreur inattendue: {e}")

    def generate_tarifs(self):
        """Génère la page tarifs"""
        self.log("\n💰 === GÉNÉRATION PAGE TARIFS ===")

        # Charger le contenu depuis JSON
        filename = self._get_page_content_filename('tarifs')
        content_path = self.base_path / 'content' / self.lang / 'pages' / filename
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except FileNotFoundError:
            self.log(f"⚠️  Fichier tarifs.json introuvable: {content_path}")
            content = {}

        # Domain
        domain = self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

        # Variables de base
        variables = {
            'PATH_PREFIX': self._get_path_prefix('subpage'),  # Chemins relatifs depuis /tarifs/
            'TELEPHONE': self.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
            'TELEPHONE_HREF': self.variables.get('contact', {}).get('phone_local', '0479890089'),
            'CANONICAL_URL': f"{domain}/tarifs/",
        }

        # Meta tags
        variables['META_TITLE'] = content.get('meta_title', 'Tarifs Dépannage Bruxelles')
        variables['META_DESCRIPTION'] = content.get('meta_description', '')

        # Open Graph
        og = content.get('open_graph', {})
        variables['OG_TITLE'] = og.get('title', variables['META_TITLE'])
        variables['OG_DESCRIPTION'] = og.get('description', variables['META_DESCRIPTION'])
        # Image OG spécifique pour la page tarifs
        variables['OG_IMAGE_1'] = f"{domain}/images/tarifs/helpcar-tarifs-hero.jpg"
        variables['OG_IMAGE_2'] = f"{domain}/images/tarifs/helpcar-tarifs-hero.jpg"

        # Hero
        hero = content.get('hero', {})
        variables['HERO_H1'] = hero.get('h1', 'Dépannage Voiture Tarif')
        h2_colored = hero.get('h2_colored', {})
        variables['HERO_H2_PART1'] = h2_colored.get('part1', 'Appelez,')
        variables['HERO_H2_PART2'] = h2_colored.get('part2', 'Décrivez,')
        variables['HERO_H2_PART3'] = h2_colored.get('part3', 'C\'est Tarifé !')
        variables['HERO_SUBTITLE_LINE1'] = hero.get('subtitle_line1', '')
        variables['HERO_SUBTITLE_LINE2'] = hero.get('subtitle_line2', '')
        variables['HERO_IMAGE_ALT'] = hero.get('image_alt', 'Tarifs dépannage Bruxelles')

        # WhatsApp button text
        cta_translations = self.ui_translations.get('cta', {})
        variables['HERO_WHATSAPP_TEXT'] = cta_translations.get('devis_whatsapp', 'Devis WhatsApp')

        # Carousel tarifs - Scanner automatiquement les images
        tarif_images_folder = self.base_path / 'images' / 'tarif'
        tarif_images = []
        processed_tarif_stems = set()

        if tarif_images_folder.exists():
            for img_file in sorted(tarif_images_folder.glob('*')):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp'] and not img_file.name.startswith('.') and img_file.name != 'README.md':
                    # Éviter les doublons .jpg/.webp
                    if img_file.stem not in processed_tarif_stems:
                        processed_tarif_stems.add(img_file.stem)

                        # Récupérer le alt depuis images-alt.json ou utiliser un fallback
                        alt_text = self.images_alt.get('tarifs', {}).get('hero', {}).get(img_file.stem)
                        if not alt_text:
                            # Fallback si pas trouvé
                            alt_text = self.images_alt.get('tarifs', {}).get('hero', {}).get('default', 'Tarification transparente pour dépannage à Bruxelles')

                        # Toujours utiliser .webp (optimisation automatique)
                        tarif_images.append({
                            "image": img_file.stem + '.webp',
                            "alt": alt_text
                        })
        variables['TARIFS_CAROUSEL'] = self._build_simple_carousel(tarif_images, 'tarif', '../')

        # Comment ça marche (3 étapes)
        ccm = content.get('comment_ca_marche', {})
        variables['CCM_LABEL'] = ccm.get('section_label', 'SIMPLE ET RAPIDE')
        variables['CCM_TITLE'] = ccm.get('section_title', 'Comment Obtenir Votre Tarif ?')
        variables['CCM_DESCRIPTION'] = ccm.get('section_description', '')

        # Générer HTML des étapes
        etapes_html = ''
        for etape in ccm.get('etapes', []):
            numero = etape.get('numero', 1)
            color = etape.get('color', '#F97316')
            titre = etape.get('titre', '')
            description = etape.get('description', '')
            etapes_html += f'''
          <div style="text-align: center; position: relative;">
            <div style="background: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.5rem; color: {color}; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 3px solid {color}; margin: 0 auto 1.5rem;">{numero}</div>
            <h3 style="font-size: 1.375rem; font-weight: 800; margin-bottom: 0.75rem; color: #0F172A;">{titre}</h3>
            <p style="color: #6B7280; line-height: 1.7; font-size: 1rem;">{description}</p>
          </div>
'''
        variables['CCM_ETAPES'] = etapes_html

        # Facteurs qui influencent le prix
        facteurs = content.get('facteurs', {})
        variables['FACTEURS_LABEL'] = facteurs.get('section_label', 'TRANSPARENCE')
        variables['FACTEURS_TITLE'] = facteurs.get('section_title', 'Facteurs Qui Peuvent Influencer le Prix')
        variables['FACTEURS_DESCRIPTION'] = facteurs.get('section_description', '')

        # Générer HTML des cartes facteurs (version compacte avec icônes Lucide)
        facteurs_html = ''
        for facteur in facteurs.get('liste', []):
            icon_name = facteur.get('icon', 'wrench')
            icon_svg = get_icon(icon_name, variant='lucide') or get_icon('wrench', variant='lucide')
            titre = facteur.get('titre', '')
            description = facteur.get('description', '')
            facteurs_html += f'''
          <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-left: 3px solid #1E3A8A; transition: all 0.3s ease; display: flex; gap: 1rem;">
            <div style="flex-shrink: 0; width: 48px; height: 48px; background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #1E3A8A;">
              {icon_svg}
            </div>
            <div style="flex: 1;">
              <h3 style="font-size: 1.125rem; font-weight: 700; margin: 0 0 0.5rem 0; color: #0F172A;">{titre}</h3>
              <p style="color: #6B7280; font-size: 0.9375rem; line-height: 1.6; margin: 0;">{description}</p>
            </div>
          </div>
'''
        variables['FACTEURS_CARDS'] = facteurs_html

        # Injecter les template_variables AVANT de construire les listes de liens
        # pour pouvoir résoudre les URL_SERVICE_* depuis variables.json
        variables = self.inject_template_variables(variables)

        # Interventions courantes
        interventions = content.get('interventions', {})
        variables['INTERVENTIONS_LABEL'] = interventions.get('section_label', 'NOS SERVICES')
        variables['INTERVENTIONS_TITLE'] = interventions.get('section_title', 'Nos Interventions Courantes')
        variables['INTERVENTIONS_DESCRIPTION'] = interventions.get('section_description', '')

        # Dépannage sur place
        depannage = interventions.get('depannage_sur_place', {})
        variables['DEPANNAGE_TITRE'] = depannage.get('titre', 'Dépannage sur Place')
        depannage_liste_html = ''
        for service in depannage.get('services', []):
            nom = service.get('nom', '')
            # Résoudre la variable URL depuis variables.json
            url_var = service.get('url_var', '')
            if url_var and url_var in variables:
                slug = variables[url_var]
                # Construire le lien relatif
                url_relative = f"../{slug}/index.html"
            else:
                # Fallback sur ancien système si url_var n'existe pas
                url_relative = service.get('slug', '')
            depannage_liste_html += f'<li><a href="{url_relative}" style="display: flex; align-items: center; gap: 0.875rem; padding: 1.125rem 1.5rem; background: white; border-radius: 12px; text-decoration: none; color: #0F172A; font-weight: 600; font-size: 1.05rem; transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-left: 4px solid transparent;"><span style="color: #F97316; font-size: 1.25rem;">→</span>{nom}</a></li>\n'
        variables['DEPANNAGE_LISTE'] = depannage_liste_html

        # Remorquage
        remorquage = interventions.get('remorquage', {})
        variables['REMORQUAGE_TITRE'] = remorquage.get('titre', 'Remorquage')
        remorquage_liste_html = ''
        for service in remorquage.get('services', []):
            nom = service.get('nom', '')
            # Résoudre la variable URL depuis variables.json
            url_var = service.get('url_var', '')
            if url_var and url_var in variables:
                slug = variables[url_var]
                # Construire le lien relatif
                url_relative = f"../{slug}/index.html"
            else:
                # Fallback sur ancien système si url_var n'existe pas
                url_relative = service.get('slug', '')
            remorquage_liste_html += f'<li><a href="{url_relative}" style="display: flex; align-items: center; gap: 0.875rem; padding: 1.125rem 1.5rem; background: white; border-radius: 12px; text-decoration: none; color: #0F172A; font-weight: 600; font-size: 1.05rem; transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-left: 4px solid transparent;"><span style="color: #F97316; font-size: 1.25rem;">→</span>{nom}</a></li>\n'
        variables['REMORQUAGE_LISTE'] = remorquage_liste_html

        # Lien tous services
        lien = interventions.get('lien_tous_services', {})
        lien_texte = lien.get('texte', 'Découvrir tous nos services')
        # Remplacer {{SERVICES_TOTAL}} par la valeur réelle depuis config/variables.json
        services_total = str(self.variables.get('stats', {}).get('services_total', ''))
        variables['LIEN_TOUS_SERVICES_TEXTE'] = lien_texte.replace('{{SERVICES_TOTAL}}', services_total)
        # Utiliser url_relative si disponible, sinon fallback sur url
        variables['LIEN_TOUS_SERVICES_URL'] = lien.get('url_relative', lien.get('url', '../services/index.html'))

        # CTA Final
        cta = content.get('cta_final', {})
        variables['CTA_FINAL_TITRE'] = cta.get('titre', 'Besoin de Votre Tarif Exact ?')
        variables['CTA_FINAL_SUBTITLE'] = cta.get('subtitle', '')
        cta_button = cta.get('button', '{{TELEPHONE}}')
        variables['CTA_FINAL_BUTTON'] = cta_button.replace('{{TELEPHONE}}', variables['TELEPHONE'])

        # Schema.org
        homepage_schema = self.schema_builder.build_homepage_schema()
        variables['SCHEMA_ORG_LOCALBUSINESS'] = self.schema_builder.to_json_ld(homepage_schema)

        # Footer et Breadcrumb
        self.add_footer_variables(variables)
        variables['BREADCRUMB_ITEMS'] = self.build_breadcrumb_items('tarifs', 'Tarifs', variables['PATH_PREFIX'])

        # Aria labels
        aria_labels = self.ui_translations.get('aria_labels', {})
        variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

        # MULTILINGUAL: Ajouter variables de langue et hreflang
        variables.update(self._get_language_variables("subpage"))
        hreflang_vars = self._generate_hreflang_urls('tarifs')
        variables.update(hreflang_vars)

        # Rendre le composant hreflang
        hreflang_html = self.renderer.render('components/hreflang.html', hreflang_vars)
        variables['COMPONENT_HREFLANG'] = hreflang_html

        # Sidebar translations
        sidebar_ui = self.ui_translations.get('sidebar', {})
        services = self.loader.load_services()
        communes = self.loader.load_communes()
        variables['SIDEBAR_POPULAR_SERVICES_TITLE'] = sidebar_ui.get('popular_services_title', 'Services Populaires')
        variables['SIDEBAR_SERVICE_TOWING'] = sidebar_ui.get('service_towing', 'Remorquage de voitures')
        variables['SIDEBAR_SERVICE_BATTERY'] = sidebar_ui.get('service_battery', 'Dépannage batterie')
        variables['SIDEBAR_SERVICE_TIRE'] = sidebar_ui.get('service_tire', 'Réparation pneu')
        variables['SIDEBAR_SERVICE_FUEL'] = sidebar_ui.get('service_fuel', 'Panne d\'essence')
        variables['SIDEBAR_SERVICE_DOOR'] = sidebar_ui.get('service_door', 'Ouverture de porte')
        variables['SIDEBAR_SERVICE_MOTO'] = sidebar_ui.get('service_moto', 'Remorquage de motos')
        variables['SIDEBAR_NEED_HELP_BADGE'] = sidebar_ui.get('need_help_badge', 'Besoin d\'aide ?')
        variables['SIDEBAR_AVAILABILITY'] = sidebar_ui.get('availability', 'Disponible 24h/24 - 7j/7')
        variables['SIDEBAR_SERVICE_AREAS_TITLE'] = sidebar_ui.get('service_areas_title', 'Zones d\'Intervention')
        variables['SIDEBAR_SERVICES_ALL'] = sidebar_ui.get('services_all', 'Voir tous les services ({{NOMBRE_SERVICES}}) →').replace('{{NOMBRE_SERVICES}}', str(len(services)))
        variables['SIDEBAR_NEARBY_ALL'] = sidebar_ui.get('nearby_all', 'Voir toutes les zones ({{NOMBRE_COMMUNES}}) →').replace('{{NOMBRE_COMMUNES}}', str(len(communes)))

        # Sidebar URLs (language-dependent)
        variables['SIDEBAR_SERVICES_URL'] = '../services/'
        variables['SIDEBAR_AREAS_URL'] = '../areas/' if self.lang == 'en' else '../zones/'

        # Rendu
        html = self.renderer.render_with_components('pages/tarifs.html', variables)
        save_path = self._get_page_save_path('tarifs')
        self.save_page(html, save_path)
        self.log("✅ Page tarifs générée")

    def generate_contact(self):
        """Génère la page contact"""
        self.log("\n📞 === GÉNÉRATION PAGE CONTACT ===")

        # Charger le contenu depuis JSON
        content_path = self.base_path / 'content' / self.lang / 'pages' / 'contact.json'
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except FileNotFoundError:
            self.log(f"⚠️  Fichier contact.json introuvable: {content_path}")
            content = {}

        # Domain
        domain = self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

        # Variables de base
        variables = {
            'PATH_PREFIX': self._get_path_prefix('subpage'),  # Chemins relatifs depuis /contact/
            'TELEPHONE': self.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
            'TELEPHONE_HREF': self.variables.get('contact', {}).get('phone_local', '0479890089'),
            'EMAIL': self.variables.get('contact', {}).get('email', 'bruxelles.car.depannage@hotmail.com'),
            'ADRESSE': self.variables.get('contact', {}).get('address', 'Square Jean-Baptiste de Greef 9, 1160 Bruxelles'),
            'CANONICAL_URL': f"{domain}/contact/",
        }

        # Meta tags
        variables['META_TITLE'] = content.get('meta_title', 'Contact Bruxelles Car Dépannage')
        variables['META_DESCRIPTION'] = content.get('meta_description', '')

        # Open Graph
        og = content.get('open_graph', {})
        variables['OG_TITLE'] = og.get('title', variables['META_TITLE'])
        variables['OG_DESCRIPTION'] = og.get('description', variables['META_DESCRIPTION'])
        # Carrousel Open Graph (2 images)
        variables['OG_IMAGE_1'] = f"{domain}/images/og/helpcar-depannage-bruxelles.jpg"
        variables['OG_IMAGE_2'] = f"{domain}/images/og/helpcar-depannage-bruxelles.jpg"

        # Hero
        hero = content.get('hero', {})
        variables['HERO_H1'] = hero.get('h1', 'Contactez-nous')
        variables['HERO_SUBTITLE'] = hero.get('subtitle', '')
        hero_cta = hero.get('cta_button', 'Urgence ? Appelez le {{TELEPHONE}}')
        variables['HERO_CTA_BUTTON'] = hero_cta.replace('{{TELEPHONE}}', variables['TELEPHONE'])
        variables['HERO_DISPONIBILITE'] = hero.get('disponibilite', 'Disponible 24h/24 - 7j/7')
        variables['HERO_IMAGE_ALT'] = hero.get('image_alt', 'Contact Bruxelles Car Dépannage')

        # WhatsApp button text
        cta_translations = self.ui_translations.get('cta', {})
        variables['HERO_WHATSAPP_TEXT'] = cta_translations.get('devis_whatsapp', 'Devis WhatsApp')

        # Carousel contact - Scanner automatiquement les images
        contact_images_folder = self.base_path / 'images' / 'contact'
        contact_images = []
        processed_contact_stems = set()

        if contact_images_folder.exists():
            for img_file in sorted(contact_images_folder.glob('*')):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp'] and not img_file.name.startswith('.') and img_file.name != 'README.md':
                    # Éviter les doublons .jpg/.webp
                    if img_file.stem not in processed_contact_stems:
                        processed_contact_stems.add(img_file.stem)

                        # Récupérer le alt depuis images-alt.json ou utiliser un fallback
                        alt_text = self.images_alt.get('contact', {}).get('hero', {}).get(img_file.stem)
                        if not alt_text:
                            # Fallback si pas trouvé
                            alt_text = self.images_alt.get('contact', {}).get('hero', {}).get('default', 'Contactez Bruxelles Car Depannage pour une intervention rapide')

                        # Toujours utiliser .webp (optimisation automatique)
                        contact_images.append({
                            "image": img_file.stem + '.webp',
                            "alt": alt_text
                        })
        variables['CONTACT_CAROUSEL'] = self._build_simple_carousel(contact_images, 'contact', '../')

        # Formulaire
        formulaire = content.get('formulaire', {})
        variables['FORM_TITRE'] = formulaire.get('titre', 'Envoyez-nous un Message')
        variables['FORM_DESCRIPTION'] = formulaire.get('description', '')

        champs = formulaire.get('champs', {})
        variables['FORM_NOM_LABEL'] = champs.get('nom', {}).get('label', 'Nom complet *')
        variables['FORM_NOM_PLACEHOLDER'] = champs.get('nom', {}).get('placeholder', 'Votre nom')
        variables['FORM_EMAIL_LABEL'] = champs.get('email', {}).get('label', 'Email *')
        variables['FORM_EMAIL_PLACEHOLDER'] = champs.get('email', {}).get('placeholder', 'votre@email.com')
        variables['FORM_TEL_LABEL'] = champs.get('telephone', {}).get('label', 'Téléphone')
        variables['FORM_TEL_PLACEHOLDER'] = champs.get('telephone', {}).get('placeholder', '0479 89 00 89')
        variables['FORM_TYPE_LABEL'] = champs.get('type_demande', {}).get('label', 'Type de demande')

        # Générer options select
        options_html = ''
        for option in champs.get('type_demande', {}).get('options', []):
            value = option.get('value', '')
            label = option.get('label', '')
            options_html += f'<option value="{value}">{label}</option>\n'
        variables['FORM_TYPE_OPTIONS'] = options_html

        variables['FORM_MESSAGE_LABEL'] = champs.get('message', {}).get('label', 'Message *')
        variables['FORM_MESSAGE_PLACEHOLDER'] = champs.get('message', {}).get('placeholder', 'Décrivez votre demande...')
        variables['FORM_BUTTON_SUBMIT'] = formulaire.get('button_submit', 'Envoyer le message')

        # Coordonnées
        coordonnees = content.get('coordonnees', {})
        variables['COORDONNEES_TITRE'] = coordonnees.get('titre', 'Coordonnées')

        # Générer HTML des items de coordonnées
        coord_html = ''
        icon_colors = {'telephone': '#F97316', 'email': '#F97316', 'adresse': '#10B981', 'horaires': '#10B981'}
        svg_paths = {
            'telephone': 'M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z',
            'email': 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
            'adresse': 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z',
            'horaires': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
        }

        for idx, item in enumerate(coordonnees.get('items', [])):
            item_type = item.get('type', '')
            label = item.get('label', '')
            value_template = item.get('value', '')

            # Remplacer les placeholders
            value = value_template.replace('{{TELEPHONE}}', variables['TELEPHONE'])
            value = value.replace('{{EMAIL}}', variables['EMAIL'])
            value = value.replace('{{ADRESSE}}', variables['ADRESSE'])

            color = icon_colors.get(item_type, '#F97316')
            svg_path = svg_paths.get(item_type, svg_paths['telephone'])

            border = '' if idx == len(coordonnees.get('items', [])) - 1 else 'border-bottom: 1px solid #E5E7EB;'

            coord_html += f'''
              <div style="margin-bottom: 1.75rem; padding-bottom: 1.75rem; {border}">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="{color}" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="{svg_path}" />
                  </svg>
                  <span style="font-weight: 600; color: #6B7280;">{label}</span>
                </div>
'''

            if item_type == 'telephone':
                href = item.get('href', '').replace('{{TELEPHONE_HREF}}', variables['TELEPHONE_HREF'])
                coord_html += f'<a href="{href}" style="color: #F97316; font-size: 1.5rem; font-weight: 700; text-decoration: none; display: block;">{value}</a>'
            elif item_type == 'email':
                href = item.get('href', '').replace('{{EMAIL}}', variables['EMAIL'])
                coord_html += f'<a href="{href}" style="color: #0F172A; font-size: 1.05rem; font-weight: 600; text-decoration: none; display: block;">{value}</a>'
            elif item_type == 'horaires':
                coord_html += f'<p style="color: #1E3A8A; font-size: 1.25rem; font-weight: 700; margin: 0;">{value}</p>'
            else:
                coord_html += f'<p style="color: #0F172A; font-size: 1.05rem; font-weight: 600; margin: 0;">{value}</p>'

            coord_html += '</div>\n'

        variables['COORDONNEES_ITEMS'] = coord_html

        # CTA Final
        cta = content.get('cta_final', {})
        variables['CTA_FINAL_TITRE'] = cta.get('titre', 'Une Urgence ? Appelez Maintenant !')
        variables['CTA_FINAL_SUBTITLE'] = cta.get('subtitle', '')
        cta_button = cta.get('button', '{{TELEPHONE}}')
        variables['CTA_FINAL_BUTTON'] = f"Appeler le {cta_button.replace('{{TELEPHONE}}', variables['TELEPHONE'])}"

        # Schema.org
        homepage_schema = self.schema_builder.build_homepage_schema()
        variables['SCHEMA_ORG_LOCALBUSINESS'] = self.schema_builder.to_json_ld(homepage_schema)

        # Footer et Breadcrumb
        self.add_footer_variables(variables)
        variables['BREADCRUMB_ITEMS'] = self.build_breadcrumb_items('contact', 'Contact', variables['PATH_PREFIX'])

        # Injecter toutes les template_variables (URLs, pricing, etc.)
        variables = self.inject_template_variables(variables)

        # Aria labels
        aria_labels = self.ui_translations.get('aria_labels', {})
        variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

        # MULTILINGUAL: Ajouter variables de langue et hreflang
        variables.update(self._get_language_variables("subpage"))
        hreflang_vars = self._generate_hreflang_urls('contact')
        variables.update(hreflang_vars)

        # Rendre le composant hreflang
        hreflang_html = self.renderer.render('components/hreflang.html', hreflang_vars)
        variables['COMPONENT_HREFLANG'] = hreflang_html

        # Sidebar translations
        sidebar_ui = self.ui_translations.get('sidebar', {})
        services = self.loader.load_services()
        communes = self.loader.load_communes()
        variables['SIDEBAR_POPULAR_SERVICES_TITLE'] = sidebar_ui.get('popular_services_title', 'Services Populaires')
        variables['SIDEBAR_SERVICE_TOWING'] = sidebar_ui.get('service_towing', 'Remorquage de voitures')
        variables['SIDEBAR_SERVICE_BATTERY'] = sidebar_ui.get('service_battery', 'Dépannage batterie')
        variables['SIDEBAR_SERVICE_TIRE'] = sidebar_ui.get('service_tire', 'Réparation pneu')
        variables['SIDEBAR_SERVICE_FUEL'] = sidebar_ui.get('service_fuel', 'Panne d\'essence')
        variables['SIDEBAR_SERVICE_DOOR'] = sidebar_ui.get('service_door', 'Ouverture de porte')
        variables['SIDEBAR_SERVICE_MOTO'] = sidebar_ui.get('service_moto', 'Remorquage de motos')
        variables['SIDEBAR_NEED_HELP_BADGE'] = sidebar_ui.get('need_help_badge', 'Besoin d\'aide ?')
        variables['SIDEBAR_AVAILABILITY'] = sidebar_ui.get('availability', 'Disponible 24h/24 - 7j/7')
        variables['SIDEBAR_SERVICE_AREAS_TITLE'] = sidebar_ui.get('service_areas_title', 'Zones d\'Intervention')
        variables['SIDEBAR_SERVICES_ALL'] = sidebar_ui.get('services_all', 'Voir tous les services ({{NOMBRE_SERVICES}}) →').replace('{{NOMBRE_SERVICES}}', str(len(services)))
        variables['SIDEBAR_NEARBY_ALL'] = sidebar_ui.get('nearby_all', 'Voir toutes les zones ({{NOMBRE_COMMUNES}}) →').replace('{{NOMBRE_COMMUNES}}', str(len(communes)))

        # Sidebar URLs (language-dependent)
        variables['SIDEBAR_SERVICES_URL'] = '../services/'
        variables['SIDEBAR_AREAS_URL'] = '../areas/' if self.lang == 'en' else '../zones/'

        # Rendu
        html = self.renderer.render_with_components('pages/contact.html', variables)
        self.save_page(html, 'contact/index.html')
        self.log("✅ Page contact générée")

    def generate_a_propos(self):
        """Génère la page à propos"""
        self.log("\n📖 === GÉNÉRATION PAGE À PROPOS ===")

        # Charger le contenu depuis JSON
        filename = self._get_page_content_filename('a-propos')
        content_path = self.base_path / 'content' / self.lang / 'pages' / filename
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except FileNotFoundError:
            self.log(f"⚠️  Fichier a-propos.json introuvable: {content_path}")
            content = {}

        # Domain
        domain = self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

        # Variables de base
        variables = {
            'PATH_PREFIX': self._get_path_prefix('subpage'),  # Chemins relatifs depuis /a-propos/
            'SITE_NAME': self.variables.get('site', {}).get('name', 'Bruxelles Car Dépannage'),
            'COMPANY_NAME': self.variables.get('company', {}).get('name_full', 'Bruxelles Car Depannage srl'),
            'FOUNDING_YEAR': self.variables.get('company', {}).get('founding_year', '2015'),
            'YEARS_EXPERIENCE': self.variables.get('company', {}).get('years_experience', '10'),
            'YEARS_EXPERIENCE_PLUS': self.variables.get('company', {}).get('years_experience_plus', '+10'),
            'GOOGLE_RATING': self.variables.get('google', {}).get('rating', '4.9'),
            'GOOGLE_REVIEWS_COUNT': self.variables.get('google', {}).get('reviews_count', '200'),
            'TELEPHONE': self.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
            'TELEPHONE_HREF': self.variables.get('contact', {}).get('phone_local', '0479890089'),
            'CANONICAL_URL': f"{domain}/a-propos/",
        }

        # Meta tags
        variables['META_TITLE'] = content.get('meta_title', 'À Propos Bruxelles Car Dépannage')
        variables['META_DESCRIPTION'] = content.get('meta_description', '')

        # Open Graph (avec remplacement des variables)
        og = content.get('open_graph', {})
        og_title = og.get('title', variables['META_TITLE'])
        og_title = og_title.replace('{{COMPANY_NAME}}', variables['COMPANY_NAME'])
        og_title = og_title.replace('{{FOUNDING_YEAR}}', variables['FOUNDING_YEAR'])
        variables['OG_TITLE'] = og_title

        og_desc = og.get('description', variables['META_DESCRIPTION'])
        og_desc = og_desc.replace('{{COMPANY_NAME}}', variables['COMPANY_NAME'])
        og_desc = og_desc.replace('{{YEARS_EXPERIENCE}}', variables['YEARS_EXPERIENCE'])
        variables['OG_DESCRIPTION'] = og_desc
        # Carrousel Open Graph (2 images)
        variables['OG_IMAGE_1'] = f"{domain}/images/og/helpcar-depannage-bruxelles.jpg"
        variables['OG_IMAGE_2'] = f"{domain}/images/og/helpcar-depannage-bruxelles.jpg"

        # Hero
        hero = content.get('hero', {})
        hero_h1 = hero.get('h1', 'À Propos')
        variables['HERO_H1'] = hero_h1.replace('{{COMPANY_NAME}}', variables['COMPANY_NAME'])
        hero_subtitle = hero.get('subtitle', '')
        variables['HERO_SUBTITLE'] = hero_subtitle.replace('{{FOUNDING_YEAR}}', variables['FOUNDING_YEAR'])
        variables['HERO_IMAGE_ALT'] = hero.get('image_alt', 'À propos de Bruxelles Car Depannage')

        # Notre histoire
        histoire = content.get('notre_histoire', {})
        variables['HISTOIRE_LABEL'] = histoire.get('section_label', 'Notre histoire')
        variables['HISTOIRE_TITLE'] = histoire.get('section_title', 'Une Passion au Service des Automobilistes')

        # Générer paragraphes avec remplacement variables
        paragraphes_html = ''
        for p in histoire.get('paragraphes', []):
            p = p.replace('{{FOUNDING_YEAR}}', variables['FOUNDING_YEAR'])
            p = p.replace('{{COMPANY_NAME}}', variables['COMPANY_NAME'])
            p = p.replace('{{YEARS_EXPERIENCE}}', variables['YEARS_EXPERIENCE'])
            margin = ' margin-bottom: 1.5rem;' if p != histoire.get('paragraphes', [])[-1] else ' margin-bottom: 0;'
            paragraphes_html += f'<p style="font-size: 1.15rem; line-height: 1.8; color: #0F172A;{margin}">\n{p}\n</p>\n'
        variables['HISTOIRE_PARAGRAPHES'] = paragraphes_html

        # Chiffres clés
        chiffres_html = ''
        for chiffre in content.get('chiffres_cles', []):
            valeur = chiffre.get('valeur', '')
            valeur = valeur.replace('{{YEARS_EXPERIENCE_PLUS}}', variables['YEARS_EXPERIENCE_PLUS'])
            valeur = valeur.replace('{{GOOGLE_RATING}}', variables['GOOGLE_RATING'])
            label = chiffre.get('label', '')
            label = label.replace('{{GOOGLE_REVIEWS_COUNT}}', variables['GOOGLE_REVIEWS_COUNT'])
            chiffres_html += f'''
          <div style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border-radius: 16px; padding: 2rem; text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #F97316; margin-bottom: 0.5rem;">{valeur}</div>
            <div style="font-weight: 600; color: #0F172A;">{label}</div>
          </div>
'''
        variables['CHIFFRES_CLES'] = chiffres_html

        # Nos valeurs
        valeurs = content.get('nos_valeurs', {})
        variables['VALEURS_LABEL'] = valeurs.get('section_label', 'Nos valeurs')
        variables['VALEURS_TITLE'] = valeurs.get('section_title', 'Ce Qui Nous Anime au Quotidien')
        variables['VALEURS_DESCRIPTION'] = valeurs.get('section_description', '')

        # Générer cartes valeurs
        valeurs_html = ''
        for valeur in valeurs.get('valeurs', []):
            emoji = valeur.get('emoji', '⚡')
            titre = valeur.get('titre', '')
            description = valeur.get('description', '')
            description = description.replace('{{GOOGLE_RATING}}', variables['GOOGLE_RATING'])
            description = description.replace('{{GOOGLE_REVIEWS_COUNT}}', variables['GOOGLE_REVIEWS_COUNT'])
            valeurs_html += f'''
          <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #1E3A8A 0%, #1E3A8A 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);">
              <span style="font-size: 2.5rem;">{emoji}</span>
            </div>
            <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; color: #0F172A;">{titre}</h3>
            <p style="color: #6B7280; line-height: 1.6;">
              {description}
            </p>
          </div>
'''
        variables['VALEURS_CARDS'] = valeurs_html

        # Garanties (section "Pourquoi nous choisir")
        garanties = content.get('garanties', {})
        variables['GARANTIES_LABEL'] = garanties.get('section_label', 'Pourquoi nous choisir')
        variables['GARANTIES_TITLE'] = garanties.get('section_title', 'Nos Garanties')

        # Générer cartes garanties
        garanties_html = ''
        for item in garanties.get('items', []):
            emoji = item.get('emoji', '✓')
            titre = item.get('titre', '')
            description = item.get('description', '')
            garanties_html += f'''
          <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); display: flex; gap: 1.5rem; align-items: start;">
            <div style="width: 60px; height: 60px; background: #EFF6FF; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <span style="font-size: 2rem;">{emoji}</span>
            </div>
            <div>
              <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 0.75rem; color: #0F172A;">{titre}</h3>
              <p style="color: #6B7280; line-height: 1.7; margin: 0;">
                {description}
              </p>
            </div>
          </div>
'''
        variables['GARANTIES_CARDS'] = garanties_html

        # Engagement
        engagement = content.get('engagement', {})
        variables['ENGAGEMENT_TITRE'] = engagement.get('titre', 'Notre Engagement envers Vous')

        # Remplacer {{COMPANY_NAME}} dans le paragraphe
        paragraphe = engagement.get('paragraphe', '')
        variables['ENGAGEMENT_PARAGRAPHE'] = paragraphe.replace('{{COMPANY_NAME}}', variables['COMPANY_NAME'])

        variables['ENGAGEMENT_CITATION'] = engagement.get('citation', '')

        # Remplacer {{SITE_NAME}} dans la signature
        signature = engagement.get('signature', '— L\'équipe {{SITE_NAME}}')
        variables['ENGAGEMENT_SIGNATURE'] = signature.replace('{{SITE_NAME}}', variables['SITE_NAME'])

        # CTA Final
        cta = content.get('cta_final', {})
        variables['CTA_FINAL_TITRE'] = cta.get('titre', 'Besoin d\'un Dépannage Maintenant ?')
        variables['CTA_FINAL_SUBTITLE'] = cta.get('subtitle', '')
        cta_button = cta.get('button', '{{TELEPHONE}}')
        variables['CTA_FINAL_BUTTON'] = f"Appeler le {cta_button.replace('{{TELEPHONE}}', variables['TELEPHONE'])}"

        # Schema.org
        homepage_schema = self.schema_builder.build_homepage_schema()
        variables['SCHEMA_ORG_LOCALBUSINESS'] = self.schema_builder.to_json_ld(homepage_schema)

        # Footer et Breadcrumb
        self.add_footer_variables(variables)
        variables['BREADCRUMB_ITEMS'] = self.build_breadcrumb_items('a-propos', 'À Propos', variables['PATH_PREFIX'])

        # Injecter toutes les template_variables (URLs, pricing, etc.)
        variables = self.inject_template_variables(variables)

        # Aria labels
        aria_labels = self.ui_translations.get('aria_labels', {})
        variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

        # MULTILINGUAL: Ajouter variables de langue et hreflang
        variables.update(self._get_language_variables("subpage"))
        hreflang_vars = self._generate_hreflang_urls('a-propos')
        variables.update(hreflang_vars)

        # Rendre le composant hreflang
        hreflang_html = self.renderer.render('components/hreflang.html', hreflang_vars)
        variables['COMPONENT_HREFLANG'] = hreflang_html

        # Sidebar translations
        sidebar_ui = self.ui_translations.get('sidebar', {})
        services = self.loader.load_services()
        communes = self.loader.load_communes()
        variables['SIDEBAR_POPULAR_SERVICES_TITLE'] = sidebar_ui.get('popular_services_title', 'Services Populaires')
        variables['SIDEBAR_SERVICE_TOWING'] = sidebar_ui.get('service_towing', 'Remorquage de voitures')
        variables['SIDEBAR_SERVICE_BATTERY'] = sidebar_ui.get('service_battery', 'Dépannage batterie')
        variables['SIDEBAR_SERVICE_TIRE'] = sidebar_ui.get('service_tire', 'Réparation pneu')
        variables['SIDEBAR_SERVICE_FUEL'] = sidebar_ui.get('service_fuel', 'Panne d\'essence')
        variables['SIDEBAR_SERVICE_DOOR'] = sidebar_ui.get('service_door', 'Ouverture de porte')
        variables['SIDEBAR_SERVICE_MOTO'] = sidebar_ui.get('service_moto', 'Remorquage de motos')
        variables['SIDEBAR_NEED_HELP_BADGE'] = sidebar_ui.get('need_help_badge', 'Besoin d\'aide ?')
        variables['SIDEBAR_AVAILABILITY'] = sidebar_ui.get('availability', 'Disponible 24h/24 - 7j/7')
        variables['SIDEBAR_SERVICE_AREAS_TITLE'] = sidebar_ui.get('service_areas_title', 'Zones d\'Intervention')
        variables['SIDEBAR_SERVICES_ALL'] = sidebar_ui.get('services_all', 'Voir tous les services ({{NOMBRE_SERVICES}}) →').replace('{{NOMBRE_SERVICES}}', str(len(services)))
        variables['SIDEBAR_NEARBY_ALL'] = sidebar_ui.get('nearby_all', 'Voir toutes les zones ({{NOMBRE_COMMUNES}}) →').replace('{{NOMBRE_COMMUNES}}', str(len(communes)))

        # Sidebar URLs (language-dependent)
        variables['SIDEBAR_SERVICES_URL'] = '../services/'
        variables['SIDEBAR_AREAS_URL'] = '../areas/' if self.lang == 'en' else '../zones/'

        # Rendu
        html = self.renderer.render_with_components('pages/a-propos.html', variables)
        save_path = self._get_page_save_path('a-propos')
        self.save_page(html, save_path)
        self.log("✅ Page à propos générée")

    def generate_mentions_legales(self):
        """Génère la page mentions légales"""
        self.log("\n⚖️  === GÉNÉRATION PAGE MENTIONS LÉGALES ===")

        # Charger le contenu depuis JSON
        filename = self._get_page_content_filename('mentions-legales')
        content_path = self.base_path / 'content' / self.lang / 'pages' / filename
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except FileNotFoundError:
            self.log(f"⚠️  Fichier mentions-legales.json introuvable: {content_path}")
            content = {}

        # Variables de base
        variables = {
            'PATH_PREFIX': self._get_path_prefix('subpage'),  # Chemins relatifs depuis /mentions-legales/
            'TELEPHONE': self.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
            'TELEPHONE_HREF': self.variables.get('contact', {}).get('phone_local', '0479890089'),
            'EMAIL': self.variables.get('contact', {}).get('email', 'bruxelles.car.depannage@hotmail.com'),
            'CANONICAL_URL': f"{self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')}/mentions-legales/",
            'COMPANY_NUMBER': self.variables.get('company', {}).get('company_number', 'BE0642945692'),
            'VAT_NUMBER': self.variables.get('company', {}).get('vat_number', 'BE0642945692'),
        }

        # Meta et Hero
        variables['META_TITLE'] = content.get('meta_title', 'Mentions Légales | Bruxelles Car Dépannage')
        variables['META_DESCRIPTION'] = content.get('meta_description', '')
        variables['HERO_H1'] = content.get('hero', {}).get('h1', 'Mentions Légales')
        variables['HERO_SUBTITLE'] = content.get('hero', {}).get('subtitle', '')

        # Sections
        sections = content.get('sections', {})

        # Section 1: Éditeur
        editeur = sections.get('editeur', {})
        variables['SECTION_1_TITRE'] = editeur.get('titre', '1. Éditeur du site')
        variables['SECTION_1_RAISON_SOCIALE_LABEL'] = editeur.get('raison_sociale_label', 'Raison sociale :')
        variables['SECTION_1_RAISON_SOCIALE'] = editeur.get('raison_sociale', 'Bruxelles Car Dépannage SRL')
        variables['SECTION_1_FORME_JURIDIQUE_LABEL'] = editeur.get('forme_juridique_label', 'Forme juridique :')
        variables['SECTION_1_FORME_JURIDIQUE'] = editeur.get('forme_juridique', 'Société à Responsabilité Limitée (SRL)')
        variables['SECTION_1_SIEGE_SOCIAL_LABEL'] = editeur.get('siege_social_label', 'Siège social :')
        variables['SECTION_1_SIEGE_SOCIAL'] = editeur.get('siege_social', 'Square Jean-Baptiste de Greef 9, 1160 Bruxelles, Belgique')
        variables['SECTION_1_NUMERO_ENTREPRISE_LABEL'] = editeur.get('numero_entreprise_label', 'Numéro d\'entreprise :')
        variables['SECTION_1_NUMERO_TVA_LABEL'] = editeur.get('numero_tva_label', 'N° TVA :')
        variables['SECTION_1_EMAIL_LABEL'] = editeur.get('email_label', 'Email :')
        variables['SECTION_1_TELEPHONE_LABEL'] = editeur.get('telephone_label', 'Téléphone :')

        # Section 2: Directeur
        directeur = sections.get('directeur', {})
        variables['SECTION_2_TITRE'] = directeur.get('titre', '2. Directeur de publication')
        variables['SECTION_2_CONTENU'] = directeur.get('contenu', '')

        # Section 3: Hébergement
        hebergement = sections.get('hebergement', {})
        variables['SECTION_3_TITRE'] = hebergement.get('titre', '3. Hébergement')
        variables['SECTION_3_HEBERGEUR_LABEL'] = hebergement.get('hebergeur_label', 'Hébergeur :')
        variables['SECTION_3_HEBERGEUR'] = hebergement.get('hebergeur', 'Netlify, Inc.')
        variables['SECTION_3_ADRESSE_LABEL'] = hebergement.get('adresse_label', 'Adresse :')
        variables['SECTION_3_ADRESSE'] = hebergement.get('adresse', '44 Montgomery Street, Suite 300, San Francisco, CA 94104, USA')
        variables['SECTION_3_SITE_WEB_LABEL'] = hebergement.get('site_web_label', 'Site web :')
        variables['SECTION_3_SITE_WEB'] = hebergement.get('site_web', 'www.netlify.com')
        variables['SECTION_3_SITE_WEB_URL'] = hebergement.get('site_web_url', 'https://www.netlify.com')

        # Section 4: Propriété intellectuelle
        propriete = sections.get('propriete_intellectuelle', {})
        variables['SECTION_4_TITRE'] = propriete.get('titre', '4. Propriété intellectuelle')
        variables['SECTION_4_PARAGRAPHE_1'] = propriete.get('paragraphe_1', '')
        variables['SECTION_4_PARAGRAPHE_2'] = propriete.get('paragraphe_2', '')
        variables['SECTION_4_PARAGRAPHE_3'] = propriete.get('paragraphe_3', '')

        # Section 5: Responsabilité
        responsabilite = sections.get('responsabilite', {})
        variables['SECTION_5_TITRE'] = responsabilite.get('titre', '5. Limitation de responsabilité')
        variables['SECTION_5_PARAGRAPHE_1'] = responsabilite.get('paragraphe_1', '')
        variables['SECTION_5_PARAGRAPHE_2'] = responsabilite.get('paragraphe_2', '')
        variables['SECTION_5_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in responsabilite.get('liste', [])])
        variables['SECTION_5_PARAGRAPHE_3'] = responsabilite.get('paragraphe_3', '')

        # Section 6: Données personnelles
        donnees = sections.get('donnees_personnelles', {})
        variables['SECTION_6_TITRE'] = donnees.get('titre', '6. Données personnelles')
        variables['SECTION_6_PARAGRAPHE_1'] = donnees.get('paragraphe_1', '')
        variables['SECTION_6_PARAGRAPHE_2'] = donnees.get('paragraphe_2', '')
        contact_liste = donnees.get('contact_liste', [])
        variables['SECTION_6_CONTACT_LISTE'] = '\n'.join([f'<li>{item.replace("{{TELEPHONE}}", variables["TELEPHONE"])}</li>' for item in contact_liste])
        variables['SECTION_6_PARAGRAPHE_3'] = donnees.get('paragraphe_3', '')

        # Section 7: Cookies
        cookies = sections.get('cookies', {})
        variables['SECTION_7_TITRE'] = cookies.get('titre', '7. Cookies')
        variables['SECTION_7_PARAGRAPHE_1'] = cookies.get('paragraphe_1', '')
        variables['SECTION_7_TYPES_TITRE'] = cookies.get('types_titre', 'Types de cookies utilisés :')
        variables['SECTION_7_TYPES_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in cookies.get('types_liste', [])])
        variables['SECTION_7_PARAGRAPHE_2'] = cookies.get('paragraphe_2', '')

        # Section 8: Liens
        liens = sections.get('liens', {})
        variables['SECTION_8_TITRE'] = liens.get('titre', '8. Liens hypertextes')
        variables['SECTION_8_PARAGRAPHE_1'] = liens.get('paragraphe_1', '')
        variables['SECTION_8_PARAGRAPHE_2'] = liens.get('paragraphe_2', '')

        # Section 9: Droit applicable
        droit = sections.get('droit_applicable', {})
        variables['SECTION_9_TITRE'] = droit.get('titre', '9. Droit applicable et juridiction')
        variables['SECTION_9_PARAGRAPHE_1'] = droit.get('paragraphe_1', '')
        variables['SECTION_9_PARAGRAPHE_2'] = droit.get('paragraphe_2', '')

        # Section 10: Contact
        contact = sections.get('contact', {})
        variables['SECTION_10_TITRE'] = contact.get('titre', '10. Contact')
        variables['SECTION_10_INTRO'] = contact.get('intro', '')
        variables['SECTION_10_EMAIL_LABEL'] = contact.get('email_label', 'Email')
        variables['SECTION_10_TELEPHONE_LABEL'] = contact.get('telephone_label', 'Téléphone')
        variables['SECTION_10_ADRESSE_LABEL'] = contact.get('adresse_label', 'Adresse')
        variables['SECTION_10_ADRESSE_LIGNE1'] = contact.get('adresse_ligne1', 'Square Jean-Baptiste de Greef 9')
        variables['SECTION_10_ADRESSE_LIGNE2'] = contact.get('adresse_ligne2', '1160 Bruxelles, Belgique')

        # CTA Final
        cta = content.get('cta_final', {})
        variables['CTA_FINAL_TITRE'] = cta.get('titre', 'Besoin d\'un dépannage ?')
        variables['CTA_FINAL_SUBTITLE'] = cta.get('subtitle', 'Notre équipe est disponible 24h/24 et 7j/7 pour vous assister')
        variables['CTA_FINAL_BUTTON'] = cta.get('button', 'Appeler Maintenant')

        # Dernière MAJ
        variables['DERNIERE_MAJ'] = content.get('derniere_maj', 'Dernière mise à jour : 30 novembre 2025')

        # Schema.org
        homepage_schema = self.schema_builder.build_homepage_schema()
        variables['SCHEMA_ORG_LOCALBUSINESS'] = self.schema_builder.to_json_ld(homepage_schema)

        # Footer
        self.add_footer_variables(variables)

        # Breadcrumb
        variables['BREADCRUMB_ITEMS'] = self.build_breadcrumb_items('mentions-legales', 'Mentions Légales', variables['PATH_PREFIX'])

        # Injecter toutes les template_variables (URLs, pricing, etc.)
        variables = self.inject_template_variables(variables)

        # Aria labels
        aria_labels = self.ui_translations.get('aria_labels', {})
        variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

        # MULTILINGUAL: Ajouter variables de langue et hreflang
        variables.update(self._get_language_variables("subpage"))
        hreflang_vars = self._generate_hreflang_urls('mentions-legales')
        variables.update(hreflang_vars)

        # Rendre le composant hreflang
        hreflang_html = self.renderer.render('components/hreflang.html', hreflang_vars)
        variables['COMPONENT_HREFLANG'] = hreflang_html

        # Sidebar translations
        sidebar_ui = self.ui_translations.get('sidebar', {})
        services = self.loader.load_services()
        communes = self.loader.load_communes()
        variables['SIDEBAR_POPULAR_SERVICES_TITLE'] = sidebar_ui.get('popular_services_title', 'Services Populaires')
        variables['SIDEBAR_SERVICE_TOWING'] = sidebar_ui.get('service_towing', 'Remorquage de voitures')
        variables['SIDEBAR_SERVICE_BATTERY'] = sidebar_ui.get('service_battery', 'Dépannage batterie')
        variables['SIDEBAR_SERVICE_TIRE'] = sidebar_ui.get('service_tire', 'Réparation pneu')
        variables['SIDEBAR_SERVICE_FUEL'] = sidebar_ui.get('service_fuel', 'Panne d\'essence')
        variables['SIDEBAR_SERVICE_DOOR'] = sidebar_ui.get('service_door', 'Ouverture de porte')
        variables['SIDEBAR_SERVICE_MOTO'] = sidebar_ui.get('service_moto', 'Remorquage de motos')
        variables['SIDEBAR_NEED_HELP_BADGE'] = sidebar_ui.get('need_help_badge', 'Besoin d\'aide ?')
        variables['SIDEBAR_AVAILABILITY'] = sidebar_ui.get('availability', 'Disponible 24h/24 - 7j/7')
        variables['SIDEBAR_SERVICE_AREAS_TITLE'] = sidebar_ui.get('service_areas_title', 'Zones d\'Intervention')
        variables['SIDEBAR_SERVICES_ALL'] = sidebar_ui.get('services_all', 'Voir tous les services ({{NOMBRE_SERVICES}}) →').replace('{{NOMBRE_SERVICES}}', str(len(services)))
        variables['SIDEBAR_NEARBY_ALL'] = sidebar_ui.get('nearby_all', 'Voir toutes les zones ({{NOMBRE_COMMUNES}}) →').replace('{{NOMBRE_COMMUNES}}', str(len(communes)))

        # Sidebar URLs (language-dependent)
        variables['SIDEBAR_SERVICES_URL'] = '../services/'
        variables['SIDEBAR_AREAS_URL'] = '../areas/' if self.lang == 'en' else '../zones/'

        # Rendu
        html = self.renderer.render_with_components('pages/mentions-legales.html', variables)

        # Sauvegarder
        save_path = self._get_page_save_path('mentions-legales')
        self.save_page(html, save_path)
        self.log("✅ Page mentions légales générée")

    def generate_politique_confidentialite(self):
        """Génère la page politique de confidentialité"""
        self.log("\n🔒 === GÉNÉRATION PAGE POLITIQUE DE CONFIDENTIALITÉ ===")

        # Charger le contenu depuis JSON
        filename = self._get_page_content_filename('politique-confidentialite')
        content_path = self.base_path / 'content' / self.lang / 'pages' / filename
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except FileNotFoundError:
            self.log(f"⚠️  Fichier politique-confidentialite.json introuvable: {content_path}")
            content = {}

        # Variables de base
        variables = {
            'PATH_PREFIX': self._get_path_prefix('subpage'),  # Chemins relatifs depuis /politique-confidentialite/
            'TELEPHONE': self.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
            'TELEPHONE_HREF': self.variables.get('contact', {}).get('phone_local', '0479890089'),
            'EMAIL': self.variables.get('contact', {}).get('email', 'bruxelles.car.depannage@hotmail.com'),
            'CANONICAL_URL': f"{self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')}/politique-confidentialite/",
        }

        # Labels UI
        ui_translations = self.loader.load_ui_translations()
        labels = ui_translations.get('labels', {})
        variables['LABEL_NOTE'] = labels.get('note', 'Note :')
        variables['LABEL_EMAIL'] = labels.get('email', 'Email :')
        variables['LABEL_SITE_WEB'] = labels.get('site_web', 'Site web :')

        # Meta et Hero
        variables['META_TITLE'] = content.get('meta_title', 'Politique de Confidentialité | Bruxelles Car Dépannage')
        variables['META_DESCRIPTION'] = content.get('meta_description', '')
        variables['HERO_H1'] = content.get('hero', {}).get('h1', 'Politique de Confidentialité')
        variables['HERO_SUBTITLE'] = content.get('hero', {}).get('subtitle', '')

        # Sections
        sections = content.get('sections', {})

        # Section 1: Introduction
        intro = sections.get('introduction', {})
        variables['SECTION_1_TITRE'] = intro.get('titre', '1. Introduction')
        variables['SECTION_1_PARAGRAPHE_1'] = intro.get('paragraphe_1', '')
        variables['SECTION_1_PARAGRAPHE_2'] = intro.get('paragraphe_2', '')

        # Section 2: Responsable
        responsable = sections.get('responsable', {})
        variables['SECTION_2_TITRE'] = responsable.get('titre', '2. Responsable du traitement')
        variables['SECTION_2_RAISON_SOCIALE_LABEL'] = responsable.get('raison_sociale_label', 'Raison sociale :')
        variables['SECTION_2_RAISON_SOCIALE'] = responsable.get('raison_sociale', 'Bruxelles Car Dépannage SRL')
        variables['SECTION_2_ADRESSE_LABEL'] = responsable.get('adresse_label', 'Adresse :')
        variables['SECTION_2_ADRESSE'] = responsable.get('adresse', 'Square Jean-Baptiste de Greef 9, 1160 Bruxelles, Belgique')
        variables['SECTION_2_EMAIL_LABEL'] = responsable.get('email_label', 'Email :')
        variables['SECTION_2_TELEPHONE_LABEL'] = responsable.get('telephone_label', 'Téléphone :')

        # Section 3: Données collectées
        donnees_collectees = sections.get('donnees_collectees', {})
        variables['SECTION_3_TITRE'] = donnees_collectees.get('titre', '3. Données personnelles collectées')
        variables['SECTION_3_INTRO'] = donnees_collectees.get('intro', '')

        appel = donnees_collectees.get('appel_telephone', {})
        variables['SECTION_3_APPEL_TITRE'] = appel.get('titre', '3.1. Lors d\'un appel téléphonique')
        variables['SECTION_3_APPEL_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in appel.get('liste', [])])

        formulaire = donnees_collectees.get('formulaire', {})
        variables['SECTION_3_FORMULAIRE_TITRE'] = formulaire.get('titre', '3.2. Via le formulaire de contact')
        variables['SECTION_3_FORMULAIRE_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in formulaire.get('liste', [])])

        navigation = donnees_collectees.get('navigation', {})
        variables['SECTION_3_NAVIGATION_TITRE'] = navigation.get('titre', '3.3. Navigation sur le site')
        variables['SECTION_3_NAVIGATION_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in navigation.get('liste', [])])

        # Section 4: Finalités
        finalites = sections.get('finalites', {})
        variables['SECTION_4_TITRE'] = finalites.get('titre', '4. Finalités du traitement')
        variables['SECTION_4_INTRO'] = finalites.get('intro', '')
        variables['SECTION_4_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in finalites.get('liste', [])])

        # Section 5: Base légale
        base_legale = sections.get('base_legale', {})
        variables['SECTION_5_TITRE'] = base_legale.get('titre', '5. Base légale du traitement')
        variables['SECTION_5_INTRO'] = base_legale.get('intro', '')
        variables['SECTION_5_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in base_legale.get('liste', [])])

        # Section 6: Conservation
        conservation = sections.get('conservation', {})
        variables['SECTION_6_TITRE'] = conservation.get('titre', '6. Durée de conservation')
        variables['SECTION_6_INTRO'] = conservation.get('intro', '')
        durees = conservation.get('durees', {})
        variables['SECTION_6_CLIENTS_LABEL'] = durees.get('clients_label', 'Données clients (interventions) :')
        variables['SECTION_6_CLIENTS_DUREE'] = durees.get('clients_duree', '10 ans')
        variables['SECTION_6_CONTACT_LABEL'] = durees.get('contact_label', 'Données de contact (formulaires) :')
        variables['SECTION_6_CONTACT_DUREE'] = durees.get('contact_duree', '3 ans maximum')
        variables['SECTION_6_COOKIES_LABEL'] = durees.get('cookies_label', 'Cookies analytiques :')
        variables['SECTION_6_COOKIES_DUREE'] = durees.get('cookies_duree', '13 mois maximum')
        variables['SECTION_6_LOGS_LABEL'] = durees.get('logs_label', 'Logs de connexion :')
        variables['SECTION_6_LOGS_DUREE'] = durees.get('logs_duree', '12 mois maximum')
        variables['SECTION_6_CONCLUSION'] = conservation.get('conclusion', '')

        # Section 7: Destinataires
        destinataires = sections.get('destinataires', {})
        variables['SECTION_7_TITRE'] = destinataires.get('titre', '7. Destinataires des données')
        variables['SECTION_7_INTRO'] = destinataires.get('intro', '')
        variables['SECTION_7_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in destinataires.get('liste', [])])
        variables['SECTION_7_IMPORTANT'] = destinataires.get('important', 'Nous ne vendons jamais vos données à des tiers.')

        # Section 8: Transferts UE
        transferts = sections.get('transferts_ue', {})
        variables['SECTION_8_TITRE'] = transferts.get('titre', '8. Transferts hors de l\'Union Européenne')
        variables['SECTION_8_PARAGRAPHE_1'] = transferts.get('paragraphe_1', '')
        variables['SECTION_8_PARAGRAPHE_2'] = transferts.get('paragraphe_2', '')
        variables['SECTION_8_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in transferts.get('liste', [])])

        # Section 9: Droits
        droits = sections.get('droits', {})
        variables['SECTION_9_TITRE'] = droits.get('titre', '9. Vos droits')
        variables['SECTION_9_INTRO'] = droits.get('intro', '')

        variables['SECTION_9_ACCES_TITRE'] = droits.get('acces', {}).get('titre', '9.1. Droit d\'accès')
        variables['SECTION_9_ACCES_TEXTE'] = droits.get('acces', {}).get('texte', '')

        variables['SECTION_9_RECTIFICATION_TITRE'] = droits.get('rectification', {}).get('titre', '9.2. Droit de rectification')
        variables['SECTION_9_RECTIFICATION_TEXTE'] = droits.get('rectification', {}).get('texte', '')

        variables['SECTION_9_EFFACEMENT_TITRE'] = droits.get('effacement', {}).get('titre', '9.3. Droit à l\'effacement')
        variables['SECTION_9_EFFACEMENT_TEXTE'] = droits.get('effacement', {}).get('texte', '')

        variables['SECTION_9_LIMITATION_TITRE'] = droits.get('limitation', {}).get('titre', '9.4. Droit à la limitation')
        variables['SECTION_9_LIMITATION_TEXTE'] = droits.get('limitation', {}).get('texte', '')

        variables['SECTION_9_PORTABILITE_TITRE'] = droits.get('portabilite', {}).get('titre', '9.5. Droit à la portabilité')
        variables['SECTION_9_PORTABILITE_TEXTE'] = droits.get('portabilite', {}).get('texte', '')

        variables['SECTION_9_OPPOSITION_TITRE'] = droits.get('opposition', {}).get('titre', '9.6. Droit d\'opposition')
        variables['SECTION_9_OPPOSITION_TEXTE'] = droits.get('opposition', {}).get('texte', '')

        variables['SECTION_9_RETRAIT_TITRE'] = droits.get('retrait_consentement', {}).get('titre', '9.7. Retrait du consentement')
        variables['SECTION_9_RETRAIT_TEXTE'] = droits.get('retrait_consentement', {}).get('texte', '')

        variables['SECTION_9_EXERCER_TITRE'] = droits.get('exercer_titre', 'Pour exercer ces droits, contactez-nous :')
        exercer_liste = droits.get('exercer_liste', [])
        variables['SECTION_9_EXERCER_LISTE'] = '\n'.join([f'<li>{item.replace("{{TELEPHONE}}", variables["TELEPHONE"])}</li>' for item in exercer_liste])
        variables['SECTION_9_DELAI'] = droits.get('delai', '')

        # Section 10: Sécurité
        securite = sections.get('securite', {})
        variables['SECTION_10_TITRE'] = securite.get('titre', '10. Sécurité des données')
        variables['SECTION_10_INTRO'] = securite.get('intro', '')
        variables['SECTION_10_MENACES'] = '\n'.join([f'<li>{item}</li>' for item in securite.get('menaces', [])])
        variables['SECTION_10_MESURES_TITRE'] = securite.get('mesures_titre', 'Mesures de sécurité appliquées :')
        variables['SECTION_10_MESURES'] = '\n'.join([f'<li>{item}</li>' for item in securite.get('mesures', [])])

        # Section 11: Cookies
        cookies = sections.get('cookies', {})
        variables['SECTION_11_TITRE'] = cookies.get('titre', '11. Cookies')
        variables['SECTION_11_INTRO'] = cookies.get('intro', '')

        types = cookies.get('types', {})
        variables['SECTION_11_TYPES_TITRE'] = types.get('titre', '11.1. Types de cookies utilisés')
        variables['SECTION_11_TECHNIQUES_TITRE'] = types.get('techniques_titre', 'Cookies techniques (essentiels) :')
        variables['SECTION_11_TECHNIQUES_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in types.get('techniques_liste', [])])
        variables['SECTION_11_ANALYTIQUES_TITRE'] = types.get('analytiques_titre', 'Cookies analytiques (Google Analytics) :')
        variables['SECTION_11_ANALYTIQUES_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in types.get('analytiques_liste', [])])

        gestion = cookies.get('gestion', {})
        variables['SECTION_11_GESTION_TITRE'] = gestion.get('titre', '11.2. Gestion des cookies')
        variables['SECTION_11_GESTION_INTRO'] = gestion.get('intro', '')
        variables['SECTION_11_GESTION_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in gestion.get('liste', [])])
        variables['SECTION_11_GESTION_NOTE'] = gestion.get('note', '')

        # Section 12: Réclamation
        reclamation = sections.get('reclamation', {})
        variables['SECTION_12_TITRE'] = reclamation.get('titre', '12. Droit de réclamation')
        variables['SECTION_12_INTRO'] = reclamation.get('intro', '')
        variables['SECTION_12_AUTORITE_NOM'] = reclamation.get('autorite_nom', 'Autorité de Protection des Données (APD)')
        variables['SECTION_12_AUTORITE_ADRESSE'] = reclamation.get('autorite_adresse', 'Rue de la Presse 35, 1000 Bruxelles')
        variables['SECTION_12_AUTORITE_EMAIL'] = reclamation.get('autorite_email', 'contact@apd-gba.be')
        variables['SECTION_12_AUTORITE_TELEPHONE'] = reclamation.get('autorite_telephone', '+32 2 274 48 00')
        variables['SECTION_12_AUTORITE_SITE'] = reclamation.get('autorite_site', 'www.autoriteprotectiondonnees.be')
        variables['SECTION_12_AUTORITE_SITE_URL'] = reclamation.get('autorite_site_url', 'https://www.autoriteprotectiondonnees.be')

        # Section 13: Modifications
        modifications = sections.get('modifications', {})
        variables['SECTION_13_TITRE'] = modifications.get('titre', '13. Modifications de la politique')
        variables['SECTION_13_INTRO'] = modifications.get('intro', '')
        variables['SECTION_13_LISTE'] = '\n'.join([f'<li>{item}</li>' for item in modifications.get('liste', [])])
        variables['SECTION_13_CONCLUSION'] = modifications.get('conclusion', '')

        # Section 14: Contact
        contact = sections.get('contact', {})
        variables['SECTION_14_TITRE'] = contact.get('titre', '14. Contact')
        variables['SECTION_14_INTRO'] = contact.get('intro', '')
        variables['SECTION_14_EMAIL_LABEL'] = contact.get('email_label', 'Email')
        variables['SECTION_14_TELEPHONE_LABEL'] = contact.get('telephone_label', 'Téléphone')
        variables['SECTION_14_ADRESSE_LABEL'] = contact.get('adresse_label', 'Adresse')
        variables['SECTION_14_ADRESSE_LIGNE1'] = contact.get('adresse_ligne1', 'Square Jean-Baptiste de Greef 9')
        variables['SECTION_14_ADRESSE_LIGNE2'] = contact.get('adresse_ligne2', '1160 Bruxelles, Belgique')

        # CTA Final
        cta = content.get('cta_final', {})
        variables['CTA_FINAL_TITRE'] = cta.get('titre', 'Besoin d\'un dépannage ?')
        variables['CTA_FINAL_SUBTITLE'] = cta.get('subtitle', 'Notre équipe est disponible 24h/24 et 7j/7 pour vous assister')
        variables['CTA_FINAL_BUTTON'] = cta.get('button', 'Appeler Maintenant')

        # Dernière MAJ
        variables['DERNIERE_MAJ'] = content.get('derniere_maj', 'Dernière mise à jour : 30 novembre 2025')

        # Schema.org
        homepage_schema = self.schema_builder.build_homepage_schema()
        variables['SCHEMA_ORG_LOCALBUSINESS'] = self.schema_builder.to_json_ld(homepage_schema)

        # Footer
        self.add_footer_variables(variables)

        # Breadcrumb
        variables['BREADCRUMB_ITEMS'] = self.build_breadcrumb_items('politique', 'Politique de Confidentialité', variables['PATH_PREFIX'])

        # Injecter toutes les template_variables (URLs, pricing, etc.)
        variables = self.inject_template_variables(variables)

        # Aria labels
        aria_labels = self.ui_translations.get('aria_labels', {})
        variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

        # MULTILINGUAL: Ajouter variables de langue et hreflang
        variables.update(self._get_language_variables("subpage"))
        hreflang_vars = self._generate_hreflang_urls('politique-confidentialite')
        variables.update(hreflang_vars)

        # Rendre le composant hreflang
        hreflang_html = self.renderer.render('components/hreflang.html', hreflang_vars)
        variables['COMPONENT_HREFLANG'] = hreflang_html

        # Sidebar translations
        sidebar_ui = self.ui_translations.get('sidebar', {})
        services = self.loader.load_services()
        communes = self.loader.load_communes()
        variables['SIDEBAR_POPULAR_SERVICES_TITLE'] = sidebar_ui.get('popular_services_title', 'Services Populaires')
        variables['SIDEBAR_SERVICE_TOWING'] = sidebar_ui.get('service_towing', 'Remorquage de voitures')
        variables['SIDEBAR_SERVICE_BATTERY'] = sidebar_ui.get('service_battery', 'Dépannage batterie')
        variables['SIDEBAR_SERVICE_TIRE'] = sidebar_ui.get('service_tire', 'Réparation pneu')
        variables['SIDEBAR_SERVICE_FUEL'] = sidebar_ui.get('service_fuel', 'Panne d\'essence')
        variables['SIDEBAR_SERVICE_DOOR'] = sidebar_ui.get('service_door', 'Ouverture de porte')
        variables['SIDEBAR_SERVICE_MOTO'] = sidebar_ui.get('service_moto', 'Remorquage de motos')
        variables['SIDEBAR_NEED_HELP_BADGE'] = sidebar_ui.get('need_help_badge', 'Besoin d\'aide ?')
        variables['SIDEBAR_AVAILABILITY'] = sidebar_ui.get('availability', 'Disponible 24h/24 - 7j/7')
        variables['SIDEBAR_SERVICE_AREAS_TITLE'] = sidebar_ui.get('service_areas_title', 'Zones d\'Intervention')
        variables['SIDEBAR_SERVICES_ALL'] = sidebar_ui.get('services_all', 'Voir tous les services ({{NOMBRE_SERVICES}}) →').replace('{{NOMBRE_SERVICES}}', str(len(services)))
        variables['SIDEBAR_NEARBY_ALL'] = sidebar_ui.get('nearby_all', 'Voir toutes les zones ({{NOMBRE_COMMUNES}}) →').replace('{{NOMBRE_COMMUNES}}', str(len(communes)))

        # Sidebar URLs (language-dependent)
        variables['SIDEBAR_SERVICES_URL'] = '../services/'
        variables['SIDEBAR_AREAS_URL'] = '../areas/' if self.lang == 'en' else '../zones/'

        # Rendu
        html = self.renderer.render_with_components('pages/politique-confidentialite.html', variables)

        # Sauvegarder
        save_path = self._get_page_save_path('politique-confidentialite')
        self.save_page(html, save_path)
        self.log("✅ Page politique de confidentialité générée")

    def generate_robots_txt(self):
        """Génère le fichier robots.txt (v4.1 - utilise template)"""
        self.log("\n🤖 === GÉNÉRATION ROBOTS.TXT ===")

        # Domaine et nom du site
        domain = self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')
        site_name = self.variables.get('site', {}).get('name', 'Bruxelles Car Depannage')

        # Générer le contenu depuis le template
        robots_content = self.content_builder.build_robots_txt(domain, site_name)

        # Sauvegarder le robots.txt à la racine du build
        robots_path = self.build_dir / 'robots.txt'
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)

        self.log(f"✅ Robots.txt généré: {robots_path}")
        self.log("   - User-agent: * (tous les robots autorisés)")
        self.log("   - Allow: / (tout le site accessible)")
        self.log(f"   - Sitemap: {domain}/sitemap.xml")

    def generate_sitemap(self):
        """Génère le sitemap.xml"""
        self.log("\n🗺️  === GÉNÉRATION SITEMAP.XML ===")

        from datetime import datetime

        # Date actuelle pour lastmod
        today = datetime.now().strftime('%Y-%m-%d')

        # Domaine du site
        domain = self.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

        # Début du sitemap
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

        # Homepage (priorité maximale)
        sitemap += '  <url>\n'
        sitemap += f'    <loc>{domain}/</loc>\n'
        sitemap += f'    <lastmod>{today}</lastmod>\n'
        sitemap += '    <changefreq>weekly</changefreq>\n'
        sitemap += '    <priority>1.0</priority>\n'
        sitemap += '  </url>\n\n'

        # Pages index (services et zones)
        index_pages = [
            {'url': '/services/', 'priority': '0.9'},
            {'url': '/zones/', 'priority': '0.9'}
        ]

        for page in index_pages:
            sitemap += '  <url>\n'
            sitemap += f'    <loc>{domain}{page["url"]}</loc>\n'
            sitemap += f'    <lastmod>{today}</lastmod>\n'
            sitemap += '    <changefreq>weekly</changefreq>\n'
            sitemap += f'    <priority>{page["priority"]}</priority>\n'
            sitemap += '  </url>\n\n'

        # Pages services
        services = self.loader.load_services()
        for service in services:
            slug = service.get('slug', '')
            if slug:
                sitemap += '  <url>\n'
                sitemap += f'    <loc>{domain}/{slug}/</loc>\n'
                sitemap += f'    <lastmod>{today}</lastmod>\n'
                sitemap += '    <changefreq>monthly</changefreq>\n'
                sitemap += '    <priority>0.8</priority>\n'
                sitemap += '  </url>\n'

        sitemap += '\n'

        # Pages communes
        communes = self.loader.load_communes()
        for commune in communes:
            slug = commune.get('slug', '')
            if slug:
                sitemap += '  <url>\n'
                sitemap += f'    <loc>{domain}/{slug}/</loc>\n'
                sitemap += f'    <lastmod>{today}</lastmod>\n'
                sitemap += '    <changefreq>monthly</changefreq>\n'
                sitemap += '    <priority>0.7</priority>\n'
                sitemap += '  </url>\n'

        sitemap += '\n'

        # Pages utilitaires
        utility_pages = [
            {'url': '/tarifs/', 'priority': '0.6'},
            {'url': '/contact/', 'priority': '0.6'},
            {'url': '/a-propos/', 'priority': '0.6'}
        ]

        for page in utility_pages:
            sitemap += '  <url>\n'
            sitemap += f'    <loc>{domain}{page["url"]}</loc>\n'
            sitemap += f'    <lastmod>{today}</lastmod>\n'
            sitemap += '    <changefreq>monthly</changefreq>\n'
            sitemap += f'    <priority>{page["priority"]}</priority>\n'
            sitemap += '  </url>\n'

        sitemap += '\n'

        # Pages légales (priorité basse)
        legal_pages = [
            {'url': '/mentions-legales/', 'priority': '0.3'},
            {'url': '/politique-confidentialite/', 'priority': '0.3'}
        ]

        for page in legal_pages:
            sitemap += '  <url>\n'
            sitemap += f'    <loc>{domain}{page["url"]}</loc>\n'
            sitemap += f'    <lastmod>{today}</lastmod>\n'
            sitemap += '    <changefreq>yearly</changefreq>\n'
            sitemap += f'    <priority>{page["priority"]}</priority>\n'
            sitemap += '  </url>\n'

        # Fin du sitemap
        sitemap += '</urlset>\n'

        # Sauvegarder le sitemap à la racine du build
        sitemap_path = self.build_dir / 'sitemap.xml'
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap)

        self.log(f"✅ Sitemap généré: {sitemap_path}")
        self.log(f"   - Homepage: 1")
        self.log(f"   - Pages index: 2")
        self.log(f"   - Services: {len(services)}")
        self.log(f"   - Communes: {len(communes)}")
        self.log(f"   - Utilitaires: 3")
        self.log(f"   - Légales: 2")
        self.log(f"   - TOTAL: {1 + 2 + len(services) + len(communes) + 3 + 2} URLs")

    def generate_all(self):
        """Génère toutes les pages du site"""
        self.log("\n" + "=" * 60)
        self.log(f"🚀 GÉNÉRATION COMPLÈTE DU SITE ({self.lang.upper()})")
        self.log("=" * 60)

        self.ensure_build_dir()

        # Statistiques
        stats = self.loader.get_stats()
        self.log(f"\n📊 STATISTIQUES:")
        self.log(f"   - Services: {stats['total_services']} ({stats['google_aligned']} Google + {stats['supplementary']} Supplémentaires)")
        self.log(f"   - Catégories: {stats['remorquage']} Remorquage + {stats['depannage']} Dépannage")
        self.log(f"   - Communes: {stats['total_communes']}")
        self.log(f"   - Langue: {self.lang.upper()}")

        # Génération du CSS depuis la configuration
        self.log("\n🎨 === GÉNÉRATION CSS ===")
        css_gen = CSSGenerator(base_path=self.base_path)
        css_gen.generate(verbose=self.verbose)

        # Copie de tous les fichiers CSS vers build
        self.copy_css_files()

        # Copie de toutes les images vers build
        self.log("\n🖼️  === COPIE DES IMAGES ===")
        self.copy_images()

        # Optimisation automatique des images (conversion WebP + redimensionnement)
        self.log("\n⚡ === OPTIMISATION DES IMAGES ===")
        self.optimize_images()

        # Génération des pages HTML
        self.generate_homepage()
        self.generate_zones_index()
        self.generate_services_index()
        self.generate_tarifs()
        self.generate_contact()
        self.generate_a_propos()
        self.generate_mentions_legales()
        self.generate_politique_confidentialite()
        self.generate_all_services()
        self.generate_all_communes()

        # Génération du sitemap.xml et robots.txt
        self.generate_sitemap()
        self.generate_robots_txt()

        total_pages = 8 + stats['total_services'] + stats['total_communes']

        self.log("\n" + "=" * 60)
        self.log(f"✅ GÉNÉRATION TERMINÉE : {total_pages} pages créées")
        self.log(f"📁 Build directory: {self.build_dir}")
        self.log("=" * 60)

    def get_build_stats(self):
        """Retourne les statistiques du build"""
        if not self.build_dir.exists():
            return None

        html_files = list(self.build_dir.glob('*.html'))

        return {
            'total_files': len(html_files),
            'build_dir': str(self.build_dir),
            'language': self.lang
        }


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Générateur de site statique Bruxelles Car Depannage v3.0'
    )

    parser.add_argument(
        '--lang', '-l',
        choices=['fr', 'en', 'nl'],
        default='fr',
        help='Langue de génération'
    )

    parser.add_argument(
        '--all-langs',
        action='store_true',
        help='Générer toutes les langues (fr, en, nl)'
    )

    parser.add_argument(
        '--services-only',
        action='store_true',
        help='Générer uniquement les pages services'
    )

    parser.add_argument(
        '--communes-only',
        action='store_true',
        help='Générer uniquement les pages communes'
    )

    parser.add_argument(
        '--homepage-only',
        action='store_true',
        help='Générer uniquement la homepage'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Mode silencieux'
    )

    args = parser.parse_args()

    # Déterminer les langues à générer
    languages = ['fr', 'en', 'nl'] if args.all_langs else [args.lang]

    # Génération pour chaque langue
    for lang in languages:
        generator = SiteGenerator(
            base_path='.',
            lang=lang,
            verbose=not args.quiet
        )

        if args.services_only:
            generator.ensure_build_dir()
            generator.copy_css_files()
            generator.generate_all_services()
        elif args.communes_only:
            generator.ensure_build_dir()
            generator.copy_css_files()
            generator.generate_all_communes()
        elif args.homepage_only:
            generator.ensure_build_dir()
            generator.copy_css_files()  # Copie aussi les JS
            generator.copy_images()
            generator.log("\n⚡ === OPTIMISATION DES IMAGES ===")
            generator.optimize_images()
            generator.generate_homepage()
        else:
            generator.generate_all()

        # Afficher stats
        if not args.quiet:
            stats = generator.get_build_stats()
            if stats:
                print(f"\n📈 Build stats: {stats['total_files']} fichiers générés")


if __name__ == '__main__':
    main()
