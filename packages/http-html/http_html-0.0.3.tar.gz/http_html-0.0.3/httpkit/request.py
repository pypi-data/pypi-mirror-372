# httpkit/request.py

from urllib.parse import parse_qs

class Request:
    def __init__(self, raw_request):
        self.raw_request = raw_request
        self.method = None
        self.path = None
        self.headers = {}
        self.body = None
        self.parse()

    def parse(self):
        try:
            lines = self.raw_request.split('\r\n')
            first_line = lines[0].split(' ')
            self.method = first_line[0]
            self.path = first_line[1]

            header_lines = lines[1:]
            for line in header_lines:
                if not line:
                    break
                key, value = line.split(': ', 1)
                self.headers[key] = value

            # استخراج محتوى الطلب (body)
            self.body = self.raw_request.split('\r\n\r\n', 1)[1]
            if 'Content-Type' in self.headers and 'application/x-www-form-urlencoded' in self.headers['Content-Type']:
                self.body = parse_qs(self.body)

        except (IndexError, ValueError):
            self.method = None
            self.path = None
