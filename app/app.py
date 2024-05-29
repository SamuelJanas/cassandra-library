import uuid
import tornado.ioloop
import tornado.web
from cassandra.cluster import Cluster
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import json

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
        
        book = self.session.execute("SELECT * FROM books WHERE book_id = %s", (book_id,)).one()
        if not book:
            return {"error": "Book not found."}
        reservation = self.session.execute("SELECT * FROM reservations WHERE book_id = %s", (book_id,)).one()
        if reservation:
            return {"error": "Book already reserved."}
        self.session.execute("INSERT INTO reservations (reservation_id, book_id, user_id) VALUES (%s, %s, %s)", (reservation_id, book_id, int(user_id)))
        return {"message": f"Reservation {str(reservation_id)} made successfully.", "reservation_id": str(reservation_id)}

    @run_on_executor
    def update_reservation(self, reservation_id, new_user_id):
        reservation = self.session.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,)).one()
        if not reservation:
            return {"error": "Reservation not found."}
        self.session.execute("UPDATE reservations SET user_id = %s WHERE reservation_id = %s", (new_user_id, reservation_id))
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
    def get_available_books(self):
        rows = self.session.execute("SELECT * FROM books")
        return [{"book_id": str(row.book_id), "title": row.title, "author": row.author} for row in rows]
    
    @run_on_executor
    def get_reservations(self):
        rows = self.session.execute("SELECT * FROM reservations")
        reservations = [{"reservation_id": str(row.reservation_id), "book_id": str(row.book_id), "user_id": row.user_id} for row in rows]
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
        new_user_id = data['new_user_id']
        result = await library_system.update_reservation(reservation_id, new_user_id)
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
        rows = await library_system.get_available_books()
        books = [{"book_id": str(row["book_id"]), "title": row["title"], "author": row["author"], "genre": row["genre"], "published_year": row["published_year"], "available": row["available"]} for row in rows]
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
        available_books = await library_system.get_available_books()
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