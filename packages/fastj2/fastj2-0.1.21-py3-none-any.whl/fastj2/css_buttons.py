primary = """
/* Primary Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  font-family: inherit;
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
  position: relative;
  overflow: hidden;
  text-decoration: none;
  user-select: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn:disabled:hover {
  transform: none !important;
  box-shadow: inherit !important;
}

/* Button Sizes */
.btn-sm {
  padding: var(--space-sm) var(--space-lg);
  font-size: var(--font-size-sm);
}

.btn-lg {
  padding: var(--space-lg) var(--space-2xl);
  font-size: var(--font-size-lg);
}

.btn-xl {
  padding: var(--space-xl) var(--space-3xl);
  font-size: var(--font-size-xl);
}

/* Button Icons */
.btn__icon {
  font-size: 1.2em;
}

.btn__text {
  position: relative;
  z-index: 1;
}

/* Loading State */
.btn--loading .btn__text {
  opacity: 0;
}

.btn--loading::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: var(--radius-full);
  animation: buttonSpin 1s linear infinite;
}

/* Block Button */
.btn-block {
  width: 100%;
}
"""

variants = """
/* Button Variants */
.btn-primary {
  background: var(--gradient-primary-alt);
  color: white;
  box-shadow: var(--shadow-button);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-button-hover);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-secondary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: var(--shadow-button);
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
}

.btn-outline {
  background: transparent;
  color: var(--primary-blue);
  border: 2px solid var(--primary-blue);
  box-shadow: none;
}

.btn-outline:hover {
  background: var(--primary-blue);
  color: white;
  transform: translateY(-1px);
  box-shadow: var(--shadow-button);
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
  border: var(--glass-border-subtle);
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.btn-success {
  background: var(--gradient-success);
  color: white;
  box-shadow: var(--shadow-success);
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(34, 197, 94, 0.4);
}

.btn-error {
  background: var(--gradient-error);
  color: white;
  box-shadow: var(--shadow-error);
}

.btn-error:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(220, 38, 38, 0.4);
}

.btn-warning {
  background: var(--gradient-warning);
  color: white;
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.3);
}

.btn-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(245, 158, 11, 0.4);
}

.btn-neutral {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: white;
  box-shadow: 0 8px 20px rgba(107, 114, 128, 0.3);
}

.btn-neutral:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(107, 114, 128, 0.4);
}
"""

effects = """
/* Button Effects */
.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left var(--duration-slow);
}

.btn:hover::before {
  left: 100%;
}

/* Ripple Effect */
.btn-ripple {
  overflow: hidden;
}

.ripple {
  position: absolute;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.3);
  animation: rippleEffect 0.6s ease-out;
  pointer-events: none;
}

/* Glass Button */
.btn-glass {
  background: var(--glass-white-soft);
  backdrop-filter: blur(10px);
  border: var(--glass-border);
  color: var(--primary-blue);
  box-shadow: var(--shadow-glass);
}

.btn-glass:hover {
  background: var(--glass-white);
  transform: translateY(-1px);
  box-shadow: var(--shadow-glass-lg);
}

/* Floating Action Button */
.btn-fab {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  padding: 0;
  position: fixed;
  bottom: var(--space-xl);
  right: var(--space-xl);
  z-index: var(--z-overlay);
  box-shadow: var(--shadow-glass-lg);
}

.btn-fab:hover {
  transform: translateY(-3px) scale(1.05);
}

/* Button Groups */
.btn-group {
  display: inline-flex;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-glass);
}

.btn-group .btn {
  border-radius: 0;
  margin: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-group .btn:first-child {
  border-top-left-radius: var(--radius-md);
  border-bottom-left-radius: var(--radius-md);
}

.btn-group .btn:last-child {
  border-top-right-radius: var(--radius-md);
  border-bottom-right-radius: var(--radius-md);
  border-right: none;
}
"""