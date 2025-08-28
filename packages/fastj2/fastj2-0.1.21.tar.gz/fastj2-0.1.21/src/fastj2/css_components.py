icons = """
/* Icon Containers */
.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  position: relative;
  margin: 0 auto;
}

.icon-container::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  background: inherit;
  animation: iconPulse 2s ease-in-out infinite;
}

.icon-content {
  position: relative;
  z-index: 1;
  color: white;
  font-weight: var(--font-weight-bold);
}

/* Icon Sizes */
.icon-sm {
  width: 40px;
  height: 40px;
}

.icon-sm .icon-content {
  font-size: var(--font-size-lg);
}

.icon-md {
  width: 64px;
  height: 64px;
}

.icon-md .icon-content {
  font-size: var(--font-size-2xl);
}

.icon-lg {
  width: 80px;
  height: 80px;
}

.icon-lg .icon-content {
  font-size: var(--font-size-4xl);
}

.icon-xl {
  width: 120px;
  height: 120px;
  border-radius: var(--radius-full);
}

.icon-xl .icon-content {
  font-size: var(--font-size-4xl);
}

/* Icon Variants */
.icon-primary {
  background: var(--gradient-primary-alt);
  box-shadow: var(--shadow-button);
}

.icon-success {
  background: var(--gradient-success);
  box-shadow: var(--shadow-success);
}

.icon-error {
  background: var(--gradient-error);
  box-shadow: var(--shadow-error);
}

.icon-warning {
  background: var(--gradient-warning);
}

/* Profile Pictures */
.profile-picture {
  background: var(--gradient-primary-alt);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-button);
  flex-shrink: 0;
}

.profile-initials {
  position: relative;
  z-index: 1;
}
"""

forms = """
/* Form Elements */
.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  margin-bottom: var(--space-sm);
  color: #374151;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.form-input {
  width: 100%;
  padding: var(--space-md) var(--space-lg);
  border: 2px solid #e5e7eb;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  background: var(--glass-white-soft);
  backdrop-filter: blur(5px);
  transition: all var(--duration-normal) var(--ease-out);
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.1);
  background: rgba(255, 255, 255, 1);
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-input--error {
  border-color: #dc2626;
}

.form-input--error:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

/* Error Messages */
.error-message {
  color: #dc2626;
  font-size: var(--font-size-sm);
  margin-top: var(--space-sm);
  display: none;
}

.error-message.show {
  display: block;
  animation: errorShake 0.5s ease-in-out;
}

/* Form Layouts */
.form-row {
  display: flex;
  gap: var(--space-md);
}

.form-row .form-group {
  flex: 1;
}

@media (max-width: 640px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
"""

status = """
/* Status Indicators */
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-xl);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  animation: statusPulse 2s ease-in-out infinite;
}

.status-available {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-available .status-dot {
  background: #10b981;
}

.status-busy {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-busy .status-dot {
  background: #ef4444;
}

.status-away {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-away .status-dot {
  background: #f59e0b;
}

.status-offline {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.status-offline .status-dot {
  background: #6b7280;
}

/* Badges */
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-primary {
  background: var(--primary-blue);
  color: white;
}

.badge-success {
  background: #10b981;
  color: white;
}

.badge-error {
  background: #ef4444;
  color: white;
}

.badge-warning {
  background: #f59e0b;
  color: white;
}

.badge-neutral {
  background: #6b7280;
  color: white;
}
"""