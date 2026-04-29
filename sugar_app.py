"""
Sugar Price Monte Carlo Risk Model — with integrated Parameter Estimator
Run with: streamlit run sugar_app.py
Requires: pip install streamlit plotly numpy scipy matplotlib pandas
"""
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

# ── Database Setup ─────────────────────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(st.secrets["database"]["url"])

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulations (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    model_type TEXT,
                    spot_price REAL,
                    horizon_days INTEGER,
                    results TEXT,
                    FOREIGN KEY(username) REFERENCES users(username)
                )
            """)
        conn.commit()

def save_simulation(username, model_type, spot_price, horizon_days, results_json):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO simulations(username, timestamp, model_type, spot_price, horizon_days, results)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, datetime.utcnow().isoformat(), model_type, spot_price, horizon_days, results_json))
        conn.commit()

def get_user_simulations(username):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, timestamp, model_type, spot_price, horizon_days
                FROM simulations WHERE username = %s ORDER BY timestamp DESC LIMIT 100
            """, (username,))
            return cursor.fetchall()

def get_simulation_detail(sim_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, timestamp, model_type, spot_price, horizon_days, results
                FROM simulations WHERE id = %s
            """, (sim_id,))
            return cursor.fetchone()

def delete_simulation(sim_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM simulations WHERE id = %s", (sim_id,))
        conn.commit()

init_db()

# Keep authenticate() and rest of code