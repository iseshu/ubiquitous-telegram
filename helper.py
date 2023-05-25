import math
import requests
from bs4 import BeautifulSoup

async def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

async def get_details(url):
    req = requests.get(url).content
    id = url.split('/')[-1]
    soup = BeautifulSoup(req,'html.parser')
    title = soup.find("meta",{"name":"description"})['content'].replace('Download File ','')
    link = soup.find("source",{"type":"video/mp4"})['src']
    created_time = soup.find('td',{"align":"center"}).text.replace("Time: ","")
    resp = requests.head(link)
    size = await convert_size(int(resp.headers.get('Content-Length',0)))
    return {"title":title, "size":size,"osize":int(resp.headers.get('Content-Length',0)), "link":link,"created_time":created_time,"id":id}

async def convert_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

async def filenam(filename):
    list  = ["mp4", "webm", "mkv","mov","avi"]
    for i in list:
        filename = filename.lower().replace(i,'')
    return filename
    