/**
 * Custom Modal Dialog System
 * Beautiful replacement for alert() and confirm()
 */

class CustomModal {
    constructor() {
        this.modalContainer = null;
        this.createModalContainer();
    }

    createModalContainer() {
        // Create modal container if it doesn't exist
        if (!document.getElementById('customModalContainer')) {
            const container = document.createElement('div');
            container.id = 'customModalContainer';
            container.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 10000;
                animation: fadeIn 0.2s ease-out;
            `;
            document.body.appendChild(container);
            this.modalContainer = container;
        } else {
            this.modalContainer = document.getElementById('customModalContainer');
        }
    }

    /**
     * Show alert modal
     */
    alert(title, message, icon = '⚠️') {
        return new Promise((resolve) => {
            const modal = this.createModal(title, message, icon, [
                {
                    text: 'OK',
                    style: 'primary',
                    onClick: () => {
                        this.close();
                        resolve(true);
                    }
                }
            ]);
            this.show(modal);
        });
    }

    /**
     * Show confirm modal
     */
    confirm(title, message, icon = '❓', options = {}) {
        return new Promise((resolve) => {
            const confirmText = options.confirmText || 'OK';
            const cancelText = options.cancelText || 'Cancel';

            const modal = this.createModal(title, message, icon, [
                {
                    text: cancelText,
                    style: 'secondary',
                    onClick: () => {
                        this.close();
                        resolve(false);
                    }
                },
                {
                    text: confirmText,
                    style: 'primary',
                    onClick: () => {
                        this.close();
                        resolve(true);
                    }
                }
            ]);
            this.show(modal);
        });
    }

    /**
     * Show quota warning modal
     */
    quotaWarning(data) {
        return new Promise((resolve) => {
            const title = '⚠️ Quota Warning';
            const message = `
                <div style="text-align: left; line-height: 1.6;">
                    <p style="margin-bottom: 16px;">The selected date range contains <strong>${data.data_points_in_range.toLocaleString()}</strong> data points.</p>
                    <p style="margin-bottom: 16px;">Your current quota limit is <strong>${data.quota_limit.toLocaleString()}</strong> data points.</p>
                    <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 12px; border-radius: 6px; margin-bottom: 16px;">
                        <p style="color: #991b1b; margin: 0;">
                            <strong>Exceeds quota by ${(data.data_points_in_range - data.quota_limit).toLocaleString()} points</strong>
                        </p>
                    </div>
                    <div style="background: #eff6ff; border-left: 4px solid #2563eb; padding: 12px; border-radius: 6px; margin-bottom: 16px;">
                        <p style="color: #1e40af; margin: 0;">
                            <strong>💡 Suggested quota:</strong> ${data.suggested_quota.toLocaleString()} DPM
                        </p>
                    </div>
                    <p style="margin: 0; font-size: 14px; color: #6b7280;">Would you like to increase your quota to <strong>${data.suggested_quota.toLocaleString()}</strong>?</p>
                </div>
            `;

            const modal = this.createModal(title, message, '', [
                {
                    text: 'Cancel',
                    style: 'secondary',
                    onClick: () => {
                        this.close();
                        resolve(false);
                    }
                },
                {
                    text: `Increase to ${data.suggested_quota.toLocaleString()}`,
                    style: 'primary',
                    onClick: () => {
                        this.close();
                        resolve(true);
                    }
                }
            ]);
            this.show(modal);
        });
    }

    /**
     * Show success modal
     */
    success(title, message) {
        return this.alert(title, message, '✅');
    }

    /**
     * Show error modal
     */
    error(title, message) {
        return this.alert(title, message, '❌');
    }

    /**
     * Create modal HTML
     */
    createModal(title, message, icon, buttons) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow: auto;
            animation: slideIn 0.3s ease-out;
        `;

        // Header
        const header = document.createElement('div');
        header.style.cssText = `
            padding: 24px 24px 16px 24px;
            border-bottom: 1px solid #e5e7eb;
        `;

        if (icon) {
            const iconEl = document.createElement('div');
            iconEl.style.cssText = `
                font-size: 48px;
                text-align: center;
                margin-bottom: 16px;
            `;
            iconEl.textContent = icon;
            header.appendChild(iconEl);
        }

        const titleEl = document.createElement('h3');
        titleEl.style.cssText = `
            margin: 0;
            font-size: 20px;
            font-weight: 600;
            color: #111827;
            text-align: center;
        `;
        titleEl.textContent = title;
        header.appendChild(titleEl);

        // Body
        const body = document.createElement('div');
        body.style.cssText = `
            padding: 24px;
            color: #374151;
            font-size: 15px;
        `;
        body.innerHTML = message;

        // Footer
        const footer = document.createElement('div');
        footer.style.cssText = `
            padding: 16px 24px 24px 24px;
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        `;

        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.textContent = btn.text;
            button.onclick = btn.onClick;

            if (btn.style === 'primary') {
                button.style.cssText = `
                    padding: 10px 20px;
                    background: #047857;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background 0.2s;
                `;
                button.onmouseover = () => button.style.background = '#065f46';
                button.onmouseout = () => button.style.background = '#047857';
            } else {
                button.style.cssText = `
                    padding: 10px 20px;
                    background: #e5e7eb;
                    color: #374151;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background 0.2s;
                `;
                button.onmouseover = () => button.style.background = '#d1d5db';
                button.onmouseout = () => button.style.background = '#e5e7eb';
            }

            footer.appendChild(button);
        });

        modal.appendChild(header);
        modal.appendChild(body);
        modal.appendChild(footer);

        return modal;
    }

    /**
     * Show modal
     */
    show(modalContent) {
        this.modalContainer.innerHTML = '';
        this.modalContainer.appendChild(modalContent);
        this.modalContainer.style.display = 'flex';

        // Close on backdrop click
        this.modalContainer.onclick = (e) => {
            if (e.target === this.modalContainer) {
                this.close();
            }
        };

        // Add animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideIn {
                from {
                    transform: translateY(-20px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
        `;
        if (!document.getElementById('customModalStyles')) {
            style.id = 'customModalStyles';
            document.head.appendChild(style);
        }
    }

    /**
     * Close modal
     */
    close() {
        if (this.modalContainer) {
            this.modalContainer.style.display = 'none';
            this.modalContainer.innerHTML = '';
        }
    }
}

// Create global instance
window.customModal = new CustomModal();

// Convenience functions
window.showAlert = (title, message, icon) => window.customModal.alert(title, message, icon);
window.showConfirm = (title, message, icon, options) => window.customModal.confirm(title, message, icon, options);
window.showSuccess = (title, message) => window.customModal.success(title, message);
window.showError = (title, message) => window.customModal.error(title, message);
