class Smartdict(dict):
    """A dict which can return its keys for inspection.

    Useful when keys contain information overlooked by equality."""
    keydict = {}

    def __delitem__(self, key):
        super().__delitem__(key)
        self.keydict.__delitem__(key)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.keydict.__setitem__(key, key)

    def getKey(self, key, default=None):
        """Return the key for inspection."""
        return self.keydict.get(key, None)
