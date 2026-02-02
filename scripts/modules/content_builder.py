#!/usr/bin/env python3
"""
Content Builder Module - v1.0
Description: Génère du HTML depuis des templates Jinja2 (remplace le HTML hardcodé)
Date: 2025-12-17
"""

import json
from pathlib import Path
from modules.service_icons import get_service_icon


class ContentBuilder:
    """
    Construit du contenu HTML depuis des templates Jinja2
    Remplace les fonctions build_* qui généraient du HTML en Python
    """

    def __init__(self, base_path, lang='fr', template_renderer=None):
        """
        Initialise le ContentBuilder

        Args:
            base_path (Path): Chemin racine du projet
            lang (str): Code langue (fr, en, nl)
            template_renderer (TemplateRenderer): Instance du renderer
        """
        self.base_path = Path(base_path)
        self.lang = lang
        self.renderer = template_renderer

        # Charger les traductions des composants
        self.components_translations = self._load_components_translations()

        # Charger les defaults (commune et service)
        self.commune_defaults = self._load_defaults('commune-defaults.json')
        self.service_defaults = self._load_defaults('service-defaults.json')

    def _load_components_translations(self):
        """Charge locales/fr/components.json"""
        file_path = self.base_path / 'locales' / self.lang / 'components.json'

        if not file_path.exists():
            print(f"⚠️  Fichier components.json introuvable : {file_path}")
            return {}

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_defaults(self, filename):
        """Charge content/fr/defaults/{filename}"""
        file_path = self.base_path / 'content' / self.lang / 'defaults' / filename

        if not file_path.exists():
            print(f"⚠️  Fichier defaults introuvable : {file_path}")
            return {}

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def build_faq_section(self, faq_data):
        """
        Construit une section FAQ depuis le template Jinja2

        Args:
            faq_data (list): Liste de dict avec 'question' et 'answer'

        Returns:
            str: HTML de la section FAQ
        """
        if not faq_data or len(faq_data) == 0:
            return ''

        # Charger le template FAQ
        template = self.renderer.load_template('components/faq-section.html')

        # Construire le HTML des items FAQ (style simple card - pas d'accordéon)
        faq_items_html = ''
        for item in faq_data:
            question = item.get('question', '')
            answer = item.get('answer', '')
            faq_items_html += f'''
            <div class="faq-item">
              <h3 class="faq-question">{question}</h3>
              <div class="faq-answer">
                <p>{answer}</p>
              </div>
            </div>
            '''

        variables = {
            'FAQ_LABEL': self.components_translations.get('faq', {}).get('section_label', 'FAQ'),
            'FAQ_TITLE': self.components_translations.get('faq', {}).get('section_title', 'Questions Fréquentes'),
            'FAQ_ITEMS': faq_items_html
        }

        return self.renderer.render(template, variables)

    def build_hero_badges(self, badge_ids):
        """
        Construit les badges hero depuis le template

        Args:
            badge_ids (list): Liste des IDs de badges (ex: ['intervention_rapide', 'disponible_24_7'])

        Returns:
            str: HTML des badges
        """
        # Charger le template
        template = self.renderer.load_template('components/hero-badges.html')

        badges_dict = self.components_translations.get('badges', {})

        # Générer le HTML des badges
        badges_html = ''
        for badge_id in badge_ids:
            badge_text = badges_dict.get(badge_id, badge_id)
            badges_html += f'<span class="badge">{badge_text}</span>\n'

        variables = {
            'BADGES_HTML': badges_html
        }

        return self.renderer.render(template, variables)

    def build_why_cards(self):
        """
        Construit les cartes "Pourquoi Nous" depuis le template

        Returns:
            str: HTML des cartes
        """
        # Charger le template
        template = self.renderer.load_template('components/why-cards.html')

        why_cards = self.components_translations.get('why_cards', {}).get('cards', [])

        # Générer le HTML des cartes
        cards_html = ''
        for card in why_cards:
            icon = card.get('icon', '✓')
            title = card.get('title', '')
            text = card.get('text', '')
            cards_html += f'''
<div class="why-commune-card">
  <div class="why-icon">{icon}</div>
  <h3>{title}</h3>
  <p>{text}</p>
</div>
'''

        variables = {
            'WHY_CARDS_HTML': cards_html
        }

        return self.renderer.render(template, variables)

    def build_service_cards(self, services, path_prefix='../'):
        """
        Construit les cartes services depuis le template (si créé plus tard)

        Args:
            services (list): Liste des services
            path_prefix (str): Préfixe de chemin pour les liens

        Returns:
            str: HTML des cartes services
        """
        # Pour l'instant, on garde la génération Python (à migrer plus tard)
        # Ce sera fait dans une prochaine itération
        html = ''
        for service in services:
            # Génération simplifiée (à remplacer par template)
            icon_html = get_service_icon(service.get('slug', ''))

            html += f'''
            <a href="{path_prefix}{service['slug']}/index.html" class="service-commune-card">
                <div class="service-icon">{icon_html}</div>
                <h3>{service['name']}</h3>
                <p>{service.get('meta_description', '')[:100]}...</p>
                <span class="service-link">{service['name']} →</span>
            </a>
            '''

        return html

    def get_commune_default_content(self, commune_name, field):
        """
        Récupère le contenu par défaut d'une commune avec remplacement de variables

        Args:
            commune_name (str): Nom de la commune
            field (str): Champ demandé (ex: 'content_h2_1_template')

        Returns:
            str: Contenu avec {{COMMUNE_NAME}} remplacé
        """
        template = self.commune_defaults.get(field, '')
        return template.replace('{{COMMUNE_NAME}}', commune_name)

    def get_service_default_content(self, service_name, field):
        """
        Récupère le contenu par défaut d'un service avec remplacement de variables

        Args:
            service_name (str): Nom du service
            field (str): Champ demandé (ex: 'hero.subtitle_default')

        Returns:
            str: Contenu avec {{SERVICE_NAME}} remplacé
        """
        # Naviguer dans la structure JSON (ex: 'hero.subtitle_default')
        keys = field.split('.')
        value = self.service_defaults

        for key in keys:
            value = value.get(key, '')
            if not value:
                break

        if isinstance(value, str):
            return value.replace('{{SERVICE_NAME}}', service_name)

        return value

    def build_robots_txt(self, domain, site_name):
        """
        Génère le contenu robots.txt depuis le template

        Args:
            domain (str): Domaine du site
            site_name (str): Nom du site

        Returns:
            str: Contenu du robots.txt
        """
        template_path = self.base_path / 'config' / 'robots.txt.template'

        if not template_path.exists():
            print(f"⚠️  Template robots.txt introuvable : {template_path}")
            return ''

        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Remplacer les variables
        content = template.replace('{{DOMAIN}}', domain)
        content = content.replace('{{SITE_NAME}}', site_name)

        return content
