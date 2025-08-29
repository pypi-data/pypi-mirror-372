import hashlib


def calculate_md5sum(file_path: str) -> str:
    file_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        chunk = file.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = file.read(8192)
    return str(file_hash.hexdigest())
