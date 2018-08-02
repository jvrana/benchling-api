def url_build(*parts):
    """Join parts of a url into a string"""
    return '/'.join(p.strip('/') for p in parts)