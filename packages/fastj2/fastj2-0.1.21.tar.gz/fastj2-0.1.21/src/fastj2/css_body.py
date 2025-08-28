base = """
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  line-height: 1.6;
  margin: 0;
  min-height: 100vh;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body.no-scroll {
  overflow: hidden;
}

html {
  scroll-behavior: smooth;
}

/* Focus styles for accessibility */
*:focus {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
}

button:focus,
input:focus,
select:focus,
textarea:focus {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
}
"""

typography = """
/* Base typography */
h1, h2, h3, h4, h5, h6 {
  margin: 0;
  font-weight: var(--font-weight-bold);
  color: white; /* Default white text */
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); /* Subtle shadow for readability */
}

h1 { font-size: var(--font-size-5xl); }
h2 { font-size: var(--font-size-4xl); }
h3 { font-size: var(--font-size-3xl); }
h4 { font-size: var(--font-size-2xl); }
h5 { font-size: var(--font-size-xl); }
h6 { font-size: var(--font-size-lg); }

p {
  margin: 0;
  color: rgba(255, 255, 255, 0.9); /* Light white for body text */
  line-height: 1.5;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

a {
  color: #60a5fa; /* Light blue that shows on dark backgrounds */
  text-decoration: none;
  font-weight: var(--font-weight-semibold);
  position: relative;
  transition: all var(--duration-normal) var(--ease-out);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

a::before {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: -2px;
  left: 50%;
  background: linear-gradient(90deg, #60a5fa, #3b82f6);
  transition: all var(--duration-normal) var(--ease-out);
  transform: translateX(-50%);
}

a:hover {
  color: #93c5fd;
  transform: translateY(-1px);
}

a:hover::before {
  width: 100%;
}

/* OPTIONAL gradient text - only when explicitly used */
.text-gradient {
  background: var(--gradient-text);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow: none; /* Remove shadow for gradient text */
}

.text-gradient-primary {
  background: var(--gradient-primary);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow: none;
}

/* DARK THEME OVERRIDES - for light backgrounds */
.theme-light,
.glass-card--light {
  color: #1f2937;
}

.theme-light h1,
.theme-light h2,
.theme-light h3,
.theme-light h4,
.theme-light h5,
.theme-light h6,
.glass-card--light h1,
.glass-card--light h2,
.glass-card--light h3,
.glass-card--light h4,
.glass-card--light h5,
.glass-card--light h6 {
  color: #1f2937;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
}

.theme-light p,
.glass-card--light p {
  color: #4b5563;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.theme-light a,
.glass-card--light a {
  color: var(--primary-blue);
  text-shadow: none;
}
"""