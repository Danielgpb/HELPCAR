# Images Help Car - Guide de Structure

## 📁 Structure des Dossiers

```
images/
├── a-propos/              # Images page À Propos
├── carousel-photos/       # Photos du carrousel (homepage)
├── communes/              # Images des communes (optionnel)
├── contact/               # Images page Contact
├── homepage/              # Images de la homepage
├── icons/                 # Icônes SVG/PNG
├── logo/                  # Logos Help Car
├── mentions-legales/      # Images mentions légales
├── politique-confidentialite/  # Images politique
├── service/               # Images génériques services
├── services-index/        # Images page index services
├── tarif/                 # Images page tarifs
└── zones-index/           # Images page index zones
```

## 🎨 Images Prioritaires à Créer

### 1. Logo (`logo/`)

**Fichiers requis :**
- `logo.png` - Logo principal PNG (pour compatibilité)
- `logo.webp` - Logo principal WebP (performance)
- `helpcar-logo.png` - Version alternative
- `favicon.ico` - Favicon du site

**Dimensions recommandées :**
- Logo principal : 300x100px (ou ratio 3:1)
- Favicon : 32x32px et 16x16px

### 2. Homepage (`homepage/`)

**Fichiers requis :**
- `hero.webp` - Image hero principale (1920x800px)
- `hero.jpg` - Version JPG fallback
- `depannage-service.webp` - Image de service (800x600px)

### 3. Carousel Photos (`carousel-photos/`)

**Fichiers suggérés :**
- `depannage-1.webp` - Dépanneuse en action
- `depannage-2.webp` - Remorquage voiture
- `depannage-3.webp` - Intervention batterie
- `depannage-4.webp` - Équipe Help Car
- `depannage-5.webp` - Véhicule Help Car

**Dimensions :** 800x600px (ratio 4:3)

### 4. Icons (`icons/`)

**Icônes de services (SVG ou PNG 64x64px) :**
- `battery.svg` - Batterie
- `car.svg` - Voiture
- `truck.svg` - Dépanneuse
- `key.svg` - Clé
- `fuel.svg` - Carburant
- `tire.svg` - Pneu
- `phone.svg` - Téléphone
- `clock.svg` - Horloge
- `map-pin.svg` - Localisation
- `check.svg` - Validation
- `star.svg` - Étoile (avis)
- `alert.svg` - Alerte/Urgence

### 5. Services (`service/`)

**Images génériques pour pages services :**
- `depannage-batterie.webp`
- `remorquage.webp`
- `pneu-creve.webp`
- `ouverture-porte.webp`
- `service-default.webp` - Image par défaut

**Dimensions :** 1200x800px

### 6. Contact (`contact/`)

**Images page contact :**
- `contact-hero.webp` - Image hero (1920x600px)
- `phone-icon.png` - Icône téléphone
- `email-icon.png` - Icône email

### 7. Zones Index (`zones-index/`)

**Images page liste des zones :**
- `bruxelles-map.webp` - Carte de Bruxelles
- `zones-hero.webp` - Image hero

### 8. Services Index (`services-index/`)

**Images page liste des services :**
- `services-hero.webp` - Image hero (1920x600px)

## 📋 Images Optionnelles

### Communes (`communes/`)
- Images spécifiques à chaque commune (optionnel)
- `bruxelles-ville.webp`
- `schaerbeek.webp`
- `ixelles.webp`
- `etterbeek.webp`

### Tarifs (`tarif/`)
- `tarif-hero.webp` - Image hero page tarifs

### Pages Légales
- `mentions-legales/` - Images pour mentions légales (rarement utilisé)
- `politique-confidentialite/` - Images pour politique (rarement utilisé)

## 🔧 Formats d'Images Recommandés

### Format Principal : WebP
- **Avantage :** Compression supérieure, meilleure performance
- **Utilisation :** Toutes les images principales

### Format Fallback : JPG/PNG
- **JPG :** Photos, images complexes
- **PNG :** Logos, icônes, images avec transparence

### Format Vectoriel : SVG
- **Utilisation :** Icônes, logos simples
- **Avantage :** Évolutif, léger

## 📐 Dimensions Recommandées

| Type d'image | Dimensions | Format |
|--------------|------------|--------|
| Hero homepage | 1920x800px | WebP + JPG |
| Hero pages | 1920x600px | WebP + JPG |
| Service detail | 1200x800px | WebP |
| Carousel | 800x600px | WebP |
| Logo principal | 300x100px | PNG + WebP |
| Icônes | 64x64px | SVG ou PNG |
| Favicon | 32x32px | ICO ou PNG |

## 🎯 Images Minimales pour Démarrer

Pour un site fonctionnel minimal, créez au moins :

1. **Logo** : `logo/logo.png`
2. **Hero homepage** : `homepage/hero.webp`
3. **Icônes de base** : `icons/phone.svg`, `icons/car.svg`, `icons/battery.svg`
4. **Image service par défaut** : `service/service-default.webp`

## 💡 Conseils

- Optimisez toutes les images avant de les uploader
- Utilisez des noms de fichiers descriptifs en minuscules
- Format : `description-du-contenu.extension`
- Évitez les espaces, utilisez des tirets `-`
- Compressez les images (TinyPNG, Squoosh, etc.)
- Cible : < 200KB par image pour une bonne performance

## 🔗 Outils d'Optimisation

- **Squoosh** : https://squoosh.app (WebP conversion)
- **TinyPNG** : https://tinypng.com (Compression PNG/JPG)
- **SVGOMG** : https://jakearchibald.github.io/svgomg/ (Optimisation SVG)

---

**Créé le :** 30 janvier 2026
**Version :** 1.0
