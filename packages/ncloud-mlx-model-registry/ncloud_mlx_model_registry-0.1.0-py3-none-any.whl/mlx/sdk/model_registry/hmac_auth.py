#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import base64
import datetime
import hmac
from hashlib import md5, sha256

import dateutil.tz
from requests.auth import AuthBase


class HmacAuth(AuthBase):
    TIMESTAMP_HTTP_HEADER = "X-MR-Timestamp"
    SIGN_HTTP_HEADER = "X-MR-Authorization"

    # NOTE: sync with model-registry config.hmac.key
    hmac_key = (
        "9634aecc76b4302e90dadde0494997c4294e7f842ff115affff429cfb7cb71e4".encode()
    )

    def __call__(self, request):
        self.encode(request)
        return request

    def encode(self, request):
        timestamp = self.get_current_timestamp()
        method = request.method.upper()
        content = request.body or ""
        # path_url : path and query string
        message = self.message_to_sign(method, content, timestamp, request.path_url)
        signature = self.sign(self.hmac_key, message)

        request.headers[HmacAuth.TIMESTAMP_HTTP_HEADER] = timestamp
        request.headers[HmacAuth.SIGN_HTTP_HEADER] = signature

    @staticmethod
    def get_current_timestamp():
        date = datetime.datetime.now(dateutil.tz.tzutc())
        return f"{int(date.timestamp())}"

    @staticmethod
    def message_to_sign(method, content, timestamp, path_url):
        md5enc = md5()
        md5enc.update(content.encode())
        content_md5 = md5enc.hexdigest()

        message = f"{method}\n{content_md5}\n{timestamp}\n{path_url}".encode()
        return message

    @staticmethod
    def sign(hmac_key, message):
        digest = hmac.new(key=hmac_key, msg=message, digestmod=sha256).digest()
        b64encoded = base64.urlsafe_b64encode(digest)
        return b64encoded.strip()
