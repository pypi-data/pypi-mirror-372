from fastapi import FastAPI
from Secweb.ContentSecurityPolicy import ContentSecurityPolicy
from Secweb.ReferrerPolicy import ReferrerPolicy
from Secweb.StrictTransportSecurity import HSTS
from Secweb.XContentTypeOptions import XContentTypeOptions
from Secweb.XFrameOptions import XFrame

from ash_utils.constants import HEADERS_POLICIES_NONE, HEADERS_POLICIES_SELF
from ash_utils.middlewares import PermissionsPolicy


def configure_security_headers(app: FastAPI) -> None:
    app.add_middleware(
        ContentSecurityPolicy,
        Option={
            "default-src": [HEADERS_POLICIES_SELF],
            "base-uri": [HEADERS_POLICIES_SELF],
            "script-src": [HEADERS_POLICIES_SELF, "https://cdn.jsdelivr.net/npm/ 'unsafe-inline'"],
            "img-src": [
                HEADERS_POLICIES_SELF,
                "https://cdn.jsdelivr.net/npm/",
                "https://fastapi.tiangolo.com/",
                "https://cdn.redoc.ly/redoc/",
                "data:",
            ],
            "style-src": [
                HEADERS_POLICIES_SELF,
                "https://cdn.jsdelivr.net/npm/",
                "https://fonts.googleapis.com/",
                "'unsafe-inline'",
            ],
            "font-src": [HEADERS_POLICIES_SELF, "https://fonts.gstatic.com/ 'unsafe-inline'"],
            "worker-src": [HEADERS_POLICIES_SELF, "blob:"],
            "frame-src": [HEADERS_POLICIES_NONE],
            "object-src": [HEADERS_POLICIES_NONE],
            "media-src": [HEADERS_POLICIES_NONE],
        },
        script_nonce=False,
        style_nonce=False,
    )
    app.add_middleware(XContentTypeOptions)
    app.add_middleware(ReferrerPolicy)
    app.add_middleware(XFrame)
    app.add_middleware(HSTS, Option={"max-age": 63072000, "preload": True})
    app.add_middleware(
        PermissionsPolicy,
        Option={
            "geolocation": [],
            "camera": [],
            "microphone": [],
            "gyroscope": [],
            "magnetometer": [],
            "accelerometer": [],
            "payment": [],
            "autoplay": [],
            "usb": [],
            "web-share": [],
        },
    )
