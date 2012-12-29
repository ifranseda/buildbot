    
import mimetypes
import httplib
# http://code.activestate.com/recipes/146306-http-client-to-post-using-multipartform-data/
def post_multipart(host, selector, fields, files,moar_headers={}):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTPSConnection(host)
    headers = {
        'User-Agent': 'INSERT USERAGENTNAME',
        'Content-Type': content_type
        }
    for (key,value) in moar_headers.iteritems():
        headers[key] = value
    h.request('POST', selector, body.decode('utf-8').encode('ascii', 'replace'), headers)
    res = h.getresponse()
    return res.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = 'ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    #L.append('Content-Type: multipart/form-data; boundary=%s' % BOUNDARY)
    #L.append('')
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        pass
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def hockeyapp_upload(api_token,app_identifier,ipa,dsym):
    print post_multipart("rink.hockeyapp.net", "/api/2/apps/%s/app_versions" % app_identifier, [], [("ipa","ipa.ipa",ipa),("dsym","dsym",dsym)],{"X-HockeyAppToken":api_token})


import unittest
class TestSequence(unittest.TestCase):
    def test_hockeyappupload(self):
        print hockeyapp_upload("9b3957ca17a446f6bdbba2f12ea085e1", "7f8b966c983bc0dfd8f93f94f13c582e", "This is not an IPA", "This is not a dsym")
