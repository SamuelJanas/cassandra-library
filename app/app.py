import uuid
import time
import tornado.ioloop
import tornado.web
import cassandra
from cassandra.cluster import Cluster
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime

class LibrarySystem:
    def __init__(self, contact_points):
        self.cluster = Cluster(contact_points=contact_points)
        self.session = self.cluster.connect()
        self.session.execute("USE library")
        self.executor = ThreadPoolExecutor(max_workers=4)

    @run_on_executor
    def make_reservation(self, book_id, user_id):
        try:
            reservation_id = uuid.uuid4()

            # Check if user_id is an integer
            try:
                user_id = int(user_id)
            except ValueError:
                return {"error": "Invalid user_id."}

            # Attempt to insert into reservation_by_book_id to lock the book
            query = "INSERT INTO reservation_by_book_id (book_id) VALUES (%s) IF NOT EXISTS"
            result = self.session.execute(query, (book_id,))
            if not result.one()[0]:
                return {"error": "Book is already reserved."}

            # Check if the book exists
            book = self.session.execute("SELECT * FROM books WHERE book_id = %s", (book_id,)).one()
            if not book:
                # Clean up the lock
                self.session.execute("DELETE FROM reservation_by_book_id WHERE book_id = %s", (book_id,))
                return {"error": "Book does not exist."}

            # Proceed with reservation
            reserved_at = datetime.now()
            self.session.execute("""
                INSERT INTO book_reservations (book_id, reservation_id, user_id, reserved_at)
                VALUES (%s, %s, %s, %s)
            """, (book_id, reservation_id, user_id, reserved_at))

            self.session.execute("""
                INSERT INTO reservations (reservation_id, book_id, user_id, reserved_at)
                VALUES (%s, %s, %s, %s)
            """, (reservation_id, book_id, user_id, reserved_at))

            self.session.execute("""
                INSERT INTO user_reservations (user_id, reservation_id, book_id, reserved_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, reservation_id, book_id, reserved_at))

            # Reservation successful
            return {"message": "Reservation made successfully."}
        except Exception as e:
            # Log the error or handle it as needed
            return {"error": str(e)}
        

    @run_on_executor
    def update_reservation(self, book_id, user_id):
        try:
            user_id = int(user_id)
        except ValueError:
            return {"error": "Invalid user_id."}
        
        reservation = self.session.execute("SELECT * FROM reservations WHERE user_id = %s AND book_id = %s", (user_id, book_id)).one()
        if not reservation:
            return {"error": "Reservation not found."}
 
        # read necessary data
        reservation_id = reservation.reservation_id
        reserved_at = datetime.now()
        # update the reservation
        self.session.execute("UPDATE reservations SET reserved_at = %s WHERE user_id = %s AND book_id = %s", (reserved_at, user_id, book_id))
        self.session.execute("UPDATE user_reservations SET reserved_at = %s WHERE reservation_id = %s AND user_id = %s", (reserved_at, reservation_id, user_id))
        self.session.execute("UPDATE book_reservations SET reserved_at = %s WHERE reservation_id = %s AND book_id = %s", (reserved_at, reservation_id, book_id))
        return {"message": "Reservation updated successfully."}

    @run_on_executor
    def remove_reservation(self, book_id, user_id):
        # Check if user_id is an integer
        try:
            user_id = int(user_id)
        except ValueError:
            return {"error": "Invalid user_id."}

        # Check book_reservation if the book is reserved
        result = self.session.execute("SELECT * FROM book_reservations WHERE book_id = %s", (book_id,))
        book = result.one() if result else None
        if book:
            reservation_id = book.reservation_id
            # Check if the user is the owner of the reservation
            if int(book.user_id) != user_id:
                return {"error": "User is not the owner of the reservation."}
            
            # Remove the reservation
            self.session.execute("DELETE FROM book_reservations WHERE book_id = %s AND reservation_id = %s", (book_id, reservation_id))
            self.session.execute("DELETE FROM reservations WHERE book_id = %s AND user_id = %s", (book_id, user_id))
            self.session.execute("DELETE FROM user_reservations WHERE user_id = %s AND reservation_id = %s", (user_id, reservation_id))
            
            # Remove the lock
            self.session.execute("DELETE FROM reservation_by_book_id WHERE book_id = %s", (book_id,))

            return {"message": "Reservation removed successfully."}

        return {"error": "Reservation not found."}
        

    @run_on_executor
    def get_books(self):
        # get 100 books
        rows = self.session.execute("SELECT * FROM books LIMIT 100")
        return [{"book_id": str(row.book_id), "title": row.title, "author": row.author, "genre": row.genre, "published_year": row.published_year} for row in rows]

    @run_on_executor
    def get_reservations(self):
        rows = self.session.execute("SELECT * FROM reservations")
        reservations = [{"reservation_id": str(row.reservation_id), "book_id": str(row.book_id), "user_id": row.user_id, "reserved_at": row.reserved_at} for row in rows]
        return reservations

contact_points = ['cas1', 'cas2', 'cas3']
library_system = LibrarySystem(contact_points)

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

class MakeReservationHandler(BaseHandler):
    async def post(self):
        data = json.loads(self.request.body)
        book_id = uuid.UUID(data['book_id'])
        user_id = data['user_id']
        result = await library_system.make_reservation(book_id, user_id)
        self.write(json.dumps(result))

class UpdateReservationHandler(BaseHandler):
    async def post(self):
        data = json.loads(self.request.body)
        book_id = uuid.UUID(data['book_id'])
        user_id = data['user_id']
        result = await library_system.update_reservation(book_id, user_id)
        self.write(json.dumps(result))

class RemoveReservationHandler(BaseHandler):
    async def post(self):
        data = json.loads(self.request.body)
        book_id = uuid.UUID(data['book_id'])
        user_id = data['user_id']
        result = await library_system.remove_reservation(book_id, user_id)
        self.write(json.dumps(result))

class GetBooksHandler(BaseHandler):
    async def get(self):
        rows = await library_system.get_books()
        books = [{"book_id": str(row["book_id"]), "title": row["title"], "author": row["author"], "genre": row["genre"], "published_year": row["published_year"]} for row in rows]
        self.write(json.dumps(books))


class GetReservationsHandler(BaseHandler):
    async def get(self):
        rows = await library_system.get_reservations()
        reservations = [{"reservation_id": str(row["reservation_id"]), "book_id": str(row["book_id"]), "user_id": row["user_id"], "reserved_at": str(row["reserved_at"])} for row in rows]
        self.write(json.dumps(reservations))

class IndexHandler(tornado.web.RequestHandler):
    async def get(self):
        available_books = await library_system.get_books()
        self.render("index.html", available_books=available_books)


def make_app():
    return tornado.web.Application([
        (r"/make_reservation", MakeReservationHandler),
        (r"/update_reservation", UpdateReservationHandler),
        (r"/remove_reservation", RemoveReservationHandler),
        (r"/api/books", GetBooksHandler),
        (r"/api/reservations", GetReservationsHandler),
        (r"/", IndexHandler),
    ],
    template_path="templates",
    static_path="static",
    debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888, address="0.0.0.0")
    print("Server started at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()