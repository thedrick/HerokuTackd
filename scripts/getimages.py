import sys
import Image
import urllib2
import ImageFile
import cStringIO
from bs4 import BeautifulSoup

def getsizes(uri):
    # get file size *and* image size (None if not known)
    file = urllib2.urlopen(uri)
    size = file.headers.get("content-length")
    if size: size = int(size)
    p = ImageFile.Parser()
    while 1:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return size, p.image.size
            break
    file.close()
    return size, None

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print "Usage: ./getimages.py <url>"
        exit(1)
    site = sys.argv[1]
    response = urllib2.urlopen(site)
    soup = BeautifulSoup(response)
    images = soup.findAll("img")
    count = 1
    largestImage = {"width" : 0, "height" : 0, "src" : ""}
    for image in images:
        try:
            src = image.get("src")
            if not src.startswith(("http://", "https://")):
                continue
            (total, (width, height)) = getsizes(src)
            if (width < 120 or height < 120):
                continue
            print "Width and height", width, height
            if width > largestImage['width'] and height > largestImage['height']:
                largestImage['width'] = width
                largestImage['height'] = height
                largestImage['src'] = src
                print largestImage
        except:
            continue
    print largestImage
        
