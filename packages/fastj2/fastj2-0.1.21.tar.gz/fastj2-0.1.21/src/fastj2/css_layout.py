containers = """
/* Layout Containers */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  position: relative;
  z-index: var(--z-content);
}

.container--sm {
  max-width: 640px;
}

.container--md {
  max-width: 768px;
}

.container--lg {
  max-width: 1024px;
}

.container--xl {
  max-width: 1280px;
}

.container--2xl {
  max-width: 1440px;
}

/* Fluid containers */
.container--fluid {
  max-width: none;
  width: 100%;
}

.container--narrow {
  max-width: 600px;
}

.container--wide {
  max-width: 1600px;
}

/* Layout Systems */
.page-layout {
  min-height: 100vh;
  padding: var(--space-lg);
}

.centered-layout {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--space-lg);
}

.centered-content {
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.fullscreen-layout {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

/* Content Sections */
.content-section {
  margin-bottom: var(--space-3xl);
}

.content-section:last-child {
  margin-bottom: 0;
}

.content-section--compact {
  margin-bottom: var(--space-xl);
}

.content-section--spacious {
  margin-bottom: var(--space-4xl);
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .container,
  .container--lg,
  .container--xl,
  .container--2xl,
  .container--wide {
    padding: 0 var(--space-md);
  }
}

@media (max-width: 768px) {
  .container,
  .container--sm,
  .container--md,
  .container--lg,
  .container--xl,
  .container--2xl,
  .container--wide {
    padding: 0 var(--space-md);
  }
  
  .page-layout,
  .centered-layout {
    padding: var(--space-md);
  }
}

@media (max-width: 480px) {
  .container,
  .container--sm,
  .container--md,
  .container--lg,
  .container--xl,
  .container--2xl,
  .container--wide {
    padding: 0 var(--space-sm);
  }
  
  .page-layout,
  .centered-layout {
    padding: var(--space-sm);
  }
  
  .content-section {
    margin-bottom: var(--space-2xl);
  }
}
"""

grid = """
/* Grid System */
.grid {
  display: grid;
  gap: var(--space-lg);
}

/* Gap variations */
.grid--gap-sm {
  gap: var(--space-sm);
}

.grid--gap-md {
  gap: var(--space-md);
}

.grid--gap-lg {
  gap: var(--space-lg);
}

.grid--gap-xl {
  gap: var(--space-xl);
}

/* Fixed column grids */
.grid--1 {
  grid-template-columns: 1fr;
}

.grid--2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid--3 {
  grid-template-columns: repeat(3, 1fr);
}

.grid--4 {
  grid-template-columns: repeat(4, 1fr);
}

.grid--5 {
  grid-template-columns: repeat(5, 1fr);
}

.grid--6 {
  grid-template-columns: repeat(6, 1fr);
}

/* Responsive auto-fit grids */
.grid--auto-sm {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.grid--auto-md {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.grid--auto-lg {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.grid--auto-xl {
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
}

/* Card grids - optimized for common card sizes */
.grid--cards {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.grid--cards-sm {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.grid--cards-lg {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

/* Flex System */
.flex {
  display: flex;
}

.flex--column {
  flex-direction: column;
}

.flex--row {
  flex-direction: row;
}

.flex--center {
  align-items: center;
  justify-content: center;
}

.flex--start {
  align-items: flex-start;
  justify-content: flex-start;
}

.flex--end {
  align-items: flex-end;
  justify-content: flex-end;
}

.flex--between {
  justify-content: space-between;
  align-items: center;
}

.flex--around {
  justify-content: space-around;
  align-items: center;
}

.flex--evenly {
  justify-content: space-evenly;
  align-items: center;
}

.flex--wrap {
  flex-wrap: wrap;
}

.flex--nowrap {
  flex-wrap: nowrap;
}

/* Flex gaps */
.flex--gap-sm {
  gap: var(--space-sm);
}

.flex--gap-md {
  gap: var(--space-md);
}

.flex--gap-lg {
  gap: var(--space-lg);
}

.flex--gap-xl {
  gap: var(--space-xl);
}

/* Responsive flex utilities */
.flex--mobile-column {
  flex-direction: column;
}

.flex--tablet-column {
  flex-direction: column;
}

.flex--desktop-row {
  flex-direction: row;
}

/* Responsive Media Queries */
/* Large screens - maintain more columns */
@media (min-width: 1200px) {
  .grid--4-responsive {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .grid--6-responsive {
    grid-template-columns: repeat(6, 1fr);
  }
}

/* Medium screens - reduce columns */
@media (max-width: 1199px) and (min-width: 769px) {
  .grid--4 {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .grid--5,
  .grid--6 {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .flex--tablet-column {
    flex-direction: column;
  }
}

/* Small screens - further reduce */
@media (max-width: 768px) {
  .grid--3,
  .grid--4,
  .grid--5,
  .grid--6 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .flex--mobile-column {
    flex-direction: column;
  }
  
  .flex--gap-lg {
    gap: var(--space-md);
  }
}

/* Extra small screens - single column */
@media (max-width: 480px) {
  .grid--2,
  .grid--3,
  .grid--4,
  .grid--5,
  .grid--6 {
    grid-template-columns: 1fr;
  }
  
  .grid {
    gap: var(--space-md);
  }
  
  .flex--gap-lg,
  .flex--gap-md {
    gap: var(--space-sm);
  }
}

/* Utility classes for common patterns */
.grid--dashboard {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-lg);
}

.grid--sidebar {
  grid-template-columns: 250px 1fr;
  gap: var(--space-lg);
}

@media (max-width: 768px) {
  .grid--sidebar {
    grid-template-columns: 1fr;
  }
}
"""