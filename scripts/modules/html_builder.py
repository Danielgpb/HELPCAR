"""
Module de construction de HTML pour sections spécifiques
Extrait du SiteGenerator pour améliorer la modularité (Refactoring #6)
Contient les méthodes privées _build_*_html
"""


def _build_quartiers_html(generator, quartiers):
    """
    Génère le HTML pour la section quartiers (v4.3 - Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur
        quartiers (list): Liste des quartiers avec icon, nom, description

    Returns:
        str: HTML de la grille de quartiers
    """
    if not quartiers:
        return ''

    # Préparer les données pour le template
    quartiers_data = []
    for quartier in quartiers:
        icon_svg = generator._get_svg_icon(quartier.get('icon', 'map-pin'))
        nom = generator.replace_variables_in_content(quartier.get('nom', ''), {})
        description = generator.replace_variables_in_content(quartier.get('description', ''), {})

        quartiers_data.append({
            'icon_svg': icon_svg,
            'nom': nom,
            'description': description
        })

    return generator.renderer.render_jinja2('components/quartiers-grid.html', {
        'quartiers': quartiers_data
    })


def _build_parkings_html(generator, parkings_data):
    """
    Génère le HTML pour la section parkings (v4.3 - Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur
        parkings_data (dict): Données de la section parkings

    Returns:
        str: HTML de la section parkings ou chaîne vide si non affiché
    """
    if not parkings_data.get('afficher', False):
        return ''

    # Préparer les données pour le template
    parkings_list = []
    for parking in parkings_data.get('parkings', []):
        icon_svg = generator._get_svg_icon(parking.get('icon', 'parking'))
        nom = generator.replace_variables_in_content(parking.get('nom', ''), {})

        parkings_list.append({
            'icon_svg': icon_svg,
            'nom': nom
        })

    return generator.renderer.render_jinja2('components/parkings-section.html', {
        'h3': generator.replace_variables_in_content(parkings_data.get('h3', ''), {}),
        'intro': generator.replace_variables_in_content(parkings_data.get('intro', ''), {}),
        'parkings': parkings_list,
        'conclusion': generator.replace_variables_in_content(parkings_data.get('conclusion', ''), {})
    })


def _get_category_class(generator, titre):
    """
    Retourne la classe CSS de couleur selon le titre de la catégorie

    Args:
        generator (SiteGenerator): Instance du générateur
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


def _build_services_categories_html(generator, categories, path_prefix='../'):
    """
    Génère le HTML pour les services groupés par catégories (v4.3 - Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur
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
        icon_svg = generator._get_svg_icon(category.get('icon', 'car'))
        titre = generator.replace_variables_in_content(category.get('titre', ''), {})
        category_class = _get_category_class(generator, titre)

        # Préparer les services de cette catégorie
        services_list = []
        for service in category.get('services', []):
            # Résoudre l'URL
            url_var = service.get('url_var', '')
            if url_var:
                slug = generator.resolve_variable_path(
                    generator.variables.get('template_variables', {}).get(url_var, ''),
                    generator.variables
                )
            else:
                slug = service.get('slug', '')

            service_url = f'{path_prefix}{slug}/index.html' if slug else '#'

            services_list.append({
                'nom': generator.replace_variables_in_content(service.get('nom', ''), {}),
                'description': generator.replace_variables_in_content(service.get('description', ''), {}),
                'url': service_url
            })

        categories_data.append({
            'icon_svg': icon_svg,
            'titre': titre,
            'class_attr': f' {category_class}' if category_class else '',
            'services': services_list
        })

    return generator.renderer.render_jinja2('components/services-categories.html', {
        'categories': categories_data,
        'path_prefix': path_prefix
    })


def _build_faq_locale_html(generator, faq_data):
    """
    Génère le HTML pour la FAQ locale (v4.3 - Jinja2)

    Args:
        generator (SiteGenerator): Instance du générateur
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
            'question': generator.replace_variables_in_content(q.get('question', ''), {}),
            'reponse': generator.replace_variables_in_content(q.get('reponse', ''), {})
        })

    return generator.renderer.render_jinja2('components/faq-locale.html', {
        'h2': faq_data.get('h2', 'Questions fréquentes'),
        'questions': questions_list
    })


def _build_hero_carousel_main(generator, images_data):
    """
    Construit le HTML du carrousel hero principal (un seul grand carrousel)

    Args:
        generator (SiteGenerator): Instance du générateur
        images_data (list): Liste des images [{image: 'xxx.webp', alt: 'xxx'}]

    Returns:
        tuple: (carousel_html, dots_html)
    """
    if not images_data or len(images_data) == 0:
        return '', ''

    carousel_parts = []
    dots_parts = []

    # Générer chaque image et son dot
    for idx, img_data in enumerate(images_data):
        image_filename = img_data.get('image', '')
        image_alt = img_data.get('alt', '')
        loading = 'eager' if idx == 0 else 'lazy'
        fetchpriority_attr = 'fetchpriority="high"' if idx == 0 else ''
        dot_active_class = 'active' if idx == 0 else ''

        # DIMENSIONS FIXES COHÉRENTES pour éviter CLS
        # Toutes les images hero DOIVENT avoir les MÊMES dimensions (ratio 4:3)
        # Le conteneur a aspect-ratio:4/3, les images doivent avoir width/height cohérents
        # Utiliser 800x600 pour toutes (ratio 4:3 parfait)
        dims_attrs = 'width="800" height="600"'

        # HTML de l'image (avec dimensions fixes cohérentes)
        carousel_parts.append(
            f'<img src="images/homepage/hero/{image_filename}" '
            f'alt="{image_alt}" '
            f'{dims_attrs} '
            f'class="hero-carousel-image" '
            f'loading="{loading}" '
            f'{fetchpriority_attr}>'
        )

        # HTML du dot (première active)
        dots_parts.append(
            f'<button class="hero-carousel-dot {dot_active_class}" data-index="{idx}" aria-label="Image {idx + 1}"></button>'
        )

    carousel_html = '\n        '.join(carousel_parts)
    dots_html = '\n        '.join(dots_parts)

    return carousel_html, dots_html


def _build_simple_carousel(generator, images_data, image_folder, path_prefix='../'):
    """
    Construit un carrousel simple réutilisable pour toutes les pages

    Args:
        generator (SiteGenerator): Instance du générateur
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
    dots_parts = []

    # Générer chaque image et son dot
    for idx, img_data in enumerate(images_data):
        image_filename = img_data.get('image', '')
        image_alt = img_data.get('alt', '')
        loading = 'eager' if idx == 0 else 'lazy'
        fetchpriority_attr = 'fetchpriority="high"' if idx == 0 else ''
        dot_active_class = 'active' if idx == 0 else ''

        # Récupérer les dimensions
        dims_attrs = generator.get_image_dimensions_attrs(f'{image_folder}/{image_filename}')

        # HTML de l'image
        carousel_parts.append(
            f'<img src="{path_prefix}images/{image_folder}/{image_filename}" '
            f'alt="{image_alt}" '
            f'{dims_attrs} '
            f'class="hero-carousel-image" '
            f'loading="{loading}" '
            f'{fetchpriority_attr}>'
        )

        # HTML du dot
        dots_parts.append(
            f'<button class="hero-carousel-dot {dot_active_class}" data-index="{idx}" aria-label="Image {idx + 1}"></button>'
        )

    carousel_images_html = '\n          '.join(carousel_parts)
    carousel_dots_html = '\n        '.join(dots_parts)

    # Construire le HTML complet du carousel
    carousel_html = f'''<div class="hero-carousel-simple">
  <div class="hero-carousel-simple-main">
    <div class="hero-carousel-track">
      {carousel_images_html}
    </div>

    <!-- Contrôles carrousel -->
    <button class="hero-carousel-prev" aria-label="Image précédente">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </button>
    <button class="hero-carousel-next" aria-label="Image suivante">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 18 15 12 9 6"></polyline>
      </svg>
    </button>
  </div>

  <!-- Dots navigation -->
  <div class="hero-carousel-dots">
    {carousel_dots_html}
  </div>
</div>'''

    return carousel_html
