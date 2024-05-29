from cassandra.cluster import Cluster
from faker import Faker
import uuid

fake = Faker()

contact_points = ['cas1', 'cas2', 'cas3']
cluster = Cluster(contact_points=contact_points)
session = cluster.connect()

# Create keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS library 
    WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 3}
""")

session.execute("USE library")

# Create books table
session.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id UUID PRIMARY KEY,
        title TEXT,
        author TEXT,
        genre TEXT,
        published_year INT
    )
""")

# Create reservations table
session.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id UUID PRIMARY KEY,
        book_id UUID,
        user_id INT,
        reserved_at TIMESTAMP
    )
""")

# Create user_reservations table
session.execute("""
    CREATE TABLE IF NOT EXISTS user_reservations (
        user_id INT,
        reservation_id UUID,
        book_id UUID,
        reserved_at TIMESTAMP,
        PRIMARY KEY (user_id, reservation_id)
    )
""")

# Create book_reservations table
session.execute("""
    CREATE TABLE IF NOT EXISTS book_reservations (
        book_id UUID,
        reservation_id UUID,
        user_id INT,
        reserved_at TIMESTAMP,
        PRIMARY KEY (book_id, reservation_id)
    )
""")

print("Tables created successfully.")
print("Populating books...")

# Populate books table with 200 records, setting available to True
for i in range(200):
    book_id = uuid.uuid4()
    title = fake.sentence(nb_words=3).replace('.', '')
    author = fake.name()
    genres = ['Mystery', 'Thriller', 'Romance', 'Science Fiction', 'Fantasy', 'Horror', 'Historical Fiction', 'Non-Fiction']
    genre = fake.random_element(elements=genres)
    published_year = int(fake.year())
    available = True
    
    session.execute("""
        INSERT INTO books (book_id, title, author, genre, published_year, available) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (book_id, title, author, genre, published_year, available))

print("Books populated successfully.")