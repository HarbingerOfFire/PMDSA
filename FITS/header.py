# Just a way to store the header easily

class Header:
    '''
    A simple class to store FITS header data.
    Attributes:
        header (dict): A dictionary to hold the header key-value pairs.
    Methods:
        __setitem__(key, value): Set a header key-value pair.
        __getitem__(key): Get the value for a header key.
        __delitem__(key): Delete a header key-value pair.
        __contains__(key): Check if a header key exists.
        __repr__(): Return a string representation of the header.
        __str__(): Return a string representation of the header.
    '''
    def __init__(self):
        self.header = {}

    def __setitem__(self, key, value):
        self.header.update({key: value})
    
    def __getitem__(self, key):
        return self.header[key]
    
    def __delitem__(self, key):
        del self.header[key]
    
    def __contains__(self, key):
        return key in self.header
    
    def __repr__(self):
        return self.header.__repr__()
    
    def __str__(self):
        return self.header.__str__()