class ConfigWriter:
    def __init__(self):
        self.misc = {}
        self.options = {}

    def get(self, key, default=None):
        return self.options.get(key, default)

    def pop(self, key, default=None):
        return self.options.pop(key, default)

    def get_misc(self, sect, key, default=None):
        return self.misc.get(sect, {}).get(key, default)

    def __setitem__(self, key, value):
        self.options[key] = value

    def __getitem__(self, key):
        return self.options[key]
