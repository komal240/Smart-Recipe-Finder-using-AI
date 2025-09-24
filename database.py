import psycopg2

conn = psycopg2.connect(
    host="ep-snowy-dawn-a1jislxp-pooler.ap-southeast-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_hvlDiTps72Ve",
    port="5432",
    sslmode="require"
)

cur = conn.cursor()

def query(q, params=None):
    print(q)
    """
    Execute a SQL query safely.
    Supports parameterized queries to avoid SQL injection and special character issues.
    """
    if params:
        cur.execute(q, params)
    else:
        cur.execute(q)

    if q.strip().lower().startswith("select"):
        result = cur.fetchall()
        return result
    else:
        conn.commit()
        return 0
