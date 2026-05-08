"""
Script de migration SkillRush v2 — à lancer UNE SEULE FOIS.
Usage : python migrate_db.py
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'skillrush.db')

def col_exists(cur, table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return col in [r[1] for r in cur.fetchall()]

def table_exists(cur, table):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None

def migrate():
    if not os.path.exists(DB_PATH):
        print("DB introuvable - lancez d'abord 'python run.py'")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    n = 0

    # 1. last_daily_reward
    if not col_exists(cur, 'users', 'last_daily_reward'):
        cur.execute("ALTER TABLE users ADD COLUMN last_daily_reward DATETIME")
        print("Ajout: users.last_daily_reward"); n+=1

    # 2. role
    if not col_exists(cur, 'users', 'role'):
        cur.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
        print("Ajout: users.role"); n+=1

    # 3. is_blocked
    if not col_exists(cur, 'users', 'is_blocked'):
        cur.execute("ALTER TABLE users ADD COLUMN is_blocked BOOLEAN DEFAULT 0")
        print("Ajout: users.is_blocked"); n+=1
    
    # 3c. competence
    if not col_exists(cur, 'users', 'competence'):
        cur.execute("ALTER TABLE users ADD COLUMN competence VARCHAR(120) DEFAULT ''")
        print("Ajout: users.competence"); n+=1

    # 3d. onboarding_done
    if not col_exists(cur, 'users', 'onboarding_done'):
        cur.execute("ALTER TABLE users ADD COLUMN onboarding_done BOOLEAN DEFAULT 0")
        print("Ajout: users.onboarding_done"); n+=1

    # 3e. onboarding_rejected
    if not col_exists(cur, 'users', 'onboarding_rejected'):
        cur.execute("ALTER TABLE users ADD COLUMN onboarding_rejected BOOLEAN DEFAULT 0")
        print("Ajout: users.onboarding_rejected"); n+=1

    # 3f. onboarding_skill_id
    if not col_exists(cur, 'users', 'onboarding_skill_id'):
        cur.execute("ALTER TABLE users ADD COLUMN onboarding_skill_id INTEGER")
        print("Ajout: users.onboarding_skill_id"); n+=1

    # 3g. streak_count
    if not col_exists(cur, 'users', 'streak_count'):
        cur.execute("ALTER TABLE users ADD COLUMN streak_count INTEGER DEFAULT 0")
        print("Ajout: users.streak_count"); n+=1

    # 3h. streak_last_date
    if not col_exists(cur, 'users', 'streak_last_date'):
        cur.execute("ALTER TABLE users ADD COLUMN streak_last_date DATE")
        print("Ajout: users.streak_last_date"); n+=1

    # 3i. profile_daily_bonus_date
    if not col_exists(cur, 'users', 'profile_daily_bonus_date'):
        cur.execute("ALTER TABLE users ADD COLUMN profile_daily_bonus_date DATE")
        print("Ajout: users.profile_daily_bonus_date"); n+=1

    # 4. course_pdf sur skills
    if not col_exists(cur, 'skills', 'course_pdf'):
        cur.execute("ALTER TABLE skills ADD COLUMN course_pdf VARCHAR(500)")
        print("Ajout: skills.course_pdf"); n+=1

    # 4b. is_flagged / is_approved sur skills
    if not col_exists(cur, 'skills', 'is_flagged'):
        cur.execute("ALTER TABLE skills ADD COLUMN is_flagged BOOLEAN DEFAULT 0")
        print("Ajout: skills.is_flagged"); n+=1

    if not col_exists(cur, 'skills', 'is_approved'):
        cur.execute("ALTER TABLE skills ADD COLUMN is_approved BOOLEAN DEFAULT 1")
        print("Ajout: skills.is_approved"); n+=1
    
    # 5. Table xp_purchases
    if not table_exists(cur, 'xp_purchases'):
        cur.execute("""
            CREATE TABLE xp_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                xp_amount INTEGER NOT NULL,
                price_eur REAL NOT NULL,
                stripe_session_id VARCHAR(255),
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME
            )
        """)
        print("Table xp_purchases creee"); n+=1

    # 6. pdf_total_pages sur skills
    if not col_exists(cur, 'skills', 'pdf_total_pages'):
        cur.execute("ALTER TABLE skills ADD COLUMN pdf_total_pages INTEGER DEFAULT 0")
        print("Ajout: skills.pdf_total_pages"); n+=1

    # 7. xp_cost sur videos
    if not col_exists(cur, 'videos', 'xp_cost'):
        cur.execute("ALTER TABLE videos ADD COLUMN xp_cost INTEGER DEFAULT 100")
        print("Ajout: videos.xp_cost"); n+=1

    # 8. Table content_unlocks
    if not table_exists(cur, 'content_unlocks'):
        cur.execute("""
            CREATE TABLE content_unlocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                skill_id INTEGER NOT NULL REFERENCES skills(id),
                content_type VARCHAR(20) NOT NULL,
                content_ref VARCHAR(50) NOT NULL,
                unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX idx_cu_user_skill ON content_unlocks(user_id, skill_id)")
        print("Table content_unlocks creee"); n+=1

    # 9. Table mission_quiz_questions
    if not table_exists(cur, 'mission_quiz_questions'):
        cur.execute("""
            CREATE TABLE mission_quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id INTEGER NOT NULL REFERENCES missions(id),
                question_text TEXT NOT NULL,
                option_a VARCHAR(300) NOT NULL,
                option_b VARCHAR(300) NOT NULL,
                option_c VARCHAR(300) NOT NULL,
                option_d VARCHAR(300) NOT NULL,
                correct_option VARCHAR(1) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX idx_mqq_mission ON mission_quiz_questions(mission_id)")
        print("Table mission_quiz_questions creee"); n+=1

    # 10. Table user_mission_quiz_attempts
    if not table_exists(cur, 'user_mission_quiz_attempts'):
        cur.execute("""
            CREATE TABLE user_mission_quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                mission_id INTEGER NOT NULL REFERENCES missions(id),
                score_10 REAL NOT NULL,
                passed BOOLEAN DEFAULT 0,
                attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX idx_umqa_user_mission ON user_mission_quiz_attempts(user_id, mission_id)")
        print("Table user_mission_quiz_attempts creee"); n+=1

    # 11. Badges system
    if not table_exists(cur, 'badges'):
        cur.execute("""
            CREATE TABLE badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(50) UNIQUE NOT NULL,
                icon VARCHAR(10) NOT NULL,
                name VARCHAR(100) NOT NULL,
                description VARCHAR(255) NOT NULL,
                rarity VARCHAR(20) DEFAULT 'common',
                condition_type VARCHAR(30) NOT NULL,
                condition_value INTEGER DEFAULT 0
            )
        """)
        print("Table badges creee"); n+=1

    # Always seed badges if table is empty
    cur.execute("SELECT count(*) FROM badges")
    if cur.fetchone()[0] == 0:
        badges_data = [
            ('first_mission',  '🎯', 'Premiere Mission',    'Completer sa premiere mission',             'common',   'missions_completed', 1),
            ('streak_3',       '🔥', 'Serie de 3 jours',    'Maintenir un streak de 3 jours consecutifs','common',   'streak',             3),
            ('streak_7',       '🔥🔥','Flamme de la semaine','Maintenir un streak de 7 jours',            'rare',     'streak',             7),
            ('streak_30',      '⚡', 'Mois de feu',          'Maintenir un streak de 30 jours',           'epic',     'streak',             30),
            ('xp_100',         '⚡', 'Club 100 XP',          'Accumuler 100 XP',                          'common',   'xp',                 100),
            ('xp_500',         '💎', 'Club 500 XP',          'Accumuler 500 XP',                          'rare',     'xp',                 500),
            ('xp_1000',        '👑', 'Club 1000 XP',         'Accumuler 1000 XP',                         'epic',     'xp',                 1000),
            ('xp_5000',        '🌟', 'Legende XP',           'Accumuler 5000 XP',                         'legendary','xp',                 5000),
            ('first_skill',    '📚', 'Premier Cours',        'Publier son premier cours',                 'common',   'skills_created',     1),
            ('five_skills',    '🏆', 'Formateur Expert',     'Publier 5 cours',                           'rare',     'skills_created',     5),
            ('five_missions',  '🏅', 'Maitre des Missions',  'Completer 5 missions',                      'rare',     'missions_completed', 5),
            ('ten_missions',   '🎖', 'Champion des Missions','Completer 10 missions',                     'epic',     'missions_completed', 10),
        ]
        cur.executemany(
            "INSERT OR IGNORE INTO badges (key, icon, name, description, rarity, condition_type, condition_value) VALUES (?,?,?,?,?,?,?)",
            badges_data
        )
        print("Badges seedes"); n+=1

    if not table_exists(cur, 'user_badges'):
        cur.execute("""
            CREATE TABLE user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                badge_id INTEGER NOT NULL REFERENCES badges(id),
                earned_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE UNIQUE INDEX idx_ub_user_badge ON user_badges(user_id, badge_id)")
        print("Table user_badges creee"); n+=1

    conn.commit()
    conn.close()
    print(f"\n{'Migration terminee: '+str(n)+' changement(s).' if n else 'Deja a jour.'}")

if __name__ == '__main__':
    migrate()
