import json



# Function to insert a new emotion record
def insert_emotion(connection, cursor,emotion):
    cursor.execute("""
    INSERT INTO emotion_history (emotion)
    VALUES (?)
    """, (emotion,))
    connection.commit()

# Function to fetch the latest emotion
def fetch_latest_emotion(connection, cursor,):
    cursor.execute("""
    SELECT emotion, timestamp
    FROM emotion_history
    ORDER BY timestamp DESC
    LIMIT 1
    """)
    row = cursor.fetchone()
    if row is None:
        return None
    # If using default sqlite3 cursor (tuple), access by index
    # If using Row factory, access by column name
    return row["emotion"] if isinstance(row, dict) or hasattr(row, "__getitem__") and "emotion" in row else row[0]

# Function to fetch all emotions
def fetch_all_emotions(connection, cursor):
    cursor.execute("""
    SELECT emotion,timestamp
    FROM emotion_history
    ORDER BY timestamp DESC
    """)
    return cursor.fetchall()

# Function to insert a new task with subtasks
def insert_task_with_subtasks(connection, cursor, task_name, subtasks):
    # Insert the main task
    cursor.execute("""
    INSERT INTO tasks (task_name)
    VALUES (?)
    """, (task_name,))
    task_id = cursor.lastrowid

    # Insert the subtasks and collect their IDs
    subtask_data = []
    for order, subtask in enumerate(subtasks, start=1):
        cursor.execute("""
        INSERT INTO subtasks (task_id, subtask_order, subtask_name, completed)
        VALUES (?, ?, ?, ?)
        """, (task_id, order, subtask,0))
        subtask_id = cursor.lastrowid
        subtask_data.append({"id": subtask_id, "text": subtask, "completed": False})

    connection.commit()
    return task_id, subtask_data

# Function to fetch the latest task and its subtasks
def fetch_latest_task_with_subtasks(connection, cursor):
    # Fetch the latest task
    cursor.execute("""
    SELECT id, task_name, timestamp
    FROM tasks
    ORDER BY timestamp DESC
    LIMIT 1
    """)
    task = cursor.fetchone()

    if not task:
        return None, []

    task_id, task_name, timestamp = task

    # Fetch the subtasks for the latest task
    cursor.execute("""
    SELECT id, subtask_name, completed
    FROM subtasks
    WHERE task_id = ?
    ORDER BY subtask_order ASC
    """, (task_id,))
    subtasks = cursor.fetchall()

    return {
        "id": task_id,
        "name": task_name,
        "timestamp": timestamp,
        "subtasks": [
            {"id": row[0], "text": row[1], "completed": bool(row[2])} for row in subtasks
        ]
    }

# Function to update the status of a subtask
def update_subtask_status(connection, cursor, subtask_id, completed):
    cursor.execute("""
    UPDATE subtasks
    SET completed = ?
    WHERE id = ?
    """, (completed, subtask_id))
    connection.commit()



