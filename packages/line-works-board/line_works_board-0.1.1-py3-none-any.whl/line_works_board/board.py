"""
LINE WORKS掲示板APIの操作クラス
"""
import requests
from typing import Optional, List
from .auth import LineWorksAuth
from .types import BoardBody, ComposeBody, ReplyBody, BoardPost, BoardReply, ApiResponse


class Board:
    """LINE WORKS掲示板の操作クラス"""
    
    def __init__(self, board_body: BoardBody, board_id: str):
        self.board_body = board_body
        self.board_id = board_id
        self.auth = LineWorksAuth(board_body)
        # 掲示板APIのエンドポイント（公式仕様に準拠）
        self.base_url = f"https://www.worksapis.com/v1.0/boards/{board_id}"
    
    def test_auth(self) -> ApiResponse:
        """認証が成功したかどうかをテスト"""
        try:
            print("🔐 認証テストを開始中...")
            
            # アクセストークンの取得を試行
            try:
                access_token = self.auth.get_access_token()
                print(f"✅ アクセストークンの取得に成功しました")
                print(f"   トークン: {access_token[:20]}...")
                
                # ヘッダーの取得をテスト
                headers = self.auth.get_headers()
                print(f"✅ 認証ヘッダーの生成に成功しました")
                print(f"   Authorization: Bearer {access_token[:20]}...")
                
                # 簡単なAPIリクエストで認証をテスト
                print("🔍 掲示板情報の取得で認証をテスト中...")
                test_response = self.get_board_info()
                
                if test_response.success:
                    print("✅ 認証テストが完了しました！APIリクエストが正常に実行されました")
                    return ApiResponse(
                        success=True,
                        data={"message": "認証が正常に動作しています", "access_token": access_token[:20] + "..."},
                        status_code=200
                    )
                else:
                    print(f"⚠️  認証は成功しましたが、APIリクエストでエラーが発生: {test_response.error}")
                    return ApiResponse(
                        success=False,
                        error=f"認証は成功しましたが、APIリクエストでエラーが発生: {test_response.error}",
                        status_code=test_response.status_code
                    )
                    
            except Exception as auth_error:
                print(f"❌ 認証に失敗しました: {str(auth_error)}")
                return ApiResponse(
                    success=False,
                    error=f"認証に失敗しました: {str(auth_error)}",
                    status_code=401
                )
                
        except Exception as e:
            print(f"❌ 認証テスト中に予期しないエラーが発生: {str(e)}")
            return ApiResponse(
                success=False,
                error=f"認証テスト中に予期しないエラーが発生: {str(e)}",
                status_code=500
            )
    
    def _make_request(self, method: str, endpoint: str = "", data: Optional[dict] = None) -> ApiResponse:
        """APIリクエストを実行"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = self.auth.get_headers()
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return ApiResponse(success=False, error=f"サポートされていないHTTPメソッド: {method}")
            
            if response.status_code in [200, 201, 204]:
                return ApiResponse(
                    success=True,
                    data=response.json() if response.content else None,
                    status_code=response.status_code
                )
            else:
                return ApiResponse(
                    success=False,
                    error=f"APIリクエストが失敗しました: {response.status_code} - {response.text}",
                    status_code=response.status_code
                )
                
        except Exception as e:
            return ApiResponse(success=False, error=f"リクエスト実行中にエラーが発生しました: {str(e)}")
    
    def compose(self, compose_body: ComposeBody) -> ApiResponse:
        """投稿を作成（公式仕様に準拠）"""
        # 公式ドキュメントに基づくパラメータ形式
        data = {
            "title": compose_body.title,
            "body": compose_body.body,
            "enableComment": compose_body.enableComment,
            "sendNotifications": compose_body.sendNotifications
        }
        
        # 必読終了日が設定されている場合のみ追加
        if compose_body.mustReadEndDate:
            data["mustReadEndDate"] = compose_body.mustReadEndDate
        
        return self._make_request("POST", "/posts", data)
    
    def modify(self, compose_body: ComposeBody, post_id: str) -> ApiResponse:
        """投稿を更新（公式仕様に準拠）"""
        # 公式ドキュメントに基づくパラメータ形式
        data = {
            "title": compose_body.title,
            "body": compose_body.body,
            "enableComment": compose_body.enableComment,
            "sendNotifications": compose_body.sendNotifications
        }
        
        # 必読終了日が設定されている場合のみ追加
        if compose_body.mustReadEndDate:
            data["mustReadEndDate"] = compose_body.mustReadEndDate
        
        return self._make_request("PUT", f"/posts/{post_id}", data)
    
    def reply(self, reply_body: ReplyBody, post_id: str) -> ApiResponse:
        """投稿にコメント（返信）を作成（公式仕様に準拠）"""
        # 公式ドキュメントに基づくパラメータ形式
        data = {
            "content": reply_body.content
        }
        
        if reply_body.attachments:
            data["attachments"] = reply_body.attachments
        
        return self._make_request("POST", f"/posts/{post_id}/comments", data)
    
    def delete(self, post_id: str) -> ApiResponse:
        """投稿を削除"""
        return self._make_request("DELETE", f"/posts/{post_id}")
    
    def get_post(self, post_id: str) -> ApiResponse:
        """投稿を取得"""
        return self._make_request("GET", f"/posts/{post_id}")
    
    def get_posts(self, limit: int = 20, offset: int = 0) -> ApiResponse:
        """投稿一覧を取得"""
        params = f"?limit={limit}&offset={offset}"
        return self._make_request("GET", f"/posts{params}")
    
    def get_replies(self, post_id: str, limit: int = 20, offset: int = 0) -> ApiResponse:
        """コメント（返信）一覧を取得（公式仕様に準拠）"""
        params = f"?limit={limit}&offset={offset}"
        return self._make_request("GET", f"/posts/{post_id}/comments{params}")
    
    def search_posts(self, query: str, limit: int = 20, offset: int = 0) -> ApiResponse:
        """投稿を検索"""
        params = f"?query={query}&limit={limit}&offset={offset}"
        return self._make_request("GET", f"/posts/search{params}")
    
    def get_board_info(self) -> ApiResponse:
        """掲示板の情報を取得"""
        return self._make_request("GET", "")
