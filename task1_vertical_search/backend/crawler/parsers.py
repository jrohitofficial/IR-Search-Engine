"""
HTML extraction logic for pureportal.coventry.ac.uk pages.

The selectors below were derived by inspecting the *actual* live markup of
the seed organisation page, a real publication detail page
(/en/publications/a-cross-sectional-study-.../) and a real profile page
(/en/persons/sally-abbott/) on 2026-08-15, using Pure CRIS's standard
rendering classes (e.g. "rendering_researchoutput", "list-result-item").
They are not guesses at a generic template.
"""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PUB_URL_RE = re.compile(r"https://pureportal\.coventry\.ac\.uk/en/publications/[a-z0-9\-]+/?$")
PERSON_URL_RE = re.compile(r"https://pureportal\.coventry\.ac\.uk/en/persons/[a-z0-9\-]+/?$")


def normalise_url(url: str) -> str:
    """Strip query strings/fragments and enforce a single trailing slash so
    the same logical page never gets crawled/stored twice under two URLs."""
    url = url.split("?")[0].split("#")[0]
    if not url.endswith("/"):
        url += "/"
    return url


def extract_links(html: str, base_url: str) -> dict:
    """Pull every publication/person link out of a page (used on the seed
    organisation page, which embeds a 'highlighted research output' and a
    'profiles' widget directly in server-rendered HTML)."""
    soup = BeautifulSoup(html, "lxml")
    publications, persons = set(), set()
    for a in soup.find_all("a", href=True):
        absolute = urljoin(base_url, a["href"])
        if PUB_URL_RE.match(absolute):
            publications.add(normalise_url(absolute))
        elif PERSON_URL_RE.match(absolute):
            persons.add(normalise_url(absolute))
    return {"publications": publications, "persons": persons}


def parse_publication_detail(html: str, url: str, source_url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    title_el = soup.select_one("div.introduction h1 span")
    title = title_el.get_text(strip=True) if title_el else soup.title.get_text(strip=True)

    authors, author_profile_urls = [], []
    persons_ul = soup.select_one("ul.relations.persons")
    if persons_ul:
        for li in persons_ul.find_all("li"):
            link = li.find("a", class_="link person")
            if link:
                name = link.get_text(strip=True)
                authors.append(name)
                author_profile_urls.append(normalise_url(urljoin(url, link["href"])))
            else:
                name = li.get_text(strip=True).lstrip(", ").strip()
                if name:
                    authors.append(name)
                    author_profile_urls.append("")
    is_centre_member = False
    centre_link = soup.select_one(
        'ul.relations.organisations a[href*="centre-for-healthcare-and-community-transformation"]'
    )
    if centre_link:
        is_centre_member = True

    type_el = soup.select_one("p.type")
    publication_type = ""
    if type_el:
        classifications = [s.get_text(strip=True) for s in type_el.select("span.type_classification")]
        publication_type = " - ".join([c for c in classifications if c and "peer-review" not in c.lower()]) \
            or (classifications[0] if classifications else "")

    abstract_el = soup.select_one("div.rendering_abstractportal .textblock")
    description = abstract_el.get_text(" ", strip=True) if abstract_el else ""

    journal = ""
    journal_el = soup.select_one('table.properties td a[rel="Journal"] span')
    if journal_el:
        journal = journal_el.get_text(strip=True)

    publication_date = ""
    status_row = soup.select_one("table.properties tr.status td span.date")
    if status_row:
        publication_date = status_row.get_text(strip=True)
    else:
        any_date = soup.select_one("table.properties td span.date")
        if any_date:
            publication_date = any_date.get_text(strip=True)

    content_parts = [title, description, journal, publication_type] + authors
    content = " ".join(p for p in content_parts if p)

    return {
        "title": title,
        "authors": authors,
        "author_profiles": author_profile_urls,
        "publication_date": publication_date,
        "publication_type": publication_type,
        "journal": journal,
        "description": description,
        "content": content,
        "document_url": normalise_url(url),
        "source_url": source_url,
        "is_centre_output": is_centre_member,
    }


def parse_profile_detail(html: str, url: str, source_url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    name_el = soup.select_one("div.header.person-details h1")
    name = name_el.get_text(strip=True) if name_el else soup.title.get_text(strip=True)

    role, department = "", ""
    org_li = soup.select_one("div.rendering_personorganisationlistrendererportal li")
    if org_li:
        job_title_el = org_li.select_one("span.job-title")
        role = job_title_el.get_text(strip=True) if job_title_el else ""
        org_link_el = org_li.select_one("a.link")
        department = org_link_el.get_text(strip=True) if org_link_el else ""

    is_centre_member = department == "Centre for Healthcare and Community Transformation" or bool(
        soup.select_one('a[href*="centre-for-healthcare-and-community-transformation"]')
    )

    interests_el = soup.select_one("div.rendering_personresearchinterestsclassificationstextportal .textblock")
    research_interests = interests_el.get_text(" ", strip=True) if interests_el else ""

    profile_el = soup.select_one("div.rendering_personcvtextrendererportal .textblock")
    description = profile_el.get_text(" ", strip=True) if profile_el else ""

    related_publications = []
    for item in soup.select("div.relation-list-publications li.list-result-item"):
        link = item.select_one("h3.title a")
        if link and link.get("href"):
            related_publications.append(normalise_url(urljoin(url, link["href"])))

    return {
        "name": name,
        "profile_url": normalise_url(url),
        "role": role,
        "department": department,
        "research_interests": research_interests,
        "description": description,
        "related_research_outputs": related_publications,
        "source_url": source_url,
        "is_centre_member": is_centre_member,
    }
