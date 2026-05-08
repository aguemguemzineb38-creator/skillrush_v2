# 📋 GUIDE DE DÉBOGAGE - Email et Daily Claim XP

## ⚙️ PART 1: TESTER LA CONFIGURATION EMAIL

### Étape 1: Exécuter le script de test
```bash
cd c:\Users\zineb\Downloads\skillrush_v2
python test_email_config.py
```

**Résultats possibles:**

**✅ Si RÉUSSI**: "CONFIGURATION CORRECTE"
- Les emails devraient fonctionner
- Allez à l'**ÉTAPE 2** pour vérifier Railway

**❌ Si ERREUR**: "VARIABLES D'ENVIRONNEMENT NON DÉFINIES"
- Vous devez configurer les variables d'environnement sur **Railway**

---

## 📡 PART 2: CONFIGURER RAILWAY

### Étape 1: Aller sur Railway
1. Connectez-vous à https://railway.app
2. Cliquez sur votre projet **skillrush_v2**
3. Allez dans **Settings** (⚙️) à droite

### Étape 2: Vérifier les variables d'environnement
Cliquez sur **Variables** et cherchez:

**CONFIGURATION POUR GMAIL (RECOMMANDÉE):**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=votre_email@gmail.com
MAIL_PASSWORD=xxxxxxxxxxxxx  (16 caractères - voir ci-dessous)
MAIL_DEFAULT_SENDER=SkillRush <votre_email@gmail.com>
APP_BASE_URL=https://web-production-skillrush.up.railway.app
```

### Étape 3: Obtenir le mot de passe Gmail
⚠️ **IMPORTANT**: Vous NE POUVEZ PAS utiliser votre mot de passe Gmail normal!

**Créer un "App Password":**
1. Allez sur https://myaccount.google.com/apppasswords
2. Sélectionnez **Mail** et **Windows** (ou votre plateforme)
3. Google génère un mot de passe à 16 caractères
4. Copiez-le dans Railway: `MAIL_PASSWORD=xxxxxxxxxxxxxxxx`

### Étape 4: Redémarrer le service
1. Dans Railway Settings, cliquez sur **Redeploy**
2. Attendez que le service redémarre (5-10 secondes)

---

## 🧪 PART 3: TESTER LOCALEMENT

### Test 1: Vérifier que la configuration est chargée
```bash
python -c "from config import Config; print('MAIL_SERVER:', Config.MAIL_SERVER); print('MAIL_USERNAME:', Config.MAIL_USERNAME)"
```

### Test 2: Tester l'inscription
1. Créez un compte utilisateur
2. Vérifiez que l'email de bienvenue est reçu

### Test 3: Vérifier les logs
Pour voir pourquoi l'email n'est pas envoyé:
```bash
# Si vous avez accès à Railway logs:
# Dans Railway Dashboard → View Logs
# Cherchez les messages avec "[EMAIL]" ou "❌ ERREUR EMAIL"
```

---

## 🎁 PART 4: TESTER LE DAILY CLAIM XP

### Test local dans le navigateur:

1. **Ouvrir DevTools**: `F12` ou `Ctrl+Shift+I`
2. **Aller à Console**
3. **Créer un compte** et vous connecter
4. **Aller au Dashboard**
5. **Cliquer sur "Réclamer le bonus quotidien +100 XP"**
6. **Regarder la Console pour les messages**

**Messages attendus:**
```
[DAILY CLAIM] Début de la fonction claimDailyReward
[DAILY CLAIM] Trouvé 1 boutons et 1 badges
[DAILY CLAIM] Envoi requête POST /user/daily-reward
[DAILY CLAIM] Réponse reçue: status=200
[DAILY CLAIM] Données JSON reçues: {success: true, message: "Récompense quotidienne reçue !", ...}
[DAILY CLAIM] ✅ Succès! XP gagné: 100
[DAILY CLAIM] ✅ Marquage comme réclamé dans l'interface
[DAILY CLAIM] Bouton caché
[DAILY CLAIM] Badge affiché
```

**Si vous voyez une ERREUR:**
```
[DAILY CLAIM] ❌ Aucun bouton trouvé! Vérifiez les sélecteurs
```
→ Cela signifie que les éléments HTML ne sont pas trouvés. Vérifiez que le dashboard.html contient les bonnes classes.

---

## 🐛 TROUBLESHOOTING

### Email ne fonctionne pas

**❌ "MAIL_PASSWORD/SMTP_PASS absent"**
→ Vérifiez Railway Settings → Variables

**❌ "Erreur d'authentification"**
→ Vérifiez le MAIL_PASSWORD est correctement défini
→ Utilisez un App Password Google (16 caractères), pas votre mot de passe normal

**❌ "Connexion refusée"**
→ Vérifiez MAIL_SERVER=smtp.gmail.com
→ Vérifiez MAIL_PORT=587
→ Vérifiez MAIL_USE_TLS=true

**❌ "Emails envoyés mais pas reçus"**
→ Vérifiez le dossier **SPAM**
→ Vérifiez que MAIL_DEFAULT_SENDER a un vrai email Gmail
→ Vous devrez peut-être autoriser les "Appareils moins sécurisés" dans Google

---

### Daily Claim XP ne se met pas à jour

**❌ "Bouton ne change pas de couleur"**
→ Ouvrez DevTools (F12)
→ Regardez les messages [DAILY CLAIM]
→ Si vous voyez "Aucun bouton trouvé" → Vérifiez le HTML

**❌ "La page se recharge après chaque claim"**
→ Le code a été corrigé pour ne plus recharger
→ Videz le cache du navigateur (Ctrl+Shift+Delete)
→ Rechargez la page

**✅ Comportement normal après le fix:**
- Cliquez sur le bouton
- Le bouton devient "Réclamation..." avec un spinner
- Le badge "Bonus quotidien déjà récupéré" s'affiche
- Une notification de succès "+100 XP" apparaît
- **PAS DE RECHARGEMENT DE PAGE**

---

## 📝 CHECKLIST FINALE

- [ ] Variables d'environnement configurées sur Railway
- [ ] `python test_email_config.py` retourne "CONFIGURATION CORRECTE"
- [ ] Un utilisateur s'inscrit et reçoit l'email de bienvenue
- [ ] Console DevTools montre "[DAILY CLAIM] ✅ Succès!"
- [ ] Le bouton Daily Claim disparaît sans rechargement de page
- [ ] Un modérateur approuve une compétence → l'auteur reçoit l'email
- [ ] Un modérateur refuse une compétence → l'auteur reçoit l'email

---

## 🆘 BESOIN D'AIDE?

1. **Consultez les logs Railway**: Settings → View Logs → Cherchez "ERROR" ou "EMAIL"
2. **Testez la connexion SMTP**: `python test_email_config.py`
3. **Ouvrez DevTools**: F12 → Console → Cherchez les messages [DAILY CLAIM]
4. **Redéployez**: Railway Dashboard → Redeploy

---

## 📚 RESSOURCES

- Google App Passwords: https://myaccount.google.com/apppasswords
- Railway Documentation: https://docs.railway.app/
- Flask-Mail: https://flask-mail.readthedocs.io/
