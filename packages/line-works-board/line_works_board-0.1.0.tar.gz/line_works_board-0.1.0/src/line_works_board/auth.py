"""
LINE WORKS APIのJWT認証処理
"""
import time
import jwt
from typing import Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from .types import BoardBody


class LineWorksAuth:
    """LINE WORKS APIのJWT認証クラス"""
    
    def __init__(self, board_body: BoardBody):
        self.client_id = board_body.client_id
        self.client_secret = board_body.client_secret
        self.service_account = board_body.service_account
        self.private_key = board_body.private_key
        self.domain = board_body.domain or "worksmobile.com"
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[int] = None
        
    def _load_private_key(self) -> rsa.RSAPrivateKey:
        """秘密鍵を読み込み"""
        try:
            # PEM形式の秘密鍵を読み込み
            private_key = serialization.load_pem_private_key(
                self.private_key.encode('utf-8'),
                password=None
            )
            return private_key
        except Exception as e:
            raise ValueError(f"秘密鍵の読み込みに失敗しました: {e}")
    
    def _create_jwt_token(self) -> str:
        """JWTトークンを作成"""
        now = int(time.time())
        
        # JWTペイロード（公式仕様に準拠）
        payload = {
            'iss': self.client_id,  # 発行者（クライアントID）
            'sub': self.service_account,  # サブジェクト（サービスアカウント）
            'aud': 'https://auth.worksmobile.com/oauth2/v2.0/token',  # 対象者（トークンエンドポイント）
            'iat': now,  # 発行時刻
            'exp': now + 3600,  # 有効期限（1時間）
        }
        
        try:
            private_key = self._load_private_key()
            jwt_token = jwt.encode(
                payload,
                private_key,
                algorithm='RS256',
                headers={'kid': self.client_id}  # キーID（クライアントID）
            )
            return jwt_token
        except Exception as e:
            raise ValueError(f"JWTトークンの作成に失敗しました: {e}")
    
    def get_access_token(self) -> str:
        """アクセストークンを取得（必要に応じて更新）"""
        # トークンが有効な場合は既存のものを返す
        if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
            return self.access_token
        
        # 新しいトークンを取得
        jwt_token = self._create_jwt_token()
        
        # アクセストークンを取得（公式仕様に準拠）
        import requests
        
        token_url = "https://auth.worksmobile.com/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': jwt_token,
            'client_id': self.client_id,  # クライアントID
            'client_secret': self.client_secret,  # クライアントシークレット
            'scope': 'board board.read'  # 掲示板のスコープ
        }
        
        response = requests.post(token_url, data=token_data)
        
        if response.status_code != 200:
            raise ValueError(f"アクセストークンの取得に失敗しました: {response.text}")
        
        token_info = response.json()
        self.access_token = token_info['access_token']
        self.token_expires_at = int(time.time()) + int(token_info['expires_in']) - 300  # 5分前に期限切れとみなす
        
        return self.access_token
    
    def get_headers(self) -> dict:
        """APIリクエスト用のヘッダーを取得"""
        access_token = self.get_access_token()
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
