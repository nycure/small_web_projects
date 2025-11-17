// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    initializeLogin();
    addEventListeners();
    createNetworkConnections();
});

// Initialize login functionality
function initializeLogin() {
    const form = document.querySelector('.login-form');
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    
    // Add input validation
    inputs.forEach(input => {
        input.addEventListener('input', validateInput);
        input.addEventListener('blur', validateInput);
    });
    
    // Form submission
    form.addEventListener('submit', handleFormSubmit);
}

// Add event listeners
function addEventListeners() {
    // Password toggle functionality
    const passwordToggle = document.querySelector('.password-toggle');
    if (passwordToggle) {
        passwordToggle.addEventListener('click', function(e) {
            e.preventDefault();
            togglePassword();
        });
    }
    
    // Remember me functionality
    const rememberCheckbox = document.querySelector('input[name="remember"]');
    if (rememberCheckbox) {
        // Load saved username if remember me was checked
        const savedUsername = localStorage.getItem('rememberedUsername');
        if (savedUsername) {
            document.getElementById('username').value = savedUsername;
            rememberCheckbox.checked = true;
        }
    }
    
    // Add floating label effect
    addFloatingLabelEffect();
}

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggle-icon');
    
    if (!passwordInput || !toggleIcon) {
        console.error('Password input or toggle icon not found');
        return;
    }
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        toggleIcon.className = 'fas fa-eye';
    }
}

// Validate input fields
function validateInput(event) {
    const input = event.target;
    const value = input.value.trim();
    
    // Remove existing validation classes
    input.classList.remove('valid', 'invalid');
    
    if (value === '') {
        return;
    }
    
    // Username validation
    if (input.name === 'username') {
        if (value.length >= 3) {
            input.classList.add('valid');
        } else {
            input.classList.add('invalid');
        }
    }
    
    // Password validation
    if (input.name === 'password') {
        if (value.length >= 6) {
            input.classList.add('valid');
        } else {
            input.classList.add('invalid');
        }
    }
}

// Handle form submission
function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitButton = form.querySelector('.login-btn');
    
    // Get form values
    const username = formData.get('username');
    const password = formData.get('password');
    const remember = formData.get('remember');
    
    // Validate required fields
    if (!username || !password) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    // Add loading state
    submitButton.classList.add('loading');
    submitButton.disabled = true;
    
    // Handle remember me
    if (remember) {
        localStorage.setItem('rememberedUsername', username);
    } else {
        localStorage.removeItem('rememberedUsername');
    }
    
    // Simulate login attempt (replace with actual login logic)
    setTimeout(() => {
        // Remove loading state
        submitButton.classList.remove('loading');
        submitButton.disabled = false;
        
        // Demo credentials for testing
        if (username === 'admin' && password === 'admin123') {
            showNotification('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                // Redirect to router dashboard
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            showNotification('Invalid username or password', 'error');
            // Add shake animation to form
            document.querySelector('.login-card').classList.add('shake');
            setTimeout(() => {
                document.querySelector('.login-card').classList.remove('shake');
            }, 500);
        }
    }, 2000);
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    // Add notification to page
    document.body.appendChild(notification);
    
    // Add close functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Get notification icon based on type
function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

// Add floating label effect
function addFloatingLabelEffect() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentNode.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            if (input.value === '') {
                input.parentNode.classList.remove('focused');
            }
        });
        
        // Check if input has value on page load
        if (input.value !== '') {
            input.parentNode.classList.add('focused');
        }
    });
}

// Create animated network connections
function createNetworkConnections() {
    const container = document.querySelector('.network-animation');
    const nodes = document.querySelectorAll('.node');
    
    // Create SVG for connection lines
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.style.position = 'absolute';
    svg.style.top = '0';
    svg.style.left = '0';
    svg.style.width = '100%';
    svg.style.height = '100%';
    svg.style.pointerEvents = 'none';
    svg.style.zIndex = '-1';
    
    container.appendChild(svg);
    
    // Animate connections between nodes
    function animateConnections() {
        // Clear existing lines
        svg.innerHTML = '';
        
        // Connect random pairs of nodes
        for (let i = 0; i < nodes.length - 1; i++) {
            if (Math.random() > 0.7) { // 30% chance of connection
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                const node1 = nodes[i];
                const node2 = nodes[i + 1];
                
                const rect1 = node1.getBoundingClientRect();
                const rect2 = node2.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                
                line.setAttribute('x1', rect1.left - containerRect.left + 4);
                line.setAttribute('y1', rect1.top - containerRect.top + 4);
                line.setAttribute('x2', rect2.left - containerRect.left + 4);
                line.setAttribute('y2', rect2.top - containerRect.top + 4);
                line.setAttribute('stroke', 'rgba(255, 255, 255, 0.2)');
                line.setAttribute('stroke-width', '1');
                line.style.opacity = '0';
                line.style.transition = 'opacity 0.5s ease';
                
                svg.appendChild(line);
                
                // Fade in line
                setTimeout(() => {
                    line.style.opacity = '1';
                }, 100);
                
                // Fade out line
                setTimeout(() => {
                    line.style.opacity = '0';
                }, 2000);
            }
        }
    }
    
    // Start animation
    setInterval(animateConnections, 3000);
}

// Utility function to detect mobile devices
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Add shake animation keyframes
const shakeKeyframes = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    .shake {
        animation: shake 0.5s ease-in-out;
    }
`;

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1000;
        min-width: 300px;
        transform: translateX(100%);
        animation: slideInRight 0.3s ease-out forwards;
    }
    
    .notification.success {
        border-left: 4px solid #48bb78;
        color: #2d3748;
    }
    
    .notification.error {
        border-left: 4px solid #f56565;
        color: #2d3748;
    }
    
    .notification.warning {
        border-left: 4px solid #ed8936;
        color: #2d3748;
    }
    
    .notification.info {
        border-left: 4px solid #4299e1;
        color: #2d3748;
    }
    
    .notification i {
        font-size: 18px;
    }
    
    .notification.success i {
        color: #48bb78;
    }
    
    .notification.error i {
        color: #f56565;
    }
    
    .notification.warning i {
        color: #ed8936;
    }
    
    .notification.info i {
        color: #4299e1;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        color: #a0aec0;
        margin-left: auto;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .notification-close:hover {
        color: #2d3748;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    /* Input validation styles */
    .input-wrapper input.valid {
        border-color: #48bb78;
        box-shadow: 0 0 0 3px rgba(72, 187, 120, 0.1);
    }
    
    .input-wrapper input.invalid {
        border-color: #f56565;
        box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.1);
    }
`;

// Inject styles into head
const styleSheet = document.createElement('style');
styleSheet.textContent = shakeKeyframes + notificationStyles;
document.head.appendChild(styleSheet);

// Initialize network status monitoring
function initializeNetworkMonitoring() {
    function updateNetworkStatus() {
        const statusElement = document.querySelector('.device-info .info-item span');
        if (navigator.onLine) {
            statusElement.textContent = 'Router Status: Online';
            statusElement.style.color = '#48bb78';
        } else {
            statusElement.textContent = 'Router Status: Offline';
            statusElement.style.color = '#f56565';
        }
    }
    
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
    updateNetworkStatus();
}

// Initialize on load
window.addEventListener('load', initializeNetworkMonitoring);

// Make togglePassword available globally for debugging
window.togglePassword = togglePassword;
