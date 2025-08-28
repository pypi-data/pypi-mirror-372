###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import StrField, IntField, RegexField, ListField


FILE_URL_PATH = StrField(default='/file', readonly=True)
FILE_URL_LENGTH = IntField(default=32, readonly=True)
FILE_HASH_LENGTH = IntField(default=40, readonly=True)

FILE_ID_REGEX = RegexField(default=r'^file_[a-zA-Z0-9]', readonly=True)
FILE_ID_MAX_SIZE = IntField(default=30, readonly=True)
FILE_ID_PREFIX = StrField(default='file_', readonly=True)

FILE_DATA_MAX_SIZE_IN_RAW = IntField(default=int(100 * 1024 * 1024), readonly=True)
FILE_DATA_MAX_SIZE_IN_BASE64 = IntField(default=139810133, readonly=True) # int(FILE_DATA_MAX_SIZE_IN_RAW / 3 * 4) # 13.33MB in BASE64 ~= 10MB in RAW

FILE_CONTENT_TYPES = ListField(
    default=[
        None,
        'application/csv',
        'application/javascript',
        'application/json',
        'application/msword',
        'application/octet-stream',
        'application/pdf',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/x-zip-compressed',
        'application/xml',
        'application/zip',
        'image/bmp',
        'image/gif',
        'image/jpeg',
        'image/png',
        'image/svg+xml',
        'image/webp',
        'text/comma-separated-values',
        'text/csv',
        'text/plain',
        'text/markdown',
        'text/x-comma-separated-values',
        'text/xml',
        'audio/mpeg',
        'audio/wav'
    ],
    readonly=True
)
