def detect_headers_and_legends(input_file):
    with open(input_file, "r") as f:
        first_line = f.readline()
        headers = [h.strip() for h in first_line.strip().split()]
        if all(h.replace(".", "", 1).isdigit() for h in headers):
            return None, None  # No header, just data
        return list(range(2, len(headers) + 1)), headers[1:]

