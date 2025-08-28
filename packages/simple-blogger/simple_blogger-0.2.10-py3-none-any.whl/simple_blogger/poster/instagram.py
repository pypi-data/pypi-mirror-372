from simple_blogger.uploader.S3Uploader import S3Uploader
from simple_blogger.preprocessor.text import SerialProcessor, MarkdownCleaner, IdentityProcessor
from simple_blogger.poster import IPoster, Post
import os, requests

class InstagramPoster(IPoster):
    def __init__(self, account_token_name='IG_BOT_TOKEN', account_id=None, uploader=S3Uploader(), processor=None, **_):
        self.uploader = uploader
        self.account_token = os.environ.get(account_token_name)
        self.account_id = account_id or self.me()['id']
        self.processor = SerialProcessor([MarkdownCleaner(), processor or IdentityProcessor()])
            
    def post(self, post:Post, processor=None, **_):
        if post.media and post.message:
            media_url = self.uploader.upload(file=post.media)
            caption = post.get_real_message(SerialProcessor([self.processor, processor or IdentityProcessor()]))
            post = self.create_post(self.account_id, media_url=media_url, caption=caption)
            self.publish(self.account_id, post['id'])

    def me(self):
        payload = { 'fields': ['user_id', 'username'], 'access_token': self.account_token }
        user_url = "https://graph.instagram.com/v22.0/me"
        response = requests.get(user_url, params=payload).json()
        return response

    def create_post(self, account_id, media_url, caption):
        payload = { 'image_url': media_url, 'access_token': self.account_token, 'caption': caption }
        crate_image_url = f"https://graph.instagram.com/v22.0/{account_id}/media"
        response = requests.post(crate_image_url, params=payload).json()
        return response

    def publish(self, account_id, creation_id):
        payload = { 'creation_id': creation_id, 'access_token': self.account_token }
        crate_image_url = f"https://graph.instagram.com/v22.0/{account_id}/media_publish"
        response = requests.post(crate_image_url, params=payload).json()
        return response

# class InstagramVideoPoster(InstagramPoster):
#     def create_post(self, account_id, media_url, caption):
#         payload = { 'video_url': media_url, 'media_type': 'VIDEO', 'access_token': self.account_token, 'caption': caption }
#         crate_image_url = f"https://graph.instagram.com/v22.0/{account_id}/media"
#         response = requests.post(crate_image_url, params=payload).json()
#         return response
    
class InstagramReelsPoster(InstagramPoster):
    def create_post(self, account_id, media_url, caption):
        payload = { 'video_url': media_url, 'media_type': 'REELS', 'access_token': self.account_token, 'caption': caption }
        crate_image_url = f"https://graph.instagram.com/v22.0/{account_id}/media"
        response = requests.post(crate_image_url, params=payload).json()
        return response