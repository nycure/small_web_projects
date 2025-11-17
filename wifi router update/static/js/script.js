// Password toggle functionality
function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const eyeIcon = document.getElementById(fieldId === 'password' ? 'passwordEye' : 'confirmPasswordEye');
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        eyeIcon.className = 'fas fa-eye-slash';
    } else {
        passwordField.type = 'password';
        eyeIcon.className = 'fas fa-eye';
    }
}

// Form validation and submission
document.addEventListener('DOMContentLoaded', function() {
    const upgradeForm = document.getElementById('upgradeForm');
    const upgradeBtn = document.getElementById('upgradeBtn');
    const errorMessage = document.getElementById('errorMessage');
    
    // Real-time password validation
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    
    function validatePasswords() {
        const password = passwordField.value;
        const confirmPassword = confirmPasswordField.value;
        
        // Clear previous error styling
        passwordField.style.borderColor = '';
        confirmPasswordField.style.borderColor = '';
        errorMessage.style.display = 'none';
        
        if (password && confirmPassword) {
            if (password !== confirmPassword) {
                confirmPasswordField.style.borderColor = '#dc3545';
                showError('Passwords do not match');
                return false;
            } else {
                confirmPasswordField.style.borderColor = '#28a745';
                passwordField.style.borderColor = '#28a745';
            }
        }
        
        if (password && password.length < 8) {
            passwordField.style.borderColor = '#dc3545';
            showError('Password must be at least 8 characters long');
            return false;
        }
        
        return true;
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
    
    function hideError() {
        errorMessage.style.display = 'none';
    }
    
    // Add event listeners for real-time validation
    passwordField.addEventListener('input', validatePasswords);
    confirmPasswordField.addEventListener('input', validatePasswords);
    
    // Handle form submission
    upgradeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const password = passwordField.value;
        const confirmPassword = confirmPasswordField.value;
        const acknowledge = document.getElementById('acknowledge').checked;
        
        // Validate form
        if (!password || !confirmPassword) {
            showError('Please fill in all required fields');
            return;
        }
        
        if (!acknowledge) {
            showError('Please acknowledge the risks before proceeding');
            return;
        }
        
        if (!validatePasswords()) {
            return;
        }
        
        // Disable form and show loading state
        upgradeBtn.disabled = true;
        upgradeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting Upgrade...';
        hideError();
        
        // Submit form data
        const formData = new FormData();
        formData.append('password', password);
        formData.append('confirm_password', confirmPassword);
        
        fetch('/upgrade', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to upgrade progress page
                window.location.href = '/upgrading';
            } else {
                // Show error message
                showError(data.message);
                upgradeBtn.disabled = false;
                upgradeBtn.innerHTML = '<i class="fas fa-arrow-circle-up"></i> Start Firmware Upgrade';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while starting the upgrade. Please try again.');
            upgradeBtn.disabled = false;
            upgradeBtn.innerHTML = '<i class="fas fa-arrow-circle-up"></i> Start Firmware Upgrade';
        });
    });
    
    // Add some interactive effects
    const formInputs = document.querySelectorAll('input');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
    
    // Add hover effects to the upgrade card
    const upgradeCard = document.querySelector('.upgrade-card');
    upgradeCard.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
    });
    
    upgradeCard.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
    
    // Animate elements on page load
    setTimeout(() => {
        const elements = document.querySelectorAll('.form-group');
        elements.forEach((element, index) => {
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }, 300);
    
    // Initialize form group animations
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        group.style.opacity = '0';
        group.style.transform = 'translateY(20px)';
        group.style.transition = 'all 0.3s ease';
    });
});

// Prevent form submission on Enter key in password fields (except when on upgrade button)
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        const activeElement = document.activeElement;
        if (activeElement.type === 'password') {
            e.preventDefault();
            // Move to next field or submit if on last field
            const form = activeElement.closest('form');
            const formElements = Array.from(form.querySelectorAll('input, button'));
            const currentIndex = formElements.indexOf(activeElement);
            
            if (currentIndex < formElements.length - 1) {
                formElements[currentIndex + 1].focus();
            } else {
                // On last element, submit form
                form.dispatchEvent(new Event('submit'));
            }
        }
    }
});

// Add some security-focused messaging
window.addEventListener('beforeunload', function(e) {
    const upgradeBtn = document.getElementById('upgradeBtn');
    if (upgradeBtn && upgradeBtn.disabled) {
        e.preventDefault();
        e.returnValue = 'Firmware upgrade is in progress. Leaving this page may interrupt the process.';
        return e.returnValue;
    }
});

// Add progress indication for password strength
function checkPasswordStrength(password) {
    let strength = 0;
    const checks = [
        { regex: /.{8,}/, message: 'At least 8 characters' },
        { regex: /[A-Z]/, message: 'Contains uppercase letter' },
        { regex: /[a-z]/, message: 'Contains lowercase letter' },
        { regex: /[0-9]/, message: 'Contains number' },
        { regex: /[^A-Za-z0-9]/, message: 'Contains special character' }
    ];
    
    checks.forEach(check => {
        if (check.regex.test(password)) {
            strength++;
        }
    });
    
    return {
        score: strength,
        level: strength < 2 ? 'weak' : strength < 4 ? 'medium' : 'strong'
    };
}
