import sqlite3
import os

# 确保数据库目录存在
if not os.path.exists('database'):
    os.makedirs('database')

# 连接到SQLite数据库
def get_db_connection():
    conn = sqlite3.connect('database/users.db')
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # 创建问题表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 创建回答表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        model_name TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

# 添加用户
def add_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 用户名已存在
        return False
    finally:
        conn.close()

# 验证用户
def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return {"id": user["id"], "username": user["username"]}
    else:
        return None

# 检查用户名是否存在
def username_exists(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    conn.close()
    return user is not None

# 保存用户问题
def save_question(user_id, question_content):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO questions (user_id, content)
    VALUES (?, ?)
    """, (user_id, question_content))
    
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id

# 保存模型回答
def save_answer(question_id, model_name, answer_content):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO answers (question_id, model_name, content)
    VALUES (?, ?, ?)
    """, (question_id, model_name, answer_content))
    
    answer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return answer_id

# 获取用户的所有问题及回答
def get_user_history(user_id, limit=20):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取用户最近的问题
    cursor.execute("""
    SELECT id, content, timestamp
    FROM questions
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
    """, (user_id, limit))
    
    questions = []
    for question_row in cursor.fetchall():
        question = dict(question_row)
        
        # 获取该问题的所有回答
        cursor.execute("""
        SELECT model_name, content, timestamp
        FROM answers
        WHERE question_id = ?
        ORDER BY model_name
        """, (question["id"],))
        
        answers = [dict(row) for row in cursor.fetchall()]
        question["answers"] = answers
        questions.append(question)
    
    conn.close()
    return questions

# 删除指定问题及其所有回答
def delete_question(question_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查问题是否属于用户
    cursor.execute("SELECT id FROM questions WHERE id = ? AND user_id = ?", (question_id, user_id))
    question = cursor.fetchone()
    
    if not question:
        conn.close()
        return False
    
    # 删除问题的所有回答
    cursor.execute("DELETE FROM answers WHERE question_id = ?", (question_id,))
    
    # 删除问题
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    
    conn.commit()
    conn.close()
    return True

# 清空用户的所有问题和回答
def clear_user_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取用户的所有问题ID
    cursor.execute("SELECT id FROM questions WHERE user_id = ?", (user_id,))
    questions = cursor.fetchall()
    
    # 删除每个问题的所有回答
    for question in questions:
        cursor.execute("DELETE FROM answers WHERE question_id = ?", (question["id"],))
    
    # 删除所有问题
    cursor.execute("DELETE FROM questions WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    return True

# 兼容旧版函数
def save_chat_history(user_id, query, response, model_name):
    question_id = save_question(user_id, query)
    save_answer(question_id, model_name, response)
    return question_id

def get_chat_history(user_id, limit=20):
    return get_user_history(user_id, limit)

def delete_chat_history(history_id, user_id):
    return delete_question(history_id, user_id)

def clear_chat_history(user_id):
    return clear_user_history(user_id)

# 修改用户密码
def update_password(user_id, old_password, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查用户ID和旧密码是否匹配
    cursor.execute("SELECT id FROM users WHERE id = ? AND password = ?", (user_id, old_password))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return False
    
    # 更新密码
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    conn.close()
    return True

# 初始化数据库
if __name__ == "__main__":
    init_db()