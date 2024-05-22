from cassandra.cluster import Cluster
from faker import Faker
import uuid

fake = Faker()

contact_points = ['172.28.1.1', '172.28.1.2', '172.28.1.3']
cluster = Cluster(contact_points=contact_points)
session = cluster.connect()

# Create keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS library 
    WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 3}
""")

session.execute("USE library")

# Create books table with reserved column as BOOLEAN
session.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id UUID PRIMARY KEY,
        title TEXT,
        author TEXT,
        reserved BOOLEAN
    )
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id UUID PRIMARY KEY,
        book_id UUID,
        user_id UUID
    )
""")
# Both needed so it's faster to query by book_id or user_id
session.execute("""
    CREATE INDEX IF NOT EXISTS ON reservations (book_id)
""")

session.execute("""
    CREATE INDEX IF NOT EXISTS ON reservations (user_id)
""")

print("Books table created successfully.")
print("Populating books...")

# Populate books table with 200 records, setting reserved to False
for i in range(200):
    book_id = uuid.uuid4()
    title = fake.sentence(nb_words=3)
    author = fake.name()
    reserved = False
    
    session.execute("INSERT INTO books (book_id, title, author, reserved) VALUES (%s, %s, %s, %s)", (book_id, title, author, reserved))

print("Books populated successfully.")
  