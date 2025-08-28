#!/usr/bin/env python3
"""
LINE WORKS Board API SDKの投稿削除テスト
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import time

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from line_works_board.types import BoardBody, ComposeBody
from line_works_board.board import Board

def main():
    """メイン関数"""
    print("🚀 LINE WORKS Board API SDKの投稿削除テスト")
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
        
        # ステップ1: 削除用のテスト投稿を作成（複数）
        print("📝 ステップ1: 削除用のテスト投稿を作成中...")
        
        created_posts = []
        
        # 1つ目のテスト投稿
        post1_compose_body = ComposeBody(
            title='削除テスト用投稿 #1',
            body='この投稿は削除テストのために作成されました。\n\n投稿番号: 1\n作成時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            enableComment=True,
            sendNotifications=False  # テスト投稿なので通知は無効
        )
        
        print("📤 テスト投稿 #1 を作成中...")
        create_response1 = board.compose(post1_compose_body)
        
        if create_response1.success:
            post_id1 = create_response1.data.get('postId') or create_response1.data.get('id') if create_response1.data else None
            if post_id1:
                created_posts.append(('投稿 #1', post_id1))
                print(f"✅ テスト投稿 #1 の作成に成功: {post_id1}")
            else:
                print("❌ 投稿 #1 のIDを取得できませんでした")
        else:
            print(f"❌ テスト投稿 #1 の作成に失敗: {create_response1.error}")
        
        # 少し待機
        time.sleep(1)
        
        # 2つ目のテスト投稿
        post2_compose_body = ComposeBody(
            title='削除テスト用投稿 #2',
            body='この投稿も削除テストのために作成されました。\n\n投稿番号: 2\n作成時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            enableComment=False,  # コメント無効
            sendNotifications=False
        )
        
        print("📤 テスト投稿 #2 を作成中...")
        create_response2 = board.compose(post2_compose_body)
        
        if create_response2.success:
            post_id2 = create_response2.data.get('postId') or create_response2.data.get('id') if create_response2.data else None
            if post_id2:
                created_posts.append(('投稿 #2', post_id2))
                print(f"✅ テスト投稿 #2 の作成に成功: {post_id2}")
            else:
                print("❌ 投稿 #2 のIDを取得できませんでした")
        else:
            print(f"❌ テスト投稿 #2 の作成に失敗: {create_response2.error}")
        
        print(f"\n📋 作成された投稿: {len(created_posts)}件")
        for name, post_id in created_posts:
            print(f"   {name}: {post_id}")
        print()
        
        if not created_posts:
            print("❌ 削除対象の投稿がありません。テストを中断します。")
            return
        
        # ステップ2: 投稿が存在することを確認
        print("📝 ステップ2: 削除前の投稿存在確認中...")
        
        for name, post_id in created_posts:
            print(f"🔍 {name} の存在確認中...")
            get_response = board.get_post(post_id)
            
            if get_response.success:
                print(f"   ✅ {name} が存在しています")
                if get_response.data:
                    title = get_response.data.get('title', 'N/A')
                    print(f"      タイトル: {title}")
            else:
                print(f"   ❌ {name} の取得に失敗: {get_response.error}")
        
        print()
        
        # ステップ3: 1つ目の投稿を削除
        if len(created_posts) >= 1:
            name, post_id = created_posts[0]
            print(f"📝 ステップ3: {name} を削除中...")
            
            print(f"🗑️  投稿ID {post_id} を削除中...")
            delete_response = board.delete(post_id)
            
            if delete_response.success:
                print(f"✅ {name} の削除に成功しました！")
                print(f"   ステータスコード: {delete_response.status_code}")
                
                # 削除後の確認
                print("🔍 削除後の確認中...")
                time.sleep(2)  # 少し待機
                confirm_response = board.get_post(post_id)
                
                if not confirm_response.success:
                    print("   ✅ 投稿が正常に削除されました（取得不可）")
                else:
                    print("   ⚠️  投稿がまだ存在している可能性があります")
            else:
                print(f"❌ {name} の削除に失敗しました")
                print(f"   エラー: {delete_response.error}")
                print(f"   ステータスコード: {delete_response.status_code}")
        
        print()
        
        # ステップ4: 2つ目の投稿も削除
        if len(created_posts) >= 2:
            name, post_id = created_posts[1]
            print(f"📝 ステップ4: {name} を削除中...")
            
            print(f"🗑️  投稿ID {post_id} を削除中...")
            delete_response2 = board.delete(post_id)
            
            if delete_response2.success:
                print(f"✅ {name} の削除に成功しました！")
                print(f"   ステータスコード: {delete_response2.status_code}")
                
                # 削除後の確認
                print("🔍 削除後の確認中...")
                time.sleep(2)  # 少し待機
                confirm_response2 = board.get_post(post_id)
                
                if not confirm_response2.success:
                    print("   ✅ 投稿が正常に削除されました（取得不可）")
                else:
                    print("   ⚠️  投稿がまだ存在している可能性があります")
            else:
                print(f"❌ {name} の削除に失敗しました")
                print(f"   エラー: {delete_response2.error}")
                print(f"   ステータスコード: {delete_response2.status_code}")
        
        print()
        
        # ステップ5: 存在しない投稿IDでの削除テスト
        print("📝 ステップ5: 存在しない投稿IDでの削除テスト...")
        
        fake_post_id = "YOUR_POST_ID"  # 存在しない投稿ID
        print(f"🗑️  存在しない投稿ID {fake_post_id} を削除中...")
        
        fake_delete_response = board.delete(fake_post_id)
        
        if fake_delete_response.success:
            print("⚠️  存在しない投稿の削除が成功してしまいました")
        else:
            print("✅ 存在しない投稿の削除は適切にエラーになりました")
            print(f"   エラー: {fake_delete_response.error}")
            print(f"   ステータスコード: {fake_delete_response.status_code}")
        
        print()
        print("🎉 投稿削除テストが完了しました！")
        print("\n📊 テスト結果まとめ:")
        
        # 結果集計
        successful_creates = len(created_posts)
        print(f"   テスト投稿作成: {successful_creates}件成功")
        
        if len(created_posts) >= 1:
            delete_result1 = "✅ 成功" if delete_response.success else "❌ 失敗"
            print(f"   投稿 #1 削除: {delete_result1}")
        
        if len(created_posts) >= 2:
            delete_result2 = "✅ 成功" if delete_response2.success else "❌ 失敗"
            print(f"   投稿 #2 削除: {delete_result2}")
        
        error_handling = "✅ 適切" if not fake_delete_response.success else "❌ 不適切"
        print(f"   エラーハンドリング: {error_handling}")
        
        print("\n📝 次のステップ:")
        print("1. 返信機能をテストする")
        print("2. 投稿一覧の取得で削除を確認")
        print("3. 検索機能をテストする")
        
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
