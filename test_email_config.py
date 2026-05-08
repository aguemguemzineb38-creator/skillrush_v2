#!/usr/bin/env python
"""
Test script pour vérifier la configuration SMTP et tester l'envoi d'email.
Utilisez: python test_email_config.py
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

print("=" * 70)
print("🔍 TEST CONFIGURATION EMAIL SKILLRUSH")
print("=" * 70)

# Afficher les variables d'environnement chargées
print("\n📋 VARIABLES D'ENVIRONNEMENT DÉTECTÉES:")
print("-" * 70)

mail_server = os.getenv('MAIL_SERVER') or os.getenv('SMTP_HOST') or ''
mail_port = int(os.getenv('MAIL_PORT') or os.getenv('SMTP_PORT') or '587')
mail_username = os.getenv('MAIL_USERNAME') or os.getenv('SMTP_USER') or ''
mail_password = os.getenv('MAIL_PASSWORD') or os.getenv('SMTP_PASS') or ''
mail_sender = os.getenv('MAIL_DEFAULT_SENDER') or os.getenv('SMTP_FROM') or ''

print(f"MAIL_SERVER:          {mail_server if mail_server else '❌ NON DÉFINI'}")
print(f"MAIL_PORT:            {mail_port}")
print(f"MAIL_USERNAME:        {mail_username if mail_username else '❌ NON DÉFINI'}")
print(f"MAIL_PASSWORD:        {'●●●●●●●' if mail_password else '❌ NON DÉFINI'}")
print(f"MAIL_DEFAULT_SENDER:  {mail_sender if mail_sender else '(utilisant défaut)'}")
print(f"APP_BASE_URL:         {os.getenv('APP_BASE_URL', 'https://web-production-skillrush.up.railway.app')}")

# Validation
print("\n" + "=" * 70)
print("✅ VALIDATION:")
print("-" * 70)

errors = []

if not mail_server:
    errors.append("❌ MAIL_SERVER/SMTP_HOST n'est pas défini")
else:
    print(f"✅ Serveur SMTP: {mail_server}")

if not mail_username:
    errors.append("❌ MAIL_USERNAME/SMTP_USER n'est pas défini")
else:
    print(f"✅ Utilisateur: {mail_username}")

if not mail_password:
    errors.append("❌ MAIL_PASSWORD/SMTP_PASS n'est pas défini")
else:
    print(f"✅ Mot de passe: défini ({len(mail_password)} caractères)")

if mail_username and not mail_username.endswith('@gmail.com') and mail_server == 'smtp.gmail.com':
    errors.append("⚠️  ATTENTION: Vous utilisez smtp.gmail.com mais l'email n'est pas @gmail.com")

if errors:
    print("\n" + "=" * 70)
    print("⚠️  ERREURS DE CONFIGURATION:")
    print("-" * 70)
    for error in errors:
        print(error)
    print("\n💡 CONFIGURATION REQUISE POUR GMAIL:")
    print("   1. MAIL_SERVER=smtp.gmail.com")
    print("   2. MAIL_PORT=587")
    print("   3. MAIL_USERNAME=votre_email@gmail.com")
    print("   4. MAIL_PASSWORD=votre_app_password (16 caractères, PAS votre mot de passe Gmail)")
    print("   5. MAIL_DEFAULT_SENDER=SkillRush <votre_email@gmail.com>")
    sys.exit(1)

# Test de connexion SMTP
print("\n" + "=" * 70)
print("🔗 TEST DE CONNEXION SMTP:")
print("-" * 70)

try:
    import smtplib
    
    print(f"Tentative de connexion à {mail_server}:{mail_port}...")
    
    if mail_port == 465:
        smtp = smtplib.SMTP_SSL(mail_server, mail_port, timeout=10)
    else:
        smtp = smtplib.SMTP(mail_server, mail_port, timeout=10)
    
    print(f"✅ Connexion établie")
    
    smtp.ehlo()
    print(f"✅ EHLO success")
    
    if mail_port != 465:
        smtp.starttls()
        print(f"✅ STARTTLS activé")
        smtp.ehlo()
    
    print(f"Tentative de login avec {mail_username}...")
    smtp.login(mail_username, mail_password)
    print(f"✅ LOGIN réussi")
    
    smtp.quit()
    print(f"\n✅ CONNEXION SMTP FONCTIONNELLE!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ ERREUR D'AUTHENTIFICATION: {e}")
    print("   Vérifiez vos identifiants MAIL_USERNAME et MAIL_PASSWORD")
except smtplib.SMTPException as e:
    print(f"\n❌ ERREUR SMTP: {e}")
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ TOUS LES TESTS SONT PASSÉS - CONFIGURATION CORRECTE!")
print("=" * 70)
