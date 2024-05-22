from flask import Flask, request, jsonify, render_template
from cassandra.cluster import Cluster
import uuid

app = Flask(__name__)

class LibrarySystem:
    def __init__(self, contact_points):
        self.cluster = Cluster(contact_points=contact_points)
        self.session = self.cluster.connect()
        self.session.execute("USE library")

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

    def update_reservation(self, reservation_id, new_user_id):
        reservation = self.session.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,)).one()
        if not reservation:
            return {"error": "Reservation not found."}
        self.session.execute("UPDATE reservations SET user_id = %s WHERE reservation_id = %s", (new_user_id, reservation_id))
        return {"message": "Reservation updated successfully."}

    def view_reservation(self, reservation_id):
        reservation = self.session.execute("SELECT * FROM reservations WHERE reservation_id = %s", (reservation_id,)).one()
        if not reservation:
            return {"error": "Reservation not found."}
        return {
            "reservation_id": str(reservation.reservation_id),
            "book_id": str(reservation.book_id),
            "user_id": reservation.user_id
        }
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

    def get_available_books(self):
        rows = self.session.execute("SELECT * FROM books")
        return [{"book_id": str(row.book_id), "title": row.title, "author": row.author} for row in rows]
    
    def get_reservations(self):
        rows = self.session.execute("SELECT * FROM reservations")
        reservations = [{"reservation_id": str(row.reservation_id), "book_id": str(row.book_id), "user_id": row.user_id} for row in rows]
        return jsonify(reservations)


contact_points = ['cas1', 'cas2', 'cas3']
library_system = LibrarySystem(contact_points)

@app.route('/make_reservation', methods=['POST'])
def make_reservation():
    data = request.json
    book_id = uuid.UUID(data['book_id'])
    user_id = data['user_id']
    result = library_system.make_reservation(book_id, user_id)
    return jsonify(result)

@app.route('/update_reservation', methods=['POST'])
def update_reservation():
    data = request.json
    reservation_id = uuid.UUID(data['reservation_id'])
    new_user_id = data['new_user_id']
    result = library_system.update_reservation(reservation_id, new_user_id)
    return jsonify(result)

@app.route('/view_reservation/<reservation_id>', methods=['GET'])
def view_reservation(reservation_id):
    reservation_id = uuid.UUID(reservation_id)
    result = library_system.view_reservation(reservation_id)
    return jsonify(result)

@app.route('/remove_reservation', methods=['POST'])
def remove_reservation():
    data = request.json
    book_id = uuid.UUID(data['book_id'])
    user_id = data['user_id']
    result = library_system.remove_reservation(book_id, user_id)
    return jsonify(result)

@app.route('/')
def index():
    available_books = library_system.get_available_books()
    return render_template('index.html', available_books=available_books)

@app.route('/reservations', methods=['GET'])
def get_reservations():
    return library_system.get_reservations()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
