# memory_cache.py

import sqlite3, time

# setup
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute(
	"CREATE TABLE cache (key TEXT PRIMARY KEY, value TEXT, expires_at REAL)"
	)
conn.commit()

# GET data from cache function
def cache_get(key):
	cur.execute(
		"SELECT value, expires_at FROM cache WHERE key=?", (key,)
		)
	row = cur.fetchone()
	if row:
		value, expires_at = row
		if expires_at > time.time():
			return value
		else:
			cur.execute(
				"DELETE FROM cache WHERE key=?", ("")
				)
			conn.commit()
	return None

# Function to set data to cache
def cache_set(key, value, ttl):
	expires_at = time.time() + ttl
	curr.execute(
		"INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
		(key, value, expires_at)
		)
	conn.commit()







