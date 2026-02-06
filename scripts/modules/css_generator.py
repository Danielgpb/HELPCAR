#!/usr/bin/env python3
"""
CSS Generator - Génère les variables CSS depuis config/variables.json
Version: 2.0 - Utilise variables.json (source unique)
"""

import json
from pathlib import Path


class CSSGenerator:
    """Générateur de variables CSS depuis la configuration du site"""

    def __init__(self, base_path='.'):
        """
        Initialise le générateur CSS

        Args:
            base_path (str): Chemin vers la racine du projet
        """
        self.base_path = Path(base_path)
        self.config_path = self.base_path / 'config' / 'variables.json'
        self.output_path = self.base_path / 'public' / 'css' / 'variables.css'
        self.config = self.load_config()

    def load_config(self):
        """Charge la configuration depuis variables.json"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration introuvable : {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_css_variables(self):
        """Génère le CSS avec les variables depuis la configuration"""
        design = self.config.get('design', {})
        colors = design.get('colors', {})
        fonts = design.get('fonts', {})
        spacing = design.get('spacing', {})
        breakpoints = design.get('breakpoints', {})

        css = """/* ========================================
   VARIABLES CSS GÉNÉRÉES AUTOMATIQUEMENT
   ⚠️ NE PAS MODIFIER CE FICHIER DIRECTEMENT
   Modifiez config/variables.json et régénérez
   ======================================== */

:root {
  /* === COULEURS (depuis config/variables.json) === */
"""

        # Couleurs principales
        if colors:
            css += self._generate_color_variables(colors)

        # Dégradés (générés à partir des couleurs)
        css += self._generate_gradient_variables(colors)

        # Typographie
        if fonts:
            css += self._generate_font_variables(fonts)

        # Spacing
        if spacing:
            css += self._generate_spacing_variables(spacing)

        # Breakpoints (en commentaire pour référence)
        if breakpoints:
            css += self._generate_breakpoint_comments(breakpoints)

        css += """}

/* === IMPORTS DES POLICES === */
"""
        # Import Google Fonts si défini
        if fonts.get('google_font_url'):
            css += f"@import url('{fonts['google_font_url']}');\n"

        return css

    def _generate_color_variables(self, colors):
        """Génère les variables de couleurs"""
        css = ""

        # Couleur primaire (rouge)
        if 'primary' in colors:
            primary = colors['primary']
            css += f"  --red: {primary};\n"
            css += f"  --red-primary: {primary};\n"
            css += f"  --red-dark: {self._darken_color(primary, 15)};\n"
            css += f"  --red-light: #FF6B6B;\n"  # Fixe pour contraste WCAG AA sur fond noir

        # Couleur secondaire (orange)
        if 'secondary' in colors:
            secondary = colors['secondary']
            css += f"  --orange: {secondary};\n"
            css += f"  --orange-accent: {secondary};\n"
            css += f"  --orange-burnt: {secondary};\n"

        # Couleur de succès (vert)
        if 'success' in colors:
            success = colors['success']
            css += f"  --green: {success};\n"
            css += f"  --green-emerald: {success};\n"
            css += f"  --green-light: {self._lighten_color(success, 40)};\n"

        # Couleurs neutres
        if 'dark' in colors:
            css += f"  --black: {colors['dark']};\n"
            css += f"  --soft-black: #1E293B;\n"

        if 'light' in colors:
            css += f"  --white: {colors['light']};\n"
            css += f"  --off-white: #F8FAFC;\n"

        if 'gray' in colors:
            css += f"  --gray-dark: {colors['gray']};\n"

        # Couleurs fixes (non configurables)
        css += "  --light-gray: #F1F5F9;\n"
        css += "  --medium-gray: #E0E0E0;\n"
        css += "  --light-red: rgba(249, 115, 22, 0.1);\n"

        css += "\n"
        return css

    def _generate_gradient_variables(self, colors):
        """Génère les dégradés"""
        css = "  /* === DÉGRADÉS === */\n"

        primary = colors.get('primary', '#F97316')
        secondary = colors.get('secondary', '#F97316')

        css += f"  --gradient-primary: linear-gradient(135deg, {primary} 0%, {self._lighten_color(primary, 15)} 50%, {secondary} 100%);\n"
        css += f"  --gradient-cta: linear-gradient(135deg, {primary} 0%, {self._lighten_color(primary, 15)} 50%, {secondary} 100%);\n"
        css += f"  --gradient-intense: linear-gradient(135deg, {self._darken_color(primary, 15)} 0%, {primary} 100%);\n"
        css += f"  --gradient-soft: linear-gradient(135deg, rgba(249, 115, 22, 0.10) 0%, rgba(239, 68, 68, 0.08) 100%);\n"
        css += "  --gradient-hero-bg: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);\n"
        css += "\n"
        return css

    def _generate_font_variables(self, fonts):
        """Génère les variables de polices"""
        css = "  /* === TYPOGRAPHIE === */\n"
        primary_font = fonts.get('primary', "'Outfit', sans-serif")
        body_font = fonts.get('body', "'DM Sans', sans-serif")

        css += f"  --font-heading: {primary_font};\n"
        css += f"  --font-display: {primary_font};\n"
        css += f"  --font-body: {body_font};\n"
        css += "\n"
        return css

    def _generate_spacing_variables(self, spacing):
        """Génère les variables d'espacement"""
        css = "  /* === SPACING === */\n"
        css += "  --spacing-xs: 0.5rem;   /* 8px */\n"
        css += "  --spacing-sm: 1rem;     /* 16px */\n"
        css += "  --spacing-md: 1.5rem;   /* 24px */\n"
        css += "  --spacing-lg: 2rem;     /* 32px */\n"
        css += "  --spacing-xl: 3rem;     /* 48px */\n"
        css += "  --spacing-2xl: 4rem;    /* 64px */\n"
        css += "  --spacing-3xl: 6rem;    /* 96px */\n"
        css += "\n"
        return css

    def _generate_breakpoint_comments(self, breakpoints):
        """Génère les commentaires pour les breakpoints"""
        css = "  /* === BREAKPOINTS (référence pour @media queries) === */\n"
        css += f"  /* Mobile: {breakpoints.get('mobile', '640px')} */\n"
        css += f"  /* Tablet: {breakpoints.get('tablet', '768px')} */\n"
        css += f"  /* Desktop: {breakpoints.get('desktop', '1024px')} */\n"
        css += "\n"
        return css

    def _lighten_color(self, hex_color, percent):
        """Éclaircit une couleur hexadécimale d'un certain pourcentage"""
        # Conversion simple pour l'exemple
        # Pour une vraie conversion, utiliser un module comme colorsys
        hex_color = hex_color.lstrip('#')

        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            # Éclaircir vers le blanc
            r = min(255, int(r + (255 - r) * percent / 100))
            g = min(255, int(g + (255 - g) * percent / 100))
            b = min(255, int(b + (255 - b) * percent / 100))

            return f"#{r:02x}{g:02x}{b:02x}".upper()

        return hex_color

    def _darken_color(self, hex_color, percent):
        """Assombrit une couleur hexadécimale d'un certain pourcentage"""
        hex_color = hex_color.lstrip('#')

        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            # Assombrir vers le noir
            r = max(0, int(r * (100 - percent) / 100))
            g = max(0, int(g * (100 - percent) / 100))
            b = max(0, int(b * (100 - percent) / 100))

            return f"#{r:02x}{g:02x}{b:02x}".upper()

        return hex_color

    def generate(self, verbose=True):
        """
        Génère le fichier variables.css

        Args:
            verbose (bool): Afficher les logs
        """
        try:
            # Générer le CSS
            css_content = self.generate_css_variables()

            # Créer le dossier si nécessaire
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Écrire le fichier
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(css_content)

            if verbose:
                print(f"✅ Variables CSS générées : {self.output_path}")
                print(f"   Couleurs depuis : {self.config_path}")

            return True

        except Exception as e:
            if verbose:
                print(f"❌ Erreur lors de la génération du CSS : {e}")
            return False


def main():
    """Point d'entrée pour utilisation standalone"""
    generator = CSSGenerator()
    generator.generate()


if __name__ == '__main__':
    main()
