import csv
from django.http import StreamingHttpResponse

class CSVBuffer:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        return value

class CSVStream:
    """Class to stream (download) an iterator to a 
    CSV file."""
    def export(self, filename, iterator, serializer):
        writer = csv.writer(CSVBuffer())
        response = StreamingHttpResponse((writer.writerow(serializer(data)) for data in iterator),
                                         content_type="text/csv")
        response['Content-Disposition'] = f"attachment; filename={filename}.csv"
        return response
