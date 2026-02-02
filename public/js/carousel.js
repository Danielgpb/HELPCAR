/**
 * Carrousel Générique et Réutilisable - Version Unifiée
 * =====================================================
 *
 * USAGE:
 * Ajouter l'attribut data-carousel sur n'importe quel conteneur
 *
 * ATTRIBUTS DISPONIBLES:
 * - data-carousel              : Identifie un carrousel (obligatoire)
 * - data-autoplay="5000"       : Temps d'autoplay en ms (0 = désactivé, défaut: 0)
 * - data-loop="true"           : Boucle infinie (défaut: true)
 * - data-pause-on-hover="true" : Pause au survol (défaut: true)
 *
 * STRUCTURE HTML:
 * <div data-carousel data-autoplay="5000">
 *   <div data-carousel-track>
 *     <div data-carousel-item><!-- Contenu (image, card, etc.) --></div>
 *     <div data-carousel-item><!-- Contenu --></div>
 *   </div>
 *   <button data-carousel-prev>←</button>
 *   <button data-carousel-next>→</button>
 *   <div data-carousel-dots></div>
 * </div>
 *
 * PERSONNALISATION:
 * Pour modifier l'apparence (bordures, couleurs, etc.),
 * il suffit de modifier les classes CSS correspondantes
 */

(function() {
  'use strict';

  // Initialisation au chargement de la page
  document.addEventListener('DOMContentLoaded', function() {
    // Trouver et initialiser tous les carrousels automatiquement
    const carousels = document.querySelectorAll('[data-carousel]');

    if (carousels.length === 0) {
      console.info('Aucun carrousel trouvé sur cette page');
      return;
    }

    console.info('Initialisation de ' + carousels.length + ' carrousel(s)');
    carousels.forEach(initCarousel);
  });

  /**
   * Initialise un carrousel générique
   * @param {HTMLElement} container - Conteneur du carrousel
   */
  function initCarousel(container) {
    // Lire la configuration depuis les attributs data-*
    const config = {
      autoplay: parseInt(container.getAttribute('data-autoplay')) || 0,
      loop: container.getAttribute('data-loop') !== 'false',
      pauseOnHover: container.getAttribute('data-pause-on-hover') !== 'false'
    };

    // Trouver les éléments du carrousel
    const track = container.querySelector('[data-carousel-track]');
    if (!track) {
      console.warn('Carrousel sans data-carousel-track trouvé, ignoré');
      return;
    }

    const items = track.querySelectorAll('[data-carousel-item]');
    const prevBtn = container.querySelector('[data-carousel-prev]');
    const nextBtn = container.querySelector('[data-carousel-next]');
    const dotsContainer = container.querySelector('[data-carousel-dots]');

    if (items.length === 0) {
      console.warn('Carrousel sans items trouvé, ignoré');
      return;
    }

    // État du carrousel
    let currentIndex = 0;
    let autoplayInterval = null;
    const totalItems = items.length;

    // ===== FONCTIONS UTILITAIRES =====

    /**
     * Va à une slide spécifique
     */
    function goToSlide(index) {
      // Gérer la boucle ou les limites
      if (config.loop) {
        currentIndex = (index + totalItems) % totalItems;
      } else {
        currentIndex = Math.max(0, Math.min(index, totalItems - 1));
      }

      // Appliquer la transformation
      const offset = -currentIndex * 100;
      track.style.transform = 'translateX(' + offset + '%)';

      // Mettre à jour les dots
      updateDots();

      // Mettre à jour les boutons (si pas de loop)
      if (!config.loop) {
        updateButtons();
      }

      // Réinitialiser l'autoplay
      if (config.autoplay > 0) {
        resetAutoplay();
      }
    }

    /**
     * Aller à la slide suivante
     */
    function nextSlide() {
      if (config.loop || currentIndex < totalItems - 1) {
        goToSlide(currentIndex + 1);
      }
    }

    /**
     * Aller à la slide précédente
     */
    function prevSlide() {
      if (config.loop || currentIndex > 0) {
        goToSlide(currentIndex - 1);
      }
    }

    /**
     * Mettre à jour l'état visuel des dots
     */
    function updateDots() {
      if (!dotsContainer) return;

      const dots = dotsContainer.querySelectorAll('[data-carousel-dot]');
      dots.forEach(function(dot, index) {
        if (index === currentIndex) {
          dot.classList.add('active');
          dot.setAttribute('aria-current', 'true');
        } else {
          dot.classList.remove('active');
          dot.setAttribute('aria-current', 'false');
        }
      });
    }

    /**
     * Mettre à jour l'état des boutons prev/next (si pas de loop)
     */
    function updateButtons() {
      if (prevBtn) {
        prevBtn.disabled = (currentIndex === 0);
        prevBtn.setAttribute('aria-disabled', currentIndex === 0 ? 'true' : 'false');
      }
      if (nextBtn) {
        nextBtn.disabled = (currentIndex === totalItems - 1);
        nextBtn.setAttribute('aria-disabled', currentIndex === totalItems - 1 ? 'true' : 'false');
      }
    }

    /**
     * Démarrer l'autoplay
     */
    function startAutoplay() {
      if (config.autoplay <= 0 || totalItems <= 1) return;

      autoplayInterval = setInterval(function() {
        nextSlide();
      }, config.autoplay);
    }

    /**
     * Arrêter l'autoplay
     */
    function stopAutoplay() {
      if (autoplayInterval) {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
      }
    }

    /**
     * Réinitialiser l'autoplay (stop + start)
     */
    function resetAutoplay() {
      stopAutoplay();
      startAutoplay();
    }

    // ===== CRÉER LES DOTS =====

    if (dotsContainer && totalItems > 1) {
      dotsContainer.innerHTML = '';

      for (let i = 0; i < totalItems; i++) {
        const dot = document.createElement('button');
        dot.setAttribute('data-carousel-dot', '');
        dot.setAttribute('aria-label', 'Aller à l\'élément ' + (i + 1));
        dot.setAttribute('type', 'button');

        if (i === 0) {
          dot.classList.add('active');
          dot.setAttribute('aria-current', 'true');
        } else {
          dot.setAttribute('aria-current', 'false');
        }

        // Event listener pour les dots
        dot.addEventListener('click', function() {
          goToSlide(i);
        });

        dotsContainer.appendChild(dot);
      }
    }

    // ===== EVENT LISTENERS =====

    // Bouton précédent
    if (prevBtn) {
      prevBtn.addEventListener('click', function(e) {
        e.preventDefault();
        prevSlide();
      });
    }

    // Bouton suivant
    if (nextBtn) {
      nextBtn.addEventListener('click', function(e) {
        e.preventDefault();
        nextSlide();
      });
    }

    // Pause au hover (si activé)
    if (config.pauseOnHover && config.autoplay > 0) {
      container.addEventListener('mouseenter', stopAutoplay);
      container.addEventListener('mouseleave', function() {
        if (totalItems > 1) {
          startAutoplay();
        }
      });
    }

    // Support touch/swipe pour mobile
    let touchStartX = 0;
    let touchEndX = 0;

    container.addEventListener('touchstart', function(e) {
      touchStartX = e.changedTouches[0].screenX;
      stopAutoplay();
    }, { passive: true });

    container.addEventListener('touchend', function(e) {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();

      if (config.autoplay > 0 && totalItems > 1) {
        startAutoplay();
      }
    }, { passive: true });

    function handleSwipe() {
      const swipeThreshold = 50;
      const diff = touchStartX - touchEndX;

      if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
          // Swipe left - next
          nextSlide();
        } else {
          // Swipe right - prev
          prevSlide();
        }
      }
    }

    // Support clavier (accessibilité)
    container.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevSlide();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        nextSlide();
      }
    });

    // ===== INITIALISATION =====

    // État initial
    goToSlide(0);

    // Démarrer l'autoplay si configuré
    if (config.autoplay > 0 && totalItems > 1) {
      startAutoplay();
    }

    // Log de succès
    console.info('Carrousel initialisé avec ' + totalItems + ' item(s)', config);
  }

})();
