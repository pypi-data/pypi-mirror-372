entrance = """
/* Entrance Animations */
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes cardSlideUp {
  0% {
    transform: translateY(100px) scale(0.8);
    opacity: 0;
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  0% {
    opacity: 0;
    transform: translateY(-30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  0% {
    opacity: 0;
    transform: translateX(-50px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  0% {
    opacity: 0;
    transform: translateX(50px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Animation Classes */
.animate-fade-in {
  animation: fadeIn 0.6s var(--ease-out) both;
}

.animate-fade-in-up {
  animation: fadeInUp 0.8s var(--ease-out) both;
}

.animate-fade-in-down {
  animation: fadeInDown 0.8s var(--ease-out) both;
}

.animate-slide-in-left {
  animation: slideInLeft 0.8s var(--ease-out) both;
}

.animate-slide-in-right {
  animation: slideInRight 0.8s var(--ease-out) both;
}

.animate-scale-in {
  animation: scaleIn 0.6s var(--ease-bounce) both;
}

.animate-bounce-in {
  animation: bounceIn 0.8s var(--ease-bounce) both;
}

.animate-card-enter {
  animation: cardSlideUp 0.8s var(--ease-smooth) both;
}

/* Animation Delays */
.animate-delay-100 { animation-delay: 0.1s; }
.animate-delay-200 { animation-delay: 0.2s; }
.animate-delay-300 { animation-delay: 0.3s; }
.animate-delay-400 { animation-delay: 0.4s; }
.animate-delay-500 { animation-delay: 0.5s; }
.animate-delay-600 { animation-delay: 0.6s; }
.animate-delay-700 { animation-delay: 0.7s; }
.animate-delay-800 { animation-delay: 0.8s; }
"""

interactive = """
/* Interactive Animations */
@keyframes iconPulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes statusPulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes rippleEffect {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(4);
    opacity: 0;
  }
}

@keyframes buttonSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes errorShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

@keyframes successBounce {
  0% {
    transform: scale(0) rotate(-180deg);
    opacity: 0;
  }
  50% {
    transform: scale(1.2) rotate(-90deg);
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

/* Hover Effects */
.hover-lift {
  transition: transform var(--duration-normal) var(--ease-out);
}

.hover-lift:hover {
  transform: translateY(-2px);
}

.hover-scale {
  transition: transform var(--duration-normal) var(--ease-out);
}

.hover-scale:hover {
  transform: scale(1.02);
}

.hover-glow {
  transition: box-shadow var(--duration-normal) var(--ease-out);
}

.hover-glow:hover {
  box-shadow: var(--shadow-glass-xl);
}

/* Focus Effects */
.focus-ring {
  transition: all var(--duration-fast) var(--ease-out);
}

.focus-ring:focus {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
}

.focus-ring:focus-visible {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
}
""",

loading = """
/* Loading Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes spinnerGlow {
  0% {
    box-shadow: 0 0 5px rgba(0, 120, 212, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 120, 212, 0.6);
  }
  100% {
    box-shadow: 0 0 5px rgba(0, 120, 212, 0.3);
  }
}

@keyframes spinnerRipple {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes loadingDots {
  0%, 20% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}

@keyframes progressBar {
  0% { width: 0%; }
  100% { width: 100%; }
}

/* Loading Components */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(229, 231, 235, 0.3);
  border-top: 4px solid var(--primary-blue);
  border-radius: var(--radius-full);
  animation: spin 1s linear infinite, spinnerGlow 2s ease-in-out infinite;
  position: relative;
}

.spinner::before {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(0, 120, 212, 0.2);
  animation: spinnerRipple 2s linear infinite;
}

.spinner-sm {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.spinner-lg {
  width: 60px;
  height: 60px;
  border-width: 6px;
}

.loading-dots {
  display: inline-block;
  animation: loadingDots 1.5s ease-in-out infinite;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(229, 231, 235, 0.3);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-primary-alt);
  border-radius: var(--radius-sm);
  animation: progressBar 2s ease-in-out;
}

.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
""",

particle_anims = """
/* Particle Animations */
@keyframes particleFloat {
  0%, 100% { 
    transform: translateY(100vh) rotate(0deg); 
    opacity: 0; 
  }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { 
    transform: translateY(-100px) rotate(360deg); 
    opacity: 0; 
  }
}

@keyframes sparkleEffect {
  0% {
    transform: scale(0) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: scale(1) rotate(180deg);
    opacity: 1;
  }
  100% {
    transform: scale(0) rotate(360deg);
    opacity: 0;
  }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}

@keyframes drift {
  0% { transform: translateX(0) translateY(0); }
  33% { transform: translateX(30px) translateY(-30px); }
  66% { transform: translateX(-20px) translateY(20px); }
  100% { transform: translateX(0) translateY(0); }
}

/* Particle Classes */
.particle-twinkle {
  animation: particleFloat 6s ease-in-out infinite, 
             twinkle 3s ease-in-out infinite;
}

.particle-drift {
  animation: particleFloat 8s ease-in-out infinite, 
             drift 4s ease-in-out infinite;
}

.particle-glow {
  box-shadow: 0 0 10px currentColor;
  animation: particleFloat 6s ease-in-out infinite, 
             pulse 2s ease-in-out infinite;
}

/* Interactive Particles */
.particles-interactive .particle {
  transition: all 0.3s ease;
}

.particles-interactive .particle:hover {
  transform: scale(1.5);
  opacity: 1 !important;
  animation-play-state: paused;
}

/* Particle Colors */
.particle-blue { background: rgba(0, 120, 212, 0.3); }
.particle-purple { background: rgba(118, 75, 162, 0.3); }
.particle-white { background: rgba(255, 255, 255, 0.1); }
.particle-gradient {
  background: var(--gradient-primary);
  opacity: 0.1;
}
"""