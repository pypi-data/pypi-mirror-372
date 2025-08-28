gradients = """
/* Background Gradient Classes */
.bg-gradient-primary {
  background: var(--gradient-primary);
  background-size: var(--gradient-size);
}

.bg-gradient-animated {
  background: var(--gradient-animated);
  background-size: var(--gradient-size);
  animation: gradientShift 8s ease infinite;
}

.bg-gradient-primary-alt {
  background: var(--gradient-primary-alt);
}

.bg-gradient-success {
  background: var(--gradient-success);
}

.bg-gradient-error {
  background: var(--gradient-error);
}

.bg-gradient-warning {
  background: var(--gradient-warning);
}

/* Overlay Gradients */
.bg-overlay-light {
  background: 
    radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
    linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.bg-overlay-dark {
  background: 
    radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.2) 0%, transparent 50%),
    linear-gradient(135deg, #1f2937 0%, #111827 100%);
}
"""

particles = """
.floating-particles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: var(--z-particles);
  pointer-events: none;
}

.floating-particles.fixed {
  position: fixed;
  top: 0;
  left: 0;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  animation: particleFloat 6s ease-in-out infinite;
  pointer-events: none;
}

.particle--glow {
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.particle--colored {
  background: var(--primary-blue);
  opacity: 0.1;
}

/* Sparkle Effects */
.sparkle {
  position: fixed;
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--radius-full);
  pointer-events: none;
  z-index: var(--z-overlay);
  animation: sparkleEffect 1s ease-out forwards;
}

.sparkle--colored {
  background: var(--primary-blue);
  opacity: 0.8;
}
"""