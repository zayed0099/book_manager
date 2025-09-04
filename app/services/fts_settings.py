from flask_sqlalchemy import SQLAlchemy
from app.extensions import db

with db.engine.connect() as conn:
    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS book_fts 
    USING fts5(
    title, subtitle, description, isbn1, isbn2, language);
    """)
    
    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS author_fts 
    USING fts5(author);
    """)
    
    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS publisher_fts 
    USING fts5(publisher);
    """)

    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS category_fts 
    USING fts5(category);
    """)

    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS review_fts 
    USING fts5(review);
    """)
    conn.commit()


def add_to_fts(table_name , row_id, **fields):
	with db.engine.begin() as conn:
		columns = ",".join(fields.keys())
		placeholders = ",".join("?" for _ in fields)
		values = tuple([row_id] + list(fields.values()))

		sql = (
			f'''INSERT INTO {table_name}_fts (row_id, {columns})
			VALUES (? , {placeholders})'''
		)

		conn.execute(sql, values)
		conn.commit()
