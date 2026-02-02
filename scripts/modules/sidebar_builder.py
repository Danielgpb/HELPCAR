#!/usr/bin/env python3
"""
Sidebar Builder Module - v1.0
Description: Génère des sidebars avec rotation intelligente
Date: 2025-12-17
"""

from pathlib import Path


class SidebarBuilder:
    """
    Construit des sidebars avec liens rotatifs
    """

    def __init__(self, base_path, lang='fr', data_loader=None):
        """
        Initialise le SidebarBuilder

        Args:
            base_path (Path): Chemin racine du projet
            lang (str): Code langue (fr, en, nl)
            data_loader (DataLoader): Instance du data loader
        """
        self.base_path = Path(base_path)
        self.lang = lang
        self.loader = data_loader

    def rotate_list(self, items, start_index):
        """
        Effectue une rotation circulaire sur une liste

        Args:
            items (list): Liste à rotater
            start_index (int): Index de début

        Returns:
            list: Liste rotatée
        """
        if not items or start_index == 0:
            return items
        return items[start_index:] + items[:start_index]

    def build_sidebar_services_links(self, limit=6, current_service_id=None, current_category=None, renderer=None):
        """
        Construit les liens services pour la sidebar avec rotation circulaire

        Args:
            limit (int): Nombre de services à afficher
            current_service_id (int): ID du service actuel (à exclure)
            current_category (str): Catégorie du service actuel
            renderer (TemplateRenderer): Instance du renderer

        Returns:
            str: HTML des liens
        """
        services = self.loader.load_services()
        links = []

        # Si on est sur une page service, prioriser la même catégorie avec rotation
        if current_category and current_service_id:
            same_category = [s for s in services if s['category'] == current_category and s['id'] != current_service_id]
            other_category = [s for s in services if s['category'] != current_category]

            # Trier par priority
            same_category_sorted = sorted(same_category, key=lambda x: x.get('priority', 999))
            other_category_sorted = sorted(other_category, key=lambda x: x.get('priority', 999))

            # Rotation circulaire basée sur service_id
            start_same = (current_service_id * 3) % len(same_category_sorted) if same_category_sorted else 0
            rotated_same = self.rotate_list(same_category_sorted, start_same)
            selected_same = rotated_same[:4]

            start_other = (current_service_id * 5) % len(other_category_sorted) if other_category_sorted else 0
            rotated_other = self.rotate_list(other_category_sorted, start_other)
            selected_other = rotated_other[:2]

            selected = selected_same + selected_other
        else:
            # Sinon, top services par priority
            selected = self.loader.get_services_by_priority(limit)

        for service in selected[:limit]:
            links.append({
                'text': service['name'],
                'url': f"../{service['slug']}/index.html",
                'category': service['category']
            })

        return renderer.build_sidebar_links(links)

    def build_sidebar_communes_links(self, limit=5, current_service_id=None, renderer=None):
        """
        Construit les liens communes pour sidebar avec rotation circulaire

        Args:
            limit (int): Nombre de communes à afficher
            current_service_id (int): ID du service actuel (pour rotation)
            renderer (TemplateRenderer): Instance du renderer

        Returns:
            str: HTML des liens
        """
        communes = self.loader.load_communes()

        # Tri par priorité
        communes_sorted = sorted(communes, key=lambda x: int(x.get('priority', 99)))
        links = []

        # Rotation circulaire basée sur service_id
        if current_service_id and len(communes_sorted) > limit:
            start_index = (current_service_id * 7) % len(communes_sorted)
            communes_rotated = self.rotate_list(communes_sorted, start_index)
            selected_communes = communes_rotated[:limit]
        else:
            selected_communes = communes_sorted[:limit]

        for commune in selected_communes:
            links.append({
                'text': commune['name'],
                'url': f"../{commune['slug']}/index.html"
            })

        return renderer.build_sidebar_links(links)

    def build_sidebar_voisines_links(self, commune_slug, renderer=None):
        """
        Construit les liens communes voisines

        Args:
            commune_slug (str): Slug de la commune actuelle
            renderer (TemplateRenderer): Instance du renderer

        Returns:
            str: HTML des liens voisines
        """
        voisines = self.loader.get_communes_voisines(commune_slug)
        links = []

        for voisine in voisines[:5]:  # Max 5
            links.append({
                'text': voisine['name'],
                'url': f"../{voisine['slug']}/index.html"
            })

        return renderer.build_sidebar_links(links)

    def build_zones_intervention_9_communes(self, current_service_id=1, path_prefix='../'):
        """
        Génère le contenu de la section Zones d'intervention avec 9 communes rotatées

        Args:
            current_service_id (int): ID du service actuel (pour rotation)
            path_prefix (str): Préfixe de chemin pour les liens

        Returns:
            str: HTML complet des 2 paragraphes
        """
        communes = self.loader.load_communes()

        # Séparer communes Bruxelles vs Périphérie
        communes_bruxelles = [c for c in communes if c.get('zone') == 'Bruxelles']
        communes_peripherie = [c for c in communes if c.get('zone') == 'Périphérie']

        # Trier par priorité
        communes_bruxelles_sorted = sorted(communes_bruxelles, key=lambda x: int(x.get('priority', 999)))
        communes_peripherie_sorted = sorted(communes_peripherie, key=lambda x: int(x.get('priority', 999)))

        # Rotation pour 3 communes Bruxelles
        start_bruxelles = (current_service_id * 3) % len(communes_bruxelles_sorted)
        communes_bxl_selected = []
        for i in range(3):
            idx = (start_bruxelles + i) % len(communes_bruxelles_sorted)
            communes_bxl_selected.append(communes_bruxelles_sorted[idx])

        # Rotation pour 6 communes Périphérie (ou moins si pas assez)
        communes_peri_selected = []
        if communes_peripherie_sorted:
            start_peripherie = (current_service_id * 6) % len(communes_peripherie_sorted)
            for i in range(min(6, len(communes_peripherie_sorted))):
                idx = (start_peripherie + i) % len(communes_peripherie_sorted)
                communes_peri_selected.append(communes_peripherie_sorted[idx])

        # Générer les liens en gras et gris
        bxl_links = [f'<a href="{path_prefix}{c["slug"]}/index.html" style="color: #6B7280; font-weight: 700;">{c["name"]}</a>' for c in communes_bxl_selected]
        peri_links_1 = [f'<a href="{path_prefix}{c["slug"]}/index.html" style="color: #6B7280; font-weight: 700;">{c["name"]}</a>' for c in communes_peri_selected[0:3]] if len(communes_peri_selected) >= 3 else []
        peri_links_2 = [f'<a href="{path_prefix}{c["slug"]}/index.html" style="color: #6B7280; font-weight: 700;">{c["name"]}</a>' for c in communes_peri_selected[3:6]] if len(communes_peri_selected) >= 6 else []

        # Paragraphe 1 - adapté si pas de périphérie
        if peri_links_1:
            p1 = f'<p>Que vous soyez coincé à {", ".join(bxl_links[0:2])}, {bxl_links[2] if len(bxl_links) > 2 else ""} ou n\'importe où dans les 19 communes de Bruxelles, on est là. Pareil pour la périphérie : {", ".join(peri_links_1[0:2])}, {peri_links_1[2] if len(peri_links_1) > 2 else ""}… En général, comptez <strong style="color: #10B981;">30 minutes</strong> et on est sur place.</p>'
        else:
            bxl_text = ", ".join(bxl_links) if bxl_links else "Bruxelles"
            p1 = f'<p>Que vous soyez coincé à {bxl_text} ou n\'importe où dans les 19 communes de Bruxelles, on est là. En général, comptez <strong style="color: #10B981;">30 minutes</strong> et on est sur place.</p>'

        # Paragraphe 2 - adapté si pas de périphérie
        if peri_links_2:
            p2 = f'<p>On se déplace aussi à {", ".join(peri_links_2[0:2])}, {peri_links_2[2] if len(peri_links_2) > 2 else ""}… bref, tout Bruxelles et les alentours. <strong style="color: #10B981;">Disponible 24h/24, 7j/7</strong>, même les jours fériés.</p>'
        else:
            p2 = f'<p>On se déplace dans tout Bruxelles et les alentours. <strong style="color: #10B981;">Disponible 24h/24, 7j/7</strong>, même les jours fériés.</p>'

        return p1 + '\n' + p2
