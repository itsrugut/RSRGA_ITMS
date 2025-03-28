document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registration-form');
    const passwordInput = document.getElementById('id_password1');
    const confirmPasswordInput = document.getElementById('id_password2');

    const requirements = {
        length: /.{8,}/,
        uppercase: /[A-Z]/,
        lowercase: /[a-z]/,
        digit: /\d/,
        special: /[!@#$%^&*()-+?_=,<>/]/
    };

    function updateRequirements() {
        const password = passwordInput.value;
        for (let req in requirements) {
            const li = document.getElementById(req);
            if (requirements[req].test(password)) {
                li.style.color = 'green';
            } else {
                li.style.color = 'red';
            }
        }
    }

    passwordInput.addEventListener('input', updateRequirements);

    form.addEventListener('submit', function(e) {
        const username = document.getElementById('id_username').value;
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (!username || !password || !confirmPassword) {
            e.preventDefault();
            alert('Please fill in all fields');
        } else if (password !== confirmPassword) {
            e.preventDefault();
            alert('Passwords do not match');
        } else {
            let requirementsMet = true;
            for (let req in requirements) {
                if (!requirements[req].test(password)) {
                    requirementsMet = false;
                    break;
                }
            }
            if (!requirementsMet) {
                e.preventDefault();
                alert('Password does not meet all requirements');
            }
        }
    });
});