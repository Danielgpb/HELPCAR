#!/usr/bin/env python3
"""
HELP CAR - Générateur de Pages HTML Statiques v1.0
Description: Script de génération pour le site Help Car
Basé sur: Bruxelles Car Dépannage v4.1
Auteur: Claude Code
Date: 2026-01-30
Version: 1.0 - Adaptation pour Help Car
"""

import argparse
import sys
from pathlib import Path

# Importer le générateur local
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(scripts_dir / 'modules'))

from generate import SiteGenerator


class HelpCarGenerator(SiteGenerator):
    """Générateur pour Help Car - hérite de SiteGenerator"""

    def __init__(self, lang='fr', verbose=True):
        """
        Initialise le générateur Help Car

        Args:
            lang (str): Code langue ('fr')
            verbose (bool): Afficher les logs détaillés
        """
        # Définir le dossier Help Car comme base
        help_car_root = Path(__file__).parent.parent

        # Appeler le constructeur parent avec le bon base_path
        super().__init__(
            base_path=str(help_car_root),
            lang=lang,
            verbose=verbose
        )

        # Surcharger le build_dir pour Help Car
        self.build_dir = help_car_root / 'build' / lang

        if verbose:
            print(f"\n🚗 === HELP CAR - GÉNÉRATEUR DE SITE v1.0 ===")
            print(f"📁 Base: {help_car_root}")
            print(f"📁 Build: {self.build_dir}")
            print(f"🌍 Langue: {lang.upper()}\n")

    def load_variables(self):
        """
        Charge les variables depuis config/variables.json de Help Car

        Returns:
            dict: Variables de configuration
        """
        import json

        # Charger variables.json (source principale)
        variables_file = self.base_path / 'config' / 'variables.json'
        variables = {}

        if variables_file.exists():
            try:
                with open(variables_file, 'r', encoding='utf-8') as f:
                    variables = json.load(f)
                if self.verbose:
                    print(f"✅ Variables chargées depuis variables.json")
            except Exception as e:
                print(f"❌ Erreur lecture variables.json: {e}")

        # Charger aussi config.json pour les infos de base
        config_file = self.base_path / 'config' / 'config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Fusionner les variables de config.json
                if 'variables' in config:
                    for key, value in config['variables'].items():
                        if key not in variables:
                            variables[key] = value

            except Exception as e:
                print(f"⚠️  Erreur lecture config.json: {e}")

        return variables


def main():
    """Point d'entrée du script"""
    parser = argparse.ArgumentParser(
        description='Générateur de site statique Help Car v1.0'
    )

    parser.add_argument(
        '--lang', '-l',
        default='fr',
        choices=['fr', 'en'],
        help='Langue du site (défaut: fr)'
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

    # Créer le générateur Help Car
    generator = HelpCarGenerator(
        lang=args.lang,
        verbose=not args.quiet
    )

    # Générer selon les options
    try:
        if args.services_only:
            generator.ensure_build_dir()
            generator.copy_css_files()
            generator.generate_all_services()
            print("\n✅ Pages services générées avec succès!")

        elif args.communes_only:
            generator.ensure_build_dir()
            generator.copy_css_files()
            generator.generate_all_communes()
            print("\n✅ Pages communes générées avec succès!")

        elif args.homepage_only:
            generator.ensure_build_dir()
            generator.copy_css_files()
            generator.copy_images()
            generator.optimize_images()
            generator.generate_homepage()
            print("\n✅ Homepage générée avec succès!")

        else:
            # Génération complète
            generator.generate_all()
            print("\n✅ Site Help Car généré avec succès!")

        # Afficher stats
        if not args.quiet:
            stats = generator.get_build_stats()
            if stats:
                print(f"📈 Build stats: {stats.get('total_files', 0)} fichiers générés")

    except Exception as e:
        print(f"\n❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
