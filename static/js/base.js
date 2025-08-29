// Fonctions utilitaires globales disponibles sur toutes les pages

// Récupère un cookie par son nom (ex: 'csrftoken')
function getCookie(name) {
  return document.cookie.split('; ').find(row => row.startsWith(name + '='))?.split('=')[1];
}

// Affiche un toast simple (succès/erreur). Requiert un <div class="toast"> dans la page.
function showToast(message, isError = false) {
  const el = document.querySelector('.toast');
  if (!el) return;
  el.textContent = message;
  el.classList.toggle('error', !!isError);
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 3000);
}