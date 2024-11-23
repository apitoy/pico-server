#!/bin/python
# pip install nltk
# pip install -r requirements.txt

import subprocess
from datetime import datetime
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Pobierz dane NLTK (jeśli jeszcze ich nie ma)
nltk.download('punkt')
nltk.download('stopwords')

# Pobierz status Gita
def get_git_status():
    try:
        status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            universal_newlines=True
        )
        return status.strip()
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas odczytu statusu Gita: {e}")
        return ""

# Analiza różnic dla pliku
def get_git_diff(file_name):
    try:
        diff = subprocess.check_output(
            ['git', 'diff', '--cached', file_name],
            universal_newlines=True
        )
        return diff.strip()
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas odczytu różnic dla pliku {file_name}: {e}")
        return ""

# Parsowanie statusu Gita
def parse_git_status(status):
    staged = []
    for line in status.splitlines():
        if line.startswith(("A", "M", "D", "R", "C")):
            staged.append(line[3:].strip())
    return staged

# Analiza zawartości zmian
def analyze_file_changes(file_name):
    diff = get_git_diff(file_name)
    if not diff:
        return "No details available."

    tokens = word_tokenize(diff.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]

    # Słowa kluczowe
    keywords = {
        "Added": ["add", "new", "insert", "create"],
        "Modified": ["modify", "update", "change", "edit"],
        "Fixed": ["fix", "resolve", "bug"],
        "Removed": ["remove", "delete", "cleanup"]
    }

    for category, words in keywords.items():
        if any(word in filtered_tokens for word in words):
            return category

    return "Updated"

# Pobierz ostatnią wersję z CHANGELOG.md
def get_last_version():
    try:
        with open("CHANGELOG.md", "r") as file:
            changelog = file.read()
        # Szukaj ostatniej wersji w formacie ## [x.y.z]
        match = re.search(r"## \[(\d+\.\d+\.\d+)\]", changelog)
        if match:
            return match.group(1)
    except FileNotFoundError:
        pass
    return "0.0.0"

# Automatyczne obliczanie kolejnej wersji
def increment_version(version):
    major, minor, patch = map(int, version.split("."))
    return f"{major}.{minor}.{patch + 1}"

# Generowanie changeloga
def generate_changelog(version, staged):
    today = datetime.now().strftime("%Y-%m-%d")
    changelog = [f"## [{version}] - {today}", ""]

    if staged:
        changelog.append("### Added")
        for file in staged:
            change_type = analyze_file_changes(file)
            if change_type == "Added":
                changelog.append(f"- [{file}](./{file})")

        changelog.append("\n### Changed")
        for file in staged:
            change_type = analyze_file_changes(file)
            if change_type == "Modified":
                changelog.append(f"- [{file}](./{file})")

        changelog.append("\n### Fixed")
        for file in staged:
            change_type = analyze_file_changes(file)
            if change_type == "Fixed":
                changelog.append(f"- [{file}](./{file})")

        changelog.append("\n### Removed")
        for file in staged:
            change_type = analyze_file_changes(file)
            if change_type == "Removed":
                changelog.append(f"- [{file}](./{file})")

    return "\n".join(changelog).strip()

# Aktualizacja istniejącego changeloga
def update_changelog_file(version, changelog_content):
    try:
        with open("CHANGELOG.md", "r") as file:
            lines = file.readlines()

        # Podziel zawartość na nagłówek i resztę
        header_index = next(
            (index for index, line in enumerate(lines) if line.strip().startswith("## ")), len(lines)
        )
        header = "".join(lines[:header_index])
        rest = "".join(lines[header_index:])

    except FileNotFoundError:
        header = (
            "# Changelog\n\n"
            "All notable changes to this project will be documented in this file.\n\n"
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\n"
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"
        )
        rest = ""

    # Dodaj nową sekcję poniżej nagłówka
    updated_content = f"{header}{changelog_content}\n\n{rest}"

    with open("CHANGELOG.md", "w") as file:
        file.write(updated_content)

if __name__ == "__main__":
    print("Generowanie changelog...")
    last_version = get_last_version()
    proposed_version = increment_version(last_version)
    print(f"Proponowana wersja: {proposed_version} (poprzednia: {last_version})")
    version = input(f"Potwierdź wersję [{proposed_version}]: ").strip()
    version = version if version else proposed_version

    status = get_git_status()
    if status:
        staged = parse_git_status(status)
        if staged:
            changelog = generate_changelog(version, staged)
            update_changelog_file(version, changelog)
            print("Changelog został zaktualizowany i zapisany jako CHANGELOG.md")
        else:
            print("Brak zstage'owanych zmian do analizy.")
    else:
        print("Brak zmian do analizy.")
