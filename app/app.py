import uuid
import tornado.ioloop
import tornado.web
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
        reservation_id = uuid.uuid4()
        # check if user_id is an integer
        try:
            user_id = int(user_id)
        except ValueError:
            return {"error": "Invalid user_id."}
        
        # Check book_reservation if the book is available
        book = self.session.execute("SELECT * FROM book_reservations WHERE book_id = %s", (book_id,)).one()
        if book:
            return {"error": "Book is already reserved."}
        
        # Make the reservation
        reserved_at = datetime.now()
        self.session.execute("INSERT INTO book_reservations (book_id, reservation_id, user_id, reserved_at) VALUES (%s, %s, %s, %s)", (book_id, reservation_id, user_id, reserved_at))
        self.session.execute("INSERT INTO reservations (reservation_id, book_id, user_id, reserved_at) VALUES (%s, %s, %s, %s)", (reservation_id, book_id, user_id, reserved_at))
        self.session.execute("INSERT INTO user_reservations (user_id, reservation_id, book_id, reserved_at) VALUES (%s, %s, %s, %s)", (user_id, reservation_id, book_id, reserved_at))
        return {"message": "Reservation made successfully."}
        

    @run_on_executor
    def update_reservation(self, reservation_id):
        reservation = self.session.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,)).one()
        if not reservation:
            return {"error": "Reservation not found."}
        # read necessary data
        user_id = reservation.user_id
        book_id = reservation.book_id
        reserved_at = datetime.now()
        # update the reservation
        self.session.execute("UPDATE reservations SET reserved_at = %s WHERE reservation_id = %s", (reserved_at, reservation_id))
        self.session.execute("UPDATE user_reservations SET reserved_at = %s WHERE reservation_id = %s AND user_id = %s", (reserved_at, reservation_id, user_id))
        self.session.execute("UPDATE book_reservations SET reserved_at = %s WHERE reservation_id = %s AND book_id = %s", (reserved_at, reservation_id, book_id))
        return {"message": "Reservation updated successfully."}

    @run_on_executor
    def view_reservation(self, reservation_id):
        reservation = self.session.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,)).one()
        if not reservation:
            return {"error": "Reservation not found."}
        return {
            "reservation_id": str(reservation.reservation_id),
            "book_id": str(reservation.book_id),
            "user_id": reservation.user_id
        }

    @run_on_executor
    def remove_reservation(self, book_id, user_id):
        # check if user_id is an integer
        try:
            user_id = int(user_id)
        except ValueError:
            return {"error": "Invalid user_id."}
        
        # Check if the reservation exists for the given book and user IDs
        reservation = self.session.execute("SELECT * FROM reservations WHERE book_id = %s AND user_id = %s", (book_id, int(user_id))).one()
        if not reservation:
            return {"error": "Reservation not found."}
        
        # Remove the reservation
        self.session.execute("DELETE FROM reservations WHERE book_id = %s AND user_id = %s", (book_id, user_id))
        return {"message": "Reservation removed successfully."}

    @run_on_executor
    def get_books(self):
        rows = self.session.execute("SELECT * FROM books")
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
        reservation_id = uuid.UUID(data['reservation_id'])
        result = await library_system.update_reservation(reservation_id)
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

class GetUsersHandler(BaseHandler):
    async def get(self):
        # Assuming there is an endpoint to get users data
        users = [{"user_id": 1, "name": "John Doe", "email": "john@example.com"}]  # Example data
        self.write(json.dumps(users))

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
        (r"/api/users", GetUsersHandler),
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