document.addEventListener("DOMContentLoaded", () => {
    const booksTable = document.getElementById("books-table").getElementsByTagName("tbody")[0];
    const reservationsTable = document.getElementById("reservations-table").getElementsByTagName("tbody")[0];
    const usersTable = document.getElementById("users-table").getElementsByTagName("tbody")[0];

    const makeReservationForm = document.getElementById("make-reservation-form");
    const updateReservationForm = document.getElementById("update-reservation-form");
    const removeReservationForm = document.getElementById("remove-reservation-form");

    function fetchBooks() {
        fetch("/api/books")
            .then(response => response.json())
            .then(data => {
                booksTable.innerHTML = "";
                data.forEach(book => {
                    const row = booksTable.insertRow();
                    row.insertCell(0).textContent = book.book_id;
                    row.insertCell(1).textContent = book.title;
                    row.insertCell(2).textContent = book.author;
                    row.insertCell(3).textContent = book.genre;
                    row.insertCell(4).textContent = book.published_year;
                    row.insertCell(5).textContent = book.available ? "Yes" : "No";
                });
            });
    }

    function fetchReservations() {
        fetch("/api/reservations")
            .then(response => response.json())
            .then(data => {
                reservationsTable.innerHTML = "";
                data.forEach(reservation => {
                    const row = reservationsTable.insertRow();
                    row.insertCell(0).textContent = reservation.reservation_id;
                    row.insertCell(1).textContent = reservation.book_id;
                    row.insertCell(2).textContent = reservation.user_id;
                    row.insertCell(3).textContent = new Date(reservation.reserved_at).toLocaleString();
                });
            });
    }

    function fetchUsers() {
        // Assuming there is an endpoint to get users data
        fetch("/api/users")
            .then(response => response.json())
            .then(data => {
                usersTable.innerHTML = "";
                data.forEach(user => {
                    const row = usersTable.insertRow();
                    row.insertCell(0).textContent = user.user_id;
                    row.insertCell(1).textContent = user.name;
                    row.insertCell(2).textContent = user.email;
                });
            });
    }

    makeReservationForm.addEventListener("submit", event => {
        event.preventDefault();
        const bookId = document.getElementById("book-id").value;
        const userId = document.getElementById("user-id").value;

        fetch("/make_reservation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ book_id: bookId, user_id: userId })
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message || data.error);
                fetchBooks();
                fetchReservations();
            });
    });

    updateReservationForm.addEventListener("submit", event => {
        event.preventDefault();
        const reservationId = document.getElementById("reservation-id").value;
        const newUserId = document.getElementById("new-user-id").value;

        fetch("/update_reservation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ reservation_id: reservationId, new_user_id: newUserId })
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message || data.error);
                fetchReservations();
            });
    });

    removeReservationForm.addEventListener("submit", event => {
        event.preventDefault();
        const bookId = document.getElementById("remove-book-id").value;
        const userId = document.getElementById("remove-user-id").value;

        fetch("/remove_reservation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ book_id: bookId, user_id: userId })
        })
            .then(response => response.json())
            .then(data => {
                alert(data.message || data.error);
                fetchBooks();
                fetchReservations();
            });
    });

    fetchBooks();
    fetchReservations();
    fetchUsers();
});