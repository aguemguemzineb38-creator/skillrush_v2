// SkillRush - JavaScript principal

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips Bootstrap
    initializeTooltips();
    
    // Vérifier les connexions d'utilisateur
    checkUserAuth();
    
    // Initialiser les animations
    initializeAnimations();
});

/**
 * Initialiser les tooltips Bootstrap
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Vérifier l'authentification
 */
function checkUserAuth() {
    // Vérifier si connecté via le header
    const isAuth = document.querySelector('[data-user-id]');
    if (!isAuth) {
        console.log('Utilisateur non authentifié');
    }
}

/**
 * Initialiser les animations
 */
function initializeAnimations() {
    // Observer les éléments pour les animations au scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    // Masquer après 5 secondes
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Gagner de l'XP (AJAX)
 */
function earnXP(amount) {
    const message = `+${amount} XP gagnés !`;
    showNotification(message, 'info');
    updateUserStats();
}

/**
 * Mettre à jour les statistiques utilisateur
 */
function updateUserStats() {
    // Récupérer les données et mettre à jour via AJAX
    // À implémenter avec un endpoint API
}

/**
 * Commencer une mission
 */
function startMission(missionId) {
    fetch(`/mission/${missionId}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        redirect: 'follow'
    })
    .then(response => {
        // La route redirige vers mission_detail; on y navigue
        window.location.href = `/mission/${missionId}`;
    })
    .catch(error => {
        console.error('Erreur :', error);
        showNotification('Erreur lors du démarrage de la mission', 'danger');
    });
}

/**
 * Compléter une mission
 */
function completeMission(missionId) {
    if (confirm('Êtes-vous sûr d\'avoir complété cette mission ?')) {
        fetch(`/mission/${missionId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            redirect: 'follow'
        })
        .then(response => {
            // La route redirige vers my_progress
            window.location.href = '/user/my-progress';
        })
        .catch(error => {
            console.error('Erreur :', error);
            showNotification('Erreur lors de la complétion de la mission', 'danger');
        });
    }
}

/**
 * Noter une compétence
 */
function rateSkill(skillId) {
    const rating = prompt('Note cette compétence de 1 à 5 étoiles :', '5');
    
    if (rating && rating >= 1 && rating <= 5) {
        fetch(`/skill/${skillId}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                rating: parseInt(rating)
            })
        })
        .then(response => response.json())
        .then(data => {
            const xpEarned = data.xp_earned || 0;
            showNotification(data.message + '\n+' + xpEarned + ' XP gagnés !', 'success');
            earnXP(xpEarned);
        })
        .catch(error => {
            console.error('Erreur :', error);
            showNotification('Erreur lors de la notation', 'danger');
        });
    }
}

/**
 * Recherche en temps réel
 */
function liveSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const results = document.querySelectorAll('.skill-card');
            
            results.forEach(card => {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const description = card.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

/**
 * Filtrer par catégorie
 */
function filterByCategory(category) {
    const cards = document.querySelectorAll('.skill-card');
    
    cards.forEach(card => {
        const cardCategory = card.querySelector('.skill-category-badge').textContent;
        
        if (category === 'all' || cardCategory === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Recevoir une récompense quotidienne
 */
function claimDailyReward() {
    console.log('[DAILY CLAIM] Début de la fonction claimDailyReward');
    
    const claimButtons = Array.from(document.querySelectorAll('[data-daily-claim-btn]'));
    const claimedBadges = Array.from(document.querySelectorAll('[data-daily-claimed-badge]'));

    console.log(`[DAILY CLAIM] Trouvé ${claimButtons.length} boutons et ${claimedBadges.length} badges`);
    
    if (claimButtons.length === 0) {
        console.error('[DAILY CLAIM] ❌ Aucun bouton trouvé! Vérifiez les sélecteurs');
        showNotification('Erreur: Interface non trouvée', 'danger');
        return;
    }

    claimButtons.forEach(button => {
        button.disabled = true;
        if (!button.dataset.originalText) {
            button.dataset.originalText = button.innerHTML;
        }
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Réclamation...';
    });

    const markClaimedInUi = () => {
        console.log('[DAILY CLAIM] ✅ Marquage comme réclamé dans l\'interface');
        claimButtons.forEach(button => {
            button.classList.add('d-none');
            console.log('[DAILY CLAIM] Bouton caché');
        });
        claimedBadges.forEach(badge => {
            badge.classList.remove('d-none');
            console.log('[DAILY CLAIM] Badge affiché');
        });
    };

    const restoreButtons = () => {
        console.log('[DAILY CLAIM] 🔄 Restauration des boutons');
        claimButtons.forEach(button => {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || '<i class="fas fa-gift"></i> Réclamer le bonus quotidien +100 XP';
        });
    };

    console.log('[DAILY CLAIM] Envoi requête POST /user/daily-reward');
    fetch('/user/daily-reward', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => {
        console.log(`[DAILY CLAIM] Réponse reçue: status=${response.status}`);
        if (!response.ok && response.status !== 429) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('[DAILY CLAIM] Données JSON reçues:', data);
        
        if (data.already_claimed) {
            console.log('[DAILY CLAIM] ⚠️ Bonus déjà réclamé');
            markClaimedInUi();
            showNotification(data.error || 'Bonus déjà réclamé aujourd\'hui.', 'info');
            return;
        }

        if (data.error) {
            console.error('[DAILY CLAIM] ❌ Erreur API:', data.error);
            restoreButtons();
            showNotification(data.error, 'warning');
        } else {
            console.log('[DAILY CLAIM] ✅ Succès! XP gagné:', data.xp);
            let msg = `${data.message} +${data.xp} XP`;
            if (data.level_up) msg += ` 🎉 Niveau ${data.new_level}!`;
            showNotification(msg, 'success');
            markClaimedInUi();
        }
    })
    .catch(error => {
        console.error('[DAILY CLAIM] ❌ Erreur réseau/parsing:', error);
        restoreButtons();
        showNotification('Erreur lors de la réclamation de la récompense', 'danger');
    });
}

/**
 * Partager sur les réseaux sociaux
 */
function shareSkill(skillName, skillUrl) {
    const text = `J'apprends "${skillName}" sur SkillRush ! Rejoins-moi !`;
    
    const shareData = {
        title: 'SkillRush',
        text: text,
        url: skillUrl
    };

    if (navigator.share) {
        navigator.share(shareData);
    } else {
        // Fallback - copier dans le presse-papiers
        const link = `${text} ${skillUrl}`;
        navigator.clipboard.writeText(link).then(() => {
            showNotification('Lien copié dans le presse-papiers !', 'info');
        });
    }
}

/**
 * Afficher/masquer les détails
 */
function toggleDetails(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Barre de recherche avec suggestions
 */
function setupSearchSuggestions() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    searchInput.addEventListener('input', async function(e) {
        const query = e.target.value;
        if (query.length < 2) return;

        // À implémenter avec une API de suggestion
        console.log('Searching for:', query);
    });
}

// Initialiser à la charge
window.addEventListener('load', function() {
    liveSearch();
    setupSearchSuggestions();
});
