"""
Multithreaded scraper for finding external links on websites using BeatifulSoup

~ jvadair 2023
"""

import requests
from bs4 import BeautifulSoup
from wk_find_external_links import main as scan_wk, get_base_url
from threading import Thread

scan_wk()  # Disable if using your own txt file

INPUT_FILE = "pages_found.txt"  # A newline-separated text file
OUTPUT_FILE = "wwwsearch.txt"
MAX_THREADS = 20  # DO NOT SET TO -1


def worker(site, results):
    found = []
    # -- Setup --
    try:
        content = requests.get(site, timeout=10).content.decode()
    except:  # Broad clause due to many connection errors
        return
    soup = BeautifulSoup(content, 'html.parser')
    # -- Link finding --
    urls = soup.find_all("a", href=lambda href: href and get_base_url(href) and get_base_url(href) != site)
    # -- Parse html --
    urls = [l['href'] for l in urls]
    urls = list(dict.fromkeys(urls))  # Remove duplicates
    urls = [get_base_url(url) for url in urls]
    for url in urls:
        if url not in results:
            results.append(url)

def main():
    open_threads = []
    results = []
    results_position = 0
    with open(INPUT_FILE, 'r') as file:
        queue = file.read().split('\n')  # Avoids placing newlines at the end of strings
    for i in range(0, MAX_THREADS):
        t = Thread(target=worker, args=(queue.pop(0), results))
        open_threads.append(t)
        t.start()
    try:
        while True:
            queue += results[results_position:]  # Add all NEW results to the queue
            results_position = len(results)
            dead_threads = [n for n, t in zip(range(0, len(open_threads)), open_threads) if not t.is_alive()]
            for i in dead_threads:
                open_threads.pop(i)
                t = Thread(target=worker, args=(queue.pop(0), results))
                open_threads.append(t)
                t.start()
    except (KeyboardInterrupt, IndexError):
        # Close all threads safely (will do nothing if program ends due to empty queue)
        print("Finishing up...")
        for t in open_threads:
            t.join()
    with open(OUTPUT_FILE, 'w') as file:
        file.write('\n'.join(results))


if __name__ == "__main__":
    main()
