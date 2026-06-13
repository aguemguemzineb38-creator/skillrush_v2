-- ============================================
-- SkillRush Database Seeding Script
-- Pour PostgreSQL / Railway
-- ============================================

-- 1. TABLE: users (Utilisateurs)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    bio TEXT,
    avatar_url VARCHAR(255),
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    total_missions_completed INTEGER DEFAULT 0,
    rank_position INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLE: skills (Compétences disponibles)
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    missions_count INTEGER DEFAULT 0,
    popularity_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLE: user_skills (Compétences apprises par les utilisateurs)
CREATE TABLE IF NOT EXISTS user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level VARCHAR(20) DEFAULT 'beginner', -- beginner, intermediate, advanced, expert
    xp_earned INTEGER DEFAULT 0,
    missions_completed INTEGER DEFAULT 0,
    is_favorite BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id)
);

-- 4. TABLE: badges (Badges disponibles)
CREATE TABLE IF NOT EXISTS badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(10),
    description TEXT,
    requirement VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. TABLE: user_badges (Badges obtenus par les utilisateurs)
CREATE TABLE IF NOT EXISTS user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id INTEGER NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_id)
);

-- 6. TABLE: missions (Missions)
CREATE TABLE IF NOT EXISTS missions (
    id SERIAL PRIMARY KEY,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    difficulty VARCHAR(20) DEFAULT 'easy', -- easy, medium, hard
    xp_reward INTEGER DEFAULT 0,
    mission_type VARCHAR(50) DEFAULT 'quest', -- quest, quiz, project
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. TABLE: user_missions (Missions complétées par les utilisateurs)
CREATE TABLE IF NOT EXISTS user_missions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mission_id INTEGER NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'completed', -- in_progress, completed, failed
    xp_earned INTEGER DEFAULT 0,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INSERTION DES COMPÉTENCES
-- ============================================

INSERT INTO skills (name, slug, description, icon, missions_count, popularity_score) VALUES
('Python', 'python', 'Programmation Python pour débutants à avancés', '🐍', 48, 95),
('Intelligence Artificielle', 'ia', 'IA et Machine Learning - Les bases essentielles', '🤖', 32, 92),
('Marketing Digital', 'marketing-digital', 'Stratégies et outils du marketing digital', '📣', 27, 85),
('Design UI/UX', 'design-uiux', 'Conception d''interfaces et expérience utilisateur', '🎨', 22, 80),
('Excel & Data', 'excel-data', 'Maîtrisez Excel et l''analyse de données', '📊', 35, 88),
('Entrepreneuriat', 'entrepreneuriat', 'Lancez votre startup avec les bonnes bases', '🚀', 19, 78),
('JavaScript', 'javascript', 'Développement web avec JavaScript', '🔗', 40, 90),
('React', 'react', 'Framework React pour applications modernes', '⚛️', 30, 87),
('Gestion de Projet', 'gestion-projet', 'Agile, Scrum et gestion de projet', '📋', 25, 82),
('Communication', 'communication', 'Soft skills et communication efficace', '💬', 20, 75),
('Graphisme', 'graphisme', 'Adobe Creative Suite & Design graphique', '🎭', 28, 83),
('Cyber Sécurité', 'cyber-securite', 'Protégez-vous dans le monde digital', '🔐', 24, 81);

-- ============================================
-- INSERTION DES BADGES
-- ============================================

INSERT INTO badges (name, icon, description, requirement) VALUES
('Débloqueur', '🏅', 'Débloquez votre première compétence', 'Skill unlocked'),
('Régulier', '🔥', 'Maintenez une progression de 7 jours consécutifs', 'Streak 7 days'),
('Top 10', '⭐', 'Entrez dans le top 10 du classement', 'Top 10 ranking'),
('Missionnaire', '🎯', 'Complétez 10 missions', 'Missions completed'),
('Expert', '👑', 'Atteignez le niveau 10 en une compétence', 'Level 10 skill'),
('Collecteur', '🏆', 'Débloquez 5 compétences différentes', '5 skills unlocked'),
('Speedrun', '⚡', 'Complétez 5 missions en 1 jour', '5 missions 1 day'),
('Niveau 5', '📈', 'Atteignez le niveau 5 global', 'Level 5 overall');

-- ============================================
-- INSERTION DES 100+ UTILISATEURS (Noms marocains & français)
-- ============================================

INSERT INTO users (username, email, full_name, bio, level, xp, streak_days, total_missions_completed, rank_position) VALUES
('sara_b', 'sara.b@example.com', 'Sara B.', 'Passionnée par le design et l''IA 🎨🤖', 5, 400, 14, 25, 1),
('ahmed_dev', 'ahmed.dev@example.com', 'Ahmed Dev', 'Développeur Python & JavaScript', 4, 320, 10, 18, 2),
('fatima_ai', 'fatima.ai@example.com', 'Fatima El Amri', 'Spécialiste en Intelligence Artificielle', 6, 520, 21, 35, 3),
('karim_code', 'karim@example.com', 'Karim Bennani', 'Entrepreneur & Developer', 4, 310, 8, 16, 4),
('layla_design', 'layla@example.com', 'Layla Zaki', 'Designer UI/UX créative', 5, 410, 15, 28, 5),
('mohammed_pro', 'mohammed@example.com', 'Mohammed Alaoui', 'Chef de projet digital', 4, 300, 9, 15, 6),
('noor_marketing', 'noor@example.com', 'Noor Al-Mansouri', 'Spécialiste Marketing Digital', 5, 420, 16, 29, 7),
('rashid_startup', 'rashid@example.com', 'Rashid Boukhili', 'Fondateur startup', 6, 550, 25, 40, 8),
('amira_code', 'amira@example.com', 'Amira Zouai', 'Développeuse Full Stack', 5, 430, 17, 31, 9),
('zainab_excel', 'zainab@example.com', 'Zainab Tahri', 'Experte Excel & Data', 4, 310, 11, 19, 10),
('hamza_python', 'hamza@example.com', 'Hamza Bennani', 'Pythonista confirmé', 5, 445, 13, 27, 11),
('yasmin_react', 'yasmin@example.com', 'Yasmin Saïd', 'Développeuse React', 4, 315, 8, 17, 12),
('adil_graphic', 'adil@example.com', 'Adil Chakir', 'Designer graphique passionné', 4, 305, 10, 18, 13),
('salma_dev', 'salma@example.com', 'Salma Qoraichi', 'Développeuse JavaScript', 4, 320, 9, 16, 14),
('omar_agile', 'omar@example.com', 'Omar Khaled', 'Scrum Master certifié', 5, 425, 14, 26, 15),
('nadia_entrepreneur', 'nadia@example.com', 'Nadia Bencheikh', 'Entrepreneures du digital', 4, 310, 10, 19, 16),
('malik_cyber', 'malik@example.com', 'Malik Safi', 'Spécialiste Cybersécurité', 6, 530, 19, 38, 17),
('rida_marketing', 'rida@example.com', 'Rida El Bakali', 'Community Manager', 3, 200, 7, 12, 18),
('hana_design', 'hana@example.com', 'Hana Moussa', 'Design thinker', 4, 315, 11, 17, 19),
('wissem_code', 'wissem@example.com', 'Wissem Boukhili', 'Dev backend Python', 5, 440, 16, 30, 20),
('lina_ia', 'lina@example.com', 'Lina Bencheikh', 'Data scientist aspirante', 3, 250, 9, 14, 21),
('brahim_excel', 'brahim@example.com', 'Brahim Tahri', 'Analyste données Excel', 4, 305, 8, 15, 22),
('mariam_startup', 'mariam@example.com', 'Mariam Zahra', 'Co-fondatrice startup edtech', 5, 435, 18, 32, 23),
('jamal_react', 'jamal@example.com', 'Jamal Bennani', 'Frontend specialist React', 4, 325, 10, 18, 24),
('leila_design', 'leila@example.com', 'Leila Chakir', 'UX designer expérimentée', 5, 450, 15, 28, 25),
('kaoutar_python', 'kaoutar@example.com', 'Kaoutar Minoui', 'Développeuse Python junior', 3, 220, 6, 11, 26),
('samir_ai', 'samir@example.com', 'Samir Mourad', 'ML engineer en formation', 4, 320, 12, 19, 27),
('dina_marketing', 'dina.sallah@example.com', 'Dina Sallah', 'Content creator', 3, 210, 8, 13, 28),
('aziz_code', 'aziz@example.com', 'Aziz Bennani', 'Full stack developer', 5, 455, 14, 29, 29),
('yasmine_graphic', 'yasmine@example.com', 'Yasmine Alaoui', 'Graphic designer freelance', 4, 310, 9, 16, 30),
('fadi_entrepreneurship', 'fadi@example.com', 'Fadi Boukhili', 'Mentor entrepreneurs', 6, 545, 22, 39, 31),
('nada_communication', 'nada@example.com', 'Nada Zaki', 'Soft skills coach', 3, 230, 7, 13, 32),
('amine_javascript', 'amine@example.com', 'Amine Bennani', 'Web developer passionné', 4, 330, 11, 20, 33),
('dounia_excel', 'dounia@example.com', 'Dounia Tahri', 'Finance analyst', 4, 305, 9, 15, 34),
('badr_cyber', 'badr@example.com', 'Badr Alaoui', 'Information security officer', 5, 465, 16, 31, 35),
('hiba_design', 'hiba@example.com', 'Hiba Saïd', 'Web designer créative', 4, 315, 10, 17, 36),
('noureddin_python', 'noureddin@example.com', 'Noureddin Bennani', 'Python enthusiast', 3, 240, 8, 14, 37),
('souhaila_ia', 'souhaila@example.com', 'Souhaila Chakir', 'AI researcher', 5, 480, 17, 33, 38),
('walid_agile', 'walid@example.com', 'Walid Mourad', 'Agile coach', 4, 320, 11, 18, 39),
('rabia_marketing', 'rabia@example.com', 'Rabia Sallah', 'Digital strategist', 4, 325, 10, 19, 40),
('chihab_react', 'chihab@example.com', 'Chihab Bennani', 'React developer senior', 6, 510, 20, 36, 41),
('samira_graphic', 'samira@example.com', 'Samira Zouai', 'Brand designer', 4, 320, 9, 17, 42),
('abdel_excel', 'abdel@example.com', 'Abdel Tahri', 'Data analyst professionnel', 5, 470, 15, 30, 43),
('meryem_startup', 'meryem@example.com', 'Meryem Alaoui', 'Startup founder', 5, 445, 14, 27, 44),
('reda_code', 'reda@example.com', 'Reda Bennani', 'Développeur full stack', 4, 315, 8, 16, 45),
('farida_design', 'farida@example.com', 'Farida Saïd', 'UX researcher', 4, 330, 12, 20, 46),
('tarek_ia', 'tarek@example.com', 'Tarek Chakir', 'AI enthusiast', 3, 260, 9, 15, 47),
('amal_communication', 'amal@example.com', 'Amal Mourad', 'Communication specialist', 3, 220, 7, 12, 48),
('medine_python', 'medine@example.com', 'Medine Bennani', 'Python teacher', 5, 475, 18, 32, 49),
('carla_marketing', 'carla@example.com', 'Carla Sallah', 'Social media manager', 3, 200, 6, 11, 50),
('hassan_cyber', 'hassan@example.com', 'Hassan Alaoui', 'Security expert', 6, 535, 21, 37, 51),
('salim_excel', 'salim@example.com', 'Salim Tahri', 'Business analyst', 4, 310, 10, 18, 52),
('hind_react', 'hind@example.com', 'Hind Bennani', 'Frontend developer', 4, 325, 9, 17, 53),
('sami_graphic', 'sami@example.com', 'Sami Zouai', 'Creative designer', 4, 300, 8, 15, 54),
('zohra_ia', 'zohra@example.com', 'Zohra Chakir', 'ML specialist', 5, 455, 16, 29, 55),
('imad_agile', 'imad@example.com', 'Imad Mourad', 'Project manager', 4, 320, 11, 19, 56),
('safiya_entrepreneurship', 'safiya@example.com', 'Safiya Sallah', 'Business coach', 5, 440, 13, 26, 57),
('azeddine_code', 'azeddine@example.com', 'Azeddine Bennani', 'Developer mentor', 5, 460, 15, 28, 58),
('rana_design', 'rana@example.com', 'Rana Saïd', 'Graphic designer', 3, 210, 7, 12, 59),
('farah_python', 'farah@example.com', 'Farah Alaoui', 'Python programmer', 4, 330, 10, 18, 60),
('jamal_communication', 'jamal.c@example.com', 'Jamal Chaoui', 'Communications officer', 3, 230, 8, 13, 61),
('nina_marketing', 'nina@example.com', 'Nina Sallah', 'Marketing manager', 4, 315, 9, 17, 62),
('bilal_excel', 'bilal@example.com', 'Bilal Tahri', 'Excel power user', 4, 305, 10, 16, 63),
('marwa_react', 'marwa@example.com', 'Marwa Bennani', 'React specialist', 5, 465, 17, 31, 64),
('elias_graphic', 'elias@example.com', 'Elias Chakir', 'Illustration artist', 3, 200, 6, 10, 65),
('ibtissam_ia', 'ibtissam@example.com', 'Ibtissam Mourad', 'Data scientist', 5, 480, 19, 34, 66),
('nawal_cyber', 'nawal@example.com', 'Nawal Alaoui', 'Cybersecurity analyst', 4, 320, 11, 19, 67),
('hafid_startup', 'hafid_startup@example.com', 'Hafid Sallah', 'Entrepreneur', 4, 310, 8, 15, 68),
('maia_design', 'maia@example.com', 'Maia Saïd', 'UI designer junior', 3, 220, 7, 12, 69),
('mourad_code', 'mourad@example.com', 'Mourad Bennani', 'Web developer', 4, 325, 9, 17, 70),
('suha_python', 'suha@example.com', 'Suha Tahri', 'Python learner', 3, 250, 9, 14, 71),
('karim_ia', 'karim.ia@example.com', 'Karim Chakir', 'AI engineer', 5, 470, 14, 28, 72),
('jalila_marketing', 'jalila@example.com', 'Jalila Mourad', 'Marketing coordinator', 3, 210, 6, 11, 73),
('rami_excel', 'rami@example.com', 'Rami Sallah', 'Data analyst', 4, 315, 10, 18, 74),
('yassar_react', 'yassar@example.com', 'Yassar Saïd', 'Frontend developer', 4, 330, 11, 19, 75),
('dina_graphic', 'dina.g@example.com', 'Dina Alaoui', 'Graphic designer', 3, 205, 7, 11, 76),
('tahar_cyber', 'tahar@example.com', 'Tahar Bennani', 'Security officer', 5, 455, 13, 27, 77),
('nesrine_entrepreneurship', 'nesrine@example.com', 'Nesrine Chakir', 'Business advisor', 4, 320, 9, 16, 78),
('akram_code', 'akram@example.com', 'Akram Tahri', 'Full stack developer', 4, 325, 12, 20, 79),
('roula_design', 'roula@example.com', 'Roula Mourad', 'Web designer', 3, 200, 6, 10, 80),
('lamine_python', 'lamine@example.com', 'Lamine Sallah', 'Python developer', 3, 240, 8, 13, 81),
('rim_ia', 'rim@example.com', 'Rim Saïd', 'Machine learning engineer', 5, 475, 16, 30, 82),
('nasser_agile', 'nasser@example.com', 'Nasser Alaoui', 'Scrum master', 4, 310, 10, 17, 83),
('samina_marketing', 'samina@example.com', 'Samina Bennani', 'Digital marketer', 3, 220, 7, 12, 84),
('slimane_excel', 'slimane@example.com', 'Slimane Chakir', 'Excel specialist', 4, 300, 9, 15, 85),
('sakina_react', 'sakina@example.com', 'Sakina Tahri', 'React developer', 4, 320, 10, 18, 86),
('ilias_graphic', 'ilias@example.com', 'Ilias Mourad', 'Designer', 3, 210, 8, 12, 87),
('inass_cyber', 'inass@example.com', 'Inass Sallah', 'IT security specialist', 4, 315, 9, 16, 88),
('oussama_startup', 'oussama@example.com', 'Oussama Saïd', 'Tech entrepreneur', 5, 440, 14, 26, 89),
('anis_code', 'anis@example.com', 'Anis Alaoui', 'Developer', 3, 230, 7, 13, 90),
('amina_design', 'amina@example.com', 'Amina Bennani', 'UX designer', 4, 330, 11, 19, 91),
('adel_python', 'adel@example.com', 'Adel Chakir', 'Python coder', 3, 250, 8, 14, 92),
('alia_ia', 'alia@example.com', 'Alia Tahri', 'AI researcher', 4, 310, 10, 17, 93),
('omari_communication', 'omari@example.com', 'Omari Mourad', 'Public speaker', 3, 200, 6, 10, 94),
('imane_marketing', 'imane@example.com', 'Imane Sallah', 'Brand specialist', 3, 215, 7, 11, 95),
('hamid_excel', 'hamid@example.com', 'Hamid Saïd', 'Financial analyst', 4, 320, 11, 18, 96),
('sawsan_react', 'sawsan@example.com', 'Sawsan Alaoui', 'Front-end engineer', 4, 325, 9, 17, 97),
('riham_graphic', 'riham@example.com', 'Riham Bennani', 'Visual designer', 3, 205, 8, 11, 98),
('issam_cyber', 'issam@example.com', 'Issam Chakir', 'Network security', 5, 460, 15, 29, 99),
('clara_entrepreneurship', 'clara@example.com', 'Clara Tahri', 'Startup founder', 4, 315, 9, 16, 100);

-- ============================================
-- INSERTION DES COMPÉTENCES POUR CHAQUE UTILISATEUR
-- ============================================

-- Sara B. → Python, IA, Excel
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'sara_b'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 300, 15, true),
((SELECT id FROM users WHERE username = 'sara_b'), (SELECT id FROM skills WHERE slug = 'ia'), 'intermediate', 250, 12, true),
((SELECT id FROM users WHERE username = 'sara_b'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'advanced', 400, 20, true);

-- Ahmed Dev → Python, JavaScript
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'ahmed_dev'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 280, 14, true),
((SELECT id FROM users WHERE username = 'ahmed_dev'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 290, 15, true);

-- Fatima AI → IA, Python, Data
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'fatima_ai'), (SELECT id FROM skills WHERE slug = 'ia'), 'advanced', 450, 25, true),
((SELECT id FROM users WHERE username = 'fatima_ai'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 420, 22, true),
((SELECT id FROM users WHERE username = 'fatima_ai'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 300, 13, false);

-- Karim Code → Python, JavaScript, Entrepreneuriat
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'karim_code'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 260, 12, true),
((SELECT id FROM users WHERE username = 'karim_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'beginner', 180, 8, false),
((SELECT id FROM users WHERE username = 'karim_code'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'intermediate', 280, 14, true);

-- Layla Design → Design UI/UX, Graphisme
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'layla_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'advanced', 380, 19, true),
((SELECT id FROM users WHERE username = 'layla_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'intermediate', 320, 15, true);

-- Mohammed Pro → Gestion de Projet, Agile
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'mohammed_pro'), (SELECT id FROM skills WHERE slug = 'gestion-projet'), 'intermediate', 270, 13, true),
((SELECT id FROM users WHERE username = 'mohammed_pro'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 240, 11, false);

-- Noor Marketing → Marketing Digital, Communication
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'noor_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'intermediate', 350, 16, true),
((SELECT id FROM users WHERE username = 'noor_marketing'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 280, 13, true);

-- Rashid Startup → Entrepreneuriat, JavaScript, Gestion de Projet
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'rashid_startup'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'advanced', 450, 24, true),
((SELECT id FROM users WHERE username = 'rashid_startup'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 320, 15, false),
((SELECT id FROM users WHERE username = 'rashid_startup'), (SELECT id FROM skills WHERE slug = 'gestion-projet'), 'intermediate', 280, 12, true);

-- Amira Code → React, JavaScript, Python
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'amira_code'), (SELECT id FROM skills WHERE slug = 'react'), 'advanced', 380, 18, true),
((SELECT id FROM users WHERE username = 'amira_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'advanced', 370, 17, true),
((SELECT id FROM users WHERE username = 'amira_code'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 240, 10, false);

-- Zainab Excel → Excel & Data
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'zainab_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'advanced', 350, 17, true);

-- Hamza Python → Python
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'hamza_python'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 400, 20, true);

-- Yasmin React → React, JavaScript
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'yasmin_react'), (SELECT id FROM skills WHERE slug = 'react'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'yasmin_react'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 280, 13, true);

-- Adil Graphic → Graphisme, Design UI/UX
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'adil_graphic'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'adil_graphic'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 200, 8, false);

-- Salma Dev → JavaScript, Python
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'salma_dev'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 310, 15, true),
((SELECT id FROM users WHERE username = 'salma_dev'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 180, 7, false);

-- Omar Agile → Gestion de Projet, Communication
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'omar_agile'), (SELECT id FROM skills WHERE slug = 'gestion-projet'), 'advanced', 360, 18, true),
((SELECT id FROM users where username = 'omar_agile'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 300, 14, true);

-- Nadia Entrepreneur → Entrepreneuriat, Marketing Digital
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'nadia_entrepreneur'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'intermediate', 280, 13, true),
((SELECT id FROM users WHERE username = 'nadia_entrepreneur'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 210, 9, false);

-- Malik Cyber → Cyber Sécurité, Python
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'malik_cyber'), (SELECT id FROM skills WHERE slug = 'cyber-securite'), 'advanced', 440, 23, true),
((SELECT id FROM users WHERE username = 'malik_cyber'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 310, 14, true);

-- Rida Marketing → Marketing Digital
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'rida_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 180, 9, true);

-- Hana Design → Design UI/UX, Graphisme
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'hana_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'hana_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 210, 8, false);

-- Wissem Code → Python, Django
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'wissem_code'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 390, 19, true),
((SELECT id FROM users WHERE username = 'wissem_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 250, 11, false);

-- Lina IA → IA, Python
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'lina_ia'), (SELECT id FROM skills WHERE slug = 'ia'), 'beginner', 220, 10, true),
((SELECT id FROM users WHERE username = 'lina_ia'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 200, 8, true),
((SELECT id FROM users WHERE username = 'lina_ia'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'beginner', 180, 7, false);

-- Brahim Excel → Excel & Data
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'brahim_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 280, 13, true);

-- Mariam Startup → Entrepreneuriat, Marketing Digital, Communication
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'mariam_startup'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'advanced', 380, 19, true),
((SELECT id FROM users WHERE username = 'mariam_startup'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'intermediate', 300, 13, true),
((SELECT id FROM users WHERE username = 'mariam_startup'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 270, 11, false);

-- Jamal React → React, JavaScript
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'jamal_react'), (SELECT id FROM skills WHERE slug = 'react'), 'intermediate', 310, 15, true),
((SELECT id FROM users WHERE username = 'jamal_react'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 300, 14, true);

-- Leila Design → Design UI/UX, Graphisme
INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
((SELECT id FROM users WHERE username = 'leila_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'advanced', 410, 21, true),
((SELECT id FROM users WHERE username = 'leila_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'intermediate', 320, 15, true);

-- 80 plus utilisateurs avec leurs compétences

INSERT INTO user_skills (user_id, skill_id, proficiency_level, xp_earned, missions_completed, is_favorite) VALUES
-- Kaoutar
((SELECT id FROM users WHERE username = 'kaoutar_python'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 200, 10, true),
((SELECT id FROM users WHERE username = 'kaoutar_python'), (SELECT id FROM skills WHERE slug = 'javascript'), 'beginner', 150, 6, false),

-- Samir
((SELECT id FROM users WHERE username = 'samir_ai'), (SELECT id FROM skills WHERE slug = 'ia'), 'intermediate', 280, 12, true),
((SELECT id FROM users WHERE username = 'samir_ai'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 270, 11, true),
((SELECT id FROM users WHERE username = 'samir_ai'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'beginner', 180, 7, false),

-- Dina
((SELECT id FROM users WHERE username = 'dina_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 190, 8, true),
((SELECT id FROM users WHERE username = 'dina_marketing'), (SELECT id FROM skills WHERE slug = 'communication'), 'beginner', 170, 7, false),

-- Aziz
((SELECT id FROM users WHERE username = 'aziz_code'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 410, 20, true),
((SELECT id FROM users WHERE username = 'aziz_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'advanced', 400, 19, true),
((SELECT id FROM users WHERE username = 'aziz_code'), (SELECT id FROM skills WHERE slug = 'react'), 'intermediate', 290, 13, false),

-- Yasmine
((SELECT id FROM users WHERE username = 'yasmine_graphic'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'yasmine_graphic'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 190, 8, false),

-- Fadi
((SELECT id FROM users WHERE username = 'fadi_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'advanced', 480, 27, true),
((SELECT id FROM users WHERE username = 'fadi_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'communication'), 'advanced', 380, 18, true),
((SELECT id FROM users WHERE username = 'fadi_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'gestion-projet'), 'intermediate', 320, 14, true),

-- Nada
((SELECT id FROM users WHERE username = 'nada_communication'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 210, 10, true),
((SELECT id FROM users WHERE username = 'nada_communication'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 180, 7, false),

-- Amine
((SELECT id FROM users WHERE username = 'amine_javascript'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 310, 15, true),
((SELECT id FROM users WHERE username = 'amine_javascript'), (SELECT id FROM skills WHERE slug = 'react'), 'beginner', 220, 9, false),
((SELECT id FROM users WHERE username = 'amine_javascript'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 200, 8, false),

-- Dounia
((SELECT id FROM users WHERE username = 'dounia_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 280, 13, true),

-- Badr
((SELECT id FROM users WHERE username = 'badr_cyber'), (SELECT id FROM skills WHERE slug = 'cyber-securite'), 'advanced', 420, 21, true),
((SELECT id FROM users WHERE username = 'badr_cyber'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 280, 12, true),

-- Hiba
((SELECT id FROM users WHERE username = 'hiba_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'hiba_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 200, 8, false),

-- Noureddin
((SELECT id FROM users WHERE username = 'noureddin_python'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 220, 10, true),
((SELECT id FROM users WHERE username = 'noureddin_python'), (SELECT id FROM skills WHERE slug = 'javascript'), 'beginner', 160, 6, false),

-- Souhaila
((SELECT id FROM users WHERE username = 'souhaila_ia'), (SELECT id FROM skills WHERE slug = 'ia'), 'advanced', 430, 22, true),
((SELECT id FROM users WHERE username = 'souhaila_ia'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 400, 19, true),
((SELECT id FROM users WHERE username = 'souhaila_ia'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 290, 12, false),

-- Walid
((SELECT id FROM users WHERE username = 'walid_agile'), (SELECT id FROM skills WHERE slug = 'gestion-projet'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'walid_agile'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 270, 12, true),

-- Rabia
((SELECT id FROM users WHERE username = 'rabia_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'rabia_marketing'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 280, 12, true),

-- Chihab
((SELECT id FROM users WHERE username = 'chihab_react'), (SELECT id FROM skills WHERE slug = 'react'), 'advanced', 450, 23, true),
((SELECT id FROM users WHERE username = 'chihab_react'), (SELECT id FROM skills WHERE slug = 'javascript'), 'advanced', 420, 21, true),
((SELECT id FROM users WHERE username = 'chihab_react'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 300, 13, false),

-- Samira
((SELECT id FROM users WHERE username = 'samira_graphic'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'samira_graphic'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'intermediate', 280, 13, true),

-- Abdel
((SELECT id FROM users WHERE username = 'abdel_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'advanced', 420, 21, true),
((SELECT id FROM users WHERE username = 'abdel_excel'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 280, 11, false),

-- Meryem
((SELECT id FROM users WHERE username = 'meryem_startup'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'advanced', 380, 19, true),
((SELECT id FROM users WHERE username = 'meryem_startup'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'intermediate', 300, 13, true),
((SELECT id FROM users WHERE username = 'meryem_startup'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 270, 11, false),

-- Reda
((SELECT id FROM users WHERE username = 'reda_code'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'reda_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 280, 13, true),

-- Farida
((SELECT id FROM users WHERE username = 'farida_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'intermediate', 310, 16, true),
((SELECT id FROM users WHERE username = 'farida_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'intermediate', 280, 13, true),

-- Tarek
((SELECT id FROM users WHERE username = 'tarek_ia'), (SELECT id FROM skills WHERE slug = 'ia'), 'beginner', 240, 11, true),
((SELECT id FROM users WHERE username = 'tarek_ia'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 220, 9, true),

-- Amal
((SELECT id FROM users WHERE username = 'amal_communication'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 200, 10, true),
((SELECT id FROM users WHERE username = 'amal_communication'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 170, 7, false),

-- Medine
((SELECT id FROM users WHERE username = 'medine_python'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 430, 22, true),
((SELECT id FROM users WHERE username = 'medine_python'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 290, 12, false),

-- Carla
((SELECT id FROM users WHERE username = 'carla_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 180, 8, true),

-- Hassan
((SELECT id FROM users WHERE username = 'hassan_cyber'), (SELECT id FROM skills WHERE slug = 'cyber-securite'), 'advanced', 460, 24, true),
((SELECT id FROM users WHERE username = 'hassan_cyber'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 380, 17, true),

-- Salim
((SELECT id FROM users WHERE username = 'salim_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 280, 13, true),

-- Hind
((SELECT id FROM users WHERE username = 'hind_react'), (SELECT id FROM skills WHERE slug = 'react'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'hind_react'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 290, 13, true),

-- Sami
((SELECT id FROM users WHERE username = 'sami_graphic'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'intermediate', 280, 13, true),
((SELECT id FROM users WHERE username = 'sami_graphic'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 190, 8, false),

-- Zohra
((SELECT id FROM users WHERE username = 'zohra_ia'), (SELECT id FROM skills WHERE slug = 'ia'), 'intermediate', 410, 20, true),
((SELECT id FROM users WHERE username = 'zohra_ia'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 340, 16, true),
((SELECT id FROM users WHERE username = 'zohra_ia'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'beginner', 190, 8, false),

-- Imad
((SELECT id FROM users WHERE username = 'imad_agile'), (SELECT id FROM skills WHERE slug = 'gestion-projet'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'imad_agile'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 270, 12, true),

-- Safiya
((SELECT id FROM users WHERE username = 'safiya_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'advanced', 390, 20, true),
((SELECT id FROM users WHERE username = 'safiya_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'intermediate', 300, 13, true),

-- Azeddine
((SELECT id FROM users WHERE username = 'azeddine_code'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 420, 21, true),
((SELECT id FROM users WHERE username = 'azeddine_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'advanced', 400, 20, true),
((SELECT id FROM users WHERE username = 'azeddine_code'), (SELECT id FROM skills WHERE slug = 'react'), 'intermediate', 310, 14, false),

-- Rana
((SELECT id FROM users WHERE username = 'rana_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 200, 9, true),
((SELECT id FROM users WHERE username = 'rana_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 180, 7, false),

-- Farah
((SELECT id FROM users WHERE username = 'farah_python'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 310, 15, true),
((SELECT id FROM users WHERE username = 'farah_python'), (SELECT id FROM skills WHERE slug = 'javascript'), 'beginner', 190, 8, false),

-- Jamal C.
((SELECT id FROM users WHERE username = 'jamal_communication'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 210, 10, true),
((SELECT id FROM users WHERE username = 'jamal_communication'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 180, 7, false),

-- Nina
((SELECT id FROM users WHERE username = 'nina_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'nina_marketing'), (SELECT id FROM skills WHERE slug = 'communication'), 'beginner', 210, 9, false),

-- Bilal
((SELECT id FROM users WHERE username = 'bilal_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 280, 13, true),

-- Marwa
((SELECT id FROM users WHERE username = 'marwa_react'), (SELECT id FROM skills WHERE slug = 'react'), 'advanced', 430, 22, true),
((SELECT id FROM users WHERE username = 'marwa_react'), (SELECT id FROM skills WHERE slug = 'javascript'), 'advanced', 410, 20, true),
((SELECT id FROM users WHERE username = 'marwa_react'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 190, 7, false),

-- Elias
((SELECT id FROM users WHERE username = 'elias_graphic'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 180, 8, true),
((SELECT id FROM users WHERE username = 'elias_graphic'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 170, 7, false),

-- Ibtissam
((SELECT id FROM users WHERE username = 'ibtissam_ia'), (SELECT id FROM skills WHERE slug = 'ia'), 'advanced', 440, 23, true),
((SELECT id FROM users WHERE username = 'ibtissam_ia'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 420, 21, true),
((SELECT id FROM users WHERE username = 'ibtissam_ia'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 300, 13, false),

-- Nawal
((SELECT id FROM users WHERE username = 'nawal_cyber'), (SELECT id FROM skills WHERE slug = 'cyber-securite'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'nawal_cyber'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 210, 9, false),

-- Hafid
((SELECT id FROM users WHERE username = 'hafid_startup'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'intermediate', 280, 13, true),
((SELECT id FROM users WHERE username = 'hafid_startup'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 210, 9, false),

-- Maia
((SELECT id FROM users WHERE username = 'maia_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 200, 9, true),
((SELECT id FROM users WHERE username = 'maia_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 180, 7, false),

-- Mourad
((SELECT id FROM users WHERE username = 'mourad_code'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'mourad_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 290, 13, true),

-- Suha
((SELECT id FROM users WHERE username = 'suha_python'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 230, 11, true),
((SELECT id FROM users WHERE username = 'suha_python'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'beginner', 190, 8, false),

-- Karim IA
((SELECT id FROM users WHERE username = 'karim_ia'), (SELECT id FROM skills WHERE slug = 'ia'), 'advanced', 420, 21, true),
((SELECT id FROM users WHERE username = 'karim_ia'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 400, 19, true),

-- Jalila
((SELECT id FROM users WHERE username = 'jalila_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 190, 8, true),
((SELECT id FROM users WHERE username = 'jalila_marketing'), (SELECT id FROM skills WHERE slug = 'communication'), 'beginner', 170, 7, false),

-- Rami
((SELECT id FROM users WHERE username = 'rami_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 290, 14, true),

-- Yassar
((SELECT id FROM users WHERE username = 'yassar_react'), (SELECT id FROM skills WHERE slug = 'react'), 'intermediate', 310, 15, true),
((SELECT id FROM users WHERE username = 'yassar_react'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 300, 14, true),

-- Dina G.
((SELECT id FROM users WHERE username = 'dina_graphic'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 190, 8, true),
((SELECT id FROM users WHERE username = 'dina_graphic'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 170, 7, false),

-- Tahar
((SELECT id FROM users WHERE username = 'tahar_cyber'), (SELECT id FROM skills WHERE slug = 'cyber-securite'), 'advanced', 410, 20, true),
((SELECT id FROM users WHERE username = 'tahar_cyber'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 290, 12, true),

-- Nesrine
((SELECT id FROM users WHERE username = 'nesrine_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'nesrine_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 270, 12, true),

-- Akram
((SELECT id FROM users WHERE username = 'akram_code'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 310, 15, true),
((SELECT id FROM users WHERE username = 'akram_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'akram_code'), (SELECT id FROM skills WHERE slug = 'react'), 'beginner', 210, 8, false),

-- Roula
((SELECT id FROM users WHERE username = 'roula_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 190, 8, true),
((SELECT id FROM users WHERE username = 'roula_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 170, 7, false),

-- Lamine
((SELECT id FROM users WHERE username = 'lamine_python'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 220, 10, true),
((SELECT id FROM users WHERE username = 'lamine_python'), (SELECT id FROM skills WHERE slug = 'javascript'), 'beginner', 180, 7, false),

-- Rim
((SELECT id FROM users WHERE username = 'rim_ia'), (SELECT id FROM skills WHERE slug = 'ia'), 'advanced', 430, 22, true),
((SELECT id FROM users WHERE username = 'rim_ia'), (SELECT id FROM skills WHERE slug = 'python'), 'advanced', 410, 20, true),
((SELECT id FROM users WHERE username = 'rim_ia'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 280, 11, false),

-- Nasser
((SELECT id FROM users WHERE username = 'nasser_agile'), (SELECT id FROM skills WHERE slug = 'gestion-projet'), 'intermediate', 280, 13, true),
((SELECT id FROM users WHERE username = 'nasser_agile'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 260, 11, true),

-- Samina
((SELECT id FROM users WHERE username = 'samina_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 200, 9, true),
((SELECT id FROM users WHERE username = 'samina_marketing'), (SELECT id FROM skills WHERE slug = 'communication'), 'beginner', 180, 8, false),

-- Slimane
((SELECT id FROM users WHERE username = 'slimane_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 270, 12, true),

-- Sakina
((SELECT id FROM users WHERE username = 'sakina_react'), (SELECT id FROM skills WHERE slug = 'react'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'sakina_react'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 280, 13, true),

-- Ilias
((SELECT id FROM users WHERE username = 'ilias_graphic'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 200, 9, true),
((SELECT id FROM users WHERE username = 'ilias_graphic'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 180, 8, false),

-- Inass
((SELECT id FROM users WHERE username = 'inass_cyber'), (SELECT id FROM skills WHERE slug = 'cyber-securite'), 'intermediate', 290, 13, true),
((SELECT id FROM users WHERE username = 'inass_cyber'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 210, 8, false),

-- Oussama
((SELECT id FROM users WHERE username = 'oussama_startup'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'advanced', 370, 18, true),
((SELECT id FROM users WHERE username = 'oussama_startup'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'intermediate', 290, 12, true),
((SELECT id FROM users WHERE username = 'oussama_startup'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 270, 11, false),

-- Anis
((SELECT id FROM users WHERE username = 'anis_code'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 210, 10, true),
((SELECT id FROM users WHERE username = 'anis_code'), (SELECT id FROM skills WHERE slug = 'javascript'), 'beginner', 190, 8, false),

-- Amina
((SELECT id FROM users WHERE username = 'amina_design'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'intermediate', 310, 15, true),
((SELECT id FROM users WHERE username = 'amina_design'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'intermediate', 290, 13, true),

-- Adel
((SELECT id FROM users WHERE username = 'adel_python'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 230, 11, true),
((SELECT id FROM users WHERE username = 'adel_python'), (SELECT id FROM skills WHERE slug = 'javascript'), 'beginner', 200, 8, false),

-- Alia
((SELECT id FROM users WHERE username = 'alia_ia'), (SELECT id FROM skills WHERE slug = 'ia'), 'intermediate', 290, 13, true),
((SELECT id FROM users WHERE username = 'alia_ia'), (SELECT id FROM skills WHERE slug = 'python'), 'beginner', 200, 8, false),

-- Omari
((SELECT id FROM users WHERE username = 'omari_communication'), (SELECT id FROM skills WHERE slug = 'communication'), 'beginner', 180, 8, true),

-- Imane
((SELECT id FROM users WHERE username = 'imane_marketing'), (SELECT id FROM skills WHERE slug = 'marketing-digital'), 'beginner', 200, 9, true),

-- Hamid
((SELECT id FROM users WHERE username = 'hamid_excel'), (SELECT id FROM skills WHERE slug = 'excel-data'), 'intermediate', 300, 14, true),

-- Sawsan
((SELECT id FROM users WHERE username = 'sawsan_react'), (SELECT id FROM skills WHERE slug = 'react'), 'intermediate', 300, 14, true),
((SELECT id FROM users WHERE username = 'sawsan_react'), (SELECT id FROM skills WHERE slug = 'javascript'), 'intermediate', 280, 13, true),

-- Riham
((SELECT id FROM users WHERE username = 'riham_graphic'), (SELECT id FROM skills WHERE slug = 'graphisme'), 'beginner', 190, 8, true),
((SELECT id FROM users WHERE username = 'riham_graphic'), (SELECT id FROM skills WHERE slug = 'design-uiux'), 'beginner', 170, 7, false),

-- Issam
((SELECT id FROM users WHERE username = 'issam_cyber'), (SELECT id FROM skills WHERE slug = 'cyber-securite'), 'advanced', 430, 22, true),
((SELECT id FROM users WHERE username = 'issam_cyber'), (SELECT id FROM skills WHERE slug = 'python'), 'intermediate', 310, 14, true),

-- Clara
((SELECT id FROM users WHERE username = 'clara_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'intermediate', 290, 14, true),
((SELECT id FROM users WHERE username = 'clara_entrepreneurship'), (SELECT id FROM skills WHERE slug = 'communication'), 'intermediate', 270, 12, true);

-- ============================================
-- INSERTION DES MISSIONS SAMPLE
-- ============================================

INSERT INTO missions (skill_id, title, description, difficulty, xp_reward, mission_type) VALUES
((SELECT id FROM skills WHERE slug = 'python'), 'Variables et types de données', 'Apprenez les bases de Python', 'easy', 50, 'quest'),
((SELECT id FROM skills WHERE slug = 'python'), 'Boucles et conditions', 'Maîtrisez les structures de contrôle', 'medium', 75, 'quiz'),
((SELECT id FROM skills WHERE slug = 'python'), 'Fonctions avancées', 'Créez des fonctions complexes', 'hard', 100, 'project'),
((SELECT id FROM skills WHERE slug = 'javascript'), 'DOM et manipulation', 'Contrôlez le HTML avec JS', 'easy', 50, 'quest'),
((SELECT id FROM skills WHERE slug = 'javascript'), 'Async et Promises', 'Programmation asynchrone', 'hard', 100, 'project'),
((SELECT id FROM skills WHERE slug = 'ia'), 'Principes de base de l''IA', 'Introduction à l''intelligence artificielle', 'easy', 50, 'quiz'),
((SELECT id FROM skills WHERE slug = 'ia'), 'Machine Learning 101', 'Premier modèle ML', 'medium', 75, 'project'),
((SELECT id FROM skills WHERE slug = 'design-uiux'), 'UX Research', 'Méthodologies de recherche utilisateur', 'medium', 75, 'quest'),
((SELECT id FROM skills WHERE slug = 'design-uiux'), 'Wireframing', 'Créez vos premiers wireframes', 'easy', 50, 'quest'),
((SELECT id FROM skills WHERE slug = 'excel-data'), 'Formules avancées', 'VLOOKUP, INDEX, MATCH', 'medium', 75, 'quiz'),
((SELECT id FROM skills WHERE slug = 'marketing-digital'), 'Stratégie réseaux sociaux', 'Planifiez vos campagnes', 'medium', 75, 'quest'),
((SELECT id FROM skills WHERE slug = 'entrepreneuriat'), 'Business Model Canvas', 'Structurez votre idée', 'easy', 50, 'quest'),
((SELECT id FROM skills WHERE slug = 'react'), 'Components et Props', 'Les bases de React', 'easy', 50, 'quest'),
((SELECT id FROM skills WHERE slug = 'react'), 'Hooks avancés', 'useState, useEffect et plus', 'medium', 75, 'project'),
((SELECT id FROM skills WHERE slug = 'gestion-projet'), 'Agile & Scrum', 'Méthodologies agiles', 'medium', 75, 'quest'),
((SELECT id FROM skills WHERE slug = 'communication'), 'Présentation efficace', 'Parlez en public', 'medium', 75, 'quest'),
((SELECT id FROM skills WHERE slug = 'graphisme'), 'Typographie', 'Choix et utilisation des polices', 'easy', 50, 'quest'),
((SELECT id FROM skills WHERE slug = 'cyber-securite'), 'Bases de la sécurité', 'Protégez-vous online', 'easy', 50, 'quest');

-- ============================================
-- INSERTION DE QUELQUES USER_BADGES (Top utilisateurs)
-- ============================================

INSERT INTO user_badges (user_id, badge_id, unlocked_at) VALUES
((SELECT id FROM users WHERE username = 'sara_b'), (SELECT id FROM badges WHERE name = 'Débloqueur'), CURRENT_TIMESTAMP - INTERVAL '60 days'),
((SELECT id FROM users WHERE username = 'sara_b'), (SELECT id FROM badges WHERE name = 'Régulier'), CURRENT_TIMESTAMP - INTERVAL '40 days'),
((SELECT id FROM users WHERE username = 'sara_b'), (SELECT id FROM badges WHERE name = 'Top 10'), CURRENT_TIMESTAMP - INTERVAL '20 days'),
((SELECT id FROM users WHERE username = 'fatima_ai'), (SELECT id FROM badges WHERE name = 'Débloqueur'), CURRENT_TIMESTAMP - INTERVAL '80 days'),
((SELECT id FROM users WHERE username = 'fatima_ai'), (SELECT id FROM badges WHERE name = 'Régulier'), CURRENT_TIMESTAMP - INTERVAL '50 days'),
((SELECT id FROM users WHERE username = 'fatima_ai'), (SELECT id FROM badges WHERE name = 'Top 10'), CURRENT_TIMESTAMP - INTERVAL '30 days'),
((SELECT id FROM users WHERE username = 'fatima_ai'), (SELECT id FROM badges WHERE name = 'Collecteur'), CURRENT_TIMESTAMP - INTERVAL '15 days'),
((SELECT id FROM users WHERE username = 'rashid_startup'), (SELECT id FROM badges WHERE name = 'Débloqueur'), CURRENT_TIMESTAMP - INTERVAL '75 days'),
((SELECT id FROM users WHERE username = 'rashid_startup'), (SELECT id FROM badges WHERE name = 'Top 10'), CURRENT_TIMESTAMP - INTERVAL '35 days'),
((SELECT id FROM users WHERE username = 'malik_cyber'), (SELECT id FROM badges WHERE name = 'Débloqueur'), CURRENT_TIMESTAMP - INTERVAL '70 days'),
((SELECT id FROM users WHERE username = 'malik_cyber'), (SELECT id FROM badges WHERE name = 'Régulier'), CURRENT_TIMESTAMP - INTERVAL '45 days'),
((SELECT id FROM users WHERE username = 'chihab_react'), (SELECT id FROM badges WHERE name = 'Débloqueur'), CURRENT_TIMESTAMP - INTERVAL '65 days'),
((SELECT id FROM users WHERE username = 'chihab_react'), (SELECT id FROM badges WHERE name = 'Régulier'), CURRENT_TIMESTAMP - INTERVAL '42 days'),
((SELECT id FROM users WHERE username = 'hassan_cyber'), (SELECT id FROM badges WHERE name = 'Débloqueur'), CURRENT_TIMESTAMP - INTERVAL '78 days'),
((SELECT id FROM users WHERE username = 'hassan_cyber'), (SELECT id FROM badges WHERE name = 'Top 10'), CURRENT_TIMESTAMP - INTERVAL '32 days');

-- ============================================
-- INSERTION DE QUELQUES USER_MISSIONS COMPLETÉES
-- ============================================

INSERT INTO user_missions (user_id, mission_id, status, xp_earned, completed_at) VALUES
((SELECT id FROM users WHERE username = 'sara_b'), (SELECT id FROM missions LIMIT 1), 'completed', 50, CURRENT_TIMESTAMP - INTERVAL '45 days'),
((SELECT id FROM users WHERE username = 'sara_b'), (SELECT id FROM missions LIMIT 1 OFFSET 1), 'completed', 75, CURRENT_TIMESTAMP - INTERVAL '40 days'),
((SELECT id FROM users WHERE username = 'ahmed_dev'), (SELECT id FROM missions WHERE skill_id = (SELECT id FROM skills WHERE slug = 'python') LIMIT 1), 'completed', 50, CURRENT_TIMESTAMP - INTERVAL '50 days'),
((SELECT id FROM users WHERE username = 'fatima_ai'), (SELECT id FROM missions WHERE skill_id = (SELECT id FROM skills WHERE slug = 'ia') LIMIT 1), 'completed', 50, CURRENT_TIMESTAMP - INTERVAL '60 days'),
((SELECT id FROM users WHERE username = 'layla_design'), (SELECT id FROM missions WHERE skill_id = (SELECT id FROM skills WHERE slug = 'design-uiux') LIMIT 1), 'completed', 50, CURRENT_TIMESTAMP - INTERVAL '55 days');

-- ============================================
-- INDEX POUR OPTIMISATION
-- ============================================

CREATE INDEX IF NOT EXISTS idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill_id ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_missions_user_id ON user_missions(user_id);
CREATE INDEX IF NOT EXISTS idx_missions_skill_id ON missions(skill_id);
CREATE INDEX IF NOT EXISTS idx_users_level ON users(level);
CREATE INDEX IF NOT EXISTS idx_users_rank ON users(rank_position);

-- ============================================
-- DONE!
-- ============================================

COMMIT;
