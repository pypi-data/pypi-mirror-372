spacing = """
/* Margin Utilities */
.m-0 { margin: 0; }
.m-xs { margin: var(--space-xs); }
.m-sm { margin: var(--space-sm); }
.m-md { margin: var(--space-md); }
.m-lg { margin: var(--space-lg); }
.m-xl { margin: var(--space-xl); }
.m-2xl { margin: var(--space-2xl); }
.m-3xl { margin: var(--space-3xl); }

/* Margin Top */
.mt-0 { margin-top: 0; }
.mt-xs { margin-top: var(--space-xs); }
.mt-sm { margin-top: var(--space-sm); }
.mt-md { margin-top: var(--space-md); }
.mt-lg { margin-top: var(--space-lg); }
.mt-xl { margin-top: var(--space-xl); }
.mt-2xl { margin-top: var(--space-2xl); }
.mt-3xl { margin-top: var(--space-3xl); }

/* Margin Bottom */
.mb-0 { margin-bottom: 0; }
.mb-xs { margin-bottom: var(--space-xs); }
.mb-sm { margin-bottom: var(--space-sm); }
.mb-md { margin-bottom: var(--space-md); }
.mb-lg { margin-bottom: var(--space-lg); }
.mb-xl { margin-bottom: var(--space-xl); }
.mb-2xl { margin-bottom: var(--space-2xl); }
.mb-3xl { margin-bottom: var(--space-3xl); }

/* Padding Utilities */
.p-0 { padding: 0; }
.p-xs { padding: var(--space-xs); }
.p-sm { padding: var(--space-sm); }
.p-md { padding: var(--space-md); }
.p-lg { padding: var(--space-lg); }
.p-xl { padding: var(--space-xl); }
.p-2xl { padding: var(--space-2xl); }
.p-3xl { padding: var(--space-3xl); }

/* Padding Top */
.pt-0 { padding-top: 0; }
.pt-xs { padding-top: var(--space-xs); }
.pt-sm { padding-top: var(--space-sm); }
.pt-md { padding-top: var(--space-md); }
.pt-lg { padding-top: var(--space-lg); }
.pt-xl { padding-top: var(--space-xl); }
.pt-2xl { padding-top: var(--space-2xl); }
.pt-3xl { padding-top: var(--space-3xl); }

/* Padding Bottom */
.pb-0 { padding-bottom: 0; }
.pb-xs { padding-bottom: var(--space-xs); }
.pb-sm { padding-bottom: var(--space-sm); }
.pb-md { padding-bottom: var(--space-md); }
.pb-lg { padding-bottom: var(--space-lg); }
.pb-xl { padding-bottom: var(--space-xl); }
.pb-2xl { padding-bottom: var(--space-2xl); }
.pb-3xl { padding-bottom: var(--space-3xl); }

/* Auto margins for centering */
.mx-auto { margin-left: auto; margin-right: auto; }
.ml-auto { margin-left: auto; }
.mr-auto { margin-right: auto; }
"""

text = """
/* Complete Text Utilities for 7-utilities/text.css */

/* Text Alignment */
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-justify { text-align: justify; }

/* Font Weights */
.font-normal { font-weight: var(--font-weight-normal); }
.font-medium { font-weight: var(--font-weight-medium); }
.font-semibold { font-weight: var(--font-weight-semibold); }
.font-bold { font-weight: var(--font-weight-bold); }

/* Font Sizes */
.text-xs { font-size: var(--font-size-xs); }
.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-lg { font-size: var(--font-size-lg); }
.text-xl { font-size: var(--font-size-xl); }
.text-2xl { font-size: var(--font-size-2xl); }
.text-3xl { font-size: var(--font-size-3xl); }
.text-4xl { font-size: var(--font-size-4xl); }
.text-5xl { font-size: var(--font-size-5xl); }

/* Text Colors - Updated for White Default System */
.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-muted { color: var(--text-muted); }
.text-disabled { color: var(--text-disabled); }

/* Explicit white text variations */
.text-white { color: white; }
.text-white-90 { color: rgba(255, 255, 255, 0.9); }
.text-white-70 { color: rgba(255, 255, 255, 0.7); }
.text-white-50 { color: rgba(255, 255, 255, 0.5); }

/* Dark text for light backgrounds */
.text-dark { color: var(--text-dark-primary); }
.text-dark-secondary { color: var(--text-dark-secondary); }
.text-dark-muted { color: var(--text-dark-muted); }

/* Status colors - updated for dark backgrounds */
.text-success { color: var(--text-success); }
.text-error { color: var(--text-error); }
.text-warning { color: var(--text-warning); }
.text-info { color: var(--text-info); }

/* Legacy gray colors - updated for glassmorphism */
.text-gray-light { color: rgba(255, 255, 255, 0.6); }
.text-gray { color: rgba(255, 255, 255, 0.8); }
.text-gray-dark { color: rgba(255, 255, 255, 0.9); }

/* Text Transform */
.uppercase { text-transform: uppercase; }
.lowercase { text-transform: lowercase; }
.capitalize { text-transform: capitalize; }
.normal-case { text-transform: none; }

/* Letter Spacing */
.tracking-tight { letter-spacing: -0.025em; }
.tracking-normal { letter-spacing: 0; }
.tracking-wide { letter-spacing: 0.025em; }
.tracking-wider { letter-spacing: 0.05em; }
.tracking-widest { letter-spacing: 0.1em; }

/* Line Height */
.leading-none { line-height: 1; }
.leading-tight { line-height: 1.25; }
.leading-snug { line-height: 1.375; }
.leading-normal { line-height: 1.5; }
.leading-relaxed { line-height: 1.625; }
.leading-loose { line-height: 2; }

/* Text Effects - Enhanced for glassmorphism */
.text-shadow { text-shadow: var(--text-shadow-light); }
.text-shadow-md { text-shadow: var(--text-shadow-medium); }
.text-shadow-lg { text-shadow: var(--text-shadow-heavy); }
.text-shadow-none { text-shadow: none; }

/* Legacy text shadow support */
.text-shadow-legacy { text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.text-shadow-lg-legacy { text-shadow: 0 4px 8px rgba(0,0,0,0.2); }

/* Gradient text - only when explicitly wanted */
.text-gradient {
  background: var(--gradient-text);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow: none;
}

.text-gradient-primary {
  background: var(--gradient-primary);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow: none;
}

.text-gradient-success {
  background: var(--gradient-success);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow: none;
}

/* Theme utilities */
.theme-light {
  color: var(--text-dark-primary);
}

.theme-light h1,
.theme-light h2,
.theme-light h3,
.theme-light h4,
.theme-light h5,
.theme-light h6 {
  color: var(--text-dark-primary);
  text-shadow: var(--text-shadow-light-theme);
}

.theme-light p {
  color: var(--text-dark-secondary);
  text-shadow: var(--text-shadow-light-theme-medium);
}

/* Light theme text color overrides */
.theme-light .text-gray-light { color: #9ca3af; }
.theme-light .text-gray { color: #6b7280; }
.theme-light .text-gray-dark { color: #374151; }
"""

visibility = """
/* Display */
.block { display: block; }
.inline-block { display: inline-block; }
.inline { display: inline; }
.flex { display: flex; }
.inline-flex { display: inline-flex; }
.grid { display: grid; }
.hidden { display: none; }

/* Visibility */
.visible { visibility: visible; }
.invisible { visibility: hidden; }

/* Opacity */
.opacity-0 { opacity: 0; }
.opacity-25 { opacity: 0.25; }
.opacity-50 { opacity: 0.5; }
.opacity-75 { opacity: 0.75; }
.opacity-100 { opacity: 1; }

/* Position */
.static { position: static; }
.fixed { position: fixed; }
.absolute { position: absolute; }
.relative { position: relative; }
.sticky { position: sticky; }

/* Z-index */
.z-0 { z-index: 0; }
.z-10 { z-index: 10; }
.z-20 { z-index: 20; }
.z-30 { z-index: 30; }
.z-40 { z-index: 40; }
.z-50 { z-index: 50; }
.z-auto { z-index: auto; }

/* Overflow */
.overflow-auto { overflow: auto; }
.overflow-hidden { overflow: hidden; }
.overflow-visible { overflow: visible; }
.overflow-scroll { overflow: scroll; }

/* Pointer Events */
.pointer-events-none { pointer-events: none; }
.pointer-events-auto { pointer-events: auto; }

/* User Select */
.select-none { user-select: none; }
.select-text { user-select: text; }
.select-all { user-select: all; }
.select-auto { user-select: auto; }
"""

responsive = """
/* Responsive Utilities */

/* Hide on mobile */
@media (max-width: 640px) {
  .sm\\:hidden { display: none; }
  .sm\\:block { display: block; }
  .sm\\:flex { display: flex; }
  .sm\\:text-center { text-align: center; }
  .sm\\:text-left { text-align: left; }

  /* Mobile spacing */
  .sm\\:p-sm { padding: var(--space-sm); }
  .sm\\:p-md { padding: var(--space-md); }
  .sm\\:p-lg { padding: var(--space-lg); }
  .sm\\:m-0 { margin: 0; }
  .sm\\:mt-md { margin-top: var(--space-md); }
  .sm\\:mb-md { margin-bottom: var(--space-md); }
}

/* Hide on tablet */
@media (max-width: 768px) {
  .md\\:hidden { display: none; }
  .md\\:block { display: block; }
  .md\\:flex { display: flex; }

  /* Tablet layout adjustments */
  .md\\:flex-col { flex-direction: column; }
  .md\\:text-center { text-align: center; }
  .md\\:w-full { width: 100%; }
}

/* Hide on desktop */
@media (min-width: 1024px) {
  .lg\\:hidden { display: none; }
  .lg\\:block { display: block; }
  .lg\\:flex { display: flex; }
  .lg\\:grid { display: grid; }
}

/* Container responsive behavior */
@media (max-width: 640px) {
  .container {
    padding: 0 var(--space-md);
  }

  .glass-card {
    margin: var(--space-md);
    padding: var(--space-lg);
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .btn:not(.btn-sm):not(.btn-lg) {
    padding: var(--space-md) var(--space-lg);
  }
}
"""