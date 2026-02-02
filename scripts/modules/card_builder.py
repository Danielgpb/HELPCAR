#!/usr/bin/env python3
"""
Card Builder Module - v1.0
Description: Génère des cartes HTML (services, communes) depuis templates Jinja2
Date: 2025-12-17
"""

from pathlib import Path
from modules.service_icons import get_service_icon


class CardBuilder:
    """
    Construit des cartes HTML depuis templates Jinja2
    """

    def __init__(self, base_path, lang='fr', template_renderer=None, icon_getter=None):
        """
        Initialise le CardBuilder

        Args:
            base_path (Path): Chemin racine du projet
            lang (str): Code langue (fr, en, nl)
            template_renderer (TemplateRenderer): Instance du renderer
            icon_getter (callable): Fonction pour récupérer le chemin d'une icône
        """
        self.base_path = Path(base_path)
        self.lang = lang
        self.renderer = template_renderer
        self._get_service_icon = icon_getter

    def build_services_cards_compact(self, services, path_prefix='../'):
        """
        Génère les cartes services compactes depuis template

        Args:
            services (list): Liste des services
            path_prefix (str): Préfixe de chemin pour les liens

        Returns:
            str: HTML des cartes services
        """
        # Charger le template
        template = self.renderer.load_template('components/service-cards-compact.html')

        # Générer le HTML des cartes
        cards_html = ''
        for service in services:
            # Utiliser les icônes SVG inline
            icon_html = get_service_icon(service['slug'])

            # Tronquer la description à 100 caractères
            description = service.get('meta_description', '')
            if len(description) > 100:
                description = description[:100] + '...'

            cards_html += f'''
            <a href="{path_prefix}{service['slug']}/index.html" class="service-card">
                <div class="service-icon">
                    {icon_html}
                </div>
                <h3 class="service-title">{service['name']}</h3>
                <p class="service-excerpt">{description}</p>
                <span class="service-link">
                    {service['name']}
                    <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
                    </svg>
                </span>
            </a>
            '''

        variables = {
            'SERVICE_CARDS': cards_html
        }

        return self.renderer.render(template, variables)

    def build_commune_services_cards(self, services, path_prefix='../'):
        """
        Génère les cartes services pour une page commune (similaire à compact)

        Args:
            services (list): Liste des services
            path_prefix (str): Préfixe de chemin pour les liens

        Returns:
            str: HTML des cartes services
        """
        # Pour l'instant, on réutilise le même template compact
        # On peut créer un template spécifique plus tard si besoin
        services_data = []
        for service in services:
            # Utiliser les icônes SVG inline
            icon_html = get_service_icon(service['slug'])

            # Tronquer la description à 100 caractères
            description = service.get('meta_description', '')[:100] + '...'

            # Pour ce cas, générer HTML directement (legacy)
            html = f'''
            <a href="{path_prefix}{service['slug']}/index.html" class="service-commune-card">
                <div class="service-icon">{icon_html}</div>
                <h3>{service['name']}</h3>
                <p>{description}</p>
                <span class="service-link">{service['name']} →</span>
            </a>
            '''
            services_data.append(html)

        return ''.join(services_data)
