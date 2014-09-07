class Smartdict(dict):
    """A dict which can return its keys for inspection.

    Useful when keys contain information overlooked by equality."""

    def __init__(self):
        self.keydict = {}

    def __delitem__(self, key):
        """Delete key from dictionary. Propagate as needed."""
        super().__delitem__(key)
        self.keydict.__delitem__(key)

    def __setitem__(self, key, value):
        """Map key to value. Store the key for later retrieval."""
        super().__setitem__(key, value)
        self.keydict.__setitem__(key, key)

    def getKey(self, key, default=None):
        """Return the key for inspection or 'default' if absent."""
        return self.keydict.get(key, default)
