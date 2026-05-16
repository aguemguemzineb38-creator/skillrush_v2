from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modèle utilisateur"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255), default='default.jpg')
    bio = db.Column(db.Text, default='')
    competence = db.Column(db.String(120), default='')

    # Onboarding
    onboarding_done = db.Column(db.Boolean, default=False)
    onboarding_rejected = db.Column(db.Boolean, default=False)
    onboarding_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)

    # Rôle : 'user' | 'moderator' | 'admin'
    role = db.Column(db.String(20), default='user', nullable=False)

    # Gamification
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    last_daily_reward = db.Column(db.DateTime, nullable=True)
    profile_daily_bonus_date = db.Column(db.Date, nullable=True)
    streak_count = db.Column(db.Integer, default=0)
    streak_last_date = db.Column(db.Date, nullable=True)

    # Statut compte
    is_blocked = db.Column(db.Boolean, default=False)

    # Relations
    skills_created = db.relationship('Skill', backref='creator', lazy=True,
                                     foreign_keys='Skill.creator_id')
    missions_completed = db.relationship('UserMission', backref='user', lazy=True)
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    xp_purchases = db.relationship('XPPurchase', backref='user', lazy=True)
    following = db.relationship('Follow', foreign_keys='Follow.follower_id',
                                backref='follower_user', lazy='dynamic',
                                cascade='all, delete-orphan')
    followers_rel = db.relationship('Follow', foreign_keys='Follow.following_id',
                                    backref='following_user', lazy='dynamic',
                                    cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def get_level_info(self):
        """Calcule le niveau et XP nécessaire pour le prochain niveau"""
        xp_in_level = self.xp % 1000
        return {
            'current': self.level,
            'xp_current': xp_in_level,
            'xp_needed': 1000 - xp_in_level
        }

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class XPPurchase(db.Model):
    """Achat de XP par carte bancaire (Stripe-ready)"""
    __tablename__ = 'xp_purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    xp_amount = db.Column(db.Integer, nullable=False)
    price_eur = db.Column(db.Float, nullable=False)        # montant payé en €
    stripe_session_id = db.Column(db.String(255))          # pour intégration Stripe future
    status = db.Column(db.String(20), default='pending')   # pending | completed | failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<XPPurchase user={self.user_id} xp={self.xp_amount}>'


class Skill(db.Model):
    """Modèle de compétence"""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default='Beginner')
    rating = db.Column(db.Float, default=0)
    views = db.Column(db.Integer, default=0)

    # Fichier PDF du cours (upload local)
    course_pdf = db.Column(db.String(500), nullable=True)
    pdf_total_pages = db.Column(db.Integer, default=0)   # Counted on upload

    # Image de couverture
    thumbnail = db.Column(db.String(500), nullable=True)

    # Modération
    is_flagged = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)

    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    videos = db.relationship('Video', backref='skill', lazy=True, cascade='all, delete-orphan')
    missions = db.relationship('Mission', backref='skill', lazy=True, cascade='all, delete-orphan')
    user_progress = db.relationship('UserProgress', backref='skill', lazy=True, cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Skill {self.name}>'


class Video(db.Model):
    """Modèle de vidéo"""
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)
    video_url = db.Column(db.String(500), nullable=False)
    thumbnail = db.Column(db.String(255))
    is_free = db.Column(db.Boolean, default=True)
    xp_cost = db.Column(db.Integer, default=100)   # XP to unlock (for non-free videos)
    order = db.Column(db.Integer, default=0)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Video {self.title}>'


class Mission(db.Model):
    """Modèle de mission"""
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    objective = db.Column(db.Text)
    reward_xp = db.Column(db.Integer, default=100)
    difficulty = db.Column(db.String(20), default='Easy')
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    user_missions = db.relationship('UserMission', backref='mission', lazy=True, cascade='all, delete-orphan')
    quiz_questions = db.relationship('MissionQuizQuestion', backref='mission', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('UserMissionQuizAttempt', backref='mission', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Mission {self.title}>'


class UserMission(db.Model):
    __tablename__ = 'user_missions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MissionQuizQuestion(db.Model):
    """Question de quiz attachée à une mission."""
    __tablename__ = 'mission_quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(300), nullable=False)
    option_b = db.Column(db.String(300), nullable=False)
    option_c = db.Column(db.String(300), nullable=False)
    option_d = db.Column(db.String(300), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # A|B|C|D
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserMissionQuizAttempt(db.Model):
    """Tentatives de quiz de mission par utilisateur."""
    __tablename__ = 'user_mission_quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=False)
    score_10 = db.Column(db.Float, nullable=False)
    passed = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    progress_percentage = db.Column(db.Integer, default=0)
    videos_watched = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer)
    is_completed = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)


class ContentUnlock(db.Model):
    """Trace les déverrouillages de contenu (vidéos, PDF) par utilisateur."""
    __tablename__ = 'content_unlocks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    # content_type: 'video' | 'pdf_full'
    content_type = db.Column(db.String(20), nullable=False)
    # content_ref: video_id as str, or 'full' for PDF
    content_ref = db.Column(db.String(50), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContentUnlock user={self.user_id} type={self.content_type} ref={self.content_ref}>'


# ── Badges ───────────────────────────────────────────────────────────────────

class Badge(db.Model):
    """Badge rare gagnable (définition globale)."""
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)   # identifiant unique
    icon = db.Column(db.String(10), nullable=False)               # emoji
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rarity = db.Column(db.String(20), default='common')           # common | rare | epic | legendary
    # Condition: type + valeur numérique (ex. xp >= 500)
    condition_type = db.Column(db.String(30), nullable=False)
    condition_value = db.Column(db.Integer, default=0)

    user_badges = db.relationship('UserBadge', backref='badge', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Badge {self.key}>'


class UserBadge(db.Model):
    """Badge obtenu par un utilisateur."""
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserBadge user={self.user_id} badge={self.badge_id}>'


# ── Follow ───────────────────────────────────────────────────────────────────

class Follow(db.Model):
    """Suivi entre utilisateurs."""
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id'),)

    def __repr__(self):
        return f'<Follow {self.follower_id} -> {self.following_id}>'
