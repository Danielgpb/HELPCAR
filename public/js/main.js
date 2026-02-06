/**
 * HELPCAR-V2 - Main Interactive JavaScript
 * Vanilla JS, no dependencies. Handles all site interactivity.
 */
(function () {
  'use strict';

  /* ==========================================================================
     1. MOBILE MENU TOGGLE
     ========================================================================== */

  function initMobileMenu() {
    var toggle = document.querySelector('.menu-toggle');
    var menu = document.querySelector('.mobile-menu');
    if (!toggle || !menu) return;

    function openMenu() {
      menu.classList.add('active');
      toggle.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
      menu.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }

    function isOpen() {
      return menu.classList.contains('active');
    }

    // Toggle on hamburger click
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      isOpen() ? closeMenu() : openMenu();
    });

    // Close when clicking a link inside the menu
    menu.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') closeMenu();
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (isOpen() && !menu.contains(e.target) && e.target !== toggle) {
        closeMenu();
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) closeMenu();
    });
  }

  /* ==========================================================================
     2. FAQ ACCORDION
     ========================================================================== */

  function initFaqAccordion() {
    var container = document.querySelector('.faq-section, .faq-container, .faq-list');
    if (!container) return;

    // Use event delegation on the nearest common ancestor
    container.addEventListener('click', handleFaqToggle);
    container.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        var question = e.target.closest('.faq-question');
        if (question) {
          e.preventDefault();
          toggleFaqItem(question);
        }
      }
    });

    function handleFaqToggle(e) {
      var question = e.target.closest('.faq-question');
      if (!question) return;
      toggleFaqItem(question);
    }

    function toggleFaqItem(question) {
      var item = question.closest('.faq-item');
      if (!item) return;

      var wasActive = item.classList.contains('active');

      // Close all other FAQ items (only one open at a time)
      var allItems = container.querySelectorAll('.faq-item.active');
      for (var i = 0; i < allItems.length; i++) {
        allItems[i].classList.remove('active');
      }

      // Toggle the clicked item
      if (!wasActive) {
        item.classList.add('active');
      }
    }
  }

  /* ==========================================================================
     3. SCROLL ANIMATIONS (Intersection Observer)
     ========================================================================== */

  function initScrollAnimations() {
    // Respect prefers-reduced-motion
    var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prefersReduced.matches) {
      // Make everything visible immediately
      var els = document.querySelectorAll('.animate-on-scroll');
      for (var i = 0; i < els.length; i++) {
        els[i].classList.add('visible');
      }
      return;
    }

    if (!('IntersectionObserver' in window)) {
      // Fallback: show everything if IO not supported
      var fallback = document.querySelectorAll('.animate-on-scroll');
      for (var j = 0; j < fallback.length; j++) {
        fallback[j].classList.add('visible');
      }
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target); // Animate only once
        }
      });
    }, { threshold: 0.1 });

    var targets = document.querySelectorAll('.animate-on-scroll');
    targets.forEach(function (el) {
      observer.observe(el);
    });
  }

  /* ==========================================================================
     4. HEADER SCROLL EFFECT
     ========================================================================== */

  function initHeaderScroll() {
    var header = document.querySelector('header, .site-header');
    if (!header) return;

    var scrollThreshold = 50;
    var ticking = false;

    function updateHeader() {
      if (window.scrollY > scrollThreshold) {
        header.classList.add('header-scrolled');
      } else {
        header.classList.remove('header-scrolled');
      }
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(updateHeader);
        ticking = true;
      }
    }, { passive: true });

    // Set initial state
    updateHeader();
  }

  /* ==========================================================================
     5. SMOOTH SCROLL FOR ANCHOR LINKS
     ========================================================================== */

  function initSmoothScroll() {
    var headerOffset = 70;

    document.addEventListener('click', function (e) {
      var link = e.target.closest('a[href^="#"]');
      if (!link) return;

      var targetId = link.getAttribute('href');
      if (targetId === '#' || targetId.length < 2) return;

      var target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();

      var top = target.getBoundingClientRect().top + window.scrollY - headerOffset;
      window.scrollTo({ top: top, behavior: 'smooth' });

      // Close mobile menu if open
      var mobileMenu = document.querySelector('.mobile-menu.active');
      if (mobileMenu) {
        mobileMenu.classList.remove('active');
        var toggle = document.querySelector('.menu-toggle');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      }
    });
  }

  /* ==========================================================================
     6. REVIEWS CAROUSEL
     ========================================================================== */

  function initReviewsCarousel() {
    var track = document.querySelector('.reviews-track');
    if (!track) return;

    var nav = document.querySelector('.reviews-nav');
    var items = track.children;
    if (!items.length) return;

    var currentIndex = 0;
    var autoplayInterval = null;
    var autoplayDelay = 5000;
    var isPaused = false;

    // Build dot indicators if nav container exists
    var dots = [];
    if (nav) {
      for (var i = 0; i < items.length; i++) {
        var dot = document.createElement('button');
        dot.className = 'reviews-dot' + (i === 0 ? ' active' : '');
        dot.setAttribute('aria-label', 'Avis ' + (i + 1));
        dot.dataset.index = i;
        nav.appendChild(dot);
        dots.push(dot);
      }

      nav.addEventListener('click', function (e) {
        var btn = e.target.closest('.reviews-dot');
        if (!btn) return;
        goTo(parseInt(btn.dataset.index, 10));
      });
    }

    function goTo(index) {
      currentIndex = ((index % items.length) + items.length) % items.length;
      track.scrollTo({ left: items[currentIndex].offsetLeft, behavior: 'smooth' });
      updateDots();
    }

    function updateDots() {
      dots.forEach(function (d, i) {
        d.classList.toggle('active', i === currentIndex);
      });
    }

    function next() {
      goTo(currentIndex + 1);
    }

    // Auto-scroll
    function startAutoplay() {
      stopAutoplay();
      autoplayInterval = setInterval(function () {
        if (!isPaused) next();
      }, autoplayDelay);
    }

    function stopAutoplay() {
      if (autoplayInterval) clearInterval(autoplayInterval);
    }

    // Pause on hover / touch
    track.addEventListener('mouseenter', function () { isPaused = true; });
    track.addEventListener('mouseleave', function () { isPaused = false; });
    track.addEventListener('touchstart', function () { isPaused = true; }, { passive: true });
    track.addEventListener('touchend', function () { isPaused = false; }, { passive: true });

    // Swipe support
    var touchStartX = 0;
    track.addEventListener('touchstart', function (e) {
      touchStartX = e.touches[0].clientX;
    }, { passive: true });

    track.addEventListener('touchend', function (e) {
      var diff = touchStartX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 50) {
        diff > 0 ? goTo(currentIndex + 1) : goTo(currentIndex - 1);
      }
    }, { passive: true });

    startAutoplay();
  }

  /* ==========================================================================
     7. IMAGE CAROUSEL (Hero)
     ========================================================================== */

  function initImageCarousel() {
    var carousels = document.querySelectorAll('[data-carousel]');
    if (!carousels.length) return;

    carousels.forEach(function (carousel) {
      var track = carousel.querySelector('.carousel-track, .carousel-slides');
      if (!track) return;

      var slides = track.children;
      if (!slides.length) return;

      var currentSlide = 0;
      var totalSlides = slides.length;
      var autoplayDelay = parseInt(carousel.dataset.autoplay, 10) || 4000;
      var autoplayTimer = null;
      var isPaused = false;

      // Generate dot indicators
      var dotsContainer = document.createElement('div');
      dotsContainer.className = 'carousel-dots';
      var dots = [];
      for (var i = 0; i < totalSlides; i++) {
        var dot = document.createElement('button');
        dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
        dot.setAttribute('aria-label', 'Slide ' + (i + 1));
        dot.dataset.slide = i;
        dotsContainer.appendChild(dot);
        dots.push(dot);
      }
      carousel.appendChild(dotsContainer);

      // Dot click handler
      dotsContainer.addEventListener('click', function (e) {
        var btn = e.target.closest('.carousel-dot');
        if (!btn) return;
        goToSlide(parseInt(btn.dataset.slide, 10));
      });

      // Prev / Next buttons
      var prevBtn = carousel.querySelector('.carousel-prev, [data-carousel-prev]');
      var nextBtn = carousel.querySelector('.carousel-next, [data-carousel-next]');

      if (prevBtn) prevBtn.addEventListener('click', function () { goToSlide(currentSlide - 1); });
      if (nextBtn) nextBtn.addEventListener('click', function () { goToSlide(currentSlide + 1); });

      function goToSlide(index) {
        // Infinite loop
        currentSlide = ((index % totalSlides) + totalSlides) % totalSlides;
        track.style.transform = 'translateX(-' + (currentSlide * 100) + '%)';
        updateDots();
        resetAutoplay();
      }

      function updateDots() {
        dots.forEach(function (d, i) {
          d.classList.toggle('active', i === currentSlide);
        });
      }

      // Autoplay
      function startAutoplay() {
        if (!carousel.dataset.autoplay) return;
        autoplayTimer = setInterval(function () {
          if (!isPaused) goToSlide(currentSlide + 1);
        }, autoplayDelay);
      }

      function resetAutoplay() {
        if (autoplayTimer) clearInterval(autoplayTimer);
        startAutoplay();
      }

      // Pause on hover
      carousel.addEventListener('mouseenter', function () { isPaused = true; });
      carousel.addEventListener('mouseleave', function () { isPaused = false; });

      startAutoplay();
    });
  }

  /* ==========================================================================
     INIT - Run everything on DOM ready
     ========================================================================== */

  document.addEventListener('DOMContentLoaded', function () {
    initMobileMenu();
    initFaqAccordion();
    initScrollAnimations();
    initHeaderScroll();
    initSmoothScroll();
    initReviewsCarousel();
    initImageCarousel();
  });

})();
