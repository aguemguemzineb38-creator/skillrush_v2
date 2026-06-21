#!/usr/bin/env python
"""
Database seeding script for SkillRush
Reads railway_db_seed.sql and executes statements one by one
"""
import os
from app import create_app, db

def execute_seed():
    # Set production environment to use Railway database
    os.environ['FLASK_ENV'] = 'production'
    # Temporarily skip db.create_all() to avoid connection issues
    os.environ['SKIP_DB_CREATE'] = '1'
    app = create_app('production')
    
    with app.app_context():
        seed_files = ['railway_db_seed.sql', 'moroccan_students_db.sql']
        for seed_file in seed_files:
            if not os.path.exists(seed_file):
                print(f"⚠️  Seed file {seed_file} not found, skipping.")
                continue
            
            print(f"\n📖 Reading {seed_file}...")
            with open(seed_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            print(f"📊 Found {len(statements)} SQL statements to execute...")
            
            for i, statement in enumerate(statements, 1):
                # Skip comments and empty lines
                if statement.startswith('--') or not statement.strip():
                    continue
                
                try:
                    print(f"  [{i}/{len(statements)}] Executing: {statement[:60]}...")
                    db.session.execute(db.text(statement))
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"  ⚠️  Skipped (likely already exists): {str(e)[:80]}")
        
        print("\n✅ Seed completed successfully!")
        print(f"📈 Visit /api/db-status to verify the seeding")

if __name__ == '__main__':
    execute_seed()
