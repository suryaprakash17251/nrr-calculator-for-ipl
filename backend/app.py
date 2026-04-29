from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
DB = "db.sqlite3"


# -------------------------------
# DB INIT (runs once)
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team TEXT,
            runs_scored INTEGER,
            overs_faced REAL,
            runs_conceded INTEGER,
            overs_bowled REAL
        )
    ''')

    conn.commit()
    conn.close()


# -------------------------------
# OVERS CONVERSION (IMPORTANT)
# -------------------------------
def convert_overs(overs):
    overs = str(overs)

    if '.' in overs:
        o, balls = overs.split('.')
        return int(o) + int(balls) / 6
    return float(overs)


# -------------------------------
# ADD MATCH API
# -------------------------------
@app.route('/add_match', methods=['POST'])
def add_match():
    data = request.json

    team = data['team']
    runs_scored = int(data['runs_scored'])
    overs_faced = convert_overs(data['overs_faced'])
    runs_conceded = int(data['runs_conceded'])
    overs_bowled = convert_overs(data['overs_bowled'])

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO matches (team, runs_scored, overs_faced, runs_conceded, overs_bowled)
        VALUES (?, ?, ?, ?, ?)
    ''', (team, runs_scored, overs_faced, runs_conceded, overs_bowled))

    conn.commit()
    conn.close()

    return jsonify({"message": "Match added successfully"})


# -------------------------------
# GET NRR API
# -------------------------------
@app.route('/nrr/<team>', methods=['GET'])
def get_nrr(team):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute('SELECT runs_scored, overs_faced, runs_conceded, overs_bowled FROM matches WHERE team=?', (team,))
    rows = cur.fetchall()

    conn.close()

    if not rows:
        return jsonify({
            "team": team,
            "matches": 0,
            "NRR": 0
        })

    total_runs = sum(r[0] for r in rows)
    total_overs = sum(r[1] for r in rows)
    total_conceded = sum(r[2] for r in rows)
    total_bowled = sum(r[3] for r in rows)

    # Safety check
    if total_overs == 0 or total_bowled == 0:
        return jsonify({"NRR": 0})

    nrr = (total_runs / total_overs) - (total_conceded / total_bowled)

    return jsonify({
        "team": team,
        "matches": len(rows),
        "total_runs": total_runs,
        "total_overs": round(total_overs, 2),
        "total_conceded": total_conceded,
        "total_bowled": round(total_bowled, 2),
        "NRR": round(nrr, 3)
    })


# -------------------------------
# GET ALL TEAMS (Leaderboard)
# -------------------------------
@app.route('/teams', methods=['GET'])
def get_all_teams():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute('SELECT DISTINCT team FROM matches')
    teams = [t[0] for t in cur.fetchall()]

    result = []

    for team in teams:
        cur.execute('SELECT runs_scored, overs_faced, runs_conceded, overs_bowled FROM matches WHERE team=?', (team,))
        rows = cur.fetchall()

        total_runs = sum(r[0] for r in rows)
        total_overs = sum(r[1] for r in rows)
        total_conceded = sum(r[2] for r in rows)
        total_bowled = sum(r[3] for r in rows)

        if total_overs == 0 or total_bowled == 0:
            nrr = 0
        else:
            nrr = (total_runs / total_overs) - (total_conceded / total_bowled)

        result.append({
            "team": team,
            "matches": len(rows),
            "NRR": round(nrr, 3)
        })

    # Sort by NRR descending
    result.sort(key=lambda x: x['NRR'], reverse=True)

    conn.close()

    return jsonify(result)


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)