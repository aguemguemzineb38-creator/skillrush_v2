from flask import Blueprint
from app.controllers import (MainController, AuthController,
                              SkillController, UserController, MissionController,
                              OnboardingController)

def register_blueprints(app):

    # ── Main ──────────────────────────────────────────────────────────────────
    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    @main_bp.route('/dashboard')
    def dashboard():
        return MainController.dashboard()

    @main_bp.route('/explore-skills')
    def explore_skills():
        return MainController.explore_skills()

    @main_bp.route('/skill/<int:skill_id>')
    def skill_detail(skill_id):
        return MainController.skill_detail(skill_id)

    @main_bp.route('/leaderboard')
    def leaderboard():
        return MainController.leaderboard()

    @main_bp.route('/network')
    def network():
        return MainController.network()

    @main_bp.route('/cours-refuse')
    def rejected_course():
        return MainController.rejected_course()

    @main_bp.route('/help')
    def help_page():
        return MainController.help_page()

    @main_bp.route('/profile/<int:user_id>')
    def user_profile(user_id):
        return MainController.user_profile(user_id)

    @main_bp.route('/espace/utilisateur')
    def user_space():
        return MainController.user_space()

    @main_bp.route('/espace/administrateur')
    def admin_space():
        return MainController.admin_space()

    @main_bp.route('/espace/moderation')
    def moderation_space():
        return MainController.moderation_space()

    app.register_blueprint(main_bp)

    # ── Auth ──────────────────────────────────────────────────────────────────
    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

    @auth_bp.route('/register', methods=['GET', 'POST'])
    def register():
        return AuthController.register()

    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        return AuthController.login()

    @auth_bp.route('/admin-login', methods=['GET', 'POST'])
    def admin_login():
        return AuthController.admin_login()

    @auth_bp.route('/moderator-login', methods=['GET', 'POST'])
    def moderator_login():
        return AuthController.moderator_login()

    @auth_bp.route('/logout')
    def logout():
        return AuthController.logout()

    @auth_bp.route('/google')
    def google_login():
        return AuthController.google_login()

    @auth_bp.route('/google/callback')
    def google_callback():
        return AuthController.google_callback()

    app.register_blueprint(auth_bp)

    # ── Skills ────────────────────────────────────────────────────────────────
    skill_bp = Blueprint('skill', __name__, url_prefix='/skill')

    @skill_bp.route('/create', methods=['GET', 'POST'])
    def create_skill():
        return SkillController.create_skill()

    @skill_bp.route('/<int:skill_id>/add-video', methods=['GET', 'POST'])
    def add_video(skill_id):
        return SkillController.add_video(skill_id)

    @skill_bp.route('/<int:skill_id>/watch/<int:video_id>')
    def watch_video(skill_id, video_id):
        return SkillController.watch_video(skill_id, video_id)

    @skill_bp.route('/<int:skill_id>/rate', methods=['POST'])
    def rate_skill(skill_id):
        return SkillController.rate_skill(skill_id)

    @skill_bp.route('/my-skills')
    def my_skills():
        return SkillController.my_skills()

    @skill_bp.route('/<int:skill_id>/edit', methods=['GET', 'POST'])
    def edit_skill(skill_id):
        return SkillController.edit_skill(skill_id)

    @skill_bp.route('/<int:skill_id>/delete', methods=['POST'])
    def delete_skill(skill_id):
        return SkillController.delete_skill(skill_id)

    @skill_bp.route('/<int:skill_id>/flag', methods=['POST'])
    def flag_skill(skill_id):
        return UserController.flag_skill(skill_id)

    @skill_bp.route('/<int:skill_id>/unlock-video/<int:video_id>', methods=['POST'])
    def unlock_video(skill_id, video_id):
        return SkillController.unlock_video(skill_id, video_id)

    @skill_bp.route('/<int:skill_id>/unlock-pdf', methods=['POST'])
    def unlock_pdf_full(skill_id):
        return SkillController.unlock_pdf_full(skill_id)

    @skill_bp.route('/<int:skill_id>/pdf')
    def serve_skill_pdf(skill_id):
        return SkillController.serve_skill_pdf(skill_id)

    app.register_blueprint(skill_bp)

    # ── User ──────────────────────────────────────────────────────────────────
    user_bp = Blueprint('user', __name__, url_prefix='/user')

    @user_bp.route('/<int:user_id>')
    def profile(user_id):
        return UserController.profile(user_id)

    @user_bp.route('/edit-profile', methods=['GET', 'POST'])
    def edit_profile():
        return UserController.edit_profile()

    @user_bp.route('/my-progress')
    def my_progress():
        return UserController.my_progress()

    @user_bp.route('/buy-xp', methods=['GET'])
    def buy_xp():
        return UserController.buy_xp()

    @user_bp.route('/buy-xp/process', methods=['POST'])
    def process_xp_purchase():
        return UserController.process_xp_purchase()

    @user_bp.route('/daily-reward', methods=['POST'])
    @user_bp.route('/claim-daily', methods=['POST'])
    def daily_reward():
        return UserController.daily_reward()

    @user_bp.route('/<int:user_id>/follow', methods=['POST'])
    def follow_user(user_id):
        return UserController.follow_user(user_id)

    app.register_blueprint(user_bp)

    # ── Missions ──────────────────────────────────────────────────────────────
    mission_bp = Blueprint('mission', __name__, url_prefix='/mission')

    @mission_bp.route('/')
    def missions_list():
        return MissionController.missions_list()

    @mission_bp.route('/<int:mission_id>')
    def mission_detail(mission_id):
        return MissionController.mission_detail(mission_id)

    @mission_bp.route('/<int:mission_id>/start', methods=['GET', 'POST'])
    def start_mission(mission_id):
        return MissionController.start_mission(mission_id)

    @mission_bp.route('/<int:mission_id>/complete', methods=['GET', 'POST'])
    def complete_mission(mission_id):
        return MissionController.complete_mission(mission_id)

    @mission_bp.route('/<int:mission_id>/quiz', methods=['GET', 'POST'])
    def take_quiz(mission_id):
        return MissionController.take_quiz(mission_id)

    @mission_bp.route('/my-missions')
    def my_missions():
        return MissionController.my_missions()

    @mission_bp.route('/skill/<int:skill_id>/create', methods=['GET', 'POST'])
    def create_mission(skill_id):
        return MissionController.create_mission(skill_id)

    app.register_blueprint(mission_bp)

    # ── Admin ─────────────────────────────────────────────────────────────────
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

    @admin_bp.route('/users')
    def admin_users():
        return UserController.admin_users()

    @admin_bp.route('/stats')
    def admin_stats():
        return UserController.admin_stats()

    @admin_bp.route('/user/<int:user_id>/block', methods=['POST'])
    def block_user(user_id):
        return UserController.block_user(user_id)

    @admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
    def change_role(user_id):
        return UserController.change_role(user_id)

    @admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
    def delete_user(user_id):
        return UserController.delete_user(user_id)

    app.register_blueprint(admin_bp)

    # ── Modération ────────────────────────────────────────────────────────────
    moderation_bp = Blueprint('moderation', __name__, url_prefix='/moderation')

    @moderation_bp.route('/')
    def moderation_dashboard():
        return UserController.moderation_dashboard()

    @moderation_bp.route('/skill/<int:skill_id>/approve', methods=['POST'])
    def approve_skill(skill_id):
        return UserController.approve_skill(skill_id)

    @moderation_bp.route('/skill/<int:skill_id>/reject', methods=['POST'])
    def reject_skill(skill_id):
        return UserController.reject_skill(skill_id)

    @moderation_bp.route('/skill/<int:skill_id>/delete', methods=['POST'])
    def delete_skill(skill_id):
        return UserController.delete_skill(skill_id)

    @moderation_bp.route('/skill/<int:skill_id>/ai-review')
    def ai_review_skill(skill_id):
        return UserController.ai_review_skill(skill_id)

    app.register_blueprint(moderation_bp)

    # ── Onboarding ────────────────────────────────────────────────────────────
    onboarding_bp = Blueprint('onboarding', __name__, url_prefix='/onboarding')

    @onboarding_bp.route('/step1', methods=['GET', 'POST'])
    def step1():
        return OnboardingController.step1()

    @onboarding_bp.route('/step2', methods=['GET', 'POST'])
    def step2():
        return OnboardingController.step2()

    @onboarding_bp.route('/step3')
    def step3():
        return OnboardingController.step3()

    app.register_blueprint(onboarding_bp)
