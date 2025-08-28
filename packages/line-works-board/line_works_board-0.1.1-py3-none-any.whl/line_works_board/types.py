"""
LINE WORKS掲示板APIで使用するデータ型定義
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class BoardBody:
    """掲示板の設定情報"""
    client_id: str
    client_secret: str
    service_account: str
    private_key: str
    domain: Optional[str] = None


@dataclass
class ComposeBody:
    """投稿内容（公式仕様に準拠）"""
    title: str  # 件名（必須、1-200文字）
    body: str   # 内容（必須、1-716800文字）
    enableComment: Optional[bool] = True  # コメント許可フラグ（デフォルト: true）
    mustReadEndDate: Optional[str] = None  # 必読終了日（最大30日、format: date）
    sendNotifications: Optional[bool] = True  # 投稿通知送信フラグ（デフォルト: true）
    
    # 下位互換性のためのプロパティ
    @property
    def content(self) -> str:
        """下位互換性: content -> body"""
        return self.body
    
    @content.setter
    def content(self, value: str):
        self.body = value
    
    @property
    def is_notice(self) -> bool:
        """下位互換性: 必読投稿の判定"""
        return self.mustReadEndDate is not None
    
    @is_notice.setter
    def is_notice(self, value: bool):
        # 必読投稿として設定する場合は、30日後を設定
        if value and not self.mustReadEndDate:
            from datetime import datetime, timedelta
            end_date = datetime.now() + timedelta(days=30)
            self.mustReadEndDate = end_date.strftime('%Y-%m-%d')
        elif not value:
            self.mustReadEndDate = None
    
    @property
    def is_secret(self) -> bool:
        """下位互換性: 秘密投稿は現在サポートされていません"""
        return False
    
    @is_secret.setter
    def is_secret(self, value: bool):
        # 秘密投稿機能は現在の仕様にはないため、何もしない
        pass


@dataclass
class ReplyBody:
    """コメント（返信）内容（公式仕様に準拠）"""
    content: str
    attachments: Optional[List[Dict[str, Any]]] = None  # 添付ファイル情報
    
    # 下位互換性のためのプロパティ（廃止予定）
    @property
    def is_secret(self) -> bool:
        """下位互換性: 秘密コメントは存在しないため常にFalse"""
        return False
    
    @is_secret.setter
    def is_secret(self, value: bool):
        """下位互換性: 秘密コメントは存在しないため何もしない"""
        pass


@dataclass
class BoardPost:
    """掲示板の投稿"""
    post_id: str
    title: str
    content: str
    author: str
    created_at: str
    updated_at: Optional[str] = None
    is_notice: bool = False
    is_secret: bool = False
    reply_count: int = 0
    attachments: Optional[List[str]] = None


@dataclass
class BoardReply:
    """掲示板の返信"""
    reply_id: str
    content: str
    author: str
    created_at: str
    is_secret: bool = False
    attachments: Optional[List[str]] = None


@dataclass
class ApiResponse:
    """APIレスポンス"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
