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

    conn.commit()
    conn.close()
    print(f"\n{'Migration terminee: '+str(n)+' changement(s).' if n else 'Deja a jour.'}")

if __name__ == '__main__':
    migrate()
