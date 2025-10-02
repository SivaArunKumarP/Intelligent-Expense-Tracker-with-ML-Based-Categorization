// JavaScript for Progress Bar Animation and Success Animation
document.addEventListener("DOMContentLoaded", function() {
    // Initialize slogan animation
    setupSlogans();
    
    // Set up form step navigation
    const form = document.getElementById('registerForm');
    const progressConnector = document.getElementById('progress-connector');
    const mainContainer = document.getElementById('main-container');
    const successContainer = document.getElementById('success-container');
    const progressSteps = document.querySelectorAll('.progress-step');
    
    // Update progress bar width based on current step
    function updateProgressBar(step) {
        const connectorWidths = ['33%', '66%', '100%'];
        progressConnector.style.width = connectorWidths[step - 1];
        
        // Add animation
        progressConnector.style.transition = 'width 0.4s ease';
    }
    
    // Update progress steps with animation
    function updateProgressSteps(step) {
        progressSteps.forEach(stepEl => {
            const stepNum = parseInt(stepEl.getAttribute('data-step'));
            stepEl.classList.remove('active', 'completed');
            
            if (stepNum === step) {
                stepEl.classList.add('active');
                // Add glow effect for current step
                stepEl.style.boxShadow = '0 0 10px rgba(0, 200, 150, 0.5)';
            } else if (stepNum < step) {
                stepEl.classList.add('completed');
                stepEl.style.boxShadow = 'none';
            } else {
                stepEl.style.boxShadow = 'none';
            }
        });
    }
    
    // Navigate to specific step with animation
    function goToStep(step) {
        const formSteps = document.querySelectorAll('.form-step');
        
        // First animate current step out
        formSteps.forEach(formStep => {
            if (formStep.classList.contains('active')) {
                formStep.style.opacity = '0';
                formStep.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    formStep.classList.remove('active');
                    
                    // Then animate new step in
                    document.getElementById(`step-${step}`).classList.add('active');
                    setTimeout(() => {
                        document.getElementById(`step-${step}`).style.opacity = '1';
                        document.getElementById(`step-${step}`).style.transform = 'translateX(0)';
                    }, 50);
                    
                }, 300);
            }
        });
        
        updateProgressBar(step);
        updateProgressSteps(step);
    }
    
    // Validate inputs in a step
    function validateStep(step) {
        let isValid = true;
        const formStep = document.getElementById(`step-${step}`);
        
        // Reset all error messages
        formStep.querySelectorAll('.error').forEach(error => {
            error.textContent = '';
            error.classList.remove('visible');
        });
        
        // Validation logic for each step (unchanged from reference)
        // Step 1 validation
        if (step === 1) {
            const firstName = document.getElementById('first_name');
            const lastName = document.getElementById('last_name');
            
            if (!firstName.value.trim()) {
                showError('firstNameError', 'First name is required');
                isValid = false;
            }
            
            if (!lastName.value.trim()) {
                showError('lastNameError', 'Last name is required');
                isValid = false;
            }
        }
        
        // Step 2 validation
        if (step === 2) {
            const username = document.getElementById('username');
            const email = document.getElementById('email');
            const phone = document.getElementById('phone');
            
            if (!username.value.trim()) {
                showError('usernameError', 'Username is required');
                isValid = false;
            }
            
            if (!email.value.trim()) {
                showError('emailError', 'Email is required');
                isValid = false;
            } else if (!isValidEmail(email.value)) {
                showError('emailError', 'Please enter a valid email');
                isValid = false;
            }
            
            if (!phone.value.trim()) {
                showError('phoneError', 'Phone number is required');
                isValid = false;
            }
        }
        
        // Step 3 validation
        if (step === 3) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (!password.value) {
                showError('passwordError', 'Password is required');
                isValid = false;
            } else if (password.value.length < 6) {
                showError('passwordError', 'Password must be at least 6 characters');
                isValid = false;
            }
            
            if (!confirmPassword.value) {
                showError('confirmPasswordError', 'Please confirm your password');
                isValid = false;
            } else if (password.value !== confirmPassword.value) {
                showError('confirmPasswordError', 'Passwords do not match');
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    // Show error message with animation
    function showError(errorId, message) {
        const errorElement = document.getElementById(errorId);
        errorElement.textContent = message;
        errorElement.classList.add('visible');
        
        // Add shake animation to the input
        const inputField = errorElement.previousElementSibling;
        if (inputField && inputField.tagName === 'INPUT') {
            inputField.classList.add('shake');
            setTimeout(() => {
                inputField.classList.remove('shake');
            }, 500);
        }
    }
    
    // Validate email format
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Event listeners for navigation buttons with animation
    document.getElementById('next-1').addEventListener('click', function() {
        if (validateStep(1)) {
            goToStep(2);
        }
    });
    
    document.getElementById('prev-2').addEventListener('click', function() {
        goToStep(1);
    });
    
    document.getElementById('next-2').addEventListener('click', function() {
        if (validateStep(2)) {
            goToStep(3);
        }
    });
    
    document.getElementById('prev-3').addEventListener('click', function() {
        goToStep(2);
    });
    
    // Handle form submission
    document.getElementById('register-btn').addEventListener('click', function(e) {
        e.preventDefault();
        
        if (validateStep(3)) {
            // Collect form data
            const formData = new FormData(form);
            
            // Send data to server using fetch API for Flask
            fetch('/register', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Network response was not ok.');
            })
            .then(data => {
                // If registration successful, show animation
                showSuccessAnimation();
            })
            .catch(error => {
                console.error('Error:', error);
                // Handle errors here
            });
        }
    });
    
    // Show success animation
    function showSuccessAnimation() {
        // Hide form with fade out
        form.style.opacity = '0';
        form.style.transform = 'translateY(20px)';
        document.querySelector('.progress-container').style.opacity = '0';
        document.querySelector('h2').style.opacity = '0';
        document.querySelector('.login-link').style.opacity = '0';
        
        setTimeout(() => {
            // Hide elements
            form.style.display = 'none';
            document.querySelector('.progress-container').style.display = 'none';
            document.querySelector('h2').style.display = 'none';
            document.querySelector('.login-link').style.display = 'none';
            
            // Show success container
            successContainer.classList.add('active');
        }, 400);
    }
    
    // Redirect to expense tracker page
    document.getElementById('redirect-btn').addEventListener('click', function() {
        window.location.href = '/dashboard';
    });
    
    // Initialize slogan animation
    function setupSlogans() {
        const slogans = [
            "Track your expenses, secure your future.",
            "Save more, spend wisely.",
            "Budget today, enjoy tomorrow.",
            "Small savings lead to big dreams.",
            "Manage money, master life."
        ];
        
        const sloganContainer = document.getElementById("slogan");
        
        // Create elements for each slogan
        slogans.forEach((text, index) => {
            const sloganElement = document.createElement("div");
            sloganElement.className = "slogan-text" + (index === 0 ? " active" : "");
            sloganElement.textContent = text;
            sloganElement.setAttribute('data-index', index);
            sloganContainer.appendChild(sloganElement);
        });
        
        let currentIndex = 0;
        
        // Rotate slogans at interval
        setInterval(() => {
            const allSlogans = document.querySelectorAll(".slogan-text");
            const currentSlogan = document.querySelector(`.slogan-text[data-index="${currentIndex}"]`);
            
            // Remove active from current, add inactive
            currentSlogan.classList.remove("active");
            currentSlogan.classList.add("inactive");
            
            // Update index
            currentIndex = (currentIndex + 1) % slogans.length;
            
            // Get next slogan and activate it
            const nextSlogan = document.querySelector(`.slogan-text[data-index="${currentIndex}"]`);
            
            // Short delay before showing next slogan
            setTimeout(() => {
                allSlogans.forEach(slogan => {
                    if (slogan !== nextSlogan) {
                        slogan.classList.remove("active");
                        slogan.classList.remove("inactive");
                    }
                });
                
                nextSlogan.classList.add("active");
            }, 400);
        }, 4000);
    }
    
    // Add animation to form fields on focus
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            const label = this.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                label.style.color = 'var(--primary)';
                this.style.transform = 'translateY(-2px)';
            }
        });
        
        input.addEventListener('blur', function() {
            const label = this.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                label.style.color = '';
                this.style.transform = '';
            }
        });
    });
});