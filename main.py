import pytesseract
from PIL import Image
from dotenv import load_dotenv
import os
import http.server as server
import uuid

load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv('EXECUTABLE')


def create_unique_uuid():
    return uuid.uuid4()


class HTTPRequestHandler(server.SimpleHTTPRequestHandler):
    def do_PUT(self):
        apikey = self.headers['x-api-key']

        if not apikey == os.getenv('APIKEY'):
            reply = 'Unauthorized Area'
            self.send_response(401)
            self.end_headers()
            self.wfile.write(reply.encode('utf-8'))
            return

        filename = create_unique_uuid()
        content_length = int(self.headers['Content-Length'])

        while True:
            filepath = 'images/' + str(filename)
            if not os.path.exists(filepath):
                with open(filepath, 'wb') as output_file:
                    file_content = self.rfile.read(content_length)
                    output_file.write(file_content)
                break
            else:
                filename = create_unique_uuid()

        text = pytesseract.image_to_string(Image.open(filepath), lang=os.getenv('TESSERACT_LANG'))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))


with server.HTTPServer((os.getenv('HOST'), int(os.getenv('PORT'))), RequestHandlerClass=HTTPRequestHandler) as Http:
    print("OCR Server listening on " + os.getenv('HOST') + ":" + os.getenv('PORT'))
    Http.serve_forever()
