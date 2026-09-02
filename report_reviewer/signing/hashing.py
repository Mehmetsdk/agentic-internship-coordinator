import hashlib


def compute_file_hash(file_path: str) -> str:
    """Bir dosyanin SHA-256 hash'ini hesaplar."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_package_hash(report_path: str, journal_path: str) -> dict:
    """Iki belgenin hash'ini hesaplar, sira bagimsiz bir kombinasyon da uretir."""
    report_hash = compute_file_hash(report_path)
    journal_hash = compute_file_hash(journal_path)
    combined = "".join(sorted([report_hash, journal_hash]))
    package_hash = hashlib.sha256(combined.encode()).hexdigest()
    return {
        "report_hash": report_hash,
        "journal_hash": journal_hash,
        "package_hash": package_hash,
    }
