css_vars = """
:root {
  /* Primary Brand Colors */
  --primary-blue: #0078d4;
  --primary-blue-dark: #106ebe;
  --primary-blue-light: #40e0ff;
  --accent-purple: #764ba2;
  --accent-purple-light: #667eea;

 /* TRUE Glassmorphism Colors - The Sweet Spot */
  --glass-white: rgba(255, 255, 255, 0.25);      /* Perfect balance */
  --glass-white-soft: rgba(255, 255, 255, 0.2);   /* Lighter */
  --glass-white-strong: rgba(255, 255, 255, 0.35); /* More opaque */
  --glass-white-ultra: rgba(255, 255, 255, 0.15);  /* Very light */
  --glass-dark: rgba(0, 0, 0, 0.25);              /* Dark glass */
  
  /* Glassmorphic Borders */
  --glass-border: 1px solid rgba(255, 255, 255, 0.18);
  --glass-border-strong: 1px solid rgba(255, 255, 255, 0.25);
  --glass-border-subtle: 1px solid rgba(255, 255, 255, 0.12);
  --glass-border-dark: 1px solid rgba(255, 255, 255, 0.1);
  
  /* True Glassmorphic Shadows */
  --shadow-glass: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  --shadow-glass-lg: 0 15px 45px 0 rgba(31, 38, 135, 0.5);
  --shadow-glass-sm: 0 4px 24px 0 rgba(31, 38, 135, 0.3);
  --shadow-glass-xl: 0 20px 60px 0 rgba(31, 38, 135, 0.6);
  
  /* Colored Glass Backgrounds */
  --glass-blue: rgba(103, 151, 255, 0.2);
  --glass-purple: rgba(159, 122, 234, 0.2);
  --glass-success: rgba(34, 197, 94, 0.2);
  --glass-error: rgba(239, 68, 68, 0.2);
  --glass-warning: rgba(245, 158, 11, 0.2);
  
  /* Colored Glass Shadows */
  --shadow-glass-blue: 0 8px 32px 0 rgba(103, 151, 255, 0.3);
  --shadow-glass-purple: 0 8px 32px 0 rgba(159, 122, 234, 0.3);
  --shadow-glass-success: 0 8px 32px 0 rgba(34, 197, 94, 0.3);
  --shadow-glass-error: 0 8px 32px 0 rgba(239, 68, 68, 0.3);
  
  /* Backdrop Filters */
  --glass-blur: blur(10px) saturate(180%);
  --glass-blur-light: blur(8px) saturate(160%);
  --glass-blur-heavy: blur(15px) saturate(200%);
  --glass-blur-ultra: blur(20px) saturate(200%) brightness(120%);
  --glass-blur-frosted: blur(15px) saturate(150%) contrast(110%);

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-primary-alt: linear-gradient(135deg, #0078d4 0%, #005a9e 100%);
  --gradient-success: linear-gradient(135deg, #22c55e, #16a34a);
  --gradient-error: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
  --gradient-warning: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  --gradient-text: linear-gradient(135deg, #1f2937, #374151);

  /* Animated Gradients */
  --gradient-animated: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-size: 400% 400%;

  /* Shadows */
  --shadow-glass: 0 8px 32px rgba(31, 38, 135, 0.37);
  --shadow-glass-lg: 0 20px 40px rgba(0,0,0,0.1);
  --shadow-glass-xl: 0 25px 50px rgba(31, 38, 135, 0.3);
  --shadow-button: 0 8px 20px rgba(0, 120, 212, 0.3);
  --shadow-button-hover: 0 12px 30px rgba(0, 120, 212, 0.4);
  --shadow-success: 0 10px 25px rgba(34, 197, 94, 0.3);
  --shadow-error: 0 10px 25px rgba(220, 38, 38, 0.3);

  /* Typography */
  --font-family-primary: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  --font-size-4xl: 36px;
  --font-size-5xl: 48px;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Text Colors - WHITE DEFAULT for glassmorphic design */
  --text-primary: white;
  --text-secondary: rgba(255, 255, 255, 0.9);
  --text-muted: rgba(255, 255, 255, 0.7);
  --text-disabled: rgba(255, 255, 255, 0.5);
  
  /* Link Colors - Light versions for dark backgrounds */
  --link-primary: #60a5fa;
  --link-hover: #93c5fd;
  --link-active: #3b82f6;
  
  /* Dark theme text colors - for light backgrounds */
  --text-dark-primary: #1f2937;
  --text-dark-secondary: #4b5563;
  --text-dark-muted: #6b7280;
  --text-dark-disabled: #9ca3af;
  
  /* Status text colors - visible on dark backgrounds */
  --text-success: #4ade80;
  --text-error: #f87171;
  --text-warning: #fbbf24;
  --text-info: #60a5fa;
  
  /* Text shadows */
  --text-shadow-light: 0 1px 2px rgba(0, 0, 0, 0.2);
  --text-shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.3);
  --text-shadow-heavy: 0 3px 6px rgba(0, 0, 0, 0.4);
  
  /* Light theme text shadows */
  --text-shadow-light-theme: 0 1px 2px rgba(255, 255, 255, 0.8);
  --text-shadow-light-theme-medium: 0 2px 4px rgba(255, 255, 255, 0.6);
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;

  /* Border Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 24px;
  --radius-full: 50%;

  /* Animation Timing */
  --duration-fast: 0.15s;
  --duration-normal: 0.3s;
  --duration-slow: 0.5s;
  --ease-out: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);

  /* Z-index Stack */
  --z-particles: 1;
  --z-content: 2;
  --z-overlay: 1000;
  --z-modal: 2000;
  --z-toast: 3000;
}

.glass-effect {
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
}

.glass-effect-light {
  backdrop-filter: var(--glass-blur-light);
  -webkit-backdrop-filter: var(--glass-blur-light);
}

.glass-effect-heavy {
  backdrop-filter: var(--glass-blur-heavy);
  -webkit-backdrop-filter: var(--glass-blur-heavy);
}
"""