"""
Module: Data Loader v3.0 - Source Unique Schema.org
Description: Charge les données depuis Schema.org (source de vérité unique)
Principe KISS & DRY
"""

import csv
import json
import sys
from pathlib import Path

# Import relatif ou absolu selon contexte
try:
    from .schema_builder import SchemaBuilder
except ImportError:
    # Si exécuté directement, utiliser import absolu
    from schema_builder import SchemaBuilder


class DataLoader:
    """Charge et structure les données sources (multilingue) depuis Schema.org"""

    def __init__(self, base_path, lang='fr'):
        """
        Initialise le loader

        Args:
            base_path (str): Chemin racine du projet
            lang (str): Code langue ('fr', 'en', 'nl')
        """
        self.base_path = Path(base_path)
        self.lang = lang

        # Nouveaux chemins pour architecture multilingue
        self.locales_dir = self.base_path / 'locales' / lang
        self.data_dir = self.base_path / 'data'  # Data à la racine maintenant

        # Config globale (non traduite)
        self.config_dir = self.base_path / 'config'
        self.content_dir = self.base_path / 'content' / lang

        # Initialiser SchemaBuilder comme source de vérité
        self.schema_builder = SchemaBuilder(base_path, lang=lang)

    def load_csv(self, filename):
        """
        Charge un fichier CSV et retourne une liste de dictionnaires

        Args:
            filename (str): Nom du fichier CSV (ex: 'communes.csv')

        Returns:
            list: Liste de dictionnaires (une ligne = un dict)
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def load_json(self, filename, from_config=True):
        """
        Charge un fichier JSON

        Args:
            filename (str): Nom du fichier JSON
            from_config (bool): Si True, charge depuis /config/, sinon depuis locales/{lang}/

        Returns:
            dict: Contenu JSON parsé
        """
        if from_config:
            filepath = self.config_dir / filename
        else:
            filepath = self.locales_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"JSON file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_services(self):
        """
        Charge la liste complète des services depuis Schema.org (source de vérité unique)

        Returns:
            list: Services avec toutes leurs métadonnées dans la langue actuelle
        """
        # Source unique : Schema.org JSON
        return self.schema_builder.get_all_services()

    def load_communes(self, active_only=True):
        """
        Charge la liste complète des communes depuis core/locations/locations-{lang}.json

        Args:
            active_only (bool): Si True, retourne uniquement les locations actives (défaut: True)

        Returns:
            list: Communes avec métadonnées dans la langue actuelle
        """
        # Nouvelle architecture v4.1 : JSON depuis config/core/locations/
        locations_dir = self.base_path / 'config' / 'core' / 'locations'
        locations_file = locations_dir / f'locations-{self.lang}.json'

        if not locations_file.exists():
            raise FileNotFoundError(f"Locations file not found: {locations_file}")

        with open(locations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            locations = data['locations']

        # Filtrer les locations actives si demandé
        if active_only:
            locations = [loc for loc in locations if loc.get('active', True)]

        return locations

    def get_communes_voisines(self, commune_slug):
        """
        Récupère les communes voisines d'une commune donnée

        Args:
            commune_slug (str): Slug de la commune (ex: 'depannage-ixelles')

        Returns:
            list: Liste des communes voisines avec leurs données complètes
        """
        # Charger toutes les communes (incluant les inactives pour trouver la commune actuelle)
        all_locations = self.load_communes(active_only=False)

        # Trouver la commune actuelle
        current_commune = None
        for loc in all_locations:
            if loc['slug'] == commune_slug:
                current_commune = loc
                break

        if not current_commune or 'neighbors' not in current_commune:
            # Fallback : retourner les communes actives par priorité
            return self.load_communes(active_only=True)[:5]

        # Récupérer les noms des voisins
        neighbors_names = current_commune['neighbors']

        # Charger les communes actives
        active_communes = self.load_communes(active_only=True)

        # Trouver les communes voisines dans les communes actives
        voisines = []
        for neighbor_name in neighbors_names:
            for commune in active_communes:
                if commune['name'] == neighbor_name:
                    voisines.append(commune)
                    break

        return voisines

    def load_ui_translations(self):
        """
        Charge les traductions UI (labels, boutons, navigation, etc.)

        Returns:
            dict: Toutes les traductions UI pour la langue actuelle
        """
        return self.load_json('ui.json', from_config=False)

    def load_component_translations(self, lang=None):
        """
        Charge les traductions des composants réutilisables

        Args:
            lang (str, optional): Langue à charger. Utilise self.lang par défaut.

        Returns:
            dict: Traductions des composants pour la langue spécifiée
        """
        if lang is None:
            lang = self.lang

        components_file = self.base_path / 'locales' / lang / 'components.json'
        try:
            with open(components_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Fichier components.json introuvable pour {lang}: {components_file}")
            return {}

    def get_service_by_id(self, service_id):
        """
        Récupère un service spécifique par son ID

        Args:
            service_id (int): ID du service (1-22)

        Returns:
            dict: Service ou None
        """
        return self.schema_builder.get_service_by_id(service_id)

    def get_service_by_slug(self, slug):
        """
        Récupère un service par son slug

        Args:
            slug (str): Slug du service (ex: 'remorquage-voiture-bruxelles')

        Returns:
            dict: Service ou None
        """
        services = self.load_services()
        for service in services:
            if service.get('slug') == slug:
                return service
        return None

    def get_services_by_category(self, category='Remorquage'):
        """
        Filtre les services par catégorie métier

        Args:
            category (str): 'Remorquage' ou 'Dépannage'

        Returns:
            list: Services filtrés
        """
        services = self.load_services()
        return [s for s in services if s.get('category') == category]

    def get_services_by_priority(self, limit=8):
        """
        Retourne les services triés par priorité

        Args:
            limit (int): Nombre de services à retourner

        Returns:
            list: Services triés par priority ASC
        """
        services = self.load_services()
        sorted_services = sorted(services, key=lambda s: s.get('priority', 999))
        return sorted_services[:limit]

    def get_google_aligned_services(self):
        """
        Retourne uniquement les services alignés Google Business Profile

        Returns:
            list: Services avec isGoogleAligned = true
        """
        services = self.load_services()
        return [s for s in services if s.get('isGoogleAligned', False)]

    def get_supplementary_services(self):
        """
        Retourne les services supplémentaires (non sur Google)

        Returns:
            list: Services avec isGoogleAligned = false
        """
        services = self.load_services()
        return [s for s in services if not s.get('isGoogleAligned', False)]

    def get_available_languages(self):
        """
        Retourne la liste des langues disponibles

        Returns:
            list: Codes langues disponibles ['fr', 'en', 'nl']
        """
        languages = []
        locales_root = self.base_path / 'locales'

        if not locales_root.exists():
            return ['fr']  # Fallback

        for lang_dir in locales_root.iterdir():
            if lang_dir.is_dir() and lang_dir.name in ['fr', 'en', 'nl']:
                languages.append(lang_dir.name)

        return sorted(languages)

    def load_commune_content(self, commune_slug):
        """
        Charge le contenu personnalisé d'une commune depuis content/{lang}/locations/{slug}.json
        Supporte les versions v1.0 (ancien format) et v2.0 (format enrichi SEO)

        Args:
            commune_slug (str): Slug de la commune (ex: 'depannage-ixelles')

        Returns:
            dict: Contenu personnalisé de la commune avec détection automatique de version
        """
        content_path = self.content_dir / 'locations' / f'{commune_slug}.json'

        if not content_path.exists():
            print(f"⚠️  Contenu commune introuvable: {content_path}")
            return {
                'version': '1.0',
                'content': {
                    'h2_1': '',
                    'content_h2_1': '',
                    'h2_3': '',
                    'content_h2_3': ''
                }
            }

        with open(content_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Détection automatique de la version
            version = data.get('version', '1.0')

            if version == '1.0':
                # Ancien format - compatibilité rétroactive
                print(f"📄 Commune {commune_slug}: format v1.0 (ancien)")
            elif version == '2.0':
                # Nouveau format enrichi SEO
                print(f"✨ Commune {commune_slug}: format v2.0 (enrichi SEO)")

            return data

    def load_homepage_content(self):
        """
        Charge le contenu éditorial de la homepage depuis content/{lang}/pages/homepage.json

        Returns:
            dict: Contenu éditorial de la homepage (hero, stats, sections, etc.)
        """
        content_path = self.content_dir / 'pages' / 'homepage.json'

        if not content_path.exists():
            print(f"⚠️  Contenu homepage introuvable: {content_path}")
            return {}

        with open(content_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_stats(self):
        """
        Retourne des statistiques sur les données chargées

        Returns:
            dict: Statistiques (nombre services, communes, langues, etc.)
        """
        services = self.load_services()
        communes = self.load_communes()

        google_aligned = [s for s in services if s.get('isGoogleAligned', False)]
        supplementary = [s for s in services if not s.get('isGoogleAligned', False)]

        remorquage = [s for s in services if s.get('category') == 'Remorquage']
        depannage = [s for s in services if s.get('category') == 'Dépannage']

        return {
            'total_services': len(services),
            'google_aligned': len(google_aligned),
            'supplementary': len(supplementary),
            'remorquage': len(remorquage),
            'depannage': len(depannage),
            'total_communes': len(communes),
            'languages': self.get_available_languages(),
            'current_language': self.lang
        }


# Tests unitaires
if __name__ == '__main__':
    print("=" * 60)
    print("TEST DATA LOADER v3.0 - SOURCE UNIQUE SCHEMA.ORG")
    print("=" * 60)
    print()

    # Test FR
    print("📄 TEST FRANÇAIS")
    print("-" * 60)
    loader_fr = DataLoader('../..', lang='fr')

    services_fr = loader_fr.load_services()
    print(f"✅ Services FR: {len(services_fr)}")
    print(f"   - Premier service: {services_fr[0]['name']}")
    print(f"   - Slug: {services_fr[0]['slug']}")
    print(f"   - Catégorie: {services_fr[0]['category']}")
    print(f"   - Google aligned: {services_fr[0]['isGoogleAligned']}")
    print()

    # Test get_service_by_id
    service_1 = loader_fr.get_service_by_id(1)
    print(f"✅ Service ID 1: {service_1['name']}")
    print()

    # Test get_service_by_slug
    service_bat = loader_fr.get_service_by_slug('depannage-batterie-bruxelles')
    print(f"✅ Service par slug: {service_bat['name']} (ID {service_bat['id']})")
    print()

    # Test catégories
    remorquage = loader_fr.get_services_by_category('Remorquage')
    depannage = loader_fr.get_services_by_category('Dépannage')
    print(f"✅ Services Remorquage: {len(remorquage)}")
    print(f"✅ Services Dépannage: {len(depannage)}")
    print()

    # Test priority
    top_8 = loader_fr.get_services_by_priority(8)
    print(f"✅ Top 8 services par priorité:")
    for i, s in enumerate(top_8, 1):
        print(f"   {i}. {s['name']} (priority: {s['priority']})")
    print()

    # Test Google aligned
    google = loader_fr.get_google_aligned_services()
    supplementary = loader_fr.get_supplementary_services()
    print(f"✅ Services Google aligned: {len(google)}")
    print(f"✅ Services supplémentaires: {len(supplementary)}")
    print()

    # Test stats
    stats = loader_fr.get_stats()
    print(f"📊 STATISTIQUES:")
    print(f"   - Total services: {stats['total_services']}")
    print(f"   - Google aligned: {stats['google_aligned']}")
    print(f"   - Supplémentaires: {stats['supplementary']}")
    print(f"   - Remorquage: {stats['remorquage']}")
    print(f"   - Dépannage: {stats['depannage']}")
    print(f"   - Communes: {stats['total_communes']}")
    print(f"   - Langues disponibles: {stats['languages']}")
    print()

    print("=" * 60)
    print("✅ TOUS LES TESTS RÉUSSIS")
    print("=" * 60)
