import datetime
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="recommendation_system",
    user="your_username",
    password="your_password"
)
cursor = conn.cursor()

# 선호도 관리 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS feedback_preference (
    situation TEXT,
    feedback TEXT,
    preference_score REAL,
    timestamp TIMESTAMP,
    PRIMARY KEY (situation, feedback)
)
''')
conn.commit()

initial_preference_score = 0.1
decay_factor = 0.99
min_preference_score = 0.01
update_interval_days = 90  # 3개월

preference_score = initial_preference_score

# 상황에 대한 선호도가 가장 높은 피드백 출력
def output_top_preference(situation):
    cursor.execute('''
    SELECT feedback FROM feedback_preference
    WHERE situation = %s
    ORDER BY preference_score DESC
    LIMIT 1
    ''', (situation,))
    top_feedback = cursor.fetchone()
    if top_feedback:
        print(f"{top_feedback[0]}")
    else:
        print(f"새로운 피드백 선호도를 추가해주세요.")

# 피드백에 대한 선호도 저장 및 업데이트 함수
def update_preference(situation, feedback, preference):
    global preference_score
    if preference > 0:
        new_preference_score = min(preference_score * (1 + decay_factor), 1.0)
    else:
        new_preference_score = max(preference_score * decay_factor, min_preference_score)
    
    cursor.execute('''
    INSERT INTO feedback_preference (situation, feedback, preference_score, timestamp)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (situation, feedback) DO UPDATE SET
        preference_score = %s,
        timestamp = %s
    ''', (situation, feedback, new_preference_score, datetime.datetime.now(), new_preference_score, datetime.datetime.now()))
    conn.commit()


# 3개월이 지난 오래된 피드백 삭제 함수
# def cleanup_old_preferences():
#    threshold_date = datetime.datetime.now() - datetime.timedelta(days=update_interval_days)
#    cursor.execute('''
#    DELETE FROM feedback_preference WHERE timestamp < %s
#    ''', (threshold_date,))
#    conn.commit()

# 프롬프트를 기반 상황별 선호도 높은 피드백 출력, 선호도 업데이트
def prompt_based_preference(prompt):
    situation = prompt.lower()
    output_top_preference(situation)
    feedback = input("상황에 맞는 피드백을 입력하세요: ")
    preference = float(input("피드백 선호도 (1: 좋아요, -1: 싫어요): "))
    update_preference(situation, feedback, preference)

# cleanup_old_preferences()
