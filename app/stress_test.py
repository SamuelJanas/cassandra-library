import csv
import uuid
import json
import random
import argparse
import requests
import concurrent.futures

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run stress tests on book reservation system.")
    parser.add_argument("test", type=int, choices=range(1, 6), help="Choose a stress test to run (1-5)")
    parser.add_argument("--size", type=int, default=1000, help="Size of the test (default: 1000)")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers to use (default: 4)")
    return parser.parse_args()

def make_reservation(book_id, user_id):
    url = "http://localhost:8888/make_reservation"
    payload = {"book_id": str(book_id), "user_id": user_id}
    response = requests.post(url, json=payload)
    return response.json()

def update_reservation(book_id, user_id):
    url = "http://localhost:8888/update_reservation"
    payload = {"book_id": str(book_id), "user_id": user_id}
    response = requests.post(url, json=payload)
    return response.json()

def remove_reservation(book_id, user_id):
    url = "http://localhost:8888/remove_reservation"
    payload = {"book_id": str(book_id), "user_id": user_id}
    response = requests.post(url, json=payload)
    return response.json()

def make_random_request(user_id, books):
    request_type = random.choice(["make_reservation", "update_reservation", "remove_reservation"])
    if request_type == "make_reservation":
        book_id = random.choice(books)["book_id"]
        return make_reservation(book_id, user_id)
    elif request_type == "update_reservation":
        book_id = random.choice(books)["book_id"]
        return update_reservation(book_id, user_id)
    else:
        book_id = random.choice(books)["book_id"]
        return remove_reservation(book_id, user_id)
    
def create_initial_reservations(books, user_id):
    """
    Create initial reservations for a list of books for a given user.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(make_reservation, book["book_id"], user_id) for book in books]
        results = [future.result() for future in futures]
        # Check if all reservations are created successfully
        success_count = sum(1 for result in results if "message" in result and result["message"] == "Reservation made successfully.")
        print(f"Created {success_count}/{len(books)} reservations successfully.")
    

def stress_test_1(book_id, user_id, number_of_requests=1000):
    """
    one user makes the same reservation `number_of_requests` times
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(make_reservation, book_id, user_id) for _ in range(number_of_requests)]
        results = [future.result() for future in futures]
        # make a histogram of the results
        # count number of occurrences of each result
        histogram = {}
        for result in results:
            result = json.dumps(result)
            if result in histogram:
                histogram[result] += 1
            else:
                histogram[result] = 1
        print(histogram)


def stress_test_2(books, number_of_requests=10000, num_workers=4):
    """
    num_workers clients make requests randomly (number_of_requests times)
    """
    def run_worker(user_id):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(make_random_request, user_id, books) for _ in range(number_of_requests)]
            results = [future.result() for future in futures]
            # make a histogram of the results
            # count number of occurrences of each result
            histogram = {}
            for result in results:
                result = json.dumps(result)
                if result in histogram:
                    histogram[result] += 1
                else:
                    histogram[result] = 1
            print(f"User {user_id} Histogram: {histogram}")

    # Start multiple workers with different user_ids
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(run_worker, range(num_workers))


def stress_test_3(books):
    """
    Immediate occupancy of all reservations by 2 clients
    """
    def reserve_seats(user_id):
        success_histogram = {"Worker 1": 0, "Worker 2": 0}
        for book in books:
            book_id = book["book_id"]
            response = make_reservation(book_id, user_id)
            if "message" in response:
                success_histogram[f"Worker {user_id}"] += 1
        print(f"Worker {user_id} Success Histogram: {success_histogram}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(reserve_seats, [1, 2])


def stress_test_4(book_id, user_id, number_of_requests=5000):
    """
    Constant cancellations and book occupancy for the same book.
    """
    def constant_operations():
        success_histogram = {"make_reservation": 0, "remove_reservation": 0}
        for _ in range(number_of_requests):  # 5000 reservations and 5000 cancellations
            make_response = make_reservation(book_id, user_id)
            if "message" in make_response:
                success_histogram["make_reservation"] += 1

            remove_response = remove_reservation(book_id, user_id)
            if "message" in remove_response:
                success_histogram["remove_reservation"] += 1
        
        print(f"User {user_id} Success Histogram: {success_histogram}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(constant_operations) for _ in range(2)]
        concurrent.futures.wait(futures)


def stress_test_5(books, user_id, num_workers=10):
    """
    Update reservations concurrently using multiple workers.
    """
    def update_worker(worker_id, book_ids):
        success_count = 0
        for book_id in book_ids:
            response = update_reservation(book_id, user_id)
            if "message" in response:
                success_count += 1
        print(f"Worker {worker_id} updated {success_count} reservations successfully.")

    # Initialize reservations
    create_initial_reservations(books, user_id)
    
    book_ids = [book["book_id"] for book in books]
    book_chunks = [book_ids[i::num_workers] for i in range(num_workers)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(update_worker, worker_id, book_chunks[worker_id]) for worker_id in range(num_workers)]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    args = parse_arguments()

    with open("books.csv") as f:
        reader = csv.DictReader(f)
        books = list(reader)

    random_book_id = uuid.UUID(books[2]["book_id"])
    random_user_id = 132

    if args.test == 1:
        stress_test_1(random_book_id, random_user_id, number_of_requests=args.size)
    elif args.test == 2:
        stress_test_2(books, number_of_requests=args.size, num_workers=args.workers)
    elif args.test == 3:
        stress_test_3(books[:args.size])
    elif args.test == 4:
        stress_test_4(random_book_id, random_user_id, number_of_requests=args.size)
    elif args.test == 5:
        stress_test_5(books[:args.size], random_user_id, num_workers=args.workers)