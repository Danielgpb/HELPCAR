/**
 * ========================================
 * WHATSAPP SMART MODULE V5 - PRODUCTION
 * Version: 7.5
 * Date: 2026-01-29
 *
 * Formulaire WhatsApp conversationnel multi-étapes :
 * - Style chat moderne avec bulles de conversation
 * - Mobile-first design
 * - Barre de progression
 * - Sélecteur de langue avec codes texte (FR/EN/NL)
 * - 5 étapes max (6 si remorquage avec destination)
 * - Messages personnalisés selon le problème
 * - Google Places Autocomplete + Directions API
 * - Icônes SVG inline
 * - Flux spécial épave (marque/modèle/année)
 *
 * Architecture: Modulaire, KISS, DRY
 * ========================================
 */

(function() {
  'use strict';

  // ========================================
  // SECTION 1: CONFIGURATION & CONSTANTS
  // ========================================

  const DEFAULT_CONFIG = {
    phoneNumber: '32479890089',
    geolocationTimeout: 5000,
    googleMapsApiKey: window.GOOGLE_MAPS_API_KEY || 'AIzaSyDDWguZ0hygny9cH7zG__Br2z6tTxud5-o',
    language: 'fr',
    debug: true,
    typingDelayInitial: 1500,      // Délai initial avant première réponse (plus long)
    typingDelayBetweenMessages: 800, // Délai entre 2 messages du bot
    typingDelayAfterUser: 1200,    // Délai après réponse utilisateur (simule réflexion)
    transitionDelay: 400            // Délai avant affichage des options
  };

  const CONFIG = window.WHATSAPP_CONFIG ? {
    ...DEFAULT_CONFIG,
    ...window.WHATSAPP_CONFIG
  } : DEFAULT_CONFIG;

  // ========================================
  // SECTION 2: TRANSLATIONS (i18n)
  // ========================================

  // Translations will be loaded dynamically from JSON files
  let TRANSLATIONS = {
    fr: {
      // Header
      header_title: 'Demande de devis',
      header_status: 'Disponible 24h/24',

      // Progress
      progress_step: 'Étape',
      progress_of: 'sur',
      progress_badge: 'Rapide et sans engagement',

      // Language selector
      lang_fr: 'Français',
      lang_en: 'English',
      lang_nl: 'Nederlands',

      // Step 0: Problem
      step0_bot_greeting: 'Bonjour ! On est disponibles pour vous aider.',
      step0_bot_question: 'Décrivez-nous votre problème et recevez un tarif, sans engagement.',

      problem_battery: 'Ma batterie est plate',
      problem_nostart: 'Ma voiture ne démarre plus',
      problem_flat: 'J\'ai un pneu crevé',
      problem_towing: 'J\'ai besoin d\'un remorquage',
      problem_wreck: 'Je veux évacuer une épave',
      problem_other: 'Autre problème',

      // Personalized responses per problem
      response_battery: 'On peut venir faire un boost ou remplacer votre batterie sur place. Pour vous donner un prix, on a besoin de quelques infos sur votre véhicule.',
      response_nostart: 'On peut venir diagnostiquer le problème sur place, ou remorquer votre véhicule chez votre garagiste. Dites-nous en plus sur votre voiture.',
      response_flat: 'On peut venir changer votre roue sur place. Pour vous donner un tarif, quelques questions rapides sur votre véhicule.',
      response_towing: 'On peut remorquer votre véhicule où vous voulez : garage, domicile, concessionnaire. Quelques infos sur votre voiture pour le tarif.',
      response_wreck: 'On s\'occupe de l\'évacuation et des formalités. Quelques infos sur le véhicule pour établir le devis.',
      response_other: 'Pas de souci, on verra ça ensemble. Donnez-nous d\'abord quelques infos sur votre véhicule.',

      // Urgent banner
      urgent_title: 'Urgence ? Appelez-nous',
      urgent_phone: '0479 89 00 89',

      // Step 1: Vehicle category
      step1_bot_question: 'Quel type de véhicule ?',

      vehicle_citadine: 'Citadine',
      vehicle_citadine_examples: 'Clio, 208, Polo...',
      vehicle_berline: 'Berline / SUV',
      vehicle_berline_examples: 'Golf, 308, A3...',
      vehicle_utilitaire: 'Utilitaire',
      vehicle_utilitaire_examples: 'Kangoo, Berlingo...',
      vehicle_premium: 'Premium / Sport',
      vehicle_premium_examples: 'BMW, Mercedes...',

      // Step 2: Transmission
      step2_bot_question: 'Boîte manuelle ou automatique ?',

      transmission_manual: 'Manuelle',
      transmission_automatic: 'Automatique',

      // Step 3: 4WD
      step3_bot_question: '4 roues motrices ?',

      fourwd_yes: 'Oui',
      fourwd_no: 'Non',

      // Step 4: Location
      step4_bot_question: 'Dernière étape : où êtes-vous ? On calcule le tarif et le temps d\'arrivée.',
      step4_gps_btn: 'Utiliser ma position actuelle',
      step4_address_btn: 'Entrer une adresse',
      step4_separator: 'ou',
      step4_address_placeholder: 'Tapez une adresse...',
      step4_back_btn: 'Retour',
      step4_privacy: 'Utilisé uniquement pour ce devis',

      gps_searching: 'Localisation en cours...',

      // Step 4b: Destination (towing only)
      step4b_bot_question: 'Où souhaitez-vous emmener le véhicule ?',
      step4b_unknown_btn: 'Je ne sais pas encore',
      step4b_hint: 'On peut vous conseiller un garage proche et de confiance.',

      distance_label: 'Distance',
      duration_label: 'Temps estimé',

      // Step 5: Summary
      step5_bot_message: 'Parfait, on a tout ce qu\'il faut. Cliquez ci-dessous pour recevoir votre tarif sur WhatsApp.',
      step5_summary_title: 'Récapitulatif',
      step5_summary_company: 'Bruxelles Car Dépannage',

      summary_problem: 'Problème',
      summary_vehicle: 'Véhicule',
      summary_transmission: 'Transmission',
      summary_location: 'Position',
      summary_destination: 'Destination',

      location_gps: 'Localisé',
      location_address: 'Adresse fournie',
      destination_unknown: 'À déterminer',

      fourwd_label_yes: '4x4',
      fourwd_label_no: '2RM',

      // Final CTA
      cta_whatsapp: 'Envoyer sur WhatsApp',
      cta_trust_title: 'Sans engagement',
      cta_trust_message: 'On ne se déplace jamais sans votre feu vert.',

      // Trust badges
      badge_rating: '4.9/5',
      badge_time: '30 min',
      badge_payment: 'Paiement sur place',

      // WhatsApp message
      msg_greeting: 'Bonjour,',
      msg_intro: 'Je souhaite obtenir un devis pour une intervention.',
      msg_problem: 'Problème :',
      msg_vehicle: 'Véhicule :',
      msg_transmission: 'Transmission :',
      msg_location: 'Localisation :',
      msg_destination: 'Destination :',
      msg_distance: 'Distance estimée :',
      msg_closing: 'Merci de me communiquer le tarif et le délai d\'intervention.',

      // Footer
      footer_privacy: 'Vos données restent confidentielles'
    },

    en: {
      // Header
      header_title: 'Quote Request',
      header_status: 'Available 24/7',

      // Progress
      progress_step: 'Step',
      progress_of: 'of',
      progress_badge: 'Fast and no commitment',

      // Language selector
      lang_fr: 'Français',
      lang_en: 'English',
      lang_nl: 'Nederlands',

      // Step 0
      step0_bot_greeting: 'Hello! We\'re here to help you.',
      step0_bot_question: 'Describe your problem and get a quote, no commitment.',

      problem_battery: 'Dead battery',
      problem_nostart: 'Won\'t start',
      problem_flat: 'Flat tire',
      problem_towing: 'Towing',
      problem_wreck: 'Wreck removal',
      problem_other: 'Other problem',

      response_battery: 'We can jump-start or replace your battery on-site. To give you a price, we need some info about your vehicle.',
      response_nostart: 'We can diagnose the problem on-site or tow your vehicle to your mechanic. Tell us about your car.',
      response_flat: 'We can change your wheel on-site. A few quick questions about your vehicle for the quote.',
      response_towing: 'We can tow your vehicle anywhere: garage, home, dealer. Some info about your car for the price.',
      response_wreck: 'We handle the removal and paperwork. Some vehicle info to establish the quote.',
      response_other: 'No problem, we\'ll figure it out together. First, tell us about your vehicle.',

      urgent_title: 'Urgent? Call us',
      urgent_phone: '0479 89 00 89',

      // Step 1
      step1_bot_question: 'What type of vehicle?',

      vehicle_citadine: 'City car',
      vehicle_citadine_examples: 'Clio, 208, Polo...',
      vehicle_berline: 'Sedan / SUV',
      vehicle_berline_examples: 'Golf, 308, A3...',
      vehicle_utilitaire: 'Van',
      vehicle_utilitaire_examples: 'Kangoo, Berlingo...',
      vehicle_premium: 'Premium / Sport',
      vehicle_premium_examples: 'BMW, Mercedes...',

      // Step 2
      step2_bot_question: 'Manual or automatic transmission?',

      transmission_manual: 'Manual',
      transmission_automatic: 'Automatic',

      // Step 3
      step3_bot_question: '4-wheel drive?',

      fourwd_yes: 'Yes',
      fourwd_no: 'No',

      // Step 4
      step4_bot_question: 'Last step: where are you? We\'ll calculate the price and arrival time.',
      step4_gps_btn: 'Use my current location',
      step4_address_btn: 'Enter an address',
      step4_separator: 'or',
      step4_address_placeholder: 'Type an address...',
      step4_back_btn: 'Back',
      step4_privacy: 'Used only for this quote',

      gps_searching: 'Locating...',

      // Step 4b
      step4b_bot_question: 'Where do you want the vehicle taken?',
      step4b_unknown_btn: 'I don\'t know yet',
      step4b_hint: 'We can recommend a nearby trusted garage.',

      distance_label: 'Distance',
      duration_label: 'Est. time',

      // Step 5
      step5_bot_message: 'Perfect, we have everything we need. Click below to receive your quote on WhatsApp.',
      step5_summary_title: 'Summary',
      step5_summary_company: 'Brussels Car Breakdown',

      summary_problem: 'Problem',
      summary_vehicle: 'Vehicle',
      summary_transmission: 'Transmission',
      summary_location: 'Location',
      summary_destination: 'Destination',

      location_gps: 'Located',
      location_address: 'Address provided',
      destination_unknown: 'To be determined',

      fourwd_label_yes: '4WD',
      fourwd_label_no: '2WD',

      cta_whatsapp: 'Send on WhatsApp',
      cta_trust_title: 'No commitment',
      cta_trust_message: 'We never dispatch without your approval.',

      badge_rating: '4.9/5',
      badge_time: '30 min',
      badge_payment: 'Payment on-site',

      // WhatsApp message
      msg_greeting: 'Hello,',
      msg_intro: 'I would like to get a quote for a service.',
      msg_problem: 'Problem:',
      msg_vehicle: 'Vehicle:',
      msg_transmission: 'Transmission:',
      msg_location: 'Location:',
      msg_destination: 'Destination:',
      msg_distance: 'Estimated distance:',
      msg_closing: 'Please provide me with the price and service time.',

      footer_privacy: 'Your data remains confidential'
    },

    nl: {
      // Header
      header_title: 'Offerte aanvraag',
      header_status: 'Beschikbaar 24/7',

      // Progress
      progress_step: 'Stap',
      progress_of: 'van',
      progress_badge: 'Snel en zonder verplichting',

      // Language selector
      lang_fr: 'Français',
      lang_en: 'English',
      lang_nl: 'Nederlands',

      // Step 0
      step0_bot_greeting: 'Dag! We zijn beschikbaar om u te helpen.',
      step0_bot_question: 'Beschrijf uw probleem en ontvang een prijs, zonder verplichting.',

      problem_battery: 'Batterij leeg',
      problem_nostart: 'Start niet',
      problem_flat: 'Lekke band',
      problem_towing: 'Slepen',
      problem_wreck: 'Wrak verwijdering',
      problem_other: 'Ander probleem',

      response_battery: 'We kunnen komen voor een boost of uw batterij ter plaatse vervangen. Om u een prijs te geven, hebben we wat info over uw voertuig nodig.',
      response_nostart: 'We kunnen het probleem ter plaatse diagnosticeren of uw voertuig naar uw garage slepen. Vertel ons meer over uw auto.',
      response_flat: 'We kunnen uw wiel ter plaatse vervangen. Een paar snelle vragen over uw voertuig voor de prijs.',
      response_towing: 'We kunnen uw voertuig overal naartoe slepen: garage, thuis, dealer. Wat info over uw auto voor de prijs.',
      response_wreck: 'We zorgen voor de verwijdering en formaliteiten. Wat info over het voertuig om de offerte op te stellen.',
      response_other: 'Geen probleem, we zullen het samen bekijken. Geef ons eerst wat info over uw voertuig.',

      urgent_title: 'Dringend? Bel ons',
      urgent_phone: '0479 89 00 89',

      // Step 1
      step1_bot_question: 'Welk type voertuig?',

      vehicle_citadine: 'Stadsauto',
      vehicle_citadine_examples: 'Clio, 208, Polo...',
      vehicle_berline: 'Sedan / SUV',
      vehicle_berline_examples: 'Golf, 308, A3...',
      vehicle_utilitaire: 'Bestelwagen',
      vehicle_utilitaire_examples: 'Kangoo, Berlingo...',
      vehicle_premium: 'Premium / Sport',
      vehicle_premium_examples: 'BMW, Mercedes...',

      // Step 2
      step2_bot_question: 'Manuele of automatische versnelling?',

      transmission_manual: 'Manueel',
      transmission_automatic: 'Automatisch',

      // Step 3
      step3_bot_question: 'Vierwielaandrijving?',

      fourwd_yes: 'Ja',
      fourwd_no: 'Nee',

      // Step 4
      step4_bot_question: 'Laatste stap: waar bent u? We berekenen de prijs en aankomsttijd.',
      step4_gps_btn: 'Gebruik mijn huidige locatie',
      step4_address_btn: 'Voer een adres in',
      step4_separator: 'of',
      step4_address_placeholder: 'Typ een adres...',
      step4_back_btn: 'Terug',
      step4_privacy: 'Alleen gebruikt voor deze offerte',

      gps_searching: 'Localiseren...',

      // Step 4b
      step4b_bot_question: 'Waar wilt u het voertuig naartoe brengen?',
      step4b_unknown_btn: 'Ik weet het nog niet',
      step4b_hint: 'We kunnen een betrouwbare garage in de buurt aanbevelen.',

      distance_label: 'Afstand',
      duration_label: 'Geschatte tijd',

      // Step 5
      step5_bot_message: 'Perfect, we hebben alles wat we nodig hebben. Klik hieronder om uw prijs op WhatsApp te ontvangen.',
      step5_summary_title: 'Samenvatting',
      step5_summary_company: 'Brussels Car Breakdown',

      summary_problem: 'Probleem',
      summary_vehicle: 'Voertuig',
      summary_transmission: 'Transmissie',
      summary_location: 'Locatie',
      summary_destination: 'Bestemming',

      location_gps: 'Gelokaliseerd',
      location_address: 'Adres verstrekt',
      destination_unknown: 'Te bepalen',

      fourwd_label_yes: '4WD',
      fourwd_label_no: '2WD',

      cta_whatsapp: 'Verstuur via WhatsApp',
      cta_trust_title: 'Geen verplichting',
      cta_trust_message: 'We komen nooit zonder uw goedkeuring.',

      badge_rating: '4.9/5',
      badge_time: '30 min',
      badge_payment: 'Betaling ter plaatse',

      // WhatsApp message
      msg_greeting: 'Dag,',
      msg_intro: 'Ik wil graag een offerte voor een dienst.',
      msg_problem: 'Probleem:',
      msg_vehicle: 'Voertuig:',
      msg_transmission: 'Transmissie:',
      msg_location: 'Locatie:',
      msg_destination: 'Bestemming:',
      msg_distance: 'Geschatte afstand:',
      msg_closing: 'Gelieve mij de prijs en de servicetijd mee te delen.',

      footer_privacy: 'Uw gegevens blijven vertrouwelijk'
    }
  };

  // Function to load translations from JSON files
  async function loadTranslations() {
    const version = '7.9'; // Cache busting
    const languages = ['fr', 'en', 'nl'];

    for (const lang of languages) {
      try {
        const response = await fetch(`public/config/whatsapp-v5/${lang}.json?v=${version}`);
        if (response.ok) {
          const data = await response.json();
          const flattened = flattenTranslations(data);

          // Debug: log flattened translations for 'locked'
          console.log(`[${lang}] Loaded translations for 'locked':`, {
            problem_locked: flattened.problem_locked,
            response_locked: flattened.response_locked
          });

          // Merge loaded translations with existing ones
          TRANSLATIONS[lang] = {
            ...TRANSLATIONS[lang],
            ...flattened
          };
        }
      } catch (error) {
        console.warn(`Failed to load ${lang} translations:`, error);
      }
    }

    // Debug: log final translations
    console.log('Final FR translations for locked:', {
      problem_locked: TRANSLATIONS.fr.problem_locked,
      response_locked: TRANSLATIONS.fr.response_locked
    });
  }

  // Helper function to flatten nested JSON into dot notation
  function flattenTranslations(obj, prefix = '') {
    const flattened = {};

    for (const [key, value] of Object.entries(obj)) {
      const newKey = prefix ? `${prefix}_${key}` : key;

      if (value && typeof value === 'object' && !Array.isArray(value)) {
        // Handle 'problems', 'vehicles', 'transmissions', etc.
        if (value.label || value.response || value.examples) {
          // Remove plural 's' from parent key (problems -> problem, vehicles -> vehicle)
          const singularPrefix = prefix.replace(/s$/, '');
          const finalKey = singularPrefix ? `${singularPrefix}_${key}` : key;

          if (value.label) flattened[finalKey] = value.label;
          if (value.response) flattened[`response_${key}`] = value.response;
          if (value.examples) flattened[`${finalKey}_examples`] = value.examples;
        } else {
          Object.assign(flattened, flattenTranslations(value, newKey));
        }
      } else {
        flattened[newKey] = value;
      }
    }

    return flattened;
  }

  // ========================================
  // SECTION 3: DATA STRUCTURES
  // ========================================

  const PROBLEMS = [
    { id: 'battery', needsDestination: false },
    { id: 'nostart', needsDestination: false },
    { id: 'flat', needsDestination: false },
    { id: 'towing', needsDestination: true },
    { id: 'wreck', needsDestination: false },
    { id: 'locked', needsDestination: false },
    { id: 'other', needsDestination: false }
  ];

  const VEHICLE_CATEGORIES = [
    { id: 'citadine' },
    { id: 'berline' },
    { id: 'utilitaire' },
    { id: 'premium' }
  ];

  const TRANSMISSIONS = [
    { id: 'manual' },
    { id: 'automatic' }
  ];

  // ========================================
  // SECTION 4: SVG ICONS
  // ========================================

  const ICONS = {
    // Navigation
    close: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
    chevronRight: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>`,

    // Status
    check: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
    zap: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
    lock: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,
    shield: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,

    // Problems
    battery: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="16" height="10" rx="2" ry="2"></rect><line x1="22" y1="11" x2="22" y2="13"></line></svg>`,
    circleSlash: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>`,
    circleDot: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3" fill="currentColor"></circle></svg>`,
    truck: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>`,
    trash: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`,
    messageCircle: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>`,

    // Vehicles
    carFront: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17h14v2a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-2z"></path><path d="M5 11h14v2H5z"></path><path d="M6 11l1.5-4.5A2 2 0 0 1 9.24 5h5.52a2 2 0 0 1 1.74 1.5L18 11"></path><circle cx="8" cy="15" r="1"></circle><circle cx="16" cy="15" r="1"></circle></svg>`,

    // Transmission
    settings2: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"></path></svg>`,
    cog: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path></svg>`,

    // Location
    navigation: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 11 22 2 13 21 11 13 3 11"></polygon></svg>`,
    search: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
    mapPin: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>`,
    loader: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>`,
    helpCircle: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,

    // Communication
    phone: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>`,
    whatsapp: `<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>`,

    // Badges
    star: `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`,
    clock: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
    creditCard: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg>`
  };

  // ========================================
  // SECTION 5: STATE MANAGEMENT
  // ========================================

  let state = {
    currentStep: 0,
    isTyping: false,
    showAddressInput: false,
    showDestinationInput: false,
    currentLanguage: detectLanguage(),
    problem: null,
    vehicle: null,
    wheelPosition: null,
    transmission: null,
    fourWheelDrive: null,
    // For wreck removal
    vehicleBrand: null,
    vehicleModel: null,
    vehicleYear: null,
    location: {
      type: null, // 'gps' ou 'manual'
      coords: null,
      address: ''
    },
    destination: {
      address: '',
      unknown: false,
      distance: null,
      duration: null
    }
  };

  let modalElement = null;
  let directionsService = null;

  // ========================================
  // SECTION 6: UTILITY FUNCTIONS
  // ========================================

  function log(message, data) {
    if (CONFIG.debug) {
      console.log(`[WhatsApp V5] ${message}`, data || '');
    }
  }

  function detectLanguage() {
    if (CONFIG.language && TRANSLATIONS[CONFIG.language]) {
      return CONFIG.language;
    }
    const pathMatch = window.location.pathname.match(/\/(fr|en|nl)\//);
    if (pathMatch) return pathMatch[1];

    const htmlLang = document.documentElement.lang;
    if (htmlLang) {
      const langCode = htmlLang.split('-')[0].toLowerCase();
      if (TRANSLATIONS[langCode]) return langCode;
    }

    const browserLang = navigator.language || navigator.userLanguage;
    if (browserLang) {
      const langCode = browserLang.split('-')[0].toLowerCase();
      if (TRANSLATIONS[langCode]) return langCode;
    }

    return 'fr';
  }

  function t(key) {
    return TRANSLATIONS[state.currentLanguage][key] || key;
  }

  function createGoogleMapsLink(lat, lng) {
    return `https://maps.google.com/?q=${lat},${lng}`;
  }

  // ========================================
  // SECTION 7: HTML BUILDERS - HEADER
  // ========================================

  function createHeader() {
    return `
      <div class="wa-header-v5">
        <div class="wa-header-left">
          <div class="wa-header-avatar">BCD</div>
          <div class="wa-header-info">
            <div class="wa-header-title">${t('header_title')}</div>
            <div class="wa-header-status">
              <span class="wa-status-dot"></span>
              ${t('header_status')}
            </div>
          </div>
        </div>
        <div class="wa-header-right">
          ${createLanguageSelector()}
          <button class="wa-close-btn" aria-label="Fermer">${ICONS.close}</button>
        </div>
      </div>
    `;
  }

  function createLanguageSelector() {
    return `
      <div class="wa-lang-selector">
        <button class="wa-lang-btn" id="wa-current-lang">
          <span class="wa-lang-code">${state.currentLanguage.toUpperCase()}</span>
        </button>
        <div class="wa-lang-dropdown" id="wa-lang-dropdown">
          ${Object.keys(TRANSLATIONS).map(lang => `
            <button class="wa-lang-option ${lang === state.currentLanguage ? 'active' : ''}" data-lang="${lang}">
              <span class="wa-lang-code">${lang.toUpperCase()}</span>
            </button>
          `).join('')}
        </div>
      </div>
    `;
  }

  // ========================================
  // SECTION 8: HTML BUILDERS - PROGRESS BAR
  // ========================================

  function createProgressBar() {
    // Juste le badge informatif, sans icône ni étapes
    return `
      <div class="wa-progress-bar">
        <div class="wa-progress-info">
          <div class="wa-progress-badge">
            <span>${t('progress_badge')}</span>
          </div>
        </div>
      </div>
    `;
  }

  // ========================================
  // SECTION 9: HTML BUILDERS - CHAT MESSAGES
  // ========================================

  function createBotMessage(text) {
    return `
      <div class="wa-message wa-bot-message wa-fade-in">
        <div class="wa-bot-avatar">
          <img src="images/logo.png" alt="BCD" class="wa-bot-logo" />
        </div>
        <div class="wa-message-bubble wa-bot-bubble">${text}</div>
      </div>
    `;
  }

  function createUserMessage(text) {
    return `
      <div class="wa-message wa-user-message wa-fade-in">
        <div class="wa-message-bubble wa-user-bubble">${text}</div>
      </div>
    `;
  }

  function createTypingIndicator() {
    return `
      <div class="wa-message wa-bot-message wa-typing-indicator">
        <div class="wa-bot-avatar">
          <img src="images/logo.png" alt="BCD" class="wa-bot-logo" />
        </div>
        <div class="wa-typing-bubble">
          <span class="wa-typing-dot"></span>
          <span class="wa-typing-dot"></span>
          <span class="wa-typing-dot"></span>
        </div>
      </div>
    `;
  }

  // ========================================
  // SECTION 10: HTML BUILDERS - BUTTONS
  // ========================================

  function createOptionButton(id, icon, label, subtitle = '') {
    return `
      <button class="wa-option-btn" data-option-id="${id}">
        <div class="wa-option-icon">${icon}</div>
        <div class="wa-option-content">
          <div class="wa-option-label">${label}</div>
          ${subtitle ? `<div class="wa-option-subtitle">${subtitle}</div>` : ''}
        </div>
        ${ICONS.chevronRight}
      </button>
    `;
  }

  function createSmallOptionButton(id, icon, label) {
    return `
      <button class="wa-small-option-btn" data-option-id="${id}">
        <div class="wa-small-option-icon">${icon}</div>
        <div class="wa-small-option-label">${label}</div>
      </button>
    `;
  }

  // ========================================
  // SECTION 11: HTML BUILDERS - STEPS
  // ========================================

  function createStep0() {
    const problemIcons = {
      battery: ICONS.battery,
      nostart: ICONS.circleSlash,
      flat: ICONS.circleDot,
      towing: ICONS.truck,
      wreck: ICONS.trash,
      locked: ICONS.lock,
      other: ICONS.messageCircle
    };

    let html = '';

    // Si on est en train de "taper" à cette étape, afficher uniquement l'indicateur
    if (state.isTyping && state.currentStep === 0) {
      html += createTypingIndicator();
    } else if (state.currentStep >= 0) {
      // Toujours afficher le message du bot (même après avoir avancé)
      html += createBotMessage(`<div class="wa-bot-text">${t('step0_bot_message')}</div>`);

      // Afficher les options SEULEMENT si on est exactement à l'étape 0
      if (state.currentStep === 0) {
        html += `<div class="wa-options-container wa-options-delayed" id="wa-step0-options">`;
        PROBLEMS.forEach(problem => {
          html += createOptionButton(
            problem.id,
            problemIcons[problem.id],
            t('problem_' + problem.id)
          );
        });
        html += `</div>`;
      }
    }

    return html;
  }

  function createStep1() {
    let html = '';

    if (state.problem) {
      // Toujours afficher la réponse de l'utilisateur
      html += createUserMessage(t('problem_' + state.problem.id));

      // Si on est en train de "taper", afficher SEULEMENT l'indicateur
      if (state.isTyping && state.currentStep === 1) {
        html += createTypingIndicator();
      }
      // Sinon, afficher le message du bot et les options (mais pas pendant le typing)
      else if (state.currentStep >= 1 && !state.isTyping) {
        // Afficher le message du bot (réponse qui contient déjà la question)
        html += createBotMessage(t('response_' + state.problem.id));

        // Afficher les options SEULEMENT si on est exactement à l'étape 1
        if (state.currentStep === 1) {
          html += `<div class="wa-options-container wa-options-delayed">`;
          VEHICLE_CATEGORIES.forEach(vehicle => {
            html += createOptionButton(
              vehicle.id,
              ICONS.carFront,
              t('vehicle_' + vehicle.id),
              t('vehicle_' + vehicle.id + '_examples')
            );
          });
          html += `</div>`;
        }
      }
    }

    return html;
  }

  // Wreck removal flow - Step 1: Brand
  function createWreckStep1() {
    let html = '';

    if (state.problem && state.problem.id === 'wreck') {
      // Si on est en train de "taper", afficher SEULEMENT l'indicateur
      if (state.isTyping && state.currentStep === 1) {
        html += createTypingIndicator();
      }
      // Sinon, afficher le message du bot et l'input (mais pas pendant le typing)
      else if (state.currentStep >= 1 && !state.isTyping) {
        html += createBotMessage(t('wreck_step1_bot_question'));

        // Afficher l'input SEULEMENT si on est exactement à l'étape 1
        if (state.currentStep === 1) {
          html += `
            <div class="wa-text-input-container">
              <input
                type="text"
                id="wa-brand-input"
                class="wa-text-input"
                placeholder="${t('wreck_step1_input_placeholder')}"
                autocomplete="off"
              />
              <button class="wa-text-submit-btn" id="wa-brand-submit">
                ${ICONS.chevronRight}
              </button>
            </div>
          `;
        } else if (state.vehicleBrand) {
          // Afficher la réponse de l'utilisateur pour les étapes suivantes
          html += createUserMessage(state.vehicleBrand);
        }
      }
    }

    return html;
  }

  // Wreck removal flow - Step 2: Model
  function createWreckStep2() {
    let html = '';

    if (state.vehicleBrand && state.problem && state.problem.id === 'wreck') {
      // Si on est en train de "taper", afficher SEULEMENT l'indicateur
      if (state.isTyping && state.currentStep === 2) {
        html += createTypingIndicator();
      }
      // Sinon, afficher le message du bot et l'input (mais pas pendant le typing)
      else if (state.currentStep >= 2 && !state.isTyping) {
        html += createBotMessage(t('wreck_step2_bot_question'));

        // Afficher l'input SEULEMENT si on est exactement à l'étape 2
        if (state.currentStep === 2) {
          html += `
            <div class="wa-text-input-container">
              <input
                type="text"
                id="wa-model-input"
                class="wa-text-input"
                placeholder="${t('wreck_step2_input_placeholder')}"
                autocomplete="off"
              />
              <button class="wa-text-submit-btn" id="wa-model-submit">
                ${ICONS.chevronRight}
              </button>
            </div>
          `;
        } else if (state.vehicleModel) {
          // Afficher la réponse de l'utilisateur pour les étapes suivantes
          html += createUserMessage(state.vehicleModel);
        }
      }
    }

    return html;
  }

  // Wreck removal flow - Step 3: Year
  function createWreckStep3() {
    let html = '';

    if (state.vehicleModel && state.problem && state.problem.id === 'wreck') {
      // Si on est en train de "taper", afficher SEULEMENT l'indicateur
      if (state.isTyping && state.currentStep === 3) {
        html += createTypingIndicator();
      }
      // Sinon, afficher le message du bot et l'input (mais pas pendant le typing)
      else if (state.currentStep >= 3 && !state.isTyping) {
        html += createBotMessage(t('wreck_step3_bot_question'));

        // Afficher l'input SEULEMENT si on est exactement à l'étape 3
        if (state.currentStep === 3) {
          html += `
            <div class="wa-text-input-container">
              <input
                type="text"
                id="wa-year-input"
                class="wa-text-input"
                placeholder="${t('wreck_step3_input_placeholder')}"
                autocomplete="off"
                inputmode="numeric"
                pattern="[0-9]*"
              />
              <button class="wa-text-submit-btn" id="wa-year-submit">
                ${ICONS.chevronRight}
              </button>
            </div>
          `;
        } else if (state.vehicleYear) {
          // Afficher la réponse de l'utilisateur pour les étapes suivantes
          html += createUserMessage(state.vehicleYear);
        }
      }
    }

    return html;
  }

  function createStep1b() {
    let html = '';

    if (state.vehicle && state.problem && state.problem.id === 'flat') {
      html += createUserMessage(t('vehicle_' + state.vehicle));

      // Si on est en train de "taper", afficher SEULEMENT l'indicateur
      if (state.isTyping && state.currentStep === 1.5) {
        html += createTypingIndicator();
      }
      // Sinon, afficher le message du bot et les options (mais pas pendant le typing)
      else if (state.currentStep >= 1.5 && !state.isTyping) {
        html += createBotMessage(t('step1b_bot_question'));

        // Afficher les options SEULEMENT si on est exactement à l'étape 1.5
        if (state.currentStep === 1.5) {
          html += `<div class="wa-small-options-container wa-options-delayed">`;
          html += createSmallOptionButton('front', ICONS.circleDot, t('wheel_position_front'));
          html += createSmallOptionButton('rear', ICONS.circleDot, t('wheel_position_rear'));
          html += `</div>`;
        }
      }
    }

    return html;
  }

  function createStep2() {
    let html = '';

    // Cas normal (non-flat): afficher après sélection véhicule
    if (state.vehicle && (!state.problem || state.problem.id !== 'flat')) {
      html += createUserMessage(t('vehicle_' + state.vehicle));

      // Si on est en train de "taper", afficher SEULEMENT l'indicateur
      if (state.isTyping && state.currentStep === 2) {
        html += createTypingIndicator();
      }
      // Sinon, afficher le message du bot et les options (mais pas pendant le typing)
      else if (state.currentStep >= 2 && !state.isTyping) {
        html += createBotMessage(t('step2_bot_question'));

        // Afficher les options SEULEMENT si on est exactement à l'étape 2
        if (state.currentStep === 2) {
          html += `<div class="wa-small-options-container wa-options-delayed">`;
          TRANSMISSIONS.forEach(trans => {
            const icon = trans.id === 'manual' ? ICONS.settings2 : ICONS.cog;
            html += createSmallOptionButton(
              trans.id,
              icon,
              t('transmission_' + trans.id)
            );
          });
          html += `</div>`;
        }
      }
    }

    // Cas flat tire: afficher après sélection position roue
    if (state.wheelPosition && state.problem && state.problem.id === 'flat') {
      html += createUserMessage(t('wheel_position_' + state.wheelPosition));

      // Si on est en train de "taper", afficher SEULEMENT l'indicateur
      if (state.isTyping && state.currentStep === 2) {
        html += createTypingIndicator();
      }
      // Sinon, afficher le message du bot et les options (mais pas pendant le typing)
      else if (state.currentStep >= 2 && !state.isTyping) {
        html += createBotMessage(t('step2_bot_question'));

        // Afficher les options SEULEMENT si on est exactement à l'étape 2
        if (state.currentStep === 2) {
          log('DEBUG createStep2 flat tire: rendering transmission options', { currentStep: state.currentStep, isTyping: state.isTyping });
          html += `<div class="wa-small-options-container wa-options-delayed">`;
          TRANSMISSIONS.forEach(trans => {
            const icon = trans.id === 'manual' ? ICONS.settings2 : ICONS.cog;
            html += createSmallOptionButton(
              trans.id,
              icon,
              t('transmission_' + trans.id)
            );
          });
          html += `</div>`;
        }
      }
    }

    return html;
  }

  function createStep3() {
    let html = '';

    if (state.transmission) {
      html += createUserMessage(t('transmission_' + state.transmission));

      // Si on est en train de "taper", afficher SEULEMENT l'indicateur
      if (state.isTyping && state.currentStep === 3) {
        html += createTypingIndicator();
      }
      // Sinon, afficher le message du bot et les options (mais pas pendant le typing)
      else if (state.currentStep >= 3 && !state.isTyping) {
        html += createBotMessage(t('step3_bot_question'));

        // Afficher les options SEULEMENT si on est exactement à l'étape 3
        if (state.currentStep === 3) {
          html += `<div class="wa-small-options-container wa-options-delayed">`;
          html += createSmallOptionButton('yes', ICONS.check, t('fourwd_yes'));
          html += createSmallOptionButton('no', ICONS.close, t('fourwd_no'));
          html += `</div>`;
        }
      }
    }

    return html;
  }

  function createStep4() {
    let html = '';

    // For wreck flow: check if vehicleYear is set
    // For normal flow: check if fourWheelDrive is set
    const isWreck = state.problem?.id === 'wreck';
    const shouldShowStep4 = isWreck ? state.vehicleYear : (state.fourWheelDrive !== null);

    if (shouldShowStep4) {
      // Show user message for previous step
      if (isWreck) {
        html += createUserMessage(state.vehicleYear);
      } else {
        html += createUserMessage(t('fourwd_' + (state.fourWheelDrive ? 'yes' : 'no')));
      }

      // Si on est en train de "taper", afficher l'indicateur
      if (state.isTyping && state.currentStep === 4) {
        html += createTypingIndicator();
        return html;
      }

      // Toujours afficher le message du bot (même après avoir avancé)
      if (state.currentStep >= 4) {
        html += createBotMessage(t('step4_bot_question'));

        // Afficher les options SEULEMENT si on est exactement à l'étape 4
        if (state.currentStep === 4) {
          if (!state.showAddressInput) {
            html += `
              <div class="wa-location-options">
                <button class="wa-gps-btn" id="wa-gps-btn">
                  ${ICONS.navigation}
                  <span>${t('step4_gps_btn')}</span>
                </button>

                <div class="wa-separator">
                  <span>${t('step4_separator')}</span>
                </div>

                <button class="wa-address-btn" id="wa-address-btn">
                  ${ICONS.search}
                  <span>${t('step4_address_btn')}</span>
                </button>

                <div class="wa-privacy-note">
                  ${ICONS.lock}
                  <span>${t('step4_privacy')}</span>
                </div>
              </div>
            `;
          } else {
            html += `
              <div class="wa-address-input-container">
                <div class="wa-input-wrapper">
                  ${ICONS.search}
                  <input
                    type="text"
                    id="wa-address-input"
                    class="wa-address-input"
                    placeholder="${t('step4_address_placeholder')}"
                    autocomplete="off"
                  />
                </div>
                <div id="wa-address-suggestions"></div>
                <button class="wa-back-link" id="wa-address-back">
                  ${t('step4_back_btn')}
                </button>
              </div>
            `;
          }
        }
      }
    }

    return html;
  }

  function createStep4b() {
    let html = '';

    if (state.location.type) {
      const locationText = state.location.type === 'gps'
        ? t('location_gps')
        : state.location.address;

      html += createUserMessage(locationText);
      html += createBotMessage(t('step4b_bot_question'));

      if (!state.showDestinationInput) {
        // Show buttons for destination selection (similar to Step4)
        html += `
          <div class="wa-location-options">
            <button class="wa-address-btn" id="wa-destination-address-btn">
              ${ICONS.mapPin}
              <span>${t('step4_address_btn')}</span>
            </button>

            <div class="wa-separator">
              <span>${t('step4_separator')}</span>
            </div>

            <button class="wa-unknown-btn" id="wa-unknown-btn">
              ${ICONS.helpCircle}
              <span>${t('step4b_unknown_btn')}</span>
            </button>

            <div class="wa-hint-note">
              ${ICONS.info}
              <span>${t('step4b_hint')}</span>
            </div>
          </div>
        `;
      } else {
        // Show address input with autocomplete
        html += `
          <div class="wa-address-input-container">
            <div class="wa-input-wrapper">
              ${ICONS.mapPin}
              <input
                type="text"
                id="wa-destination-input"
                class="wa-address-input"
                placeholder="${t('step4_address_placeholder')}"
                autocomplete="off"
              />
            </div>
            <div id="wa-destination-suggestions"></div>
            <div id="wa-distance-info" style="display:none;"></div>
            <button class="wa-back-link" id="wa-destination-back">
              ${t('step4_back_btn')}
            </button>
          </div>
        `;
      }
    }

    return html;
  }

  function createStep5() {
    let html = '';

    const finalCondition = state.problem?.needsDestination
      ? (state.destination.address || state.destination.unknown)
      : state.location.type;

    if (finalCondition) {
      if (state.problem?.needsDestination) {
        const destText = state.destination.unknown
          ? t('destination_unknown')
          : state.destination.address;
        html += createUserMessage(destText);
      }

      // Determine final step number (5 for normal, 6 for needsDestination)
      const finalStep = state.problem?.needsDestination ? 6 : 5;

      // Show typing indicator first
      if (state.isTyping && state.currentStep === finalStep) {
        html += createTypingIndicator();
      }
      // Then show message
      else if (state.currentStep >= finalStep) {
        html += createBotMessage(t('step5_bot_message'));

        // Show summary card only after a delay (step 5.5 or 6.5)
        if (state.currentStep > finalStep) {
          html += '<div style="margin: 0.75rem 0;"></div>';
          html += createSummaryCard();
        }
      }
    }

    return html;
  }

  function createSummaryCard() {
    const problem = PROBLEMS.find(p => p.id === state.problem.id);
    const locationText = state.location.type === 'gps'
      ? t('location_gps')
      : t('location_address');

    // Different summary for wreck removal
    const isWreck = state.problem.id === 'wreck';

    return `
      <div class="wa-summary-card">
        <div class="wa-summary-header">
          <div class="wa-summary-avatar">
            <img src="images/logo.png" alt="BCD Logo" class="wa-summary-logo" />
          </div>
          <div>
            <div class="wa-summary-title">${t('step5_summary_title')}</div>
            <div class="wa-summary-company">${t('step5_summary_company')}</div>
          </div>
        </div>

        <div class="wa-summary-items">
          <div class="wa-summary-item">
            <span class="wa-summary-label">
              ${ICONS.messageCircle}
              ${t('summary_problem')}
            </span>
            <span class="wa-summary-value">${t('problem_' + state.problem.id)}</span>
          </div>

          <div class="wa-summary-item">
            <span class="wa-summary-label">
              ${ICONS.carFront}
              ${t('summary_vehicle')}
            </span>
            <span class="wa-summary-value">${isWreck ? `${state.vehicleBrand} ${state.vehicleModel} (${state.vehicleYear})` : t('vehicle_' + state.vehicle)}</span>
          </div>

          ${!isWreck ? `
            <div class="wa-summary-item">
              <span class="wa-summary-label">
                ${ICONS.settings2}
                ${t('summary_transmission')}
              </span>
              <span class="wa-summary-value">
                ${t('transmission_' + state.transmission)},
                ${state.fourWheelDrive ? t('fourwd_label_yes') : t('fourwd_label_no')}
              </span>
            </div>
          ` : ''}

          <div class="wa-summary-item">
            <span class="wa-summary-label">
              ${ICONS.mapPin}
              ${t('summary_location')}
            </span>
            <span class="wa-summary-value wa-summary-success">
              ${ICONS.check}
              ${locationText}
            </span>
          </div>

          ${state.problem.needsDestination ? `
            <div class="wa-summary-item">
              <span class="wa-summary-label">
                ${ICONS.navigation}
                ${t('summary_destination')}
              </span>
              <span class="wa-summary-value">
                ${state.destination.unknown ? t('destination_unknown') : state.destination.address}
              </span>
            </div>
            ${state.destination.distance ? `
              <div class="wa-distance-display">
                <div><strong>${t('distance_label')}:</strong> ${state.destination.distance}</div>
                <div><strong>${t('duration_label')}:</strong> ~${state.destination.duration}</div>
              </div>
            ` : ''}
          ` : ''}
        </div>

        <a
          href="#"
          id="wa-final-whatsapp-btn"
          target="_blank"
          rel="noopener noreferrer"
          class="wa-whatsapp-btn"
        >
          ${ICONS.whatsapp}
          <span>${t('cta_whatsapp')}</span>
        </a>

        <div class="wa-trust-message">
          ${ICONS.shield}
          <div>
            <strong>${t('cta_trust_title')}</strong> — ${t('cta_trust_message')}
          </div>
        </div>
      </div>

      <div class="wa-trust-badges">
        <div class="wa-badge">
          ${ICONS.star}
          <span>${t('badge_rating')}</span>
        </div>
        <span class="wa-badge-separator">|</span>
        <div class="wa-badge">
          ${ICONS.clock}
          <span>${t('badge_time')}</span>
        </div>
        <span class="wa-badge-separator">|</span>
        <div class="wa-badge">
          ${ICONS.creditCard}
          <span>${t('badge_payment')}</span>
        </div>
      </div>
    `;
  }

  // ========================================
  // SECTION 12: MODAL BUILDER
  // ========================================

  function createModal() {
    const modal = document.createElement('div');
    modal.id = 'wa-modal-v5';
    modal.className = 'wa-modal-overlay-v5';
    modal.innerHTML = `
      <div class="wa-modal-v5">
        ${createHeader()}
        ${createProgressBar()}
        <div class="wa-chat-area" id="wa-chat-area"></div>
        <div class="wa-footer">
          ${ICONS.lock}
          <span>${t('footer_privacy')}</span>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    return modal;
  }

  // ========================================
  // SECTION 13: RENDER & NAVIGATION
  // ========================================

  function renderCurrentStep() {
    const chatArea = document.getElementById('wa-chat-area');
    if (!chatArea) return;

    let html = '';

    // Render all previous steps + current step
    if (state.currentStep >= 0) html += createStep0();

    // Different flow for wreck removal
    if (state.problem?.id === 'wreck') {
      if (state.currentStep >= 1) html += createWreckStep1();
      if (state.currentStep >= 2) html += createWreckStep2();
      if (state.currentStep >= 3) html += createWreckStep3();
      if (state.currentStep >= 4) html += createStep4();
      if (state.currentStep >= 5) html += createStep5();
    } else {
      // Normal flow
      if (state.currentStep >= 1) html += createStep1();
      // Step1b seulement pour flat tire
      if (state.currentStep >= 1.5 && state.problem?.id === 'flat') html += createStep1b();
      if (state.currentStep >= 2) html += createStep2();
      if (state.currentStep >= 3) html += createStep3();
      if (state.currentStep >= 4) html += createStep4();
      if (state.currentStep >= 5 && state.problem?.needsDestination) html += createStep4b();
      if (state.currentStep >= (state.problem?.needsDestination ? 6 : 5)) html += createStep5();
    }

    chatArea.innerHTML = html;

    // Update progress bar
    const progressContainer = document.querySelector('.wa-progress-bar');
    if (progressContainer) {
      progressContainer.outerHTML = createProgressBar();
    }

    // Attach event listeners for current step
    attachStepEvents();
  }

  function goToNextStep() {
    // 1. Afficher immédiatement la réponse de l'utilisateur avec typing indicator
    state.currentStep++;
    state.isTyping = true;
    renderCurrentStep();
    smoothScrollToBottom();

    // 2. Après le délai de "réflexion", afficher la question suivante
    setTimeout(() => {
      state.isTyping = false;
      renderCurrentStep();
      smoothScrollToBottom();

      // Si on vient d'atteindre l'étape finale, montrer le récapitulatif après 2 secondes
      const finalStep = state.problem?.needsDestination ? 6 : 5;
      if (state.currentStep === finalStep) {
        setTimeout(() => {
          state.currentStep += 0.5; // Passer à 5.5 ou 6.5 pour afficher le récap
          renderCurrentStep();
          smoothScrollToBottom();
        }, 2000); // Attendre 2 secondes avant de montrer le récap
      } else {
        // Afficher les options après un petit délai
        setTimeout(() => {
          smoothScrollToBottom();
        }, CONFIG.transitionDelay);
      }
    }, CONFIG.typingDelayAfterUser);
  }

  function smoothScrollToBottom() {
    const chatArea = document.getElementById('wa-chat-area');
    if (chatArea) {
      chatArea.scrollTo({
        top: chatArea.scrollHeight,
        behavior: 'smooth'
      });
    }
  }

  // ========================================
  // SECTION 14: EVENT HANDLERS
  // ========================================

  function attachStepEvents() {
    // Step 0: Problem selection
    const problemBtns = document.querySelectorAll('#wa-step0-options .wa-option-btn');
    problemBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const problemId = btn.getAttribute('data-option-id');
        state.problem = PROBLEMS.find(p => p.id === problemId);
        log('Problem selected', state.problem);
        setTimeout(goToNextStep, CONFIG.transitionDelay);
      });
    });

    // Step 1: Vehicle selection (excluding step0)
    const allOptionBtns = document.querySelectorAll('.wa-options-container:not(#wa-step0-options) .wa-option-btn');
    allOptionBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const vehicleId = btn.getAttribute('data-option-id');
        state.vehicle = vehicleId;
        log('Vehicle selected', state.vehicle);

        // Si c'est un pneu crevé, aller à Step1.5 (wheel position)
        if (state.problem?.id === 'flat') {
          state.currentStep = 1.5;
          state.isTyping = true;
          renderCurrentStep();
          smoothScrollToBottom();

          setTimeout(() => {
            state.isTyping = false;
            renderCurrentStep();
            smoothScrollToBottom();
            setTimeout(() => smoothScrollToBottom(), CONFIG.transitionDelay);
          }, CONFIG.typingDelayAfterUser);
        } else {
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        }
      });
    });

    // Wreck removal: Brand input (Step 1)
    const brandInput = document.getElementById('wa-brand-input');
    const brandSubmit = document.getElementById('wa-brand-submit');
    if (brandInput && brandSubmit) {
      const handleBrandSubmit = () => {
        const value = brandInput.value.trim();
        if (value) {
          state.vehicleBrand = value;
          log('Brand entered', value);
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        }
      };
      brandSubmit.addEventListener('click', handleBrandSubmit);
      brandInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleBrandSubmit();
      });
      // Auto-focus
      setTimeout(() => brandInput.focus(), 100);
    }

    // Wreck removal: Model input (Step 2)
    const modelInput = document.getElementById('wa-model-input');
    const modelSubmit = document.getElementById('wa-model-submit');
    if (modelInput && modelSubmit) {
      const handleModelSubmit = () => {
        const value = modelInput.value.trim();
        if (value) {
          state.vehicleModel = value;
          log('Model entered', value);
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        }
      };
      modelSubmit.addEventListener('click', handleModelSubmit);
      modelInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleModelSubmit();
      });
      // Auto-focus
      setTimeout(() => modelInput.focus(), 100);
    }

    // Wreck removal: Year input (Step 3)
    const yearInput = document.getElementById('wa-year-input');
    const yearSubmit = document.getElementById('wa-year-submit');
    if (yearInput && yearSubmit) {
      const handleYearSubmit = () => {
        const value = yearInput.value.trim();
        if (value) {
          state.vehicleYear = value;
          log('Year entered', value);
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        }
      };
      yearSubmit.addEventListener('click', handleYearSubmit);
      yearInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleYearSubmit();
      });
      // Auto-focus
      setTimeout(() => yearInput.focus(), 100);
    }

    // Step 1.5, 2, 3: Wheel position, Transmission, 4WD selection
    document.querySelectorAll('.wa-small-options-container .wa-small-option-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const value = btn.getAttribute('data-option-id');

        // Check which step we're on
        if (state.currentStep === 1.5) {
          state.wheelPosition = value;
          log('Wheel position selected', state.wheelPosition);
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        } else if (state.currentStep === 2) {
          state.transmission = value;
          log('Transmission selected', state.transmission);
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        } else if (state.currentStep === 3) {
          state.fourWheelDrive = value === 'yes';
          log('4WD selected', state.fourWheelDrive);
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        }
      });
    });

    // Step 4: Location
    const gpsBtn = document.getElementById('wa-gps-btn');
    if (gpsBtn) {
      gpsBtn.addEventListener('click', handleGPSLocation);
    }

    const addressBtn = document.getElementById('wa-address-btn');
    if (addressBtn) {
      addressBtn.addEventListener('click', () => {
        state.showAddressInput = true;
        renderCurrentStep();
        setTimeout(() => {
          const input = document.getElementById('wa-address-input');
          if (input) input.focus();
          initGooglePlaces('wa-address-input', 'wa-address-suggestions', handleAddressSelect);
        }, 100);
      });
    }

    const addressBack = document.getElementById('wa-address-back');
    if (addressBack) {
      addressBack.addEventListener('click', () => {
        state.showAddressInput = false;
        renderCurrentStep();
      });
    }

    // Step 4b: Destination (towing only)
    const destAddressBtn = document.getElementById('wa-destination-address-btn');
    if (destAddressBtn) {
      destAddressBtn.addEventListener('click', () => {
        state.showDestinationInput = true;
        renderCurrentStep();
        setTimeout(() => {
          const input = document.getElementById('wa-destination-input');
          if (input) input.focus();
          initGooglePlaces('wa-destination-input', 'wa-destination-suggestions', handleDestinationSelect);
        }, 100);
      });
    }

    const destInput = document.getElementById('wa-destination-input');
    if (destInput) {
      initGooglePlaces('wa-destination-input', 'wa-destination-suggestions', handleDestinationSelect);
    }

    const destBack = document.getElementById('wa-destination-back');
    if (destBack) {
      destBack.addEventListener('click', () => {
        state.showDestinationInput = false;
        renderCurrentStep();
      });
    }

    const unknownBtn = document.getElementById('wa-unknown-btn');
    if (unknownBtn) {
      unknownBtn.addEventListener('click', () => {
        state.destination.unknown = true;
        state.destination.address = '';
        log('Destination: unknown');
        setTimeout(goToNextStep, CONFIG.transitionDelay);
      });
    }

    // Final WhatsApp button
    const finalWhatsAppBtn = document.getElementById('wa-final-whatsapp-btn');
    if (finalWhatsAppBtn) {
      finalWhatsAppBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const url = generateWhatsAppURL();
        log('Opening WhatsApp with URL:', url);
        window.open(url, '_blank');
      });
    }

    // Language selector
    const langBtn = document.getElementById('wa-current-lang');
    const langDropdown = document.getElementById('wa-lang-dropdown');
    if (langBtn && langDropdown) {
      langBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        langDropdown.classList.toggle('active');
      });

      document.querySelectorAll('.wa-lang-option').forEach(option => {
        option.addEventListener('click', () => {
          const newLang = option.getAttribute('data-lang');
          if (newLang !== state.currentLanguage) {
            state.currentLanguage = newLang;
            log('Language changed to', newLang);

            // Re-render everything
            const modal = document.querySelector('.wa-modal-v5');
            modal.querySelector('.wa-header-v5').outerHTML = createHeader();
            renderCurrentStep();

            // Re-attach header events
            attachHeaderEvents();
          }
          langDropdown.classList.remove('active');
        });
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', () => {
        langDropdown.classList.remove('active');
      });
    }
  }

  function attachHeaderEvents() {
    const closeBtn = document.querySelector('.wa-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', hideModal);
    }

    attachStepEvents(); // Re-attach language selector events
  }

  // ========================================
  // SECTION 15: GEOLOCATION
  // ========================================

  function handleGPSLocation() {
    const gpsBtn = document.getElementById('wa-gps-btn');
    if (!gpsBtn) return;

    gpsBtn.disabled = true;
    gpsBtn.innerHTML = `
      <div class="wa-spinner">${ICONS.loader}</div>
      <span>${t('gps_searching')}</span>
    `;

    if (!navigator.geolocation) {
      alert('Géolocalisation non disponible sur votre appareil');
      gpsBtn.disabled = false;
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        state.location.type = 'gps';
        state.location.coords = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        log('GPS location obtained', state.location.coords);

        if (state.problem?.needsDestination) {
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        } else {
          setTimeout(goToNextStep, CONFIG.transitionDelay);
        }
      },
      (error) => {
        log('GPS error', error);
        let errorMessage = 'Impossible d\'obtenir votre position. ';

        switch(error.code) {
          case error.PERMISSION_DENIED:
            errorMessage += 'Permission refusée. Veuillez autoriser la localisation dans les paramètres de votre navigateur.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage += 'Position non disponible.';
            break;
          case error.TIMEOUT:
            errorMessage += 'Délai dépassé.';
            break;
          default:
            errorMessage += 'Erreur inconnue.';
        }

        errorMessage += '\n\nVeuillez entrer une adresse manuellement.';
        alert(errorMessage);

        gpsBtn.disabled = false;
        state.showAddressInput = true;
        renderCurrentStep();
      },
      {
        enableHighAccuracy: true,
        timeout: 10000, // Augmenté à 10 secondes
        maximumAge: 0
      }
    );
  }

  // ========================================
  // SECTION 16: GOOGLE PLACES AUTOCOMPLETE
  // ========================================

  function initGooglePlaces(inputId, suggestionsId, callback, retryCount = 0) {
    if (typeof google === 'undefined' || !google.maps || !google.maps.places) {
      if (retryCount < 10) {
        setTimeout(() => initGooglePlaces(inputId, suggestionsId, callback, retryCount + 1), 300);
      } else {
        log('Google Maps API failed to load');
      }
      return;
    }

    const input = document.getElementById(inputId);
    if (!input) {
      log('Input not found:', inputId);
      return;
    }

    // Check if already initialized (avoid double initialization)
    if (input.dataset.autocompleteInitialized === 'true') {
      log('Google Places already initialized for', inputId);
      return;
    }

    try {
      const autocomplete = new google.maps.places.Autocomplete(input, {
        componentRestrictions: { country: 'be' },
        fields: ['formatted_address', 'geometry', 'address_components'],
        types: ['address']
      });

      autocomplete.addListener('place_changed', () => {
        const place = autocomplete.getPlace();
        log('Place selected:', place);

        if (place && place.formatted_address) {
          callback(place.formatted_address);
        } else if (place && place.name) {
          // Fallback au nom si pas d'adresse formatée
          callback(place.name);
        }
      });

      input.dataset.autocompleteInitialized = 'true';
      log('Google Places initialized for', inputId);
    } catch (error) {
      log('Error initializing Google Places:', error);
    }

    // Initialize Directions Service if not already done
    if (!directionsService) {
      directionsService = new google.maps.DirectionsService();
      log('Directions Service initialized');
    }
  }

  function handleAddressSelect(address) {
    state.location.type = 'manual';
    state.location.address = address;
    log('Address selected', address);

    if (state.problem?.needsDestination) {
      setTimeout(goToNextStep, CONFIG.transitionDelay);
    } else {
      setTimeout(goToNextStep, CONFIG.transitionDelay);
    }
  }

  function handleDestinationSelect(address) {
    state.destination.address = address;
    state.destination.unknown = false;
    log('Destination selected', address);

    // Calculate distance
    calculateDistance();
  }

  // ========================================
  // SECTION 17: GOOGLE DIRECTIONS API
  // ========================================

  function calculateDistance() {
    if (!directionsService) return;

    const origin = state.location.type === 'gps'
      ? `${state.location.coords.lat},${state.location.coords.lng}`
      : state.location.address;

    const destination = state.destination.address;

    directionsService.route({
      origin: origin,
      destination: destination,
      travelMode: 'DRIVING'
    }, (result, status) => {
      if (status === 'OK' && result.routes[0]) {
        const leg = result.routes[0].legs[0];
        state.destination.distance = leg.distance.text;
        state.destination.duration = leg.duration.text;

        log('Distance calculated', state.destination);

        // Display distance info
        const distanceInfo = document.getElementById('wa-distance-info');
        if (distanceInfo) {
          distanceInfo.innerHTML = `
            <div class="wa-distance-result">
              <div><strong>${t('distance_label')}:</strong> ${state.destination.distance}</div>
              <div><strong>${t('duration_label')}:</strong> ~${state.destination.duration}</div>
            </div>
          `;
          distanceInfo.style.display = 'block';
        }

        // Auto-advance to next step after 1 second
        setTimeout(goToNextStep, 1000);
      } else {
        log('Distance calculation failed', status);
      }
    });
  }

  // ========================================
  // SECTION 18: WHATSAPP MESSAGE GENERATOR
  // ========================================

  function generateWhatsAppURL() {
    const message = buildWhatsAppMessage();
    return `https://wa.me/${CONFIG.phoneNumber}?text=${encodeURIComponent(message)}`;
  }

  function buildWhatsAppMessage() {
    let msg = `${t('msg_greeting')}\n\n${t('msg_intro')}\n\n`;

    msg += `${t('msg_problem')} ${t('problem_' + state.problem.id)}\n`;

    // Different message format for wreck removal
    if (state.problem.id === 'wreck') {
      msg += `${t('msg_vehicle')} ${state.vehicleBrand} ${state.vehicleModel} (${state.vehicleYear})\n`;
    } else {
      msg += `${t('msg_vehicle')} ${t('vehicle_' + state.vehicle)}\n`;
      msg += `${t('msg_transmission')} ${t('transmission_' + state.transmission)}, `;
      msg += `${state.fourWheelDrive ? t('fourwd_label_yes') : t('fourwd_label_no')}\n`;
    }

    if (state.location.type === 'gps') {
      const link = createGoogleMapsLink(state.location.coords.lat, state.location.coords.lng);
      msg += `${t('msg_location')} ${link}\n`;
    } else {
      msg += `${t('msg_location')} ${state.location.address}\n`;
    }

    if (state.problem.needsDestination) {
      if (state.destination.unknown) {
        msg += `${t('msg_destination')} ${t('destination_unknown')}\n`;
      } else {
        msg += `${t('msg_destination')} ${state.destination.address}\n`;
        if (state.destination.distance) {
          msg += `${t('msg_distance')} ${state.destination.distance}`;
          if (state.destination.duration) {
            msg += ` (~${state.destination.duration})`;
          }
          msg += `\n`;
        }
      }
    }

    msg += `\n${t('msg_closing')}`;

    return msg;
  }

  // ========================================
  // SECTION 19: MODAL SHOW/HIDE
  // ========================================

  function showModal() {
    if (!modalElement) {
      modalElement = createModal();
      attachHeaderEvents();
    }

    // Reset state
    state.currentStep = 0;
    state.isTyping = true;
    state.showAddressInput = false;
    state.problem = null;
    state.vehicle = null;
    state.transmission = null;
    state.fourWheelDrive = null;
    state.location = { type: null, coords: null, address: '' };
    state.destination = { address: '', unknown: false, distance: null, duration: null };

    // Render
    renderCurrentStep();

    // Show typing indicator then options (délai initial plus long pour humaniser)
    setTimeout(() => {
      state.isTyping = false;
      renderCurrentStep();
    }, CONFIG.typingDelayInitial);

    modalElement.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    log('Modal opened');

    // Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'whatsapp_modal_open_v5', {'event_category': 'engagement'});
    }
  }

  function hideModal() {
    if (modalElement) {
      modalElement.style.display = 'none';
      document.body.style.overflow = '';
      log('Modal closed');
    }
  }

  // ========================================
  // SECTION 20: STYLES INJECTION
  // ========================================

  function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      /* ========================================
         WHATSAPP SMART V5 - STYLES
         ======================================== */

      /* Modal Overlay */
      /* Google Autocomplete dropdown fix */
      .pac-container {
        z-index: 100000 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        border-radius: 8px;
        margin-top: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .wa-modal-overlay-v5 {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(8px);
        z-index: 99999;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        overflow-y: auto;
      }

      /* Modal Container */
      .wa-modal-v5 {
        background: #fff;
        width: 100%;
        max-width: 480px;
        height: 85vh;
        max-height: 700px;
        border-radius: 20px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        animation: wa-slide-up 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      }

      @keyframes wa-slide-up {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      /* Mobile full screen */
      @media (max-width: 640px) {
        .wa-modal-overlay-v5 {
          padding: 0;
          align-items: flex-end;
        }

        .wa-modal-v5 {
          max-width: 100%;
          max-height: 95vh;
          border-radius: 20px 20px 0 0;
        }
      }

      /* ========================================
         HEADER
         ======================================== */

      .wa-header-v5 {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        color: #fff;
        padding: 1rem 1.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-shrink: 0;
      }

      .wa-header-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
      }

      .wa-header-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #fff;
        color: #DC2626;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.875rem;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
      }

      .wa-header-info {
        display: flex;
        flex-direction: column;
        gap: 0.125rem;
      }

      .wa-header-title {
        font-weight: 700;
        font-size: 1rem;
        line-height: 1.2;
      }

      .wa-header-status {
        display: flex;
        align-items: center;
        gap: 0.375rem;
        font-size: 0.75rem;
        color: #9ca3af;
      }

      .wa-status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        animation: wa-pulse 2s ease-in-out infinite;
      }

      @keyframes wa-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }

      .wa-header-right {
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }

      /* Language Selector */
      .wa-lang-selector {
        position: relative;
      }

      .wa-lang-btn {
        background: rgba(255, 255, 255, 0.1);
        border: none;
        color: #fff;
        padding: 0.375rem 0.625rem;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.8125rem;
        font-weight: 600;
        letter-spacing: 0.5px;
      }

      .wa-lang-btn:hover {
        background: rgba(255, 255, 255, 0.2);
      }

      .wa-lang-code {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }

      .wa-lang-dropdown {
        position: absolute;
        top: calc(100% + 0.5rem);
        right: 0;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        opacity: 0;
        visibility: hidden;
        transform: translateY(-10px);
        transition: all 0.2s;
        min-width: 80px;
        z-index: 10;
      }

      .wa-lang-dropdown.active {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
      }

      .wa-lang-option {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.625rem 1rem;
        border: none;
        background: none;
        width: 100%;
        cursor: pointer;
        transition: background 0.2s;
        color: #1f2937;
        font-size: 0.8125rem;
        font-weight: 600;
        letter-spacing: 0.5px;
      }

      .wa-lang-option:hover {
        background: #f3f4f6;
      }

      .wa-lang-option.active {
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
      }

      /* Close Button */
      .wa-close-btn {
        background: rgba(255, 255, 255, 0.1);
        border: none;
        color: #fff;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
      }

      .wa-close-btn:hover {
        background: rgba(255, 255, 255, 0.2);
      }

      /* ========================================
         PROGRESS BAR
         ======================================== */

      .wa-progress-bar {
        background: #fff;
        padding: 0.875rem 1.25rem;
        border-bottom: 1px solid #e5e7eb;
        flex-shrink: 0;
      }

      .wa-progress-info {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 0.625rem;
        font-size: 0.75rem;
      }

      .wa-progress-text {
        color: #6b7280;
        font-weight: 500;
      }

      .wa-progress-badge {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        color: #f97316;
        font-weight: 600;
      }

      .wa-progress-track {
        height: 6px;
        background: #e5e7eb;
        border-radius: 999px;
        overflow: hidden;
      }

      .wa-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
        border-radius: 999px;
        transition: width 0.5s ease-out;
      }

      /* ========================================
         CHAT AREA
         ======================================== */

      .wa-chat-area {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
        background: #fff;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        -webkit-overflow-scrolling: touch;
      }

      /* Messages */
      .wa-message {
        display: flex;
        gap: 0.625rem;
        animation: wa-fade-in 0.3s ease-out;
      }

      @keyframes wa-fade-in {
        from {
          opacity: 0;
          transform: translateY(10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .wa-bot-message {
        align-items: flex-start;
      }

      .wa-user-message {
        justify-content: flex-end;
      }

      .wa-bot-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
      }

      .wa-bot-logo {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 4px;
      }

      .wa-message-bubble {
        max-width: 320px;
        padding: 0.875rem 1rem;
        border-radius: 16px;
        line-height: 1.5;
      }

      .wa-bot-bubble {
        background: rgba(220, 248, 198, 0.4);
        color: #1f2937;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(200, 230, 180, 0.5);
      }

      .wa-bot-text {
        margin-bottom: 0.625rem;
      }

      .wa-bot-text:last-child {
        margin-bottom: 0;
      }

      .wa-user-bubble {
        background: rgba(147, 197, 253, 0.3);
        color: #1f2937;
        border-bottom-right-radius: 4px;
        border: 1px solid rgba(147, 197, 253, 0.5);
        box-shadow: 0 4px 12px rgba(147, 197, 253, 0.15);
      }

      /* Typing Indicator */
      .wa-typing-indicator {
        align-items: center;
      }

      .wa-typing-bubble {
        background: rgba(220, 248, 198, 0.4);
        border: 1px solid rgba(200, 230, 180, 0.5);
        border-radius: 16px;
        border-bottom-left-radius: 4px;
        padding: 0.75rem 1rem;
        display: flex;
        gap: 0.375rem;
      }

      .wa-typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #9ca3af;
        animation: wa-bounce 1.4s infinite ease-in-out;
      }

      .wa-typing-dot:nth-child(1) {
        animation-delay: -0.32s;
      }

      .wa-typing-dot:nth-child(2) {
        animation-delay: -0.16s;
      }

      @keyframes wa-bounce {
        0%, 80%, 100% {
          transform: scale(0);
        }
        40% {
          transform: scale(1);
        }
      }

      /* ========================================
         BUTTONS
         ======================================== */

      /* Option Buttons (Tag/Pill Style) */
      .wa-options-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: flex-end;
      }

      .wa-options-delayed {
        opacity: 0;
        animation: wa-options-appear 0.3s ease-out 0.4s forwards;
      }

      @keyframes wa-options-appear {
        from {
          opacity: 0;
          transform: translateY(10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .wa-option-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.875rem;
        background: #ffffff;
        border: 1.5px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
        white-space: nowrap;
      }

      .wa-option-btn:hover {
        background: rgba(59, 130, 246, 0.05);
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
      }

      .wa-option-btn:active {
        transform: translateY(0);
      }

      .wa-option-icon {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(59, 130, 246, 0.7);
        flex-shrink: 0;
        transition: all 0.2s;
      }

      .wa-option-btn:hover .wa-option-icon {
        color: rgba(59, 130, 246, 1);
      }

      .wa-option-content {
        display: flex;
        flex-direction: column;
      }

      .wa-option-label {
        font-weight: 500;
        color: #1f2937;
        font-size: 0.875rem;
        line-height: 1.2;
      }

      .wa-option-subtitle {
        font-size: 0.6875rem;
        color: #9ca3af;
        line-height: 1.2;
        margin-top: 0.125rem;
      }

      .wa-option-btn > svg {
        display: none;
      }

      .wa-option-btn:hover > svg {
        color: #DC2626;
      }

      /* Small Option Buttons (Tag Style) */
      .wa-small-options-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: flex-end;
      }

      .wa-small-option-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.5rem 0.875rem;
        background: #ffffff;
        border: 1.5px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.2s;
      }

      .wa-small-option-btn:hover {
        background: rgba(59, 130, 246, 0.05);
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
      }

      .wa-small-option-icon {
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(59, 130, 246, 0.7);
        transition: all 0.2s;
      }

      .wa-small-option-btn:hover .wa-small-option-icon {
        color: rgba(59, 130, 246, 1);
      }

      .wa-small-option-label {
        font-weight: 500;
        color: #1f2937;
        font-size: 0.875rem;
      }

      /* ========================================
         URGENT TAG
         ======================================== */

      .wa-urgent-tag-container {
        margin-top: 1rem;
        display: flex;
        justify-content: center;
      }

      .wa-urgent-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem 1rem;
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        border: none;
        border-radius: 25px;
        text-decoration: none;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
        color: #fff;
        font-weight: 600;
        font-size: 0.875rem;
      }

      .wa-urgent-tag:hover {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(249, 115, 22, 0.4);
      }

      .wa-urgent-tag:active {
        transform: translateY(0);
      }

      .wa-urgent-tag svg {
        width: 18px;
        height: 18px;
        color: #fff;
      }

      .wa-urgent-tag-text {
        color: #fff;
      }

      /* ========================================
         LOCATION SECTION
         ======================================== */

      .wa-location-options {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        align-items: flex-end;
      }

      .wa-gps-btn,
      .wa-address-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.5rem 0.875rem;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
        border: 1.5px solid rgba(59, 130, 246, 0.3);
        background: #ffffff;
        color: #1f2937;
      }

      .wa-gps-btn {
        box-shadow: 0 2px 6px rgba(59, 130, 246, 0.1);
      }

      .wa-gps-btn:hover:not(:disabled) {
        background: rgba(59, 130, 246, 0.05);
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
      }

      .wa-gps-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
      }

      .wa-gps-btn svg,
      .wa-address-btn svg {
        color: rgba(59, 130, 246, 0.7);
      }

      .wa-spinner {
        animation: wa-spin 1s linear infinite;
      }

      @keyframes wa-spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }

      .wa-address-btn:hover {
        background: rgba(59, 130, 246, 0.05);
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
      }

      .wa-separator {
        position: relative;
        text-align: center;
        color: #9ca3af;
        font-size: 0.75rem;
        margin: 0.25rem 0;
      }

      .wa-separator span {
        background: #fff;
        padding: 0 0.5rem;
      }

      .wa-privacy-note {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 0.25rem;
        color: #9ca3af;
        font-size: 0.6875rem;
      }

      .wa-privacy-note svg {
        width: 12px;
        height: 12px;
      }

      /* Address Input */
      .wa-address-input-container {
        display: flex;
        flex-direction: column;
        gap: 0.875rem;
      }

      .wa-input-wrapper {
        position: relative;
        display: flex;
        align-items: center;
      }

      .wa-input-wrapper > svg {
        position: absolute;
        left: 1rem;
        color: #9ca3af;
        pointer-events: none;
      }

      .wa-address-input {
        width: 100%;
        padding: 1rem 1rem 1rem 3rem;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        font-size: 1rem;
        color: #1f2937;
        transition: all 0.2s;
      }

      .wa-address-input:focus {
        outline: none;
        border-color: rgba(59, 130, 246, 0.6);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }

      .wa-address-input::placeholder {
        color: #9ca3af;
      }

      /* ========================================
         TEXT INPUT (WRECK REMOVAL)
         ======================================== */

      .wa-text-input-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        justify-content: flex-end;
        margin-top: 0.75rem;
      }

      .wa-text-input {
        flex: 0 0 auto;
        max-width: 250px;
        padding: 0.625rem 1rem;
        border: 1.5px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        font-size: 0.875rem;
        color: #1f2937;
        background: #ffffff;
        transition: all 0.2s;
        outline: none;
      }

      .wa-text-input:focus {
        border-color: rgba(59, 130, 246, 0.6);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }

      .wa-text-input::placeholder {
        color: #9ca3af;
      }

      .wa-text-submit-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        padding: 0;
        background: rgba(59, 130, 246, 0.1);
        border: 1.5px solid rgba(59, 130, 246, 0.3);
        border-radius: 50%;
        cursor: pointer;
        transition: all 0.2s;
      }

      .wa-text-submit-btn:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.5);
        transform: scale(1.05);
      }

      .wa-text-submit-btn:active {
        transform: scale(0.98);
      }

      .wa-text-submit-btn svg {
        width: 20px;
        height: 20px;
        color: rgba(59, 130, 246, 0.8);
      }

      .wa-back-link {
        background: none;
        border: none;
        color: #6b7280;
        font-size: 0.875rem;
        cursor: pointer;
        padding: 0.5rem;
        transition: color 0.2s;
      }

      .wa-back-link:hover {
        color: #1f2937;
      }

      /* Destination */
      .wa-destination-container {
        display: flex;
        flex-direction: column;
        gap: 0.875rem;
        align-items: flex-end;
      }

      .wa-unknown-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.5rem 0.875rem;
        background: #ffffff;
        border: 1.5px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        color: #1f2937;
        font-weight: 500;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
      }

      .wa-unknown-btn svg {
        color: rgba(59, 130, 246, 0.7);
        width: 18px;
        height: 18px;
      }

      .wa-unknown-btn:hover {
        background: rgba(59, 130, 246, 0.05);
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
      }

      .wa-hint-note {
        font-size: 0.75rem;
        color: #9ca3af;
        text-align: right;
        padding: 0 0.5rem;
      }

      .wa-distance-result {
        padding: 0.875rem 1rem;
        background: #eff6ff;
        border: 2px solid #bfdbfe;
        border-radius: 12px;
        color: #1e40af;
        font-size: 0.875rem;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }

      /* ========================================
         SUMMARY CARD
         ======================================== */

      .wa-summary-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
      }

      .wa-summary-header {
        display: flex;
        align-items: center;
        gap: 0.875rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
      }

      .wa-summary-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #ffffff;
        border: 2px solid #e5e7eb;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 8px;
        flex-shrink: 0;
        overflow: hidden;
      }

      .wa-summary-logo {
        width: 120%;
        height: auto;
        object-fit: contain;
        transform: scale(0.85);
      }

      .wa-summary-title {
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.125rem;
      }

      .wa-summary-company {
        font-size: 0.875rem;
        color: #6b7280;
      }

      .wa-summary-items {
        display: flex;
        flex-direction: column;
      }

      .wa-summary-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid #e5e7eb;
      }

      .wa-summary-item:last-child {
        border-bottom: none;
      }

      .wa-summary-label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #6b7280;
        font-size: 0.875rem;
      }

      .wa-summary-value {
        font-weight: 600;
        color: #1f2937;
        font-size: 0.875rem;
        text-align: right;
      }

      .wa-summary-success {
        color: #059669;
        display: flex;
        align-items: center;
        gap: 0.375rem;
      }

      .wa-distance-display {
        margin-top: 0.5rem;
        padding: 0.875rem;
        background: #eff6ff;
        border-radius: 10px;
        font-size: 0.8125rem;
        color: #1e40af;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }

      /* WhatsApp CTA Button */
      .wa-whatsapp-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        width: 100%;
        padding: 1rem;
        background: #25d366;
        color: #fff;
        border-radius: 12px;
        font-weight: 700;
        text-decoration: none;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25);
        transition: all 0.2s;
        margin-top: 0.5rem;
      }

      .wa-whatsapp-btn:hover {
        background: #1fb854;
        box-shadow: 0 6px 20px rgba(37, 211, 102, 0.35);
        transform: translateY(-2px);
      }

      .wa-trust-message {
        display: flex;
        align-items: flex-start;
        gap: 0.625rem;
        padding: 0.875rem;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-radius: 10px;
        font-size: 0.8125rem;
        color: #1f2937;
      }

      .wa-trust-message svg {
        color: #f97316;
        flex-shrink: 0;
        margin-top: 2px;
      }

      /* Trust Badges */
      .wa-trust-badges {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        font-size: 0.75rem;
        color: #6b7280;
        padding-top: 0.5rem;
      }

      .wa-badge {
        display: flex;
        align-items: center;
        gap: 0.25rem;
      }

      .wa-badge svg {
        color: #f97316;
      }

      .wa-badge-separator {
        color: #d1d5db;
      }

      /* ========================================
         FOOTER
         ======================================== */

      .wa-footer {
        background: #1f2937;
        padding: 0.875rem 1.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        color: #9ca3af;
        font-size: 0.75rem;
        flex-shrink: 0;
      }

      .wa-footer svg {
        flex-shrink: 0;
      }

      /* ========================================
         RESPONSIVE
         ======================================== */

      @media (max-width: 480px) {
        .wa-chat-area {
          padding: 1rem;
        }

        .wa-message-bubble {
          max-width: 280px;
        }

        .wa-option-btn {
          padding: 0.875rem;
        }

        .wa-small-option-btn {
          min-height: 90px;
          padding: 0.875rem;
        }
      }
    `;
    document.head.appendChild(style);
  }

  // ========================================
  // SECTION 21: INITIALIZATION
  // ========================================

  function handleWhatsAppClick(event) {
    event.preventDefault();
    log('WhatsApp button clicked');
    showModal();
  }

  async function init() {
    log('Initializing WhatsApp Smart V5');

    // Load translations from JSON files first
    await loadTranslations();
    log('Translations loaded');

    injectStyles();

    const buttons = document.querySelectorAll(
      'a[href*="wa.me"], a[href*="whatsapp.com"], ' +
      '.btn-whatsapp-smart, .btn-hero-secondary, .btn-sticky-whatsapp, ' +
      '.btn-cta-final-secondary, .hero-btn-whatsapp'
    );

    if (buttons.length === 0) {
      log('No WhatsApp buttons found');
      return;
    }

    log(`Found ${buttons.length} WhatsApp buttons`);
    buttons.forEach((btn, idx) => {
      const originalHref = btn.getAttribute('href');
      if (originalHref) {
        btn.setAttribute('data-original-href', originalHref);
      }
      btn.style.cursor = 'pointer';
      btn.addEventListener('click', handleWhatsAppClick);
      log(`Button ${idx + 1} initialized`);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modalElement && modalElement.style.display === 'flex') {
        hideModal();
      }
    });

    // Click outside to close
    document.addEventListener('click', (e) => {
      if (modalElement && e.target === modalElement) {
        hideModal();
      }
    });

    log('✅ WhatsApp Smart V5 ready');
  }

  // ========================================
  // AUTO-INIT
  // ========================================

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
