import gzip
import zlib
from base64 import b64decode
from io import BytesIO

from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser


class GzippedJSONParser(JSONParser):
    def _parse(self, data, media_type, parser_context):
        try:
            return super(GzippedJSONParser, self).parse(
                stream=BytesIO(data),
                media_type=media_type,
                parser_context=parser_context,
            )
        except ParseError:
            decompressed_data = gzip.decompress(data)

            try:
                return super(GzippedJSONParser, self).parse(
                    stream=BytesIO(decompressed_data),
                    media_type=media_type,
                    parser_context=parser_context,
                )
            except ParseError:
                decompressed_data = b64decode(zlib.decompress(data))

                return super(GzippedJSONParser, self).parse(
                    stream=BytesIO(decompressed_data),
                    media_type=media_type,
                    parser_context=parser_context,
                )

    def parse(self, stream, media_type=None, parser_context=None):
        data = stream.read()

        try:
            return self._parse(data, media_type, parser_context)
        except Exception as e:
            raise ParseError("gzipped json parse error - %s" % str(e)) from e
