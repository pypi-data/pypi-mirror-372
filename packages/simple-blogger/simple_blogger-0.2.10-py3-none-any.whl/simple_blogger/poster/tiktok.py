from simple_blogger.uploader.S3Uploader import S3Uploader
from simple_blogger.preprocessor.text import SerialProcessor, MarkdownCleaner, IdentityProcessor
from simple_blogger.poster import IPoster, Post
import os, requests

class TikTokVideoPoster(IPoster):
    BASE_URL = 'https://open.tiktokapis.com/v2'

    def __init__(self, user_token_name='TT_BOT_TOKEN', review_mode=True, uploader=None, processor=None):
        self.uploader = uploader or S3Uploader()
        self.token = os.environ.get(user_token_name)
        self.review_mode = review_mode
        self.processor = SerialProcessor([MarkdownCleaner(), processor or IdentityProcessor()])
            
    def check_status(self, publish_id, user_token_name=None):
        token = (user_token_name and os.environ.get(user_token_name)) or self.token
        fetch_url = f'{TikTokVideoPoster.BASE_URL}/post/publish/status/fetch/'
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json; charset=UTF-8'
        }
        body = {
            "publish_id": f"{publish_id}"
        }
        response = requests.post(url=fetch_url, json=body, headers=headers).json()
        return response
    
    def cancel(self, publish_id, user_token_name=None):
        token = (user_token_name and os.environ.get(user_token_name)) or self.token
        fetch_url = f'{TikTokVideoPoster.BASE_URL}/post/publish/cancel/ '
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json; charset=UTF-8'
        }
        body = {
            "publish_id": f"{publish_id}"
        }
        response = requests.post(url=fetch_url, json=body, headers=headers).json()
        return response
    
    def list_videos(self, user_token_name=None):
        token = (user_token_name and os.environ.get(user_token_name)) or self.token
        fetch_url = f'{TikTokVideoPoster.BASE_URL}/video/list/?fields=cover_image_url,id,title'
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        body = {
            'max_count': 20
        }
        response = requests.post(url=fetch_url, json=body, headers=headers).json()
        return response
    
    def _review_url(self, post:Post, user_token_name):
        token = user_token_name
        url = self.uploader.upload(post.media)
        init_url = f'{TikTokVideoPoster.BASE_URL}/post/publish/inbox/video/init/'
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        body = {
            'source_info': {
                'source': 'PULL_FROM_URL',
                "video_url": f"{url}"
            }
        }
        response = requests.post(url=init_url, json=body, headers=headers).json()
        publish_id = response['data']['publish_id']
        return publish_id

    def _review(self, post:Post, user_token_name):
        token = user_token_name
        init_url = f'{TikTokVideoPoster.BASE_URL}/post/publish/inbox/video/init/'
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        video_size = len(post.get_real_media().read())
        body = {
            'source_info': {
                'source': 'FILE_UPLOAD',
                'video_size': video_size,
                'chunk_size': video_size,
                'total_chunk_count': 1
            }
        }
        response = requests.post(url=init_url, json=body, headers=headers).json()
        upload_url = response['data']['upload_url']
        publish_id = response['data']['publish_id']
        headers = {
            'Content-Type': post.media.get_content_type(),
            'Content-Range' : f"bytes 0-{video_size-1}/{video_size}",
            'Content-Length': f"{video_size}",
        }
        response = requests.put(url=upload_url, headers=headers, data=post.get_real_media())
        return publish_id

    def _send(self, post:Post, user_token_name, processor):
        token = user_token_name
        init_url = f'{TikTokVideoPoster.BASE_URL}/post/publish/video/init/'
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json; charset=UTF-8'
        }
        video_size = len(post.get_real_media().read())
        title = post.get_real_message(processor)
        body = {
            'post_info' : {
                'privacy_level': 'PUBLIC_TO_EVERYONE',
                'title': title, 
                'is_aigc': True,
            }, 
            'source_info': {
                'source': 'FILE_UPLOAD',
                'video_size': video_size,
                'chunk_size': video_size,
                'total_chunk_count': 1
            }
        }
        response = requests.post(url=init_url, json=body, headers=headers).json()
        upload_url = response['data']['upload_url']
        publish_id = response['data']['publish_id']
        headers = {
            'Content-Type': post.media.get_content_type(),
            'Content-Range' : f"bytes 0-{video_size-1}/{video_size}",
            'Content-Length': f"{video_size}",
        }
        response = requests.put(url=upload_url, headers=headers, data=post.get_real_media())
        return publish_id

    def post(self, post:Post, user_token_name=None, processor=None):
        token = (user_token_name and os.environ.get(user_token_name)) or self.token
        processor = SerialProcessor([self.processor, processor or IdentityProcessor()])
        if self.review_mode:
            return self._review(post, user_token_name=token)
        else:
            self._send(post, user_token_name=token, processor=processor) 