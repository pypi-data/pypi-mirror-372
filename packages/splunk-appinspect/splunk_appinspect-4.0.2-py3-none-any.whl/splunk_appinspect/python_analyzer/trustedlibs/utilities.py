import hashlib


def get_hash_file(file_content: bytes) -> str:
    """
    Returns:
         sha256 hash of a zipped app package file.
    """
    assert isinstance(file_content, bytes)
    sha256 = hashlib.sha256()
    sha256.update(file_content)
    return sha256.hexdigest()
