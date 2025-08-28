cards = """
/* Base Glass Card */
.glass-card {
  background: var(--glass-white);
  backdrop-filter: blur(10px);
  border: var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-glass-lg);
  padding: var(--space-2xl) var(--space-xl);
  position: relative;
  z-index: var(--z-content);
  transition: all var(--duration-normal) var(--ease-out);
}

.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glass-xl);
}

/* Card Variants */
.glass-card--center {
  text-align: center;
  max-width: 450px;
  width: 100%;
}

.glass-card--sm {
  padding: var(--space-lg) var(--space-lg);
  max-width: 380px;
}

.glass-card--lg {
  padding: var(--space-3xl) var(--space-2xl);
  max-width: 600px;
}

.glass-card--dark {
  background: var(--glass-dark);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.glass-card--subtle {
  background: var(--glass-white-subtle);
  border: var(--glass-border-subtle);
}

.glass-card--strong {
  background: var(--glass-white);
  border: var(--glass-border-strong);
  box-shadow: var(--shadow-glass-xl);
}

/* Card Content */
.card-header {
  margin-bottom: var(--space-lg);
}

.card-body {
  margin-bottom: var(--space-lg);
}

.card-footer {
  margin-top: var(--space-lg);
  padding-top: var(--space-lg);
  border-top: 1px solid rgba(107, 114, 128, 0.1);
}

/* Info Cards */
.info-card {
  padding: var(--space-lg);
  border-radius: var(--radius-lg);
  background: var(--glass-white-soft);
  backdrop-filter: blur(5px);
  border: var(--glass-border-subtle);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) 0;
  border-bottom: 1px solid rgba(107, 114, 128, 0.1);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #6b7280;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.info-value {
  color: #1f2937;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}
"""

modals = """
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
}

.modal-content {
  background: var(--glass-white);
  backdrop-filter: blur(15px);
  border: var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-glass-xl);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  padding: var(--space-xl) var(--space-xl) 0;
  border-bottom: 1px solid rgba(107, 114, 128, 0.1);
  margin-bottom: var(--space-lg);
}

.modal-body {
  padding: 0 var(--space-xl);
}

.modal-footer {
  padding: var(--space-lg) var(--space-xl) var(--space-xl);
  border-top: 1px solid rgba(107, 114, 128, 0.1);
  margin-top: var(--space-lg);
}

.modal-close {
  position: absolute;
  top: var(--space-md);
  right: var(--space-md);
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  cursor: pointer;
  color: #6b7280;
  transition: color var(--duration-fast) var(--ease-out);
}

.modal-close:hover {
  color: #374151;
}
"""
