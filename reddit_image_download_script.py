import re, praw, requests, os, glob, sys, time
from bs4 import BeautifulSoup

MIN_SCORE = 100
user_agent_string = 'Image Downloader by /u/Jesusfarted v 1.0'
already_done = []
subreddit_name = ''

def downloadImage(imageUrl, localFileName):
    response = requests.get(imageUrl)
    if response.status_code == 200:
        print('Downloading %s\n from %s' % (localFileName, subreddit_name))
        with open(localFileName, 'wb') as fo:
            for chunk in response.iter_content(4096):
                fo.write(chunk)

def main():
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python %s subreddit [minimum score]' % (sys.argv[0]))
        sys.exit()
    elif len(sys.argv) >= 2:
        targetSubreddit = sys.argv[1]
    if len(sys.argv) >= 3:
        MIN_SCORE = int(sys.argv[2])

    imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
  
    r = praw.Reddit(user_agent=user_agent_string)

    while True:
        submissions = r.get_subreddit(targetSubreddit).get_new(limit=30)
            
        # Process all the submissions from the front page
        for submission in submissions:
            global subreddit_name
            subreddit_name = submission.subreddit.display_name
            
            if "imgur.com/" not in submission.url:
                continue
            if submission.score < MIN_SCORE:
                continue
            if len(glob.glob('reddit_%s_%s_*' % (subreddit_name, submission.id))) > 0:
                continue

            if 'http://imgur.com/a/' in submission.url:
                # This is an album submission.
                albumId = submission.url[len('http://imgur.com/a/'):]
                htmlSource = requests.get(submission.url).text

                soup = BeautifulSoup(htmlSource, "html.parser")
                matches = soup.select('.album-view-image-link a')
                for match in matches:
                    imageUrl = match['href']
                    if '?' in imageUrl:
                        imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
                    else:
                        imageFile = imageUrl[imageUrl.rfind('/') + 1:]
                    localFileName = 'reddit_%s_%s_album_%s_imgur_%s' % (subreddit_name, submission.id, albumId, imageFile)
                    downloadImage('http:' + match['href'], localFileName)

            elif 'http://i.imgur.com/' in submission.url:
                # The URL is a direct link to the image.
                mo = imgurUrlPattern.search(submission.url)

                imgurFilename = mo.group(2)
                if '?' in imgurFilename:
                    imgurFilename = imgurFilename[:imgurFilename.find('?')]

                localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (subreddit_name, submission.id, imgurFilename)
                downloadImage(submission.url, localFileName)

            elif 'http://imgur.com/' in submission.url:
                # This is an Imgur page with a single image.
                htmlSource = requests.get(submission.url).text
                soup = BeautifulSoup(htmlSource, "html.parser")
                imageUrl = soup.select('.image a')[0]['href']
                if imageUrl.startswith('//'):
                    imageUrl = 'http:' + imageUrl
                imageId = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('.')]

                if '?' in imageUrl:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
                else:
                    imageFile = imageUrl[imageUrl.rfind('/') + 1:]

                localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (subreddit_name, submission.id, imageFile)
                downloadImage(imageUrl, localFileName)
                
        print('Still running...')
        time.sleep(1800)
        
if __name__ == '__main__':
    main()
