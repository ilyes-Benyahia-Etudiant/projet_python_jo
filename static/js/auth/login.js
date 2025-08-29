document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const payload = {
      email: formData.get('email'),
      password: formData.get('password'),
    };
    try {
      const res = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        credentials: 'same-origin',
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        showToast(data.detail || 'Échec de la connexion', true);
        return;
      }
      if (data.redirect_url) {
        window.location.href = data.redirect_url; // admin -> /admin/, user -> /user/
      } else {
        showToast('Connexion réussie !');
        window.location.href = '/user/';
      }
    } catch (err) {
      showToast('Erreur réseau', true);
    }
  });
});