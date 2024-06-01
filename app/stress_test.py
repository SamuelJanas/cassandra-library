import requests
import random
import uuid
import csv
import json
import concurrent.futures

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
    

def stress_test_1(book_id, user_id):
    """
    one user makes the same reservation 10,000 times
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(make_reservation, book_id, user_id) for _ in range(1000)]
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



def stress_test_2(books):
    """
    Two or more clients make requests randomly (10000 times)
    """
    def run_worker(user_id):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(make_random_request, user_id, books) for _ in range(1000)]
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

    # Number of workers (users)
    num_workers = 2
    # Start multiple workers with different user_ids
    for user_id in range(num_workers):
        run_worker(user_id)

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


if __name__ == "__main__":
    # read books.csv 
    with open("books.csv") as f:
        reader = csv.DictReader(f)
        books = list(reader)

    random_book_id = uuid.UUID(books[2]["book_id"])
    random_user_id = 132

    stress_test_3(books)