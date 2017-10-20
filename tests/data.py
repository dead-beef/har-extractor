TEST_ARCHIVE = {
    'log': {
        'entries': [
            {
                'request': {
                    'method': 'GET',
                    'url': 'https://127.0.0.1/',
                },
                'response': {
                    'status': 200,
                    'statusText': 'OK',
                    'content': {
                        'mimeType': 'text/plain',
                        'size': 4,
                        'text': 'test'
                    }
                }
            },
            {
                'request': {
                    'method': 'GET',
                    'url': 'https://127.0.0.1/dir/',
                },
                'response': {
                    'status': 200,
                    'statusText': 'OK',
                    'content': {
                        'mimeType': "text/plain",
                        'size': 8,
                        'encoding': 'base64',
                        'text': 'dGVzdDIK'
                    }
                }
            },
            {
                'request': {
                    'method': 'GET',
                    'url': 'https://127.0.0.1/404',
                },
                'response': {
                    'status': 404,
                    'statusText': 'Not Found',
                    'content': {
                        'mimeType': "text/plain",
                        'size': 0,
                        'text': ''
                    }
                }
            }
        ]
    }
}

TEST_ARCHIVE_INVALID = {
    'log': {
        'entries': [
            {
                'response': {
                    'status': 200,
                    'statusText': 'OK',
                    'content': {
                        'mimeType': 'text/plain',
                        'size': 4,
                        'text': 'test'
                    }
                }
            },
            {},
            {
                'request': {
                    'method': 'GET',
                    'url': 'https://127.0.0.1/404',
                },
                'response': {
                    'status': 404,
                    'statusText': 'Not Found',
                    'content': {
                        'mimeType': "text/plain",
                        'size': 3,
                        'text': '404'
                    }
                }
            }
        ]
    }
}

TEST_ARCHIVE_CONTENTS = [
    ('test', 'index.html'),
    (b'test2\n', 'dir')
]

TEST_ARCHIVE_VERBOSE = '''GET https://127.0.0.1/ -> 200 OK text/plain 4B
\t----> dir/index.html
GET https://127.0.0.1/dir/ -> 200 OK text/plain 8B
\t----> dir/dir
GET https://127.0.0.1/404 -> 404 Not Found text/plain 0B
\t----> <no content>
'''

TEST_ARCHIVE_INVALID_VERBOSE = '''<no method> <no url> -> 200 OK text/plain 4B
<no method> <no url> -> <no status> <no status text> <no mime type> <invalid size>
\t----> <no content>
GET https://127.0.0.1/404 -> 404 Not Found text/plain 3B
\t----> dir/404
'''

TEST_ARCHIVE_LIST = '''GET https://127.0.0.1/ -> 200 OK text/plain 4B
GET https://127.0.0.1/dir/ -> 200 OK text/plain 8B
GET https://127.0.0.1/404 -> 404 Not Found text/plain 0B
'''

TEST_ARCHIVE_INVALID_LIST = '''<no method> <no url> -> 200 OK text/plain 4B
<no method> <no url> -> <no status> <no status text> <no mime type> <invalid size>
GET https://127.0.0.1/404 -> 404 Not Found text/plain 3B
'''
