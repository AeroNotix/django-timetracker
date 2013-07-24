'''In the timetracker we sometimes require writers to interface with other
systems. Here are any writers which are required for these purposes.
'''

try: # pragma: no cover
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import csv, codecs

class UnicodeWriter(object): # pragma: no cover
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    Taken from the python documentation.
    """

    def __init__(self, fio, dialect=csv.excel, encoding="utf-8", **kwds):
        '''
        The constructor for our Unicode compliant csv writer.

        :param f: This is anything which has the interface of a file. I.e. it
                  has both the read and write methods.
        :param dialect: The dialect of the csv file you're using, you can find
                        a selection of these in the CSV package. Defaults to
                        excel's dialect.
        :param encoding: The encoding of the document which you are creating.
                         Defaults to UTF-8.
        '''
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = fio
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        '''Implements the writerow function as a csv writer would do so.'''
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        '''Implements the writerows function as a csv writer would do so.'''
        for row in rows:
            self.writerow(row)
