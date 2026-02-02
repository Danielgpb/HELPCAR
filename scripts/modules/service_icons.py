"""
Icônes SVG inline pour les services - Style moderne filled/dégradé
Utilisé par grid_builder.py et card_builder.py
"""

# Icônes SVG inline par slug de service (style filled, bicolore rouge/orange)
SERVICE_ICONS = {
    # Remorquage Voiture → dépanneuse
    'remorquage-voiture': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zM18 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="url(#g1)"/>
    </svg>''',
    # Dépannage Batterie → batterie
    'batterie': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4zM13 16h-2v-4H9l3-6v4h2l-3 6h2z" fill="url(#g2)"/>
    </svg>''',
    # Dépannage Batterie (slug alternatif)
    'depannage-batterie': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g2b" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4zM13 16h-2v-4H9l3-6v4h2l-3 6h2z" fill="url(#g2b)"/>
    </svg>''',
    # Réparation Pneu → pneu / roue
    'reparation-pneu': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g3" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <circle cx="12" cy="12" r="10" fill="url(#g3)" opacity="0.15"/>
        <circle cx="12" cy="12" r="10" stroke="url(#g3)" stroke-width="1.5" fill="none"/>
        <circle cx="12" cy="12" r="3" fill="url(#g3)"/>
        <path d="M12 2v4M12 18v4M2 12h4M18 12h4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" stroke="url(#g3)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>''',
    # Fourniture Carburant → pompe à essence
    'fourniture-carburant': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g4" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33a2.5 2.5 0 0 0 2.5 2.5c.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77zM12 10H6V5h6v5z" fill="url(#g4)"/>
    </svg>''',
    # Remorquage Moto → moto
    'remorquage-moto': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g5" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M19.44 9.03L15.41 5H11v2h3.59l2 2H5c-2.8 0-5 2.2-5 5s2.2 5 5 5c2.46 0 4.45-1.69 4.9-4h1.65l2.77-2.77c-.21.54-.32 1.14-.32 1.77 0 2.8 2.2 5 5 5s5-2.2 5-5c0-2.65-1.97-4.77-4.56-4.97zM7.82 15C7.4 16.15 6.28 17 5 17c-1.63 0-3-1.37-3-3s1.37-3 3-3c1.28 0 2.4.85 2.82 2H5v2h2.82zM19 17c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z" fill="url(#g5)"/>
    </svg>''',
    # Remorquage Motos (slug alternatif)
    'remorquage-motos': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g5b" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M19.44 9.03L15.41 5H11v2h3.59l2 2H5c-2.8 0-5 2.2-5 5s2.2 5 5 5c2.46 0 4.45-1.69 4.9-4h1.65l2.77-2.77c-.21.54-.32 1.14-.32 1.77 0 2.8 2.2 5 5 5s5-2.2 5-5c0-2.65-1.97-4.77-4.56-4.97zM7.82 15C7.4 16.15 6.28 17 5 17c-1.63 0-3-1.37-3-3s1.37-3 3-3c1.28 0 2.4.85 2.82 2H5v2h2.82zM19 17c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z" fill="url(#g5b)"/>
    </svg>''',
    # Véhicules Spéciaux → camion lourd
    'remorquage-vehicules-speciaux': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g6" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4z" fill="url(#g6)" opacity="0.2"/>
        <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zM18 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="url(#g6)"/>
        <rect x="4" y="6" width="8" height="3" rx="0.5" fill="white" opacity="0.5"/>
    </svg>''',
    # Remplacement Batterie → batterie + outil
    'remplacement-batterie': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g7" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4zM11 20v-5.5H9L13 7v5.5h2L11 20z" fill="url(#g7)"/>
    </svg>''',
    # Transport Routier Local → camion livraison
    'transport-routier-local': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g8" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zM18 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="url(#g8)"/>
    </svg>''',
    # Transport Longue Distance → camion route
    'transport-routier-longue-distance': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g9" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zM18 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="url(#g9)"/>
        <path d="M6 7h5l1.5 1.5L11 10H6V7z" fill="white" opacity="0.4"/>
    </svg>''',
    # Ouverture Porte Voiture → clé serrure
    'ouverture-de-porte': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g10" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M12.65 10C11.83 7.67 9.61 6 7 6c-3.31 0-6 2.69-6 6s2.69 6 6 6c2.61 0 4.83-1.67 5.65-4H17v4h4v-4h2v-4H12.65zM7 14c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z" fill="url(#g10)"/>
    </svg>''',
    # Ouverture Porte Voiture (slug alternatif)
    'ouverture-porte-voiture': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g10b" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M12.65 10C11.83 7.67 9.61 6 7 6c-3.31 0-6 2.69-6 6s2.69 6 6 6c2.61 0 4.83-1.67 5.65-4H17v4h4v-4h2v-4H12.65zM7 14c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z" fill="url(#g10b)"/>
    </svg>''',
    # Panne d'Essence → jauge vide
    'panne-essence': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g11" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33a2.5 2.5 0 0 0 2.5 2.5c.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77zM12 10H6V5h6v5z" fill="url(#g11)" opacity="0.5"/>
        <path d="M7 12l2 6h1l1-3 1 3h1l2-6" stroke="url(#g11)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>''',
    # Placement Roue de Secours → roue
    'placement-roue-secours': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g12" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <circle cx="12" cy="12" r="10" fill="url(#g12)" opacity="0.12"/>
        <circle cx="12" cy="12" r="10" stroke="url(#g12)" stroke-width="1.5" fill="none"/>
        <circle cx="12" cy="12" r="6" stroke="url(#g12)" stroke-width="1.5" fill="none"/>
        <circle cx="12" cy="12" r="2.5" fill="url(#g12)"/>
        <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="url(#g12)" stroke-width="2" stroke-linecap="round"/>
    </svg>''',
    # Dépannage Parking Souterrain → parking P
    'depannage-parking-souterrain': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g13" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <rect x="2" y="2" width="20" height="20" rx="4" fill="url(#g13)"/>
        <path d="M9 17V7h4a3.5 3.5 0 0 1 0 7H9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>''',
    # Voiture Embourbée → voiture + vagues
    'voiture-embourbee': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g14" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16C5.67 16 5 15.33 5 14.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" fill="url(#g14)"/>
        <path d="M2 21c1.5-1 3-1 4.5 0s3 1 4.5 0 3-1 4.5 0 3 1 4.5 0" stroke="url(#g14)" stroke-width="1.5" stroke-linecap="round" fill="none" opacity="0.6"/>
    </svg>''',
    # Siphonnage Réservoir / Erreur Carburant → avertissement
    'erreur-carburant': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g15" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M1 21h22L12 2 1 21z" fill="url(#g15)" opacity="0.15"/>
        <path d="M1 21h22L12 2 1 21z" stroke="url(#g15)" stroke-width="1.5" stroke-linejoin="round" fill="none"/>
        <path d="M12 9v4" stroke="url(#g15)" stroke-width="2" stroke-linecap="round"/>
        <circle cx="12" cy="16" r="1" fill="url(#g15)"/>
    </svg>''',
    'siphonnage-reservoir': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g15b" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M1 21h22L12 2 1 21z" fill="url(#g15b)" opacity="0.15"/>
        <path d="M1 21h22L12 2 1 21z" stroke="url(#g15b)" stroke-width="1.5" stroke-linejoin="round" fill="none"/>
        <path d="M12 9v4" stroke="url(#g15b)" stroke-width="2" stroke-linecap="round"/>
        <circle cx="12" cy="16" r="1" fill="url(#g15b)"/>
    </svg>''',
    # Enlèvement Épave → recyclage
    'enlevement-epave': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g16" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="url(#g16)" opacity="0.12"/>
        <path d="M5.5 7.5l2.5 4H4l2.5-4z" fill="url(#g16)"/>
        <path d="M18.5 7.5L16 11.5h4l-1.5-4z" fill="url(#g16)"/>
        <path d="M12 16.5l-2.5-4h5L12 16.5z" fill="url(#g16)"/>
        <path d="M7 8l5 8.5M17 8l-5 8.5M6 12h12" stroke="url(#g16)" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    </svg>''',
    # Panne Moteur → moteur
    'panne-moteur': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g17" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M7 10h10v6H7z" fill="url(#g17)" opacity="0.2"/>
        <rect x="7" y="10" width="10" height="6" rx="1" stroke="url(#g17)" stroke-width="1.5" fill="none"/>
        <path d="M5 11V9h2v2M17 11V9h2v2M5 15v2h2v-2M17 15v2h2v-2M9 10V7M15 10V7M3 13h4M17 13h4" stroke="url(#g17)" stroke-width="1.5" stroke-linecap="round"/>
    </svg>''',
    # Sortie de Fourrière → barrière levée
    'sortie-fourriere': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g18" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <rect x="4" y="10" width="4" height="12" rx="1" fill="url(#g18)"/>
        <path d="M8 12l12-6" stroke="url(#g18)" stroke-width="3" stroke-linecap="round"/>
        <path d="M8 14l10-5" stroke="white" stroke-width="1" stroke-linecap="round" opacity="0.4"/>
        <circle cx="6" cy="14" r="1.5" fill="white"/>
    </svg>''',
    # Dépannage Voiture Électrique → éclair
    'depannage-voiture-electrique': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g19" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <circle cx="12" cy="12" r="10" fill="url(#g19)" opacity="0.12"/>
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" fill="url(#g19)"/>
    </svg>''',
    # Dépannage Accident → voiture + croix urgence
    'depannage-accident': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g20" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16C5.67 16 5 15.33 5 14.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" fill="url(#g20)"/>
        <circle cx="19" cy="3" r="3" fill="url(#g20)"/>
        <path d="M19 1.5v3M17.5 3h3" stroke="white" stroke-width="1.2" stroke-linecap="round"/>
    </svg>''',
    # Dépannage Voiture → clé à molette
    'depannage-voiture': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g21" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z" fill="url(#g21)"/>
    </svg>''',
    # Dépannage Camionnette → utilitaire
    'depannage-camionnette': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g22" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M17 5H3c-1.1 0-2 .89-2 2v9h2c0 1.65 1.34 3 3 3s3-1.35 3-3h5.5c0 1.65 1.34 3 3 3s3-1.35 3-3H23v-5l-3-4h-3V5zM6 17.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM20 11l1.96 2.5H17V9.5h1.5L20 11zm-2.5 6.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="url(#g22)"/>
    </svg>''',
    # === SLUGS ALTERNATIFS pour la page services ===

    # Transport Routier (slug court)
    'transport-routier': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="gtr" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zM18 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="url(#gtr)"/>
    </svg>''',
    # Transport Local
    'transport-local': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="gtl" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zM18 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="url(#gtl)"/>
        <circle cx="8" cy="8" r="2" fill="white" opacity="0.4"/>
    </svg>''',
    # Transport Longue Distance
    'transport-longue-distance': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="gtld" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zM18 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" fill="url(#gtld)"/>
        <path d="M5 7h7l1.5 1-1.5 1H5V7z" fill="white" opacity="0.4"/>
    </svg>''',
    # Sortie de Fourrière (slug avec "de")
    'sortie-de-fourriere': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="gsf" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <rect x="4" y="10" width="4" height="12" rx="1" fill="url(#gsf)"/>
        <path d="M8 12l12-6" stroke="url(#gsf)" stroke-width="3" stroke-linecap="round"/>
        <path d="M8 14l10-5" stroke="white" stroke-width="1" stroke-linecap="round" opacity="0.4"/>
        <circle cx="6" cy="14" r="1.5" fill="white"/>
    </svg>''',
    # Voiture Embourbée (slug "embourbe")
    'embourbe': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="gem" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16C5.67 16 5 15.33 5 14.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" fill="url(#gem)"/>
        <path d="M1 21c1.5-1 3-1 4.5 0s3 1 4.5 0 3-1 4.5 0 3 1 4.5 0" stroke="url(#gem)" stroke-width="1.5" stroke-linecap="round" fill="none" opacity="0.5"/>
        <path d="M1 23.5c1.5-1 3-1 4.5 0s3 1 4.5 0 3-1 4.5 0 3 1 4.5 0" stroke="url(#gem)" stroke-width="1" stroke-linecap="round" fill="none" opacity="0.3"/>
    </svg>''',
    # Dépannage Parking Souterrain / Sous-sol
    'depannage-sous-sol': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="gss" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <rect x="2" y="2" width="20" height="20" rx="4" fill="url(#gss)"/>
        <path d="M9 17V7h4a3.5 3.5 0 0 1 0 7H9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <path d="M6 20l2-3M18 20l-2-3" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
    </svg>''',
    # Achat Voiture Accidentée → voiture + euro
    'achat-voiture-accidentee': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="gava" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16C5.67 16 5 15.33 5 14.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" fill="url(#gava)" opacity="0.6"/>
        <circle cx="18" cy="5" r="5" fill="url(#gava)"/>
        <text x="18" y="7.5" text-anchor="middle" fill="white" font-size="7" font-weight="700" font-family="Arial">€</text>
    </svg>''',
    # Dépannage Accident (slug alternatif)
    'depannage-accident-bruxelles': '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g20b" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
        <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16C5.67 16 5 15.33 5 14.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" fill="url(#g20b)"/>
        <circle cx="19" cy="3" r="3" fill="url(#g20b)"/>
        <path d="M19 1.5v3M17.5 3h3" stroke="white" stroke-width="1.2" stroke-linecap="round"/>
    </svg>''',
}

# Icône par défaut (clé à molette avec dégradé)
DEFAULT_SERVICE_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none">
    <defs><linearGradient id="gdef" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#CF5706"/><stop offset="100%" stop-color="#CF5706"/></linearGradient></defs>
    <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z" fill="url(#gdef)"/>
</svg>'''


# Photos de services (slug → nom de fichier jpg)
SERVICE_PHOTOS = {
    'remorquage-voiture': 'remorquage-voiture.jpg',
    'batterie': 'depannage-batterie.jpg',
    'depannage-batterie': 'depannage-batterie.jpg',
    'fourniture-carburant': 'fourniture-carburant.jpg',
    'remorquage-moto': 'remorquage-moto.jpg',
    'remorquage-motos': 'remorquage-moto.jpg',
    'remorquage-vehicules-speciaux': 'remorquage-vehicules-speciaux.jpg',
    'remplacement-batterie': 'remplacement-batterie.jpg',
}


def get_service_photo(slug, path_prefix=''):
    """Retourne le chemin de la photo pour un slug, ou None."""
    photo = SERVICE_PHOTOS.get(slug)
    if not photo:
        short_slug = slug.replace('-bruxelles', '').replace('-brussels', '')
        photo = SERVICE_PHOTOS.get(short_slug)
    if photo:
        return f'{path_prefix}images/services/{photo}'
    return None


_icon_counter = 0

def get_service_icon(slug):
    """
    Retourne l'icône SVG pour un slug donné.
    Chaque appel génère des id de gradient uniques pour éviter les conflits
    quand le même service apparaît plusieurs fois sur une page.
    """
    global _icon_counter
    _icon_counter += 1

    icon = SERVICE_ICONS.get(slug)
    if not icon:
        short_slug = slug.replace('-bruxelles', '').replace('-brussels', '')
        icon = SERVICE_ICONS.get(short_slug, DEFAULT_SERVICE_ICON)

    # Rendre les id de gradient uniques en ajoutant le compteur
    import re
    icon = re.sub(r'id="(g[^"]*)"', lambda m: f'id="{m.group(1)}_{_icon_counter}"', icon)
    icon = re.sub(r'url\(#(g[^)]*)\)', lambda m: f'url(#{m.group(1)}_{_icon_counter})', icon)
    return icon
