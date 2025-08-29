document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.getElementById('logoutBtn');
  const userInfo = document.getElementById('userInfo');

  async function loadMe() {
    try {
      const res = await fetch('/api/auth/me/', {
        method: 'GET',
        credentials: 'same-origin',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
      });
      if (res.status === 401 || res.status === 403) {
        window.location.href = '/login/';
        return;
      }
      const data = await res.json();
      if (userInfo) {
        userInfo.innerHTML = `
          <p><strong>Identifiant:</strong> ${data.id}</p>
          <p><strong>Nom d'utilisateur:</strong> ${data.username}</p>
          <p><strong>Email:</strong> ${data.email || '(non fourni)'}</p>
          <p><strong>Rôle:</strong> ${data.is_staff ? 'Administrateur' : 'Utilisateur'}</p>
        `;
      }
    } catch (e) {
      showToast('Erreur lors du chargement des informations.', true);
    }
  }

  async function logout() {
    try {
      const res = await fetch('/api/auth/logout/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      });
      const data = await res.json();
      if (!res.ok) {
        showToast(data.detail || 'Erreur lors de la déconnexion', true);
        return;
      }
      showToast('Déconnexion réussie');
      setTimeout(() => window.location.href = '/', 500);
    } catch (e) {
      showToast('Erreur réseau', true);
    }
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  loadMe();
});