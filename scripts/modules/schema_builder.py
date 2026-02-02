"""
Module: Schema.org Builder v2.0 - Multilingual
Description: Génère les blocs JSON-LD Schema.org pour chaque page (fr/en/nl)
Principe KISS & DRY
"""

import json
from pathlib import Path


class SchemaBuilder:
    """Construit les structures Schema.org pour SEO local (multilingue)"""

    def __init__(self, base_path='.', lang='fr'):
        """
        Initialise le builder avec langue

        Args:
            base_path (str): Chemin racine du projet
            lang (str): Code langue ('fr', 'en', 'nl')
        """
        self.base_path = Path(base_path)
        self.lang = lang

        # Nouvelle architecture v4.1 avec sous-dossiers
        self.core_dir = self.base_path / 'config' / 'core'
        self.schema_dir = self.base_path / 'config' / 'schema'

        # Charger les fichiers depuis nouvelle structure
        self.base_data = self._load_json('base.json', from_core=True)
        self.services_data = self._load_json(f'services/services-{lang}.json', from_core=True)
        self.templates = self._load_json('templates.json', from_core=False)

    def _load_json(self, filename, from_core=True):
        """
        Charge un fichier JSON depuis config/core/ ou config/schema/

        Args:
            filename (str): Nom du fichier
            from_core (bool): Si True, charge depuis core/, sinon depuis schema/
        """
        if from_core:
            filepath = self.core_dir / filename
        else:
            filepath = self.schema_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Schema file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_base_url(self):
        """Retourne l'URL de base selon la langue"""
        base = self.base_data['organization']['url']
        # Ne pas ajouter /fr/ pour la version française (langue par défaut)
        # Ajouter /en/ ou /nl/ uniquement pour les autres langues
        if self.lang == 'fr':
            return base
        else:
            return f"{base}/{self.lang}"

    def _get_aggregate_rating(self):
        """
        Retourne le bloc AggregateRating si les données sont disponibles

        Returns:
            dict: AggregateRating ou None si données manquantes
        """
        # Charger les variables depuis config/variables.json
        variables_path = self.base_path / 'config' / 'variables.json'

        if not variables_path.exists():
            return None

        with open(variables_path, 'r', encoding='utf-8') as f:
            variables = json.load(f)

        rating = variables.get('google', {}).get('rating')
        review_count = variables.get('google', {}).get('reviews_count')

        if not rating or not review_count:
            return None

        return {
            "@type": "AggregateRating",
            "ratingValue": str(rating),
            "reviewCount": str(review_count),
            "bestRating": "5",
            "worstRating": "1"
        }

    def build_homepage_schema(self):
        """
        Génère le schema complet pour la homepage avec AggregateRating

        Returns:
            dict: Schema AutoRepair complet avec inLanguage et aggregateRating
        """
        org = self.base_data['organization']

        schema = {
            "@context": "https://schema.org",
            "@type": "AutoRepair",
            "@id": org['@id'],
            "name": org['name'],
            "alternateName": org.get('alternateName'),
            "description": "Service de dépannage automobile 24h/24 à Bruxelles et périphérie. Intervention rapide en 30 minutes.",
            "url": self._get_base_url(),
            "logo": org['logo'],
            "image": org['image'],
            "telephone": org['telephone'],
            "email": org['email'],
            "priceRange": org['priceRange'],
            "inLanguage": self.lang,
            "address": org['address'],
            "geo": org['geo'],
            "openingHoursSpecification": org['openingHoursSpecification'],
            "areaServed": {
                "@type": "City",
                "name": "Bruxelles"
            },
            "sameAs": org.get('sameAs', []),
            "contactPoint": [
                {
                    "@type": "ContactPoint",
                    "telephone": org['telephone'],
                    "contactType": "Emergency Service",
                    "areaServed": "BE",
                    "availableLanguage": ["French", "Dutch", "English"]
                },
                {
                    "@type": "ContactPoint",
                    "telephone": org['telephone'],
                    "contactType": "Customer Service",
                    "areaServed": "BE",
                    "availableLanguage": ["French", "Dutch", "English"],
                    "contactOption": "TollFree",
                    "url": f"https://wa.me/{org['telephone'].replace('+', '').replace(' ', '')}"
                }
            ]
        }

        # Ajouter AggregateRating si disponible (★★★★★ dans Google SERP)
        aggregate_rating = self._get_aggregate_rating()
        if aggregate_rating:
            schema['aggregateRating'] = aggregate_rating

        return schema

    def build_service_schema(self, service_id=None, service_slug=None):
        """
        Génère le schema Service pour une page service

        Args:
            service_id (int, optional): ID du service (1-22)
            service_slug (str, optional): Slug du service

        Returns:
            dict: Schema Service avec inLanguage
        """
        # Trouver le service dans core data
        service = None

        if service_id:
            for s in self.services_data['services']:
                if s['id'] == service_id:
                    service = s
                    break

        if not service and service_slug:
            # Recherche par slug (à implémenter si nécessaire)
            pass

        if not service:
            raise ValueError(f"Service not found: id={service_id}, slug={service_slug}")

        org = self.base_data['organization']

        schema = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": service['name'],
            "serviceType": service['serviceType'],
            "description": service.get('meta_description', ''),
            "inLanguage": self.lang,
            "provider": {
                "@type": "AutoRepair",
                "@id": org['@id'],
                "name": org['name'],
                "telephone": org['telephone'],
                "url": self._get_base_url()
            },
            "areaServed": {
                "@type": "City",
                "name": "Bruxelles"
            },
            "availableChannel": {
                "@type": "ServiceChannel",
                "servicePhone": {
                    "@type": "ContactPoint",
                    "telephone": org['telephone'],
                    "contactType": "Emergency Service",
                    "areaServed": "BE",
                    "availableLanguage": ["French", "Dutch", "English"]
                }
            }
        }

        # PAS de prix (indicatif uniquement)
        # Comme spécifié par l'utilisateur

        return schema

    def build_commune_schema(self, commune_name, postal_code=None, description=None):
        """
        Génère le schema pour une page commune avec AggregateRating

        Args:
            commune_name (str): Nom de la commune
            postal_code (str, optional): Code postal
            description (str, optional): Description personnalisée

        Returns:
            dict: Schema AutoRepair pour la commune avec aggregateRating
        """
        org = self.base_data['organization']

        if not description:
            description = f"Service de dépannage automobile 24/7 à {commune_name}"

        schema = {
            "@context": "https://schema.org",
            "@type": "AutoRepair",
            "name": f"{org['name']} - {commune_name}",
            "description": description,
            "telephone": org['telephone'],
            "email": org['email'],
            "inLanguage": self.lang,
            "url": f"{self._get_base_url()}/depannage-{commune_name.lower().replace(' ', '-')}/",
            "areaServed": {
                "@type": "City",
                "name": commune_name,
                "addressCountry": "BE"
            },
            "parentOrganization": {
                "@type": "AutoRepair",
                "@id": org['@id'],
                "name": org['name'],
                "telephone": org['telephone']
            },
            "contactPoint": [
                {
                    "@type": "ContactPoint",
                    "telephone": org['telephone'],
                    "contactType": "Emergency Service",
                    "areaServed": "BE",
                    "availableLanguage": ["French", "Dutch", "English"]
                },
                {
                    "@type": "ContactPoint",
                    "telephone": org['telephone'],
                    "contactType": "Customer Service",
                    "areaServed": "BE",
                    "availableLanguage": ["French", "Dutch", "English"],
                    "contactOption": "TollFree",
                    "url": f"https://wa.me/{org['telephone'].replace('+', '').replace(' ', '')}"
                }
            ]
        }

        if postal_code:
            schema['areaServed']['postalCode'] = postal_code

        # Ajouter AggregateRating si disponible (★★★★★ dans Google SERP)
        aggregate_rating = self._get_aggregate_rating()
        if aggregate_rating:
            schema['aggregateRating'] = aggregate_rating

        return schema

    def build_breadcrumb_schema(self, items):
        """
        Génère le schema BreadcrumbList

        Args:
            items (list): Liste de tuples (name, url)
                         Ex: [("Home", "/"), ("Services", "/services")]

        Returns:
            dict: Schema BreadcrumbList
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        }

        for position, (name, url) in enumerate(items, start=1):
            schema['itemListElement'].append({
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": url
            })

        return schema

    def build_faq_schema(self, questions_answers):
        """
        Génère le schema FAQPage

        Args:
            questions_answers (list): Liste de tuples (question, answer)

        Returns:
            dict: Schema FAQPage
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "inLanguage": self.lang,
            "mainEntity": []
        }

        for question, answer in questions_answers:
            schema['mainEntity'].append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer
                }
            })

        return schema

    def build_organization_complete_schema(self):
        """
        Génère le schema organization complet avec hasOfferCatalog

        Returns:
            dict: Schema AutoRepair + LocalBusiness complet
        """
        org = self.base_data['organization']

        # Créer la liste des services
        services_list = []
        for service in self.services_data['services']:
            services_list.append({
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Service",
                    "name": service['name'],
                    "serviceType": service['serviceType'],
                    "description": service.get('meta_description', '')
                }
            })

        schema = {
            "@context": "https://schema.org",
            "@type": ["AutoRepair", "LocalBusiness"],
            "@id": org['@id'],
            "name": org['name'],
            "alternateName": org.get('alternateName'),
            "description": "Service de dépannage automobile 24h/24 à Bruxelles et périphérie. Intervention rapide en 30 minutes.",
            "url": self._get_base_url(),
            "logo": org['logo'],
            "image": org['image'],
            "telephone": org['telephone'],
            "email": org['email'],
            "priceRange": org['priceRange'],
            "inLanguage": self.lang,
            "address": org['address'],
            "geo": org['geo'],
            "openingHoursSpecification": org['openingHoursSpecification'],
            "sameAs": org.get('sameAs', []),
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": self._get_catalog_name(),
                "itemListElement": services_list
            }
        }

        # Ajouter AggregateRating si disponible (★★★★★ dans Google SERP)
        aggregate_rating = self._get_aggregate_rating()
        if aggregate_rating:
            schema['aggregateRating'] = aggregate_rating

        return schema

    def _get_catalog_name(self):
        """Retourne le nom du catalogue selon la langue"""
        names = {
            'fr': "Services de dépannage automobile",
            'en': "Car breakdown services",
            'nl': "Autopech diensten"
        }
        return names.get(self.lang, names['fr'])

    def to_json_ld(self, schema):
        """
        Convertit un dict schema en JSON-LD pour injection HTML

        Args:
            schema (dict): Schema dict

        Returns:
            str: JSON-LD formaté dans une balise <script type="application/ld+json">
        """
        json_content = json.dumps(schema, ensure_ascii=False, indent=2)
        return f'<script type="application/ld+json">\n{json_content}\n</script>'

    def get_all_services(self):
        """
        Retourne la liste complète des 22 services dans la langue actuelle

        Returns:
            list: Services avec id, name, serviceType, description, category
        """
        return self.services_data['services']

    def get_service_by_id(self, service_id):
        """
        Récupère un service spécifique par son ID

        Args:
            service_id (int): ID du service (1-22)

        Returns:
            dict: Service ou None
        """
        for service in self.services_data['services']:
            if service['id'] == service_id:
                return service
        return None

    def get_services_by_category(self, category='google_aligned'):
        """
        Filtre les services par catégorie

        Args:
            category (str): 'google_aligned' ou 'supplementaire'

        Returns:
            list: Services filtrés
        """
        return [s for s in self.services_data['services'] if s.get('category') == category]


# Exemple d'utilisation
if __name__ == '__main__':
    print("=" * 60)
    print("TEST SCHEMA BUILDER v2.0 - MULTILINGUAL")
    print("=" * 60)
    print()

    # Test FR
    print("📄 TEST FRANÇAIS")
    print("-" * 60)
    builder_fr = SchemaBuilder('../..', lang='fr')

    homepage_fr = builder_fr.build_homepage_schema()
    print(f"✅ Homepage schema FR:")
    print(f"   - @id: {homepage_fr['@id']}")
    print(f"   - inLanguage: {homepage_fr['inLanguage']}")
    print(f"   - name: {homepage_fr['name']}")
    print()

    service_fr = builder_fr.build_service_schema(service_id=1)
    print(f"✅ Service schema FR:")
    print(f"   - name: {service_fr['name']}")
    print(f"   - serviceType: {service_fr['serviceType']}")
    print(f"   - inLanguage: {service_fr['inLanguage']}")
    print()

    # Test EN
    print("📄 TEST ENGLISH")
    print("-" * 60)
    builder_en = SchemaBuilder('../..', lang='en')

    service_en = builder_en.build_service_schema(service_id=1)
    print(f"✅ Service schema EN:")
    print(f"   - name: {service_en['name']}")
    print(f"   - serviceType: {service_en['serviceType']}")
    print(f"   - inLanguage: {service_en['inLanguage']}")
    print()

    # Test services count
    print("📊 TEST SERVICES COUNT")
    print("-" * 60)
    services_fr = builder_fr.get_all_services()
    services_en = builder_en.get_all_services()
    print(f"✅ Services FR: {len(services_fr)}")
    print(f"✅ Services EN: {len(services_en)}")
    print()

    # Test categories
    google_aligned = builder_fr.get_services_by_category('google_aligned')
    supplementaires = builder_fr.get_services_by_category('supplementaire')
    print(f"✅ Services Google alignés: {len(google_aligned)}")
    print(f"✅ Services supplémentaires: {len(supplementaires)}")
    print()

    print("=" * 60)
    print("✅ TOUS LES TESTS RÉUSSIS")
    print("=" * 60)
