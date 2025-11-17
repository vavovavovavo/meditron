from flask import Flask, request, jsonify, send_from_directory
import psycopg2
import os
import json

app = Flask(__name__)

# Подключение к БД

# database_url = os.getenv("DATABASE_URL")
# conn = psycopg2.connect(database_url)
conn = psycopg2.connect(
    host="localhost",
    database="meditron_test2",
    user="postgres",
    password="12"
)
cur = conn.cursor()


# 1. POST /surveys — добавить результат анкетирования
@app.route('/surveys', methods=['POST'])
def create_survey():
    data = request.json
    user_id = data['user_id']
    anket_type = data['anket_type']
    answers = data['answers']
    visible = data.get('visible', True)

    cur.execute(
        "INSERT INTO surveys (user_id, anket_type, visible, answers) VALUES (%s, %s, %s, %s)",
        (user_id, anket_type, visible, json.dumps(answers))
    )
    conn.commit()

    return jsonify({"status": "ok"}), 201

# 2. GET /surveys/stats/<department_id>?visible=1 — статистика по отделу (только видимые)
# @app.route('/surveys/stats/<int:department_id>', methods=['GET'])
# def get_stats_by_department(department_id):
#     visible = request.args.get('visible', type=int)
#     if visible is not None and visible != 1:
#         return jsonify({"error": "visible must be 1"}), 400

#     cur.execute("""
#         SELECT
#             s.anket_type,
#             COUNT(*) AS count,
#             JSON_AGG(s.answers) AS answers
#         FROM surveys s
#         JOIN users u ON s.user_id = u.id
#         WHERE u.department_id = %s AND s.visible = TRUE
#         GROUP BY s.anket_type
#     """, (department_id,))

#     rows = cur.fetchall()

#     result = []
#     for row in rows:
#         result.append({
#             "anket_type": row[0],
#             "count": row[1],
#             "answers": row[2]
#         })

#     return jsonify(result)

@app.route('/surveys/stats/<int:department_id>')
def get_dept_stats(department_id):
    visible = request.args.get('visible', type=int)
    # if visible != 1:
    #     return jsonify({"error": "visible must be 1"}), 400

    cur = conn.cursor()
    cur.execute("""
        SELECT s.answers->'ans' AS ans_array
        FROM surveys s
        JOIN users u ON s.user_id = u.id
        WHERE u.department_id = %s AND s.visible = TRUE
    """, (department_id,))

    rows = cur.fetchall()
    print(len(rows))
    if not rows:
        return jsonify({"error": "No data"}), 404

    # Извлекаем все ответы
    all_answers = []
    for row in rows:
        ans = row[0]
        if isinstance(ans, list) and len(ans) == 10:
            all_answers.append(ans)

    if not all_answers:
        return jsonify({"error": "No valid answers"}), 400

    # Подготавливаем гистограммы по каждому из 10 вопросов
    histograms = []
    for q in range(10):  # q0...q9
        values = [ans[q] for ans in all_answers if isinstance(ans[q], (int, float))]
        # Строим гистограмму: количество ответов для значений 0–10
        hist = [0] * 11  # индексы 0..10
        for v in values:
            if 1 <= v <= 10:
                hist[int(v)] += 1
        histograms.append(hist)

    return jsonify({
        "department_id": department_id,
        "question_histograms": histograms  # массив из 10 гистограмм
    })

# 3. GET /surveys/<user_id> — получить все анкеты пользователя
@app.route('/surveys/<int:user_id>', methods=['GET'])
def get_user_surveys(user_id):
    cur.execute(
        "SELECT id, anket_type, visible, answers, created_at FROM surveys WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cur.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "anket_type": row[1],
            "visible": row[2],
            "answers": row[3],
            "created_at": row[4]
        })

    return jsonify(result)

@app.route('/dashboard')
def dashboard():
    return send_from_directory('.', 'dashboard.html')


if __name__ == '__main__':
    app.run(debug=True, host='172.18.208.1', port='5000')