import sys
import Image
import urllib2
import ImageFile
import cStringIO
import urlparse
from time import time
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

def is_valid_url(url):
    return url.startswith(("http://", "https://"))

def get_largest_image(soup, url):
    imgs = soup.findAll("img")
    images = []
    start_time = time()
    for img in imgs:
        src = img.get("src")
        if img is None or src is None:
            continue
        if not is_valid_url(src):
            src = urlparse.urljoin(url, src)
        images.append(src)
    largestImage = {"width" : 0, "height" : 0, "src" : ""}
    for src in images:
        current_time = time()
        # 3 Second timeout
        if (current_time - start_time) > 3:
            print "TIME OUT!"
            return largestImage
        try:
            if not is_valid_url(src):
                continue
            (total, (width, height)) = getsizes(src)
            if (width < 101 or height < 101):
                continue
            if width > largestImage['width'] or height > largestImage['height']:
                largestImage['width'] = width
                largestImage['height'] = height
                largestImage['src'] = src
        except:
            continue
    return largestImage

def parse_metadata(url):
    if not is_valid_url(url):
        url = "http://" + url
    response = urllib2.urlopen(url)
    soup = BeautifulSoup(response)
    data = {}
    photo_data = get_largest_image(soup, url)
    print photo_data
    data['photo'] = photo_data
    image = Image.open(cStringIO.StringIO(urllib2.urlopen(photo_data['src']).read())) if photo_data['src'] else None
    max_height = 1024
    max_width = 1024
    if photo_data['width'] > max_width or photo_data['height'] > max_height:
        heightp = float(max_height) / float(photo_data['height'])
        widthp = float(max_width) / float(photo_data['width'])
        p = min(heightp, widthp)
        photo_data['width'] = int(p * photo_data['width'])
        photo_data['height'] *= int(p * photo_data['height'])
        image = image.resize((photo_data['width'], photo_data['height']))
    data['image'] = image
    data['title'] = soup.title.text.strip() if soup.title else None
    data['first_header'] = soup.h1.text.strip() if soup.h1 else None
    return data

        
