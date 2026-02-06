"""
Module de construction de pages complètes
Extrait du SiteGenerator pour améliorer la modularité (Refactoring #6)
"""

import json


def build_service_page(generator, service_data):
    """
    Génère une page service

    Args:
        generator (SiteGenerator): Instance du générateur
        service_data (dict): Données du service depuis Schema.org

    Returns:
        str: HTML complet de la page
    """
    generator.log(f"  🔧 Génération: {service_data['name']}")

    # Domain depuis variables
    domain = generator.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

    # Architecture v4.1 : Charger le contenu depuis JSON
    content_data = generator.load_service_content(service_data['slug'])

    # Variables de base (core data + SEO data from config)
    variables = {
        # SEO depuis config/core/services/services-fr.json
        'META_TITLE': service_data.get('meta_title', ''),
        'META_DESCRIPTION': service_data.get('meta_description', ''),
        'KEYWORDS': ', '.join(service_data.get('seo_related_keywords', [])),

        # Hero depuis content JSON
        'H1': content_data.get('hero', {}).get('h1', service_data['name']),

        # Core data
        'PATH_PREFIX': generator._get_path_prefix('subpage'),  # Chemins relatifs depuis sous-dossier /service/
        'CANONICAL_URL': f"{domain}/{service_data['slug']}/",
        # Carrousel Open Graph (2 images)
        'OG_IMAGE_1': f"{domain}/images/og/helpcar-depannage-bruxelles.jpg",
        'OG_IMAGE_2': f"{domain}/images/og/helpcar-depannage-bruxelles.jpg",
        'SERVICE_NAME': service_data['name'],
        'SERVICE_IMAGE': '../images/services/depannage.webp',  # Image par défaut pour tous les services
        'SERVICE_HERO_IMAGE': '../images/service/service.webp?v=3',  # Image par défaut pour le hero
        'SERVICE_ICON': service_data.get('icon', ''),
        'LANGUAGE': generator.lang,
        'TELEPHONE': generator.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
        'TELEPHONE_HREF': generator.variables.get('contact', {}).get('phone_local', '0479890089'),
        'GOOGLE_RATING': generator.variables.get('google', {}).get('rating', '4.9'),
        'GOOGLE_REVIEWS': generator.variables.get('google', {}).get('reviews_count', '190'),
        'GOOGLE_MY_BUSINESS_URL': generator.variables.get('google', {}).get('my_business_url', '#'),
        'FACEBOOK_URL': generator.variables.get('social', {}).get('facebook_url', '#'),
        'INSTAGRAM_URL': generator.variables.get('social', {}).get('instagram_url', '#'),
    }

    # Calculer NOMBRE_COMMUNES depuis locations actives
    communes = generator.loader.load_communes()
    variables['NOMBRE_COMMUNES'] = len(communes)

    # Téléphone cliquable (v4.2)
    phone_international = generator.variables.get('contact', {}).get('phone', '+32479890089')
    phone_display = generator.variables.get('contact', {}).get('phone_local', '0479 89 00 89')
    variables['TELEPHONE_LINK'] = f'<a href="tel:{phone_international}">{phone_display}</a>'

    # Communes actives avec liens (v4.3) - rotation basée sur service_id pour meilleur maillage
    communes_sorted = sorted(communes, key=lambda x: x.get('priority', 999))
    service_id = content_data.get('service_id', 1)
    # Rotation circulaire : chaque service affiche 4 communes différentes
    start_index = ((service_id - 1) * 4) % len(communes_sorted)
    selected_communes = []
    for i in range(4):
        commune_index = (start_index + i) % len(communes_sorted)
        selected_communes.append(communes_sorted[commune_index])
    communes_links = []
    path_prefix = variables['PATH_PREFIX']
    for commune in selected_communes:
        communes_links.append(f'<a href="{path_prefix}{commune["slug"]}/index.html">{commune["name"]}</a>')
    variables['COMMUNES_LINKS'] = ' | '.join(communes_links)

    # Nouvelle section Zones d'intervention avec 9 communes (v4.5)
    variables['ZONES_INTERVENTION_CONTENT'] = generator.build_zones_intervention_9_communes(service_id, variables['PATH_PREFIX'])

    # Badges hero (convertir les IDs en HTML)
    badges_html = generator.build_hero_badges(content_data.get('hero', {}).get('badges', []))
    variables['AB_REASSURANCE_BADGES'] = badges_html

    # Hero subtitle depuis JSON (v4.4)
    hero_subtitle = content_data.get('hero', {}).get('subtitle', 'Intervention rapide partout à Bruxelles en moins de 30 minutes')
    variables['ACCROCHE'] = hero_subtitle

    # Hero CTAs (defaults génériques)
    phone_formatted = generator.format_phone_number(generator.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'))
    variables['CTA_PRIMARY'] = phone_formatted
    variables['CTA_SECONDARY'] = generator.ui_translations.get('cta', {}).get('devis_gratuit', 'Devis gratuit')

    # H2 Sections depuis content JSON
    sections = content_data.get('sections', [])
    for i, section in enumerate(sections, start=1):
        if i <= 6:
            variables[f'H2_{i}'] = section.get('h2', '')
            # Remplacer les variables dans le contenu
            content_html = section.get('content', '')
            content_html = generator.replace_variables_in_content(content_html, variables)
            variables[f'CONTENT_H2_{i}'] = content_html

    # Remplir les sections manquantes avec du contenu vide
    contenu_a_venir = generator.ui_translations.get('defaults', {}).get('contenu_a_venir', 'Contenu à venir...')
    for i in range(len(sections) + 1, 7):
        variables[f'H2_{i}'] = ''
        variables[f'CONTENT_H2_{i}'] = f'<p>{contenu_a_venir}</p>'

    # CTA Final depuis content JSON
    cta_data = content_data.get('cta', {})
    cta_defaults = generator.ui_translations.get('cta', {})
    phone_display = generator.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89')

    variables['CTA_FINAL_TITRE'] = generator.replace_variables_in_content(cta_data.get('title', cta_defaults.get('besoin_aide', 'Besoin d\'aide ?')), variables)
    variables['CTA_FINAL_SUBTITLE'] = generator.replace_variables_in_content(cta_data.get('subtitle', cta_defaults.get('contactez_nous', 'Contactez-nous maintenant')), variables)
    button_default = cta_defaults.get('appeler_template', 'Appelez {{PHONE}}').replace('{{PHONE}}', phone_display)
    variables['CTA_FINAL_BUTTON'] = generator.replace_variables_in_content(cta_data.get('button_text', button_default), variables)

    # FAQ Section - Charger depuis le fichier JSON spécifique du service
    service_slug = service_data.get('slug')
    service_json_path = generator.base_path / 'content' / generator.lang / 'services' / f'{service_slug}.json'

    faq_data = []
    if service_json_path.exists():
        try:
            with open(service_json_path, 'r', encoding='utf-8') as f:
                service_content = json.load(f)
                faq_data = service_content.get('faq', [])
        except Exception as e:
            print(f"Erreur chargement FAQ pour {service_slug}: {e}")

    variables['FAQ_SECTION'] = generator.build_faq_section(faq_data)

    # Générer le Schema.org FAQPage pour les services (v4.6)
    if faq_data:
        faq_questions_answers = [(item['question'], item['answer']) for item in faq_data]
        faq_schema = generator.schema_builder.build_faq_schema(faq_questions_answers)
        variables['SCHEMA_ORG_FAQ'] = generator.schema_builder.to_json_ld(faq_schema)
    else:
        variables['SCHEMA_ORG_FAQ'] = ''

    # Autres variables A/B (defaults)
    variables['AB_TARIFS_TITRE'] = 'Tarifs'
    variables['PRIX'] = 'Sur devis'
    variables['AB_FAQ_SECTION'] = ''  # Pas de FAQ pour l'instant

    # Configuration WhatsApp pour le script JS
    whatsapp_config = generator.variables.get('whatsapp', {})
    # Adapter les chemins d'icônes avec PATH_PREFIX pour les sous-dossiers
    services_with_prefix = []
    for service in whatsapp_config.get('services', []):
        service_copy = service.copy()
        if 'icon' in service_copy:
            service_copy['icon'] = variables['PATH_PREFIX'] + service_copy['icon']
        services_with_prefix.append(service_copy)

    variables['WHATSAPP_CONFIG_JSON'] = json.dumps({
        'phoneNumber': whatsapp_config.get('phone_number', '32479890089'),
        'services': services_with_prefix,
        'language': generator.lang
    }, ensure_ascii=False)

    # Génération Schema.org (utilise service_id)
    service_schema = generator.schema_builder.build_service_schema(service_id=service_data['id'])

    # Breadcrumb traduit
    home_label = generator.ui_translations.get('nav', {}).get('home', 'Accueil')
    services_label = generator.ui_translations.get('nav', {}).get('services', 'Services')

    breadcrumb_schema = generator.schema_builder.build_breadcrumb_schema([
        (home_label, f"{domain}/"),
        (services_label, f"{domain}/#services"),
        (service_data['name'], f"{domain}/{service_data['slug']}/")
    ])

    variables['SCHEMA_ORG_SERVICE'] = generator.schema_builder.to_json_ld(service_schema)
    variables['SCHEMA_ORG_BREADCRUMB'] = generator.schema_builder.to_json_ld(breadcrumb_schema)

    # Génération sidebar (services connexes + communes) avec rotation v4.0
    sidebar_services = generator.build_sidebar_services_links(
        current_service_id=service_data['id'],
        current_category=service_data['category']
    )
    sidebar_communes = generator.build_sidebar_communes_links(
        current_service_id=service_data['id']
    )

    variables['SIDEBAR_SERVICES'] = sidebar_services
    variables['SIDEBAR_COMMUNES'] = sidebar_communes

    # Sidebar translations
    sidebar_ui = generator.ui_translations.get('sidebar', {})
    services = generator.loader.load_services()
    communes = generator.loader.load_communes()
    variables['SIDEBAR_OTHER_SERVICES_TITLE'] = sidebar_ui.get('other_services_title', 'Autres Services')
    variables['SIDEBAR_INTERVENTION_BADGE'] = sidebar_ui.get('intervention_badge', 'Intervention en 30 minutes')
    variables['SIDEBAR_AVAILABILITY'] = sidebar_ui.get('availability', 'Disponible 24h/24 - 7j/7')
    variables['SIDEBAR_SERVED_AREAS_TITLE'] = sidebar_ui.get('served_areas_title', 'Communes Desservies')
    variables['SIDEBAR_SERVICES_ALL'] = sidebar_ui.get('services_all', 'Voir tous les services ({{NOMBRE_SERVICES}}) →').replace('{{NOMBRE_SERVICES}}', str(len(services)))
    variables['SIDEBAR_NEARBY_ALL'] = sidebar_ui.get('nearby_all', 'Voir toutes les zones ({{NOMBRE_COMMUNES}}) →').replace('{{NOMBRE_COMMUNES}}', str(len(communes)))

    # Sidebar URLs (language-dependent)
    variables['SIDEBAR_SERVICES_URL'] = '../services/'
    variables['SIDEBAR_AREAS_URL'] = '../areas/' if generator.lang == 'en' else '../zones/'

    # Charger et rendre le composant sidebar
    sidebar_template = generator.renderer.load_template('components/sidebar-service.html')
    sidebar_html = generator.renderer.render(sidebar_template, variables)
    variables['COMPONENT_SIDEBAR_SERVICE'] = sidebar_html

    # Charger et rendre le carrousel photos
    carousel_template = generator.renderer.load_template('components/carousel-photos.html')
    carousel_html = generator.renderer.render(carousel_template, variables)
    variables['CAROUSEL_PHOTOS'] = carousel_html

    # Ajouter les variables du footer (communes dynamiques)
    generator.add_footer_variables(variables)

    # Breadcrumb
    variables['BREADCRUMB_ITEMS'] = generator.build_breadcrumb_items('service', service_data['name'], variables['PATH_PREFIX'])

    # Injecter toutes les template_variables (URLs, pricing, etc.)
    variables = generator.inject_template_variables(variables)

    # Aria labels
    aria_labels = generator.ui_translations.get('aria_labels', {})
    variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

    # MULTILINGUAL: Ajouter variables de langue et hreflang
    variables.update(generator._get_language_variables("subpage"))
    hreflang_vars = generator._generate_hreflang_urls('service', slug=service_data['slug'])
    variables.update(hreflang_vars)

    # Rendre le composant hreflang
    hreflang_html = generator.renderer.render('components/hreflang.html', hreflang_vars)
    variables['COMPONENT_HREFLANG'] = hreflang_html

    # Rendu du template
    html = generator.renderer.render_with_components('pages/service.html', variables)

    return html


def build_commune_page(generator, commune_data):
    """
    Génère une page commune

    Args:
        generator (SiteGenerator): Instance du générateur
        commune_data (dict): Données de la commune depuis CSV

    Returns:
        str: HTML complet de la page
    """
    generator.log(f"  📍 Génération: {commune_data['name']}")

    # Domain depuis variables
    domain = generator.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

    # Récupération des textes UI depuis translations
    communes_ui = generator.ui_translations.get('communes', {})

    # Variables de base (core data + SEO data)
    # Utiliser les données SEO optimisées du config si disponibles, sinon valeurs par défaut
    seo_data = commune_data.get('seo', {})

    # Templates SEO depuis ui.json
    meta_title_tpl = communes_ui.get('meta', {}).get('title_default', 'Dépannage Auto {{COMMUNE_NAME}} ({{POSTAL_CODE}}) | Service Professionnel')
    meta_desc_tpl = communes_ui.get('meta', {}).get('description_default', 'Service de dépannage automobile à {{COMMUNE_NAME}}. Équipe professionnelle locale, intervention rapide. Devis gratuit. ☎ 0479 89 00 89')
    seo_templates = communes_ui.get('seo', {})

    variables = {
        # SEO optimisé depuis locations-fr.json
        'META_TITLE': seo_data.get('meta_title', meta_title_tpl.replace('{{COMMUNE_NAME}}', commune_data['name']).replace('{{POSTAL_CODE}}', commune_data['postal_code'])),
        'META_DESCRIPTION': seo_data.get('meta_description', meta_desc_tpl.replace('{{COMMUNE_NAME}}', commune_data['name'])),
        'H1': seo_data.get('h1', seo_templates.get('h1_default', 'Dépannage Voiture à {{COMMUNE_NAME}}').replace('{{COMMUNE_NAME}}', commune_data['name'])),
        'H2_1': seo_data.get('h2', seo_templates.get('h2_1_default', 'Service de Dépannage à {{COMMUNE_NAME}}').replace('{{COMMUNE_NAME}}', commune_data['name'])),
        'H2_2': seo_templates.get('h2_2_default', 'Nos Services à {{COMMUNE_NAME}}').replace('{{COMMUNE_NAME}}', commune_data['name']),
        'H2_3': seo_templates.get('h2_3_default', "Zones d'Intervention"),
        'H2_4': seo_templates.get('h2_4_default', 'Nos Tarifs à {{COMMUNE_NAME}}').replace('{{COMMUNE_NAME}}', commune_data['name']),
        'H2_5': seo_templates.get('h2_5_default', 'Pourquoi Nous Choisir à {{COMMUNE_NAME}}').replace('{{COMMUNE_NAME}}', commune_data['name']),

        # Core data
        'PATH_PREFIX': generator._get_path_prefix('subpage'),  # Chemins relatifs depuis sous-dossier /commune/
        'CANONICAL_URL': f"{domain}/{commune_data['slug']}/",
        'COMMUNE_NAME': commune_data['name'],
        'COMMUNE': commune_data['name'],  # Alias pour compatibilité template
        'COMMUNE_IMAGE': generator._get_commune_image(commune_data['slug']),
        'CODE_POSTAL': commune_data['postal_code'],
        'KEYWORDS': '',  # Meta keywords obsolètes, non utilisés par Google
        'LANGUAGE': generator.lang,
        'TELEPHONE': generator.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
        'TELEPHONE_HREF': generator.variables.get('contact', {}).get('phone_local', '0479890089'),
        'GOOGLE_RATING': generator.variables.get('google', {}).get('rating', '4.9'),
        'GOOGLE_REVIEWS': generator.variables.get('google', {}).get('reviews_count', '190'),
        'GOOGLE_MY_BUSINESS_URL': generator.variables.get('google', {}).get('my_business_url', '#'),
        'FACEBOOK_URL': generator.variables.get('social', {}).get('facebook_url', '#'),
        'INSTAGRAM_URL': generator.variables.get('social', {}).get('instagram_url', '#'),
        # Carrousel Open Graph (2 images)
        'OG_IMAGE_1': f"{domain}/images/og/helpcar-depannage-bruxelles.jpg",
        'OG_IMAGE_2': f"{domain}/images/og/helpcar-depannage-bruxelles.jpg",

        # UI translations (ACCROCHE utilise maintenant H2_1 pour cohérence SEO)
        'ACCROCHE': seo_data.get('h2', communes_ui.get('hero', {}).get('accroche_template', 'Notre équipe locale intervient rapidement à {{COMMUNE_NAME}} et alentours. Service de qualité disponible 24h/24.').replace('{{COMMUNE_NAME}}', commune_data["name"])).replace('Intervention rapide', '<strong>Intervention rapide</strong>'),
        'CTA_PRIMARY': communes_ui.get('hero', {}).get('cta_primary', 'Nous Contacter'),
        'CTA_FINAL_TITRE': communes_ui.get('cta_final', {}).get('titre_template', 'En Panne à {{COMMUNE_NAME}} ?').replace('{{COMMUNE_NAME}}', commune_data["name"]),
        'CTA_FINAL_BUTTON': communes_ui.get('cta_final', {}).get('button', 'Devis Gratuit Immédiat'),
    }

    # Components commune_hero depuis components.json
    components = generator.loader.load_component_translations(generator.lang)
    commune_hero = components.get('commune_hero', {})
    variables['HERO_STAT_INTERVENTION_VALUE'] = commune_hero.get('stat_intervention_value', '30 min')
    variables['HERO_STAT_INTERVENTION_LABEL'] = commune_hero.get('stat_intervention_label', 'Intervention rapide')
    variables['HERO_STAT_DISPONIBLE_VALUE'] = commune_hero.get('stat_disponible_value', '24h/24 - 7j/7')
    variables['HERO_STAT_DISPONIBLE_LABEL'] = commune_hero.get('stat_disponible_label', 'Disponible')
    variables['HERO_BTN_VOIR_SERVICES'] = commune_hero.get('btn_voir_services', 'Voir les services')
    variables['HERO_DEVIS_TITRE'] = commune_hero.get('devis_titre', 'Obtenez Votre Tarif en 2 Minutes')
    variables['HERO_DEVIS_SUBTITLE'] = commune_hero.get('devis_subtitle', 'Appelez-nous, décrivez votre panne, recevez un prix exact. Sans engagement.')
    variables['SECTION_SERVICES_LABEL'] = commune_hero.get('section_services_label', 'NOS SERVICES')
    variables['SECTION_ZONES_LABEL'] = commune_hero.get('section_zones_label', 'ZONES VOISINES')
    cta_subtitle_tpl = commune_hero.get('cta_subtitle_template', 'Intervention rapide à {{COMMUNE_NAME}} en moins de 30 minutes')
    variables['CTA_FINAL_SUBTITLE'] = cta_subtitle_tpl.replace('{{COMMUNE_NAME}}', commune_data["name"])

    # Sidebar translations
    sidebar_ui = generator.ui_translations.get('sidebar', {})
    variables['SIDEBAR_SERVICES_TITLE'] = sidebar_ui.get('services_title', 'Nos Services à {{COMMUNE}}').replace('{{COMMUNE}}', commune_data['name'])
    variables['SIDEBAR_BREAKDOWN_BADGE'] = sidebar_ui.get('breakdown_badge', 'En panne à {{COMMUNE}} ?').replace('{{COMMUNE}}', commune_data['name'])
    variables['SIDEBAR_AVAILABILITY'] = sidebar_ui.get('availability', 'Disponible 24h/24 - 7j/7')
    variables['SIDEBAR_NEARBY_TITLE'] = sidebar_ui.get('nearby_title', 'Communes Voisines')

    # Schema.org commune
    commune_schema = generator.schema_builder.build_commune_schema(
        commune_name=commune_data['name'],
        postal_code=commune_data['postal_code']
    )

    home_label = generator.ui_translations.get('nav', {}).get('home', 'Accueil')
    zones_label = generator.ui_translations.get('nav', {}).get('zones', 'Zones')

    breadcrumb_schema = generator.schema_builder.build_breadcrumb_schema([
        (home_label, f"{domain}/"),
        (zones_label, f"{domain}/#zones"),
        (commune_data['name'], f"{domain}/{commune_data['slug']}/")
    ])

    variables['SCHEMA_ORG_COMMUNE'] = generator.schema_builder.to_json_ld(commune_schema)
    variables['SCHEMA_ORG_BREADCRUMB'] = generator.schema_builder.to_json_ld(breadcrumb_schema)

    # Sidebar avec rotation des services basée sur l'ID de la commune (meilleur maillage)
    sidebar_services = generator.build_sidebar_services_for_commune(commune_data['id'])
    sidebar_voisines = generator.build_sidebar_voisines_links(commune_data['slug'])

    variables['SIDEBAR_SERVICES'] = sidebar_services
    variables['SIDEBAR_VOISINES'] = sidebar_voisines
    variables['COMMUNE'] = commune_data['name']  # Ajouter la variable COMMUNE pour la sidebar

    # Ajouter NOMBRE_SERVICES et NOMBRE_COMMUNES pour les CTAs de la sidebar
    services = generator.loader.load_services()
    communes = generator.loader.load_communes()
    variables['NOMBRE_SERVICES'] = len(services)
    variables['NOMBRE_COMMUNES'] = len(communes)

    # Sidebar CTA links translations
    variables['SIDEBAR_SERVICES_ALL'] = sidebar_ui.get('services_all', 'Voir tous les services ({{NOMBRE_SERVICES}}) →').replace('{{NOMBRE_SERVICES}}', str(len(services)))
    variables['SIDEBAR_NEARBY_ALL'] = sidebar_ui.get('nearby_all', 'Voir toutes les zones ({{NOMBRE_COMMUNES}}) →').replace('{{NOMBRE_COMMUNES}}', str(len(communes)))

    # Sidebar URLs (language-dependent)
    variables['SIDEBAR_SERVICES_URL'] = '../services/'
    variables['SIDEBAR_AREAS_URL'] = '../areas/' if generator.lang == 'en' else '../zones/'

    # Zones section translations
    zones_ui = generator.ui_translations.get('zones', {})
    variables['ZONES_VIEW_ALL'] = zones_ui.get('view_all', 'Voir toutes les zones ({{NOMBRE_COMMUNES}}) →').replace('{{NOMBRE_COMMUNES}}', str(len(communes)))

    # Aria labels
    aria_labels = generator.ui_translations.get('aria_labels', {})
    variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

    # Initialiser les variables v2.0 par défaut (seront écrasées si v2.0)
    variables['H2_ON_CONNAIT'] = ''
    variables['INTRO_ON_CONNAIT'] = ''
    variables['QUARTIERS_HTML'] = ''
    variables['CONCLUSION_ON_CONNAIT'] = ''
    variables['SHOW_ON_CONNAIT'] = 'none'
    variables['SECTION_PARKINGS_HTML'] = ''
    variables['INTRO_SERVICES'] = ''
    variables['SERVICES_CATEGORIES_HTML'] = ''
    variables['SERVICES_CTA_TEXT'] = 'Voir tous nos services'
    variables['SERVICES_CTA_URL'] = '/services/'
    variables['FAQ_LOCALE_HTML'] = ''
    variables['SCHEMA_ORG_FAQ'] = ''

    # Configuration WhatsApp pour le script JS
    whatsapp_config = generator.variables.get('whatsapp', {})
    # Adapter les chemins d'icônes avec PATH_PREFIX pour les sous-dossiers
    services_with_prefix = []
    for service in whatsapp_config.get('services', []):
        service_copy = service.copy()
        if 'icon' in service_copy:
            service_copy['icon'] = variables['PATH_PREFIX'] + service_copy['icon']
        services_with_prefix.append(service_copy)

    variables['WHATSAPP_CONFIG_JSON'] = json.dumps({
        'phoneNumber': whatsapp_config.get('phone_number', '32479890089'),
        'services': services_with_prefix,
        'language': generator.lang
    }, ensure_ascii=False)

    # Charger et rendre le composant sidebar
    sidebar_template = generator.renderer.load_template('components/sidebar-commune.html')
    sidebar_html = generator.renderer.render(sidebar_template, variables)
    variables['COMPONENT_SIDEBAR_COMMUNE'] = sidebar_html

    # Charger et rendre le carrousel photos
    carousel_template = generator.renderer.load_template('components/carousel-photos.html')
    carousel_html = generator.renderer.render(carousel_template, variables)
    variables['CAROUSEL_PHOTOS'] = carousel_html

    # Nouvelles variables pour le design moderne avec rotation basée sur l'ID commune
    variables['SERVICES_CARDS'] = generator.build_commune_services_cards(6, commune_data['id'], variables['PATH_PREFIX'])
    variables['WHY_US_CARDS'] = generator.build_commune_why_cards()
    variables['COMMUNES_VOISINES_TAGS'] = generator.build_communes_voisines_tags(commune_data['slug'], 5, variables['PATH_PREFIX'])

    # Charger le contenu personnalisé de la commune depuis le fichier individuel
    commune_slug = commune_data['slug']
    commune_content_data = generator.loader.load_commune_content(commune_slug)
    content_version = commune_content_data.get('version', '1.0')
    custom_content = commune_content_data.get('content', {})

    # === GESTION VERSION 2.0 (Format enrichi SEO) ===
    if content_version == '2.0':
        # Hero personnalisé
        hero_data = commune_content_data.get('hero', {})
        if hero_data.get('h1'):
            variables['H1'] = hero_data['h1']
        if hero_data.get('accroche'):
            variables['ACCROCHE'] = hero_data['accroche'].replace('Intervention rapide', '<strong>Intervention rapide</strong>')

        # SEO meta depuis v2.0
        seo_v2 = commune_content_data.get('seo', {})
        if seo_v2.get('meta_title'):
            variables['META_TITLE'] = seo_v2['meta_title']
        if seo_v2.get('meta_description'):
            variables['META_DESCRIPTION'] = seo_v2['meta_description']

        # Section intro_autorite (v2.0: 3 paragraphes)
        intro_autorite = custom_content.get('intro_autorite', {})
        if intro_autorite:
            paragraphe_0 = intro_autorite.get('paragraphe_0', '')
            paragraphe_1 = intro_autorite.get('paragraphe_1', '')
            paragraphe_2 = intro_autorite.get('paragraphe_2', '')

            # Remplacer les variables dans les paragraphes
            paragraphe_0 = generator.replace_variables_in_content(paragraphe_0, {})
            paragraphe_1 = generator.replace_variables_in_content(paragraphe_1, {})
            paragraphe_2 = generator.replace_variables_in_content(paragraphe_2, {})

            # Construire le contenu avec les 3 paragraphes si disponibles
            content_parts = []
            if paragraphe_0:
                content_parts.append(f'<p class="intro-kw">{paragraphe_0}</p>')
            if paragraphe_1:
                content_parts.append(f'<p>{paragraphe_1}</p>')
            if paragraphe_2:
                content_parts.append(f'<p>{paragraphe_2}</p>')

            variables['CONTENT_H2_1'] = '\n'.join(content_parts)

        # Section "On connaît [Commune]"
        section_on_connait = custom_content.get('section_on_connait', {})
        if section_on_connait and section_on_connait.get('h2'):
            h2_on_connait = section_on_connait.get('h2', '')
            intro_on_connait = section_on_connait.get('intro', '')
            conclusion_on_connait = section_on_connait.get('conclusion', '')

            # Remplacer les variables dans les textes
            variables['H2_ON_CONNAIT'] = generator.replace_variables_in_content(h2_on_connait, {})
            variables['INTRO_ON_CONNAIT'] = generator.replace_variables_in_content(intro_on_connait, {})
            variables['QUARTIERS_HTML'] = generator._build_quartiers_html(section_on_connait.get('quartiers', []))
            variables['CONCLUSION_ON_CONNAIT'] = generator.replace_variables_in_content(conclusion_on_connait, {})
            variables['SHOW_ON_CONNAIT'] = 'block'
        else:
            variables['SHOW_ON_CONNAIT'] = 'none'

        # Section parkings (conditionnelle)
        section_parkings = custom_content.get('section_parkings', {})
        variables['SECTION_PARKINGS_HTML'] = generator._build_parkings_html(section_parkings)

        # Section services réorganisée par catégories
        section_services = custom_content.get('section_services', {})
        if section_services:
            h2_services = section_services.get('h2', variables['H2_2'])
            intro_services = section_services.get('intro', '')
            cta_text = section_services.get('cta_text', 'Voir tous nos services')
            cta_url = section_services.get('cta_url', '/services/')

            # Remplacer les variables dans les textes
            variables['H2_2'] = generator.replace_variables_in_content(h2_services, {})

            # Styliser l'intro services : gras gris foncé + "24h/24" en vert
            intro_text = generator.replace_variables_in_content(intro_services, {})
            if intro_text:
                # Remplacer "24h/24" par une version stylée en vert
                intro_text = intro_text.replace('24h/24', '<span style="color: #10B981; font-weight: 700;">24h/24</span>')
                variables['INTRO_SERVICES'] = f'<p class="services-intro">{intro_text}</p>'
            else:
                variables['INTRO_SERVICES'] = ''

            variables['SERVICES_CATEGORIES_HTML'] = generator._build_services_categories_html(
                section_services.get('categories', []),
                variables['PATH_PREFIX']
            )
            variables['SERVICES_CTA_TEXT'] = generator.replace_variables_in_content(cta_text, {})
            variables['SERVICES_CTA_URL'] = cta_url

        # FAQ locale
        faq_locale = custom_content.get('faq_locale', {})
        if faq_locale and faq_locale.get('questions'):
            variables['FAQ_LOCALE_HTML'] = generator._build_faq_locale_html(faq_locale)

            # Générer le Schema.org FAQPage (v4.6 - utilise schema_builder)
            questions = faq_locale.get('questions', [])
            faq_questions_answers = [(q['question'], q['reponse']) for q in questions]
            faq_schema = generator.schema_builder.build_faq_schema(faq_questions_answers)
            if faq_schema:
                variables['SCHEMA_ORG_FAQ'] = generator.schema_builder.to_json_ld(faq_schema)

        # Section zones voisines enrichie
        section_zones_voisines = custom_content.get('section_zones_voisines', {})
        if section_zones_voisines:
            h2_zones = section_zones_voisines.get('h2', variables['H2_3'])
            content_zones = section_zones_voisines.get('content', '')

            # Remplacer les variables dans les textes
            variables['H2_3'] = generator.replace_variables_in_content(h2_zones, {})
            variables['CONTENT_H2_3'] = generator.replace_variables_in_content(content_zones, {})

            # Générer les tags des communes voisines depuis le JSON v2.0
            communes_voisines = section_zones_voisines.get('communes_voisines', [])
            if communes_voisines:
                tags_html = ''
                for commune_voisine in communes_voisines:
                    nom = commune_voisine.get('nom', '')
                    slug = commune_voisine.get('slug', '')
                    tags_html += f'<a href="{variables["PATH_PREFIX"]}{slug}/" class="zone-tag">{nom}</a>\n'
                variables['COMMUNES_VOISINES_TAGS'] = tags_html

    # Contenu H2_3 par défaut si toujours vide
    if not variables.get('CONTENT_H2_3'):
        h2_3_default = communes_ui.get('content', {}).get('h2_3_default', 'Nous intervenons également dans les communes voisines de {{COMMUNE_NAME}}. Notre proximité nous permet une intervention rapide partout dans la région.')
        variables['CONTENT_H2_3'] = f'<p>{h2_3_default.replace("{{COMMUNE_NAME}}", commune_data["name"])}</p>'

    # Contenu H2_1 par défaut si vide
    if not variables.get('CONTENT_H2_1'):
        h2_1_default = communes_ui.get('content', {}).get('h2_1_default', 'Service de dépannage professionnel à {{COMMUNE_NAME}}. Nous intervenons rapidement dans toute la commune et ses alentours.')
        variables['CONTENT_H2_1'] = f'<p>{h2_1_default.replace("{{COMMUNE_NAME}}", commune_data["name"])}</p>'

    # Ajouter les variables du footer (communes dynamiques)
    generator.add_footer_variables(variables)

    # Breadcrumb
    variables['BREADCRUMB_ITEMS'] = generator.build_breadcrumb_items('commune', commune_data['name'], variables['PATH_PREFIX'])

    # Injecter toutes les template_variables (URLs, pricing, etc.)
    variables = generator.inject_template_variables(variables)

    # MULTILINGUAL: Ajouter variables de langue et hreflang
    variables.update(generator._get_language_variables("subpage"))
    hreflang_vars = generator._generate_hreflang_urls('location', slug=commune_data['slug'])
    variables.update(hreflang_vars)

    # Rendre le composant hreflang
    hreflang_html = generator.renderer.render('components/hreflang.html', hreflang_vars)
    variables['COMPONENT_HREFLANG'] = hreflang_html

    # Rendu
    html = generator.renderer.render_with_components('pages/commune.html', variables)

    return html


def build_homepage(generator):
    """
    Génère la homepage

    Args:
        generator (SiteGenerator): Instance du générateur

    Returns:
        str: HTML complet de la homepage
    """
    generator.log("\n🏠 === GÉNÉRATION HOMEPAGE ===")

    # Récupération des données depuis variables.json
    domain = generator.variables.get('site', {}).get('domain', 'https://bruxelles-car-depannage.be')

    # Charger le Critical CSS pour optimiser le LCP
    critical_css_path = generator.base_path / 'config' / 'critical.css'
    try:
        with open(critical_css_path, 'r', encoding='utf-8') as f:
            critical_css = f.read()
    except FileNotFoundError:
        generator.log("⚠️  Fichier critical.css introuvable, Critical CSS non injecté")
        critical_css = ''

    # Variables de base depuis la configuration
    variables = {
        'PATH_PREFIX': generator._get_path_prefix('base'),  # Chemins relatifs pour Netlify (dynamique selon langue)
        'LANGUAGE': generator.lang,
        'CANONICAL_URL': f"{domain}/",
        'TELEPHONE': generator.variables.get('contact', {}).get('phone_local_display', '0479 89 00 89'),
        'TELEPHONE_HREF': generator.variables.get('contact', {}).get('phone_local', '0479890089'),
        'GOOGLE_RATING': generator.variables.get('google', {}).get('rating', '4.9'),
        'GOOGLE_REVIEWS': generator.variables.get('google', {}).get('reviews_count', '190'),
        'GOOGLE_MY_BUSINESS_URL': generator.variables.get('google', {}).get('my_business_url', '#'),
        'FACEBOOK_URL': generator.variables.get('social', {}).get('facebook_url', '#'),
        'INSTAGRAM_URL': generator.variables.get('social', {}).get('instagram_url', '#'),
        'KEYWORDS': 'dépannage automobile bruxelles, remorquage voiture, panne batterie, assistance 24h',
        # Variables stats pour infinite scroll
        'STATS_YEARS_EXPERIENCE': str(generator.variables.get('stats', {}).get('years_experience', 15)),
        'STATS_YEARS_EXISTENCE': str(generator.variables.get('stats', {}).get('years_existence', 10)),
        'STATS_ARRIVAL_TIME': generator.variables.get('stats', {}).get('arrival_time', '30 min'),
        'STATS_SATISFACTION_RATE': generator.variables.get('stats', {}).get('satisfaction_rate', '98%'),
        'STATS_LOCATIONS_BRUXELLES': str(generator.variables.get('stats', {}).get('locations_bruxelles', 19)),
        'STATS_LOCATIONS_PERIPHERIE': str(generator.variables.get('stats', {}).get('locations_peripherie', 16)),
        'STATS_SERVICES_REMORQUAGE': str(generator.variables.get('stats', {}).get('services_remorquage', 13)),
        'STATS_SERVICES_DEPANNAGE': str(generator.variables.get('stats', {}).get('services_depannage', 9)),
        # Critical CSS inline pour optimiser le LCP
        'CRITICAL_CSS': critical_css,
    }

    # Configuration WhatsApp pour le script JS
    whatsapp_config = generator.variables.get('whatsapp', {})
    variables['WHATSAPP_CONFIG_JSON'] = json.dumps({
        'phoneNumber': whatsapp_config.get('phone_number', '32479890089'),
        'services': whatsapp_config.get('services', []),
        'language': generator.lang
    }, ensure_ascii=False)

    # Lien WhatsApp direct pour devis
    whatsapp_phone = whatsapp_config.get('phone_number', '32479890089')
    whatsapp_message = "Bonjour, j'aimerais obtenir un devis pour un dépannage à Bruxelles."
    variables['WHATSAPP_LINK'] = f"https://wa.me/{whatsapp_phone}?text={whatsapp_message.replace(' ', '%20')}"

    # Variables contenu homepage depuis content/fr/pages/homepage.json
    homepage_ui = generator.loader.load_homepage_content()

    # Mapping des variables UI
    variables['META_TITLE'] = homepage_ui.get('meta_title', 'Dépannage Auto Bruxelles 24/7')
    variables['META_DESCRIPTION'] = homepage_ui.get('meta_description', 'Service de dépannage automobile à Bruxelles')
    # Carrousel Open Graph (2 images)
    variables['OG_IMAGE_1'] = f"{domain}/images/og/helpcar-depannage-bruxelles.jpg"
    variables['OG_IMAGE_2'] = f"{domain}/images/og/helpcar-depannage-bruxelles.jpg"
    variables['H1'] = homepage_ui.get('h1', 'Service de Dépannage Automobile à Bruxelles')
    variables['HERO_SUBTITLE'] = homepage_ui.get('hero', {}).get('h2', 'Intervention rapide 24h/24 et 7j/7')
    variables['CTA_PRIMARY'] = homepage_ui.get('hero', {}).get('cta_text', 'Appeler Maintenant')
    variables['CTA_FINAL_TITRE'] = homepage_ui.get('cta_final', {}).get('titre', 'Besoin d\'un Service de Dépannage ?')
    variables['CTA_FINAL_SUBTITLE'] = homepage_ui.get('cta_final', {}).get('sous_titre', 'Contactez-nous pour une intervention rapide')
    variables['CTA_FINAL_BUTTON'] = homepage_ui.get('cta_final', {}).get('bouton', 'Nous Contacter')

    # Générer les sections alternées
    sections_alternees_data = homepage_ui.get('sections_alternees', [])
    sections_alternees_html = ''

    for section in sections_alternees_data:
        # Récupérer le path_prefix pour cette section
        path_prefix = variables.get('PATH_PREFIX', '')

        # Déterminer la classe CSS selon le type
        section_class = 'section-alternee'
        if section.get('type') == 'image-droite':
            section_class += ' section-alternee-image-droite'
        else:
            section_class += ' section-alternee-image-gauche'

        # Remplacer les variables dans tous les champs texte
        label = section.get('label', '')
        titre = section.get('titre', '')
        paragraphe = section.get('paragraphe', '')
        image_alt = section.get('image_alt', '')

        for var_name, var_value in variables.items():
            label = label.replace('{{' + var_name + '}}', str(var_value))
            titre = titre.replace('{{' + var_name + '}}', str(var_value))
            paragraphe = paragraphe.replace('{{' + var_name + '}}', str(var_value))
            image_alt = image_alt.replace('{{' + var_name + '}}', str(var_value))

        # Générer les points HTML (avec remplacement des variables)
        points_html = ''
        for point in section.get('points', []):
            # Remplacer les variables dans chaque point
            point_text = point
            for var_name, var_value in variables.items():
                point_text = point_text.replace('{{' + var_name + '}}', str(var_value))
            points_html += f'              <li>{point_text}</li>\n'

        # Scanner le dossier d'images automatiquement
        images_folder = section.get('images_folder', '')
        carousel_images_html = ''
        carousel_dots_html = ''

        if images_folder:
            import os
            import glob as glob_module

            # Chercher toutes les images dans le dossier (jpg, jpeg, png, webp)
            folder_path = os.path.join(os.getcwd(), images_folder)
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.JPG', '*.JPEG', '*.PNG', '*.WEBP']
            images_list = []

            for ext in image_extensions:
                images_list.extend(glob_module.glob(os.path.join(folder_path, ext)))

            # Filtrer les doublons : si .jpg et .webp existent, garder uniquement .webp (optimisé)
            unique_images = {}
            for img_path in images_list:
                base_name = os.path.splitext(img_path)[0]
                ext = os.path.splitext(img_path)[1].lower()

                # Prioriser les formats .webp s'ils existent (déjà optimisés)
                if base_name not in unique_images or ext == '.webp':
                    unique_images[base_name] = img_path

            # Trier par ordre alphabétique
            images_list = sorted(unique_images.values())

            # Générer le HTML du carrousel (sans classe active car on utilise transform)
            for idx, img_path in enumerate(images_list):
                # Extraire le nom du fichier relatif
                img_relative = os.path.relpath(img_path, os.getcwd())

                # Récupérer les dimensions
                img_key = img_relative.split('images/')[-1] if 'images/' in img_relative else img_relative
                dims_attrs = generator.get_image_dimensions_attrs(img_key)

                # Ajout de data-carousel-item pour le nouveau système de carrousel générique
                carousel_images_html += f'              <img src="{path_prefix}{img_relative}" alt="{image_alt}" {dims_attrs} class="alternee-carousel-image" data-carousel-item loading="lazy">\n'

        # Construire le HTML de la section selon le type
        # Utilisation du carrousel générique avec attributs data-*
        # Dots à l'extérieur du conteneur overflow:hidden pour éviter le débordement
        image_html = f'''
          <div class="alternee-image">
            <div class="alternee-carousel-wrapper" data-carousel data-autoplay="5000" data-loop="true" data-pause-on-hover="true">
              <div class="alternee-carousel">
                <div class="alternee-carousel-track" data-carousel-track>
{carousel_images_html}                </div>
                <button class="carousel-prev" data-carousel-prev aria-label="Image précédente">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="15 18 9 12 15 6"></polyline>
                  </svg>
                </button>
                <button class="carousel-next" data-carousel-next aria-label="Image suivante">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </button>
              </div>
              <div class="alternee-carousel-dots" data-carousel-dots></div>
            </div>
          </div>'''

        # Générer le CTA selon le type
        cta_type = section.get('cta_type', 'link')
        cta_html = ''

        if cta_type == 'double':
            # Deux boutons côte à côte
            primary_texte = section.get('cta_primary_texte', 'Appelez-nous')
            primary_url = section.get('cta_primary_url', '#')
            secondary_texte = section.get('cta_secondary_texte', 'WhatsApp')
            secondary_url = section.get('cta_secondary_url', '#')

            # Remplacer les variables dans les URLs et textes
            for var_name, var_value in variables.items():
                primary_texte = primary_texte.replace('{{' + var_name + '}}', str(var_value))
                primary_url = primary_url.replace('{{' + var_name + '}}', str(var_value))
                secondary_texte = secondary_texte.replace('{{' + var_name + '}}', str(var_value))
                secondary_url = secondary_url.replace('{{' + var_name + '}}', str(var_value))

            cta_html = f'''
            <div class="alternee-cta-group">
              <a href="{primary_url}" class="btn-hero-phone">
                <svg class="phone-icon phone-icon-green" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span class="phone-text">{primary_texte.replace('📞 ', '')}</span>
              </a>
              <a href="{secondary_url}" class="hero-btn-whatsapp" target="_blank" rel="noopener noreferrer">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                </svg>
                <span class="hero-btn-whatsapp-text">{secondary_texte.replace('💬 ', '').replace('Devis ', '')}</span>
              </a>
            </div>'''

        elif cta_type == 'phone':
            # Bouton téléphone unique
            cta_texte = section.get('cta_texte', 'Appelez-nous')
            cta_url = section.get('cta_url', '#')

            # Remplacer les variables
            for var_name, var_value in variables.items():
                cta_texte = cta_texte.replace('{{' + var_name + '}}', str(var_value))
                cta_url = cta_url.replace('{{' + var_name + '}}', str(var_value))

            cta_html = f'''
            <a href="{cta_url}" class="btn-hero-phone">
              <svg class="phone-icon phone-icon-green" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <span class="phone-text">{cta_texte.replace('📞 ', '')}</span>
            </a>'''

        else:
            # Lien simple par défaut
            cta_texte = section.get('cta_texte', 'En savoir plus →')
            cta_url = section.get('cta_url', '#')

            # Remplacer les variables
            for var_name, var_value in variables.items():
                cta_texte = cta_texte.replace('{{' + var_name + '}}', str(var_value))
                cta_url = cta_url.replace('{{' + var_name + '}}', str(var_value))

            cta_html = f'''
            <a href="{path_prefix}{cta_url}" class="btn-outline">{cta_texte}</a>'''

        content_html = f'''
          <div class="alternee-content">
            <span class="section-label">{label}</span>
            <h2>{titre}</h2>
            <p>{paragraphe}</p>
            <ul class="alternee-points">
{points_html}            </ul>
{cta_html}
          </div>'''

        # Ordre selon le type : image-droite = contenu puis image, image-gauche = image puis contenu
        if section.get('type') == 'image-droite':
            sections_alternees_html += f'''
    <section class="{section_class}">
      <div class="container">
        <div class="alternee-grid">
{content_html}
{image_html}
        </div>
      </div>
    </section>
'''
        else:
            sections_alternees_html += f'''
    <section class="{section_class}">
      <div class="container">
        <div class="alternee-grid">
{image_html}
{content_html}
        </div>
      </div>
    </section>
'''

    variables['SECTIONS_ALTERNEES'] = sections_alternees_html

    # Section Services
    section_services = homepage_ui.get('section_services', {})
    variables['SECTION_SERVICES_LABEL'] = section_services.get('label', 'Nos Services')
    variables['SECTION_SERVICES_TITRE'] = section_services.get('titre', 'Comment pouvons-nous vous aider ?')

    # Section Comment ça marche
    section_comment = homepage_ui.get('section_comment_ca_marche', {})
    variables['SECTION_COMMENT_CA_MARCHE_LABEL'] = section_comment.get('label', 'Comment ça marche')
    variables['SECTION_COMMENT_CA_MARCHE_TITRE'] = section_comment.get('titre', 'Dépannage en 4 Étapes Simples')

    # Section Avis
    section_avis = homepage_ui.get('section_avis', {})
    variables['SECTION_AVIS_LABEL'] = section_avis.get('label', 'Avis Clients')
    variables['SECTION_AVIS_TITRE'] = section_avis.get('titre', 'Ce que nos clients disent de nous')

    # Intro avis avec remplacement des variables
    avis_intro = section_avis.get('intro', '')
    avis_intro = avis_intro.replace('{{GOOGLE_RATING}}', variables['GOOGLE_RATING'])
    avis_intro = avis_intro.replace('{{GOOGLE_REVIEWS}}', variables['GOOGLE_REVIEWS'])
    variables['SECTION_AVIS_INTRO'] = avis_intro

    # Aria labels avis
    aria_labels = section_avis.get('aria_labels', {})
    variables['AVIS_ARIA_BTN_PREV'] = aria_labels.get('btn_prev', 'Avis précédent')
    variables['AVIS_ARIA_BTN_NEXT'] = aria_labels.get('btn_next', 'Avis suivant')
    variables['AVIS_ARIA_DOT_PREFIX'] = aria_labels.get('dot_prefix', 'Aller à l\'avis')
    variables['AVIS_ARIA_GOOGLE_CARD'] = aria_labels.get('google_card', 'Laisser un avis Google')

    # Google card suffix
    google_card = section_avis.get('google_card', {})
    variables['AVIS_REVIEWS_COUNT_SUFFIX'] = google_card.get('reviews_count_suffix', 'avis clients')

    # Générer le carousel d'avis
    variables['REVIEWS_CAROUSEL'] = generator.build_reviews_carousel(section_avis, variables)

    # Section Zones
    section_zones = homepage_ui.get('section_zones', {})
    variables['SECTION_ZONES_LABEL'] = section_zones.get('label', 'Zones d\'intervention')
    variables['SECTION_ZONES_TITRE'] = section_zones.get('titre', 'Nous intervenons partout à Bruxelles')
    variables['SECTION_ZONES_PARAGRAPHE'] = section_zones.get('paragraphe', '')
    variables['SECTION_ZONES_CTA'] = section_zones.get('cta_text', 'Voir toutes les communes')
    variables['ZONES_MAP_CARD_TITLE'] = section_zones.get('map_card_title', 'Zone d\'Intervention')
    variables['ZONES_MAP_CARD_DESCRIPTION'] = section_zones.get('map_card_description', 'Nous couvrons Bruxelles et {{NOMBRE_COMMUNES}} communes environnantes')

    # Section FAQ
    section_faq = homepage_ui.get('section_faq', {})
    variables['SECTION_FAQ_LABEL'] = section_faq.get('label', 'FAQ')
    variables['SECTION_FAQ_TITRE'] = section_faq.get('titre', 'Questions Fréquentes')

    # Générer les items FAQ
    variables['FAQ_ITEMS'] = generator.build_faq_items(section_faq, variables)

    # Variables Hero
    hero_vars = generator.get_hero_variables(homepage_ui)
    variables.update(hero_vars)

    # Schema.org homepage (corrigé: SCHEMA_ORG_LOCALBUSINESS au lieu de HOMEPAGE)
    homepage_schema = generator.schema_builder.build_homepage_schema()
    variables['SCHEMA_ORG_LOCALBUSINESS'] = generator.schema_builder.to_json_ld(homepage_schema)

    # Services cards pour homepage (top 6)
    top_services = generator.loader.get_services_by_priority(6)
    variables['SERVICES_CARDS'] = generator.build_services_grid(top_services, variables['PATH_PREFIX'])

    # Contenu "Comment ça marche" - Étapes (à partir des variables UI)
    variables['ETAPES_ITEMS'] = generator.build_comment_ca_marche_section(homepage_ui)

    # Tags communes (depuis Schema.org)
    variables['ZONES_TAGS'] = generator.build_zones_tags(12, variables['PATH_PREFIX'])

    # Hero image (placeholder)
    variables['HERO_IMAGE'] = ''

    # Chargement du composant Hero (v4.0 - un seul hero moderne)
    hero_template = generator.renderer.load_template('components/hero.html')
    hero_html = generator.renderer.render(hero_template, variables)
    variables['HERO_SECTION'] = hero_html

    # Stats Infinite Scroll (v5.4.2)
    stats_scroll_data = homepage_ui.get('stats_infinite_scroll', {})
    variables['STATS_SCROLL_TITRE'] = stats_scroll_data.get('titre', 'POURQUOI NOUS CHOISIR')
    variables['STATS_SCROLL_SOUS_TITRE'] = stats_scroll_data.get('sous_titre', 'Le Meilleur Service de Dépannage')

    # Générer HTML des stats items
    stats_items_html = ''
    for item in stats_scroll_data.get('items', []):
        valeur = item.get('valeur', '')
        label = item.get('label', '')

        # Remplacer les variables dans valeur et label
        for var_name, var_value in variables.items():
            valeur = valeur.replace('{{' + var_name + '}}', str(var_value))
            label = label.replace('{{' + var_name + '}}', str(var_value))

        stats_items_html += f'''
              <div class="stat-item">
                <div class="stat-value">{valeur}</div>
                <div class="stat-label">{label}</div>
              </div>
            '''

    variables['STATS_SCROLL_ITEMS'] = stats_items_html

    # Charger et rendre le composant stats-infinite-scroll
    stats_scroll_template = generator.renderer.load_template('components/stats-infinite-scroll.html')
    stats_scroll_html = generator.renderer.render(stats_scroll_template, variables)
    variables['STATS_INFINITE_SECTION'] = stats_scroll_html

    # Ajouter les variables du footer (communes dynamiques)
    generator.add_footer_variables(variables)

    # Injecter toutes les template_variables (URLs, pricing, etc.)
    variables = generator.inject_template_variables(variables)

    # Aria labels
    aria_labels = generator.ui_translations.get('aria_labels', {})
    variables['ARIA_LABEL_GOOGLE_REVIEWS'] = aria_labels.get('google_reviews', 'Voir nos avis Google')

    # MULTILINGUAL: Ajouter variables de langue et hreflang
    variables.update(generator._get_language_variables("base"))
    hreflang_vars = generator._generate_hreflang_urls('homepage')
    variables.update(hreflang_vars)

    # Rendre le composant hreflang
    hreflang_html = generator.renderer.render('components/hreflang.html', hreflang_vars)
    variables['COMPONENT_HREFLANG'] = hreflang_html

    # Rendu
    html = generator.renderer.render_with_components('pages/homepage.html', variables)

    return html
