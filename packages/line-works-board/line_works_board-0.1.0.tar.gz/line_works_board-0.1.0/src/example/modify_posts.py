#!/usr/bin/env python3
"""
LINE WORKS Board API SDKの投稿更新テスト
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from line_works_board.types import BoardBody, ComposeBody
from line_works_board.board import Board

def main():
    """メイン関数"""
    print("🚀 LINE WORKS Board API SDKの投稿更新テスト")
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
        
        # ステップ1: 更新用のテスト投稿を作成
        print("📝 ステップ1: 更新用のテスト投稿を作成中...")
        
        original_compose_body = ComposeBody(
            title='更新テスト用投稿',
            body='この投稿は更新テストのために作成されました。\n\n作成時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            enableComment=True,
            sendNotifications=True
        )
        
        print("📤 テスト投稿を作成中...")
        create_response = board.compose(original_compose_body)
        
        if not create_response.success:
            print(f"❌ テスト投稿の作成に失敗しました: {create_response.error}")
            return
        
        # 投稿IDを取得
        post_id = None
        if create_response.data:
            post_id = create_response.data.get('postId') or create_response.data.get('id')
        
        if not post_id:
            print("❌ 投稿IDを取得できませんでした")
            return
        
        print("✅ テスト投稿の作成に成功しました！")
        print(f"   投稿ID: {post_id}")
        print()
        
        # ステップ2: 投稿を更新（基本的な更新）
        print("📝 ステップ2: 基本的な投稿更新を実行中...")
        
        updated_compose_body = ComposeBody(
            title='【更新済み】更新テスト用投稿',
            body='この投稿は更新されました！\n\n✅ タイトルが変更されました\n✅ 内容が更新されました\n\n更新時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            enableComment=True,
            sendNotifications=True
        )
        
        print("📤 投稿を更新中...")
        update_response = board.modify(updated_compose_body, post_id)
        
        if update_response.success:
            print("✅ 基本的な投稿更新に成功しました！")
            print(f"   ステータスコード: {update_response.status_code}")
        else:
            print(f"❌ 基本的な投稿更新に失敗しました")
            print(f"   エラー: {update_response.error}")
            print(f"   ステータスコード: {update_response.status_code}")
        
        print()
        
        # ステップ3: 必読投稿に更新
        print("📝 ステップ3: 必読投稿に更新中...")
        
        # 7日後を必読終了日に設定
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        must_read_compose_body = ComposeBody(
            title='【必読】重要な更新情報',
            body='この投稿は必読投稿に更新されました！\n\n🔥 必読期限: 7日間\n📵 コメント無効\n\n重要な情報が含まれています。必ずお読みください。\n\n更新時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            mustReadEndDate=end_date,  # 7日後の必読終了日
            enableComment=False,  # コメントを無効化
            sendNotifications=True
        )
        
        print("📤 必読投稿に更新中...")
        must_read_response = board.modify(must_read_compose_body, post_id)
        
        if must_read_response.success:
            print("✅ 必読投稿への更新に成功しました！")
            print(f"   ステータスコード: {must_read_response.status_code}")
            print(f"   必読終了日: {end_date}")
        else:
            print(f"❌ 必読投稿への更新に失敗しました")
            print(f"   エラー: {must_read_response.error}")
            print(f"   ステータスコード: {must_read_response.status_code}")
        
        print()
        
        # ステップ4: 通知無効で更新
        print("📝 ステップ4: 通知無効で更新中...")
        
        silent_compose_body = ComposeBody(
            title='【通知無効】静かな更新',
            body='この更新は通知を送信しません。\n\n🔇 通知無効\n💬 コメント有効\n\n静かに内容を更新しました。\n\n更新時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            enableComment=True,  # コメントを有効化
            sendNotifications=False,  # 通知を無効化
            mustReadEndDate=None  # 必読を解除
        )
        
        print("📤 通知無効で更新中...")
        silent_response = board.modify(silent_compose_body, post_id)
        
        if silent_response.success:
            print("✅ 通知無効での更新に成功しました！")
            print(f"   ステータスコード: {silent_response.status_code}")
        else:
            print(f"❌ 通知無効での更新に失敗しました")
            print(f"   エラー: {silent_response.error}")
            print(f"   ステータスコード: {silent_response.status_code}")
        
        print()
        
        # ステップ5: 最終確認のための投稿取得
        print("📝 ステップ5: 更新後の投稿を確認中...")
        
        get_response = board.get_post(post_id)
        if get_response.success and get_response.data:
            print("✅ 更新後の投稿情報を取得しました:")
            post_data = get_response.data
            print(f"   タイトル: {post_data.get('title', 'N/A')}")
            print(f"   内容: {post_data.get('body', 'N/A')[:100]}...")
            print(f"   コメント許可: {post_data.get('enableComment', 'N/A')}")
            print(f"   必読終了日: {post_data.get('mustReadEndDate', '設定なし')}")
        else:
            print(f"❌ 更新後の投稿取得に失敗: {get_response.error}")
        
        print()
        print("🎉 投稿更新テストが完了しました！")
        print("\n📊 テスト結果まとめ:")
        print(f"   テスト投稿作成: {'✅ 成功' if create_response.success else '❌ 失敗'}")
        print(f"   基本的な更新: {'✅ 成功' if update_response.success else '❌ 失敗'}")
        print(f"   必読投稿に更新: {'✅ 成功' if must_read_response.success else '❌ 失敗'}")
        print(f"   通知無効で更新: {'✅ 成功' if silent_response.success else '❌ 失敗'}")
        
        print(f"\n📋 作成された投稿ID: {post_id}")
        print("\n📝 次のステップ:")
        print("1. 投稿の削除を試す")
        print("2. 返信機能をテストする")
        print("3. 投稿一覧で更新内容を確認")
        
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
