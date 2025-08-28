#!/usr/bin/env python3
"""
LINE WORKS Board API SDKの投稿作成テスト
"""
import os
import sys
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from line_works_board.types import BoardBody, ComposeBody
from line_works_board.board import Board

def main():
    """メイン関数"""
    print("🚀 LINE WORKS Board API SDKの投稿作成テスト")
    print("=" * 60)
    
    # 環境変数の読み込み
    load_dotenv()
    
    board_id = "YOUR_BOARD_ID"
    
    # 設定値の取得
    client_id = os.getenv('LINE_WORKS_CLIENT_ID')
    client_secret = os.getenv('LINE_WORKS_CLIENT_SECRET')
    service_account = os.getenv('LINE_WORKS_SERVICE_ACCOUNT')
    private_key = os.getenv('LINE_WORKS_PRIVATE_KEY')
    domain = os.getenv('LINE_WORKS_DOMAIN', 'worksmobile.com')
    
    # 必須設定値のチェック
    if not all([client_id, client_secret, service_account, private_key]):
        print("❌ 必要な環境変数が設定されていません")
        print("以下の環境変数を設定してください:")
        print("  - LINE_WORKS_CLIENT_ID")
        print("  - LINE_WORKS_CLIENT_SECRET")
        print("  - LINE_WORKS_SERVICE_ACCOUNT")
        print("  - LINE_WORKS_PRIVATE_KEY")
        print("  - LINE_WORKS_DOMAIN (オプション)")
        return
    
    print("✅ 設定の読み込みが完了しました")
    print(f"   クライアントID: {client_id}")
    print(f"   サービスアカウント: {service_account}")
    print(f"   掲示板ID: {board_id}")
    print(f"   ドメイン: {domain}")
    print()
    
    try:
        # BoardBodyの作成
        board_body = BoardBody(
            client_id=client_id,
            client_secret=client_secret,
            service_account=service_account,
            private_key=private_key,
            domain=domain
        )
        
        # Boardインスタンスの作成
        print("🔧 Boardインスタンスを作成中...")
        board = Board(board_body, board_id)
        print("✅ Boardインスタンスが作成されました")
        print()
        
        # 認証テストの実行
        print("🔐 認証テストを実行中...")
        auth_result = board.test_auth()
        if not auth_result.success:
            print(f"❌ 認証に失敗しました: {auth_result.error}")
            return
        print("✅ 認証テストが成功しました！")
        print()
        
        # 投稿作成テストの実行
        print("📝 投稿作成テストを実行中...")
        
        # テスト投稿の作成
        compose_body = ComposeBody(
            title='APIテスト投稿',
            body='この投稿はLINE WORKS Board API SDKのテストで作成されました。\n\n機能テスト内容:\n- 認証処理\n- 投稿作成\n- パラメータ検証',
            enableComment=True,
            sendNotifications=True
        )
        
        print("📤 投稿を作成中...")
        response = board.compose(compose_body)
        
        if response.success:
            print("✅ 投稿の作成に成功しました！")
            print(f"   ステータスコード: {response.status_code}")
            if response.data:
                post_id = response.data.get('postId') or response.data.get('id')
                if post_id:
                    print(f"   投稿ID: {post_id}")
                print(f"   レスポンス: {response.data}")
        else:
            print(f"❌ 投稿の作成に失敗しました")
            print(f"   エラー: {response.error}")
            print(f"   ステータスコード: {response.status_code}")
            return
        
        print()
        
        # 通知投稿のテスト
        print("📢 通知投稿のテストを実行中...")
        
        # 必読投稿として作成（30日間有効）
        from datetime import datetime, timedelta
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        notice_compose_body = ComposeBody(
            title='【重要】APIテスト必読投稿',
            body='これは必読投稿のテストです。\n\n30日間の必読期限が設定されています。',
            mustReadEndDate=end_date,  # 必読終了日を設定
            enableComment=False,  # コメントを無効化
            sendNotifications=True
        )
        
        print("📤 通知投稿を作成中...")
        notice_response = board.compose(notice_compose_body)
        
        if notice_response.success:
            print("✅ 通知投稿の作成に成功しました！")
            print(f"   ステータスコード: {notice_response.status_code}")
            if notice_response.data:
                notice_post_id = notice_response.data.get('postId') or notice_response.data.get('id')
                if notice_post_id:
                    print(f"   投稿ID: {notice_post_id}")
        else:
            print(f"❌ 通知投稿の作成に失敗しました")
            print(f"   エラー: {notice_response.error}")
            print(f"   ステータスコード: {notice_response.status_code}")
        
        print()
        
        # コメント無効投稿のテスト
        print("🔒 コメント無効投稿のテストを実行中...")
        
        secret_compose_body = ComposeBody(
            title='コメント無効投稿テスト',
            body='この投稿はコメントが無効になっています。\n\n返信・コメントはできません。',
            enableComment=False,  # コメントを無効化
            sendNotifications=False  # 通知も無効化
        )
        
        print("📤 コメント無効投稿を作成中...")
        secret_response = board.compose(secret_compose_body)
        
        if secret_response.success:
            print("✅ コメント無効投稿の作成に成功しました！")
            print(f"   ステータスコード: {secret_response.status_code}")
            if secret_response.data:
                secret_post_id = secret_response.data.get('postId') or secret_response.data.get('id')
                if secret_post_id:
                    print(f"   投稿ID: {secret_post_id}")
        else:
            print(f"❌ コメント無効投稿の作成に失敗しました")
            print(f"   エラー: {secret_response.error}")
            print(f"   ステータスコード: {secret_response.status_code}")
        
        print()
        print("🎉 投稿作成テストが完了しました！")
        print("\n📊 テスト結果まとめ:")
        print(f"   通常投稿: {'✅ 成功' if response.success else '❌ 失敗'}")
        print(f"   必読投稿: {'✅ 成功' if notice_response.success else '❌ 失敗'}")
        print(f"   コメント無効投稿: {'✅ 成功' if secret_response.success else '❌ 失敗'}")
        
        print("\n📝 次のステップ:")
        print("1. 投稿の更新・削除を試す")
        print("2. 返信機能をテストする")
        print("3. 投稿一覧の取得で作成した投稿を確認")
        
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
