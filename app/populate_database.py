import csv
from cassandra.cluster import Cluster
from faker import Faker
import uuid
import argparse

# Initialize Faker
fake = Faker()

# Function to read books from CSV and insert into the database
def insert_books_from_csv(session, file_path):
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            session.execute("""
                INSERT INTO books (book_id, title, author, genre, published_year) 
                VALUES (%s, %s, %s, %s, %s)
            """, (uuid.UUID(row['book_id']), row['title'], row['author'], row['genre'], int(row['published_year'])))

# Function to insert randomly generated books into the database
def insert_random_books(session, num_records=200):
    genres = ['Mystery', 'Thriller', 'Romance', 'Science Fiction', 'Fantasy', 'Horror', 'Historical Fiction', 'Non-Fiction']
    for _ in range(num_records):
        book_id = uuid.uuid4()
        title = fake.sentence(nb_words=3).replace('.', '')
        author = fake.name()
        genre = fake.random_element(elements=genres)
        published_year = int(fake.year())
        session.execute("""
            INSERT INTO books (book_id, title, author, genre, published_year) 
            VALUES (%s, %s, %s, %s, %s)
        """, (book_id, title, author, genre, published_year))

def main(csv_file=None, num_records=200):
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
            reservation_id UUID,
            book_id UUID,
            user_id INT,
            reserved_at TIMESTAMP,
            PRIMARY KEY (user_id, book_id)
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

    # Create reservation_by_book_id table
    session.execute("""
        CREATE TABLE IF NOT EXISTS reservation_by_book_id (
            book_id UUID PRIMARY KEY
        )
    """)

    print("Tables created successfully.")
    print("Populating books...")

    if csv_file is not None:
        print(f"Inserting book records from {csv_file}...")
        insert_books_from_csv(session, csv_file)
    else:
        print(f"Generating {num_records} random book records...")
        insert_random_books(session, num_records)

    print("Books populated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Populate Cassandra database with book records.')
    parser.add_argument('--csv_file', type=str, help='Path to the CSV file containing book records.')
    parser.add_argument('--num_records', type=int, default=200, help='Number of random book records to generate if not using a CSV file.')
    
    args = parser.parse_args()

    main(args.csv_file, args.num_records)