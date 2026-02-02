#!/usr/bin/env python3
"""
Breadcrumb Builder Module - v1.0
Description: Génère des breadcrumbs dynamiques depuis templates Jinja2
Date: 2025-12-17
"""

import json
from pathlib import Path


class BreadcrumbBuilder:
    """
    Construit des breadcrumbs HTML depuis templates Jinja2
    """

    def __init__(self, base_path, lang='fr', template_renderer=None, translations=None):
        """
        Initialise le BreadcrumbBuilder

        Args:
            base_path (Path): Chemin racine du projet
            lang (str): Code langue (fr, en, nl)
            template_renderer (TemplateRenderer): Instance du renderer
            translations (dict): Traductions des composants
        """
        self.base_path = Path(base_path)
        self.lang = lang
        self.renderer = template_renderer
        self.translations = translations or {}

    def build_breadcrumb_items(self, breadcrumb_type, name='', path_prefix='../'):
        """
        Génère les items du breadcrumb selon le type de page (v4.1 - utilise template Jinja2)

        Args:
            breadcrumb_type (str): Type de breadcrumb ('service', 'commune', 'contact', etc.)
            name (str): Nom de la page actuelle (optionnel)
            path_prefix (str): Préfixe de chemin pour les liens

        Returns:
            str: HTML des items du breadcrumb
        """
        breadcrumb_translations = self.translations.get('breadcrumb', {})
        items = []

        if breadcrumb_type == 'service':
            # Accueil > Services > [Service Name]
            items = [
                {
                    'name': breadcrumb_translations.get('services', 'Services'),
                    'url': f'{path_prefix}services/index.html',
                    'position': 2,
                    'is_current': False
                },
                {
                    'name': name,
                    'url': '',
                    'position': 3,
                    'is_current': True
                }
            ]

        elif breadcrumb_type == 'commune':
            # Accueil > Zones > [Commune Name]
            items = [
                {
                    'name': breadcrumb_translations.get('zones_index', "Zones d'Intervention"),
                    'url': f'{path_prefix}zones/index.html',
                    'position': 2,
                    'is_current': False
                },
                {
                    'name': name,
                    'url': '',
                    'position': 3,
                    'is_current': True
                }
            ]

        elif breadcrumb_type == 'services-index':
            # Accueil > Services
            items = [
                {
                    'name': breadcrumb_translations.get('services_index', 'Nos Services'),
                    'url': '',
                    'position': 2,
                    'is_current': True
                }
            ]

        elif breadcrumb_type == 'zones-index':
            # Accueil > Zones
            items = [
                {
                    'name': breadcrumb_translations.get('zones_index', "Zones d'Intervention"),
                    'url': '',
                    'position': 2,
                    'is_current': True
                }
            ]

        else:
            # Pages utilitaires : Accueil > [Page Name]
            items = [
                {
                    'name': name,
                    'url': '',
                    'position': 2,
                    'is_current': True
                }
            ]

        # Générer le HTML des items en Python
        items_html = ''
        for item in items:
            if item['is_current']:
                # Item actuel (sans lien)
                items_html += f'''
      <li class="breadcrumb-item" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
        <span class="breadcrumb-link" aria-current="page" itemprop="name">{item['name']}</span>
        <meta itemprop="position" content="{item['position']}" />
      </li>'''
            else:
                # Item avec lien
                items_html += f'''
      <li class="breadcrumb-item" itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
        <a class="breadcrumb-link" itemprop="item" href="{item['url']}">
          <span itemprop="name">{item['name']}</span>
        </a>
        <meta itemprop="position" content="{item['position']}" />
      </li>'''

        return items_html
