import json
import psycopg

def load_json_to_postgres(json_path, db_params):
    with open(json_path, 'r') as f:
        data = json.load(f)

    conn = None
    try:
        conn = psycopg.connect(**db_params)
        cur = conn.cursor()
        for record in data:
            cur.execute(
                "INSERT INTO users (user_id, username, email, creation_date) VALUES (%s, %s, %s, %s)",
                (record['id'], record['username'], record['email'], record['creation_date'])
            )
        conn.commit()
        print("Data loaded successfully into PostgreSQL.")
        cur.close()
    except (Exception, psycopg.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    # IMPORTANT: Replace with your actual database connection details
    db_connection_params = {
        "host": "localhost",
        "database": "mydatabase",
        "user": "myuser",
        "password": "mypassword"
    }
    load_json_to_postgres('users.json', db_connection_params)