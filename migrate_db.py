import sqlite3

def migrate():
    conn = sqlite3.connect('projects.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE project ADD COLUMN repo_url TEXT")
        conn.commit()
        print("Migração bem-sucedida: Coluna repo_url adicionada.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Migração ignorada: Coluna repo_url já existe.")
        else:
            print(f"Falha na migração: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
