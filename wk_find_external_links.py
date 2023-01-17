"""
Single-threaded scraper for finding external links on Wikipedia using BeatifulSoup

~ jvadair 2023
"""

import requests
from bs4 import BeautifulSoup


OUTPUT_FILE = "pages_found.txt"
STARTING_PAGE = "https://en.wikipedia.org/wiki/Monty_Python_and_the_Holy_Grail"
NUM_PAGES = 300  # Change to -1 to run indefinitely


def get_base_url(url):
    try:
        url = url.split("://", maxsplit=1)
        schema = url[0]
        page = url[1]
        site = page.split('/')[0]
        return f'{schema}://{site}'
    except:  # No base url in link
        return False


def main(starting_page, num_pages, output_file):
    print("Now scanning Wikipedia...")
    queue = [starting_page]
    found_links = []  # Full links
    found_sites = []  # Domains
    checked_pages = []
    try:
        runs = 0
        while runs != num_pages:
            # -- Setup --
            current_url = queue.pop(0)
            content = requests.get(current_url).content.decode()
            soup = BeautifulSoup(content, 'html.parser')
            # -- Link finding --
            internal_urls = soup.find_all("a", href=lambda href: href and href.startswith('/wiki/'))
            external_urls = soup.find_all('a', attrs={'class': 'external'})
            # -- Parse html --
            external_urls = [l['href'] for l in external_urls if l]
            internal_urls = ["https://en.wikipedia.org" + l['href'] for l in internal_urls if l]
            external_urls = list(dict.fromkeys(external_urls))  # Remove duplicates
            internal_urls = list(dict.fromkeys(internal_urls))
            found_links += [l for l in external_urls if l not in found_links]
            # # -- Debug --
            # print(*external_urls, sep='\n')
            # input()
            # print(*internal_urls, sep='\n')
            # input()
            # -- Prepare for next run --
            checked_pages.append(current_url)
            queue += [l for l in internal_urls if l not in queue and l not in checked_pages]
            runs += 1
    except KeyboardInterrupt:  # For infinite runs, we want to save on cancel
        pass
    print('Done.')


    found_sites += [get_base_url(l) for l in found_links if get_base_url(l) not in found_sites]
    found_sites = list(dict.fromkeys(found_sites))  # Remove duplicates
    found_sites.remove(False)  # Removes any errors (which would only appear once)
    # print(*found_sites, sep='\n')
    with open(output_file, 'w') as file:
        file.write('\n'.join(found_sites))


if __name__ == "__main__":
    main(STARTING_PAGE, NUM_PAGES, OUTPUT_FILE)