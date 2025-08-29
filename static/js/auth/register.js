document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');

    // Optionnel: s'assurer que le cookie CSRF est bien présent
    fetch('/api/auth/csrf/', { credentials: 'same-origin' }).catch(() => {});

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password'),
            password_confirm: formData.get('password_confirm')
        };

        try {
            const response = await fetch('/api/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'same-origin', // <-- important: inclut les cookies
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                showToast('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success');
                setTimeout(() => {
                    window.location.href = '/login/';
                }, 1500);
            } else {
                // Afficher proprement les erreurs
                displayFormErrors(result);
            }
        } catch (error) {
            console.error('Erreur:', error);
            showToast('Erreur de connexion au serveur', 'error');
        }
    });

    function displayFormErrors(errors) {
        // Effacer les anciennes erreurs
        clearFormErrors();
        
        // Afficher les erreurs spécifiques à chaque champ
        if (errors.username) {
            showFieldError('username', errors.username);
        }
        if (errors.email) {
            showFieldError('email', errors.email);
        }
        if (errors.password) {
            showFieldError('password', errors.password);
        }
        if (errors.password_confirm) {
            showFieldError('password_confirm', errors.password_confirm);
        }
        if (errors.non_field_errors) {
            showToast(errors.non_field_errors.join(', '), 'error');
        }
    }

    function showFieldError(fieldName, errorMessages) {
        const field = document.getElementById(fieldName);
        const errorText = Array.isArray(errorMessages) ? errorMessages.join(', ') : errorMessages;
        
        // Ajouter la classe d'erreur au champ
        field.classList.add('is-invalid');
        
        // Créer ou mettre à jour le message d'erreur
        let errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = errorText;
    }

    function clearFormErrors() {
        // Supprimer toutes les classes d'erreur et messages
        const errorFields = form.querySelectorAll('.is-invalid');
        errorFields.forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        const errorMessages = form.querySelectorAll('.invalid-feedback');
        errorMessages.forEach(msg => {
            msg.remove();
        });
    }
});