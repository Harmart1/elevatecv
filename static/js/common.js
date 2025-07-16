// This file contains common JavaScript functions used across the site.

// --- Reusable Login Handler ---
function handleLoginForm(formId, redirectUrl, adminOnly = false) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const usernameOrEmail = form.querySelector('input[type="text"], input[type="email"]').value;
        const password = form.querySelector('input[type="password"]').value;
        const messageDiv = document.getElementById('form-message');
        const submitBtn = form.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnSpinner = submitBtn.querySelector('.btn-spinner');

        // Reset message and show spinner
        messageDiv.textContent = '';
        messageDiv.className = 'mt-4 text-center text-sm';
        btnText.classList.add('hidden');
        btnSpinner.classList.remove('hidden');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: usernameOrEmail, username: usernameOrEmail, password: password })
            });

            const data = await response.json();

            if (response.ok) {
                if (adminOnly && data.user.role !== 'admin') {
                    throw new Error('Access denied. Administrator privileges required.');
                }
                localStorage.setItem('elevateCVToken', data.token);
                messageDiv.textContent = 'Login successful! Redirecting...';
                messageDiv.classList.add('text-green-600');
                window.location.href = redirectUrl;
            } else {
                throw new Error(data.message || 'An error occurred.');
            }
        } catch (error) {
            messageDiv.textContent = error.message;
            messageDiv.classList.add('text-red-600');
        } finally {
            // Hide spinner and re-enable button
            btnText.classList.remove('hidden');
            btnSpinner.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
}


// --- API Fetch Wrapper with Auth ---
async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('elevateCVToken');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = { ...options, headers };

    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            if (response.status === 401) {
                // Token is invalid or expired
                showNotification('Your session has expired. Please log in again.', 'error');
                localStorage.removeItem('elevateCVToken');
                setTimeout(() => window.location.href = '/login.html', 3000);
            }
            const errorData = await response.json();
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}


// --- Notification System ---
function showNotification(message, type = 'info', duration = 5000) {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
    }

    const notification = document.createElement('div');
    const icons = {
        success: 'fa-check-circle', error: 'fa-times-circle', info: 'fa-info-circle'
    };
    const colors = {
        success: 'green', error: 'red', info: 'blue'
    };

    notification.className = `notification border-${colors[type]}-500`;
    notification.innerHTML = `
        <i class="fas ${icons[type]} text-${colors[type]}-500"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    if (duration > 0) {
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 500);
        }, duration);
    }
}

// Ensure common CSS for notifications is available
document.head.insertAdjacentHTML('beforeend', `
<style>
#notification-container { position: fixed; top: 20px; right: 20px; z-index: 9999; }
.notification { display: flex; align-items: center; gap: 1rem; background: white; color: #333; padding: 1rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-left-width: 4px; margin-bottom: 1rem; transform: translateX(120%); transition: transform 0.5s ease-in-out; }
.notification.show { transform: translateX(0); }
.notification button { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999; }
</style>
`);
