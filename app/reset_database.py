from cassandra.cluster import Cluster

class CassandraStateResetter:
    def __init__(self, contact_points):
        self.cluster = Cluster(contact_points=contact_points)
        self.session = self.cluster.connect()

    def reset_state(self):
        # truncate tables
        self.session.execute("TRUNCATE library.books")
        self.session.execute("TRUNCATE library.reservations")

        # Drop tables if they exist
        self.session.execute("DROP TABLE IF EXISTS library.books")
        self.session.execute("DROP TABLE IF EXISTS library.reservations")

        print("Tables dropped successfully.")

if __name__ == "__main__":
    contact_points = ['172.28.1.1', '172.28.1.2', '172.28.1.3']
    resetter = CassandraStateResetter(contact_points)
    resetter.reset_state()
