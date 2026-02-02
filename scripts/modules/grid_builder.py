"""
Module de construction de grilles, listes, cartes et tags
Extrait du SiteGenerator pour améliorer la modularité (Refactoring #6)
"""

from modules.service_icons import get_service_icon, get_service_photo

# LEGACY - ancien dictionnaire déplacé dans service_icons.py
_REMOVED_SERVICE_ICONS = {
    # Remorquage Voiture → dépanneuse
    'remorquage-voiture': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 14l1-3h4l3-4h5l2 4h5l1 3"/><circle cx="6.5" cy="16.5" r="2.5"/><circle cx="17.5" cy="16.5" r="2.5"/><path d="M9 17H15"/><path d="M5 9V6l3-2"/></svg>',
    # Dépannage Batterie → batterie
    'batterie': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M7 7V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2"/><path d="M13 7V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2"/><path d="M6 14h4"/><path d="M8 12v4"/><path d="M14 14h4"/></svg>',
    # Réparation Pneu → pneu
    'reparation-pneu': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/><path d="M12 2v4"/><path d="M12 18v4"/><path d="M2 12h4"/><path d="M18 12h4"/></svg>',
    # Fourniture Carburant → pompe à essence
    'fourniture-carburant': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 22V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v17"/><path d="M15 10h2a2 2 0 0 1 2 2v3a2 2 0 0 0 2 2h0a2 2 0 0 0 2-2V8l-3-3"/><rect x="5" y="8" width="8" height="5" rx="1"/><path d="M3 22h12"/></svg>',
    # Remorquage Moto → moto
    'remorquage-moto': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M5 14l4-7h4l2 3h3"/><path d="M9 7l-1 3"/><path d="M16 10l3 4"/></svg>',
    # Véhicules Spéciaux → camion
    'remorquage-vehicules-speciaux': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
    # Remplacement Batterie → batterie + clé
    'remplacement-batterie': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="8" width="16" height="12" rx="2"/><path d="M5 8V6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2"/><path d="M11 8V6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2"/><path d="M4 14h4"/><path d="M6 12v4"/><path d="M19 4l3 3-5 5-2-2 4-6z"/></svg>',
    # Transport Routier Local → camion plateau
    'transport-routier-local': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="6" width="15" height="10" rx="1"/><path d="M16 9h4l3 4v3h-7V9z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/><path d="M8 16h6"/></svg>',
    # Transport Longue Distance → camion + flèche
    'transport-routier-longue-distance': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="6" width="15" height="10" rx="1"/><path d="M16 9h4l3 4v3h-7V9z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/><path d="M3 3h8l2 2-2 2H3"/></svg>',
    # Ouverture Porte Voiture → clé/serrure
    'ouverture-de-porte': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="10" r="6"/><circle cx="8" cy="10" r="2"/><path d="M14 10h8"/><path d="M18 7v6"/><path d="M22 7v6"/></svg>',
    # Panne d'Essence → jauge vide
    'panne-essence': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 22V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v17"/><rect x="5" y="8" width="8" height="5" rx="1"/><path d="M3 22h12"/><path d="M19 10l2-2"/><path d="M18 5l3 3"/><line x1="12" y1="16" x2="6" y2="12" stroke-dasharray="2 2"/></svg>',
    # Placement Roue de Secours → roue
    'placement-roue-secours': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="M12 2v6"/><path d="M12 16v6"/><path d="M2 12h6"/><path d="M16 12h6"/></svg>',
    # Dépannage Parking Souterrain → parking
    'depannage-parking-souterrain': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/></svg>',
    # Voiture Embourbée → voiture enlisée
    'voiture-embourbee': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 14l2-4h4l2-3h5l2 3h3l1 4"/><circle cx="6.5" cy="16.5" r="2.5"/><circle cx="17.5" cy="16.5" r="2.5"/><path d="M2 20c1-1 3-1 4 0s3 1 4 0 3-1 4 0 3 1 4 0"/><path d="M1 23c1-1 3-1 4 0s3 1 4 0 3-1 4 0 3 1 4 0"/></svg>',
    # Siphonnage Réservoir → avertissement carburant
    'erreur-carburant': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4"/><circle cx="12" cy="16" r="0.5" fill="currentColor"/></svg>',
    # Enlèvement Épave → recyclage
    'enlevement-epave': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19H2v-5"/><path d="M17 5h5v5"/><path d="M2 14l5.7 5.7a1 1 0 0 0 1.4 0L12 17"/><path d="M22 10l-5.7-5.7a1 1 0 0 0-1.4 0L12 7"/><path d="M12 7v10"/></svg>',
    # Panne Moteur → moteur
    'panne-moteur': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10h10v6H7z"/><path d="M5 10V8h2v2"/><path d="M17 10V8h2v2"/><path d="M5 16v2h2v-2"/><path d="M17 16v2h2v-2"/><path d="M9 10V6"/><path d="M15 10V6"/><path d="M3 13h4"/><path d="M17 13h4"/></svg>',
    # Sortie de Fourrière → barrière
    'sortie-fourriere': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="4" height="18" rx="1"/><path d="M7 8h14"/><path d="M7 5h10"/><path d="M7 11h8"/><circle cx="5" cy="14" r="1" fill="currentColor"/><path d="M5 16v5"/></svg>',
    # Dépannage Voiture Électrique → éclair
    'depannage-voiture-electrique': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    # Dépannage Accident → voiture + croix
    'depannage-accident': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 14l2-4h4l2-3h5l2 3h3l1 4"/><circle cx="6.5" cy="16.5" r="2.5"/><circle cx="17.5" cy="16.5" r="2.5"/><path d="M14 2l-4 4m0-4l4 4"/></svg>',
    # Dépannage Voiture → clé à molette
    'depannage-voiture': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    # Dépannage Camionnette → utilitaire
    'depannage-camionnette': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="15" height="12" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
    # Siphonnage Réservoir (slug alternatif)
    'siphonnage-reservoir': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4"/><circle cx="12" cy="16" r="0.5" fill="currentColor"/></svg>',
    # Remorquage Motos (slug alternatif)
    'remorquage-motos': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M5 14l4-7h4l2 3h3"/><path d="M9 7l-1 3"/><path d="M16 10l3 4"/></svg>',
    # Dépannage Batterie (slug alternatif)
    'depannage-batterie': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M7 7V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2"/><path d="M13 7V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2"/><path d="M6 14h4"/><path d="M8 12v4"/><path d="M14 14h4"/></svg>',
    # Ouverture Porte Voiture (slug alternatif)
    'ouverture-porte-voiture': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="10" r="6"/><circle cx="8" cy="10" r="2"/><path d="M14 10h8"/><path d="M18 7v6"/><path d="M22 7v6"/></svg>',
}

# Icône par défaut (clé à molette)
DEFAULT_SERVICE_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>'


def build_commune_services_cards(generator, limit=6, commune_id=1, path_prefix='../'):
    """
    Génère les cartes services pour une page commune (v4.1 - utilise CardBuilder avec rotation)

    Args:
        generator (SiteGenerator): Instance du générateur
        limit (int): Nombre de services à afficher
        commune_id (int): ID de la commune (pour rotation circulaire)
        path_prefix (str): Préfixe de chemin pour les liens

    Returns:
        str: HTML des cartes services
    """
    services = generator.loader.load_services()

    # Trier par priorité
    services_sorted = sorted(services, key=lambda x: x.get('priority', 999))

    # Rotation circulaire avec multiplicateur premier (7) pour meilleure distribution
    start_index = ((commune_id - 1) * 7) % len(services_sorted)

    selected_services = []
    for i in range(limit):
        service_index = (start_index + i) % len(services_sorted)
        selected_services.append(services_sorted[service_index])

    return generator.card_builder.build_commune_services_cards(selected_services, path_prefix)


def build_commune_why_cards(generator):
    """
    Génère les cartes "Pourquoi nous" (v4.1 - utilise ContentBuilder + template Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur

    Returns:
        str: HTML des cartes
    """
    return generator.content_builder.build_why_cards()


def build_communes_voisines_tags(generator, commune_slug, limit=5, path_prefix='../'):
    """
    Génère les tags des communes voisines (v4.3 - Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur
        commune_slug (str): Slug de la commune actuelle
        limit (int): Nombre de communes à afficher
        path_prefix (str): Préfixe de chemin pour les liens

    Returns:
        str: HTML des tags communes
    """
    voisines = generator.loader.get_communes_voisines(commune_slug)

    return generator.renderer.render_jinja2('components/communes-voisines-tags.html', {
        'voisines': voisines[:limit],
        'path_prefix': path_prefix
    })


def build_zones_tags(generator, limit=12, path_prefix=''):
    """
    Génère les tags des communes pour la section zones (v4.2 - Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur
        limit (int): Nombre de communes à afficher
        path_prefix (str): Préfixe de chemin pour les liens

    Returns:
        str: HTML des tags zones
    """
    communes = generator.loader.load_communes()
    featured_communes = communes[:limit] if len(communes) > limit else communes

    return generator.renderer.render_jinja2('components/zones-tags.html', {
        'communes': featured_communes,
        'path_prefix': path_prefix
    })


def build_communes_grid(generator, path_prefix='../'):
    """
    Génère les cartes de communes pour la page zones index (v4.2 - Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur
        path_prefix (str): Préfixe de chemin pour les liens

    Returns:
        str: HTML de la grille communes
    """
    communes = generator.loader.load_communes()
    voir_services_text = generator.ui_translations.get('links', {}).get('voir_services', 'Voir les services →')

    return generator.renderer.render_jinja2('components/communes-grid.html', {
        'communes': communes,
        'path_prefix': path_prefix,
        'voir_services_text': voir_services_text
    })


def build_footer_communes_links(generator, limit=6, path_prefix=''):
    """
    Génère les liens des communes pour le footer (v4.3 - Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur
        limit (int): Nombre de communes à afficher (défaut: 6)
        path_prefix (str): Préfixe de chemin pour les liens ('' pour homepage, '../' pour sous-pages)

    Returns:
        str: HTML des liens <li> pour le footer
    """
    communes = generator.loader.load_communes()
    communes_sorted = sorted(communes, key=lambda x: int(x.get('priority', 999)))

    return generator.renderer.render_jinja2('components/footer-communes-links.html', {
        'communes': communes_sorted[:limit],
        'path_prefix': path_prefix
    })


def build_zones_intervention_9_communes(generator, current_service_id=1, path_prefix='../'):
    """
    Génère le contenu Zones d'intervention (v4.1 - utilise SidebarBuilder)

    Args:
        generator (SiteGenerator): Instance du générateur
        current_service_id (int): ID du service actuel (pour rotation)
        path_prefix (str): Préfixe de chemin pour les liens

    Returns:
        str: HTML complet des 2 paragraphes
    """
    return generator.sidebar_builder.build_zones_intervention_9_communes(current_service_id, path_prefix)


def build_services_grid(generator, services, path_prefix=''):
    """
    Construit les cartes de services pour homepage (sans wrapper div)

    Args:
        generator (SiteGenerator): Instance du générateur
        services (list): Liste des services
        path_prefix (str): Préfixe de chemin pour les liens

    Returns:
        str: HTML des cartes services (le template fournit le wrapper)
    """
    html = ''
    for service in services:
        slug = service.get('slug', '')
        svg_icon = get_service_icon(slug)
        photo_path = get_service_photo(slug, path_prefix)
        photo_html = f'<div class="service-photo"><img src="{photo_path}" alt="{service["name"]}" width="400" height="250" loading="lazy"></div>' if photo_path else ''

        html += f'''
            <a href="{path_prefix}{service['slug']}/index.html" class="service-card">
                {photo_html}
                <div class="service-icon">
                    {svg_icon}
                </div>
                <h3>{service['name']}</h3>
                <p>{service['meta_description'][:120]}...</p>
                <span class="service-link">{service['name']} →</span>
            </a>
            '''
    return html


def build_services_cards_compact(generator, services, path_prefix='../'):
    """
    Génère les cartes services compactes (v4.1 - utilise CardBuilder)

    Args:
        generator (SiteGenerator): Instance du générateur
        services (list): Liste des services
        path_prefix (str): Préfixe de chemin pour les liens

    Returns:
        str: HTML des cartes services
    """
    return generator.card_builder.build_services_cards_compact(services, path_prefix)
