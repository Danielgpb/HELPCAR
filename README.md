# Help Car - Guide de Configuration

## 📁 Structure du Projet

```
help_car/
├── config/
│   └── config.json          # Configuration principale du site
├── content/
│   ├── locations/           # Fichiers JSON des 4 communes
│   │   ├── bruxelles-ville.json
│   │   ├── schaerbeek.json
│   │   ├── ixelles.json
│   │   └── etterbeek.json
│   └── services/            # Fichiers JSON des 22 services
│       ├── depannage-batterie-helpcar.json
│       ├── depannage-voiture-helpcar.json
│       └── ... (20 autres services)
├── templates/               # Templates HTML personnalisables
│   ├── base.html
│   ├── pages/
│   └── components/
├── images/                  # Images du site (voir images/README.md)
│   ├── logo/               # Logos Help Car
│   ├── homepage/           # Images homepage
│   ├── icons/              # Icônes
│   └── ... (11 autres)
├── public/
│   └── js/
│       └── whatsapp-smart.js
└── README.md               # Ce fichier
```

## 🎯 Fichiers à Personnaliser

### 1. Configuration Principale (`config/config.json`)

**Données à modifier en priorité :**

```json
{
  "site_name": "Help Car",
  "phone": "0479 89 00 89",                    // ← VOTRE NUMÉRO
  "email": "contact@helpcar.be",               // ← VOTRE EMAIL
  "domain": "helpcar.be",                      // ← VOTRE DOMAINE

  "company": {
    "legal_name": "Help Car SPRL",             // ← RAISON SOCIALE
    "tva": "BE 0XXX.XXX.XXX",                  // ← NUMÉRO TVA
    "address": "Rue Example 123, 1000 Bruxelles" // ← ADRESSE
  },

  "ratings": {
    "google_rating": "4.9",                    // ← VOS NOTES
    "google_reviews": "150"
  },

  "whatsapp": {
    "number": "+32479890089"                   // ← VOTRE WHATSAPP
  }
}
```

### 2. Fichiers de Contenu des Communes

**Localisation :** `content/locations/*.json`

**4 communes configurées :**
- Bruxelles-Ville
- Schaerbeek
- Ixelles
- Etterbeek

**Éléments personnalisables dans chaque fichier :**
- `seo.meta_title` : Titre SEO de la page
- `seo.meta_description` : Description SEO
- `hero.h1` : Titre principal
- `hero.accroche` : Sous-titre accrocheur
- `content.intro_autorite.paragraphe_*` : Textes d'introduction
- `content.faq_locale.questions[]` : FAQ spécifique à la commune

### 3. Fichiers de Contenu des Services

**Localisation :** `content/services/*.json`

**22 services disponibles :**
- Dépannage batterie
- Dépannage voiture
- Remorquage voiture
- Remorquage motos
- Ouverture porte voiture
- Panne essence
- Réparation pneu
- Et 15 autres...

**Éléments personnalisables :**
- `hero.h1` : Titre du service
- `sections[].content` : Contenu des sections
- `faq[]` : Questions fréquentes
- `cta` : Appels à l'action

### 4. Templates HTML

**Localisation :** `templates/`

**Templates copiés pour personnalisation :**
- `base.html` : Structure HTML de base
- `pages/*.html` : Pages individuelles
- `components/*.html` : Composants réutilisables

**Personnalisations possibles :**
- Couleurs (rechercher `#CF5706` pour le rouge, `#CF5706` pour l'orange)
- Polices de caractères
- Structure des pages
- Textes fixes dans les templates

## 🚀 Générer le Site Help Car

### Commandes de Génération

```bash
# Générer tout le site (recommandé)
python3 scripts/generate_helpcar.py

# Générer uniquement les pages services
python3 scripts/generate_helpcar.py --services-only

# Générer uniquement les pages communes
python3 scripts/generate_helpcar.py --communes-only

# Générer uniquement la homepage
python3 scripts/generate_helpcar.py --homepage-only

# Mode silencieux
python3 scripts/generate_helpcar.py --quiet
```

### Résultat de la Génération

Les fichiers HTML générés se trouvent dans :
```
help_car/build/fr/
├── index.html                    # Homepage
├── services/                     # Pages services
│   ├── depannage-batterie/
│   ├── remorquage-voiture/
│   └── ... (22 services)
├── zones/                        # Pages communes
│   ├── bruxelles-ville/
│   ├── schaerbeek/
│   ├── ixelles/
│   └── etterbeek/
└── public/                       # CSS, JS, images
    ├── css/                      # 8 fichiers CSS
    └── js/
```

### Tester le Site Localement

**Méthode 1 - Serveur HTTP (Recommandé) :**
```bash
# Lancer le serveur de développement
./scripts/serve.sh

# Ouvrir dans le navigateur :
# http://localhost:8000
```

**Méthode 2 - Ouvrir directement :**
```bash
open build/fr/index.html
```

⚠️ **Note** : Si les CSS ne s'affichent pas en ouvrant directement le fichier, utilisez la méthode 1 avec le serveur HTTP.

## 📝 Personnalisation

### Étape 1 : Configuration Principale

**Fichier :** `config/config.json`

Modifiez :
- ✏️ `phone` : Votre numéro
- ✏️ `email` : Votre email
- ✏️ `domain` : Votre domaine
- ✏️ `company.tva` : Votre TVA
- ✏️ `company.address` : Votre adresse

**Fichier :** `config/core/base.json`

Modifiez les informations Schema.org :
- Coordonnées géographiques
- Adresse complète
- Réseaux sociaux

### Étape 2 : Contenu des Communes

**Dossier :** `content/locations/` (4 fichiers)

Personnalisez pour chaque commune :
- SEO (meta_title, meta_description)
- Textes d'introduction
- FAQ localisées

### Étape 3 : Contenu des Services

**Dossier :** `content/services/` (22 fichiers)

Adaptez :
- Descriptions des services
- FAQ par service
- Mentions de tarifs

### Étape 4 : Design

**Dossier :** `templates/`

Modifiez :
- Couleurs (`#CF5706`, `#CF5706`, `#10B981`)
- Polices
- Textes fixes (header, footer)

### Étape 5 : Images

**Dossier :** `images/`

**📖 Guide complet :** Consultez `images/README.md` pour la liste détaillée

**Images prioritaires à créer :**
- ✏️ `logo/logo.png` - Logo Help Car
- ✏️ `homepage/hero.webp` - Image hero homepage
- ✏️ `icons/*.svg` - Icônes de services (batterie, voiture, etc.)
- ✏️ `carousel-photos/*.webp` - Photos du carrousel (5-8 photos)

**Structure créée :**
- 14 dossiers prêts à recevoir vos images
- Guide détaillé dans `images/README.md`
- Dimensions et formats recommandés

## 📝 Variables Disponibles

Les fichiers de contenu peuvent utiliser ces variables :

- `{{YEARS_EXPERIENCE}}` : Années d'expérience
- `{{GOOGLE_RATING}}` : Note Google
- `{{GOOGLE_REVIEWS}}` : Nombre d'avis Google
- `{{PHONE}}` : Numéro de téléphone
- `{{EMAIL}}` : Email
- `{{SITE_NAME}}` : Nom du site

Ces variables sont remplacées automatiquement lors de la génération.

## 🎨 Personnalisation Visuelle

### Couleurs Principales

Recherchez et remplacez dans les templates :

- **Rouge principal** : `#CF5706` → Votre couleur
- **Orange accent** : `#CF5706` → Votre couleur
- **Vert succès** : `#10B981` → Votre couleur

### Polices

Les polices utilisées sont définies dans les templates. Vous pouvez les changer dans `base.html`.

## 📞 Support

Pour toute question sur la configuration, référez-vous au projet principal `bruxelles-car-depannage` ou consultez la documentation des templates.

---

**Créé le :** 30 janvier 2026
**Version :** 1.0
**Projet source :** Bruxelles Car Dépannage
# HELPCAR
