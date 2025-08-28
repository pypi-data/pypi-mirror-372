import json
import time
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from huggingface_hub import HfApi

BASE_URL = 'https://nonexistentfandomsfandom.neocities.org/'
CAST_URL = urljoin(BASE_URL, 'AAcats/cast')


def get_cat_links() -> list[str]:
    resp = requests.get(CAST_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/AAcats/') and not href.endswith('.html'):
            links.append(urljoin(BASE_URL, href))

    return list(set(links))


def extract_ascii_from_page(url: str) -> list[tuple[str, str]]:
    def remove_combining_marks(text: str) -> str:
        return ''.join(
            ch
            for ch in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(ch)
        )

    def sanitize_ascii_art(text: str) -> str:
        return text.replace('\u25cc', '').replace('\u3000', '  ')

    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []

    for header in soup.find_all(['h1', 'h3']):
        next_sibling = header.find_next_sibling()
        if (
            next_sibling
            and next_sibling.name == 'div'
            and 'scrollbox' in next_sibling.get('class', [])
        ):
            span = next_sibling.find('span', class_='dqn')
            if span:
                name = header.get_text(strip=True)
                ascii_art = BeautifulSoup(
                    span.decode_contents(), 'html.parser'
                ).get_text('\n')
                results.append((name, sanitize_ascii_art(ascii_art)))

    return results


def scrape_all(output_file: str) -> None:
    all_cats = []
    links = get_cat_links()

    for link in links:
        print(f'Scraping {link}')
        try:
            pairs = extract_ascii_from_page(link)
            for name, art in pairs:
                all_cats.append({'name': name, 'ascii': art})
        except Exception as e:
            print(f'Failed {link}: {e}')
        time.sleep(0.3)  # be polite

    # filter out repeated cats by name
    all_cats = list({cat['name']: cat for cat in all_cats}.values())

    with open(output_file, 'w', encoding='utf-8') as f:
        for cat in all_cats:
            f.write(json.dumps(cat, ensure_ascii=False) + '\n')

    print(f'\nSaved {len(all_cats)} cats to {output_file}')


def upload_to_huggingface(output_file: str) -> None:
    api = HfApi()

    api.upload_file(
        path_or_fileobj=output_file,
        path_in_repo=f'data/{output_file}',
        repo_id='pielet/ascii-cats',
        repo_type='dataset',
        commit_message=f'Update {output_file} dataset',
        create_pr=True,
    )


if __name__ == '__main__':
    scrape_all('ascii-cats.jsonl')
    upload_to_huggingface('ascii-cats.jsonl')
