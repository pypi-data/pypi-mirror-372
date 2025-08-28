#!/usr/bin/env python3
"""
LINE WORKS Board API SDKの投稿返信テスト
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import time

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from line_works_board.types import BoardBody, ComposeBody, ReplyBody
from line_works_board.board import Board

def main():
    """メイン関数"""
    print("🚀 LINE WORKS Board API SDKの投稿返信テスト")
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
        
        # ステップ1: 返信用のテスト投稿を作成
        print("📝 ステップ1: 返信用のテスト投稿を作成中...")
        
        main_post_compose_body = ComposeBody(
            title='返信テスト用メイン投稿',
            body='この投稿は返信機能のテストに使用されます。\n\n以下の返信テストを実施予定:\n- 通常の返信\n- 秘密返信\n- 複数返信\n\n作成時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            enableComment=True,  # 返信を許可
            sendNotifications=False  # テスト投稿なので通知は無効
        )
        
        print("📤 メイン投稿を作成中...")
        create_response = board.compose(main_post_compose_body)
        
        if not create_response.success:
            print(f"❌ メイン投稿の作成に失敗しました: {create_response.error}")
            return
        
        # 投稿IDを取得
        main_post_id = None
        if create_response.data:
            main_post_id = create_response.data.get('postId') or create_response.data.get('id')
        
        if not main_post_id:
            print("❌ メイン投稿のIDを取得できませんでした")
            return
        
        print("✅ メイン投稿の作成に成功しました！")
        print(f"   投稿ID: {main_post_id}")
        print()
        
        # ステップ2: 通常のコメントを作成
        print("📝 ステップ2: 通常のコメントを作成中...")
        
        reply1_body = ReplyBody(
            content='これは通常のコメントです。\n\n✅ 公開コメント\n✅ 全員に表示される\n\nコメント時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        print("💬 通常のコメントを作成中...")
        reply1_response = board.reply(reply1_body, main_post_id)
        
        if reply1_response.success:
            print("✅ 通常のコメント作成に成功しました！")
            print(f"   ステータスコード: {reply1_response.status_code}")
            if reply1_response.data:
                reply1_id = reply1_response.data.get('commentId') or reply1_response.data.get('id')
                if reply1_id:
                    print(f"   コメントID: {reply1_id}")
        else:
            print(f"❌ 通常のコメント作成に失敗しました")
            print(f"   エラー: {reply1_response.error}")
            print(f"   ステータスコード: {reply1_response.status_code}")
        
        print()
        
        # 少し待機
        time.sleep(1)
        
        # ステップ3: 追加のコメントを作成（会話の流れをシミュレート）
        print("📝 ステップ3: 追加のコメントを作成中...")
        
        reply2_body = ReplyBody(
            content='フォローアップのコメントです。\n\n📋 追加情報:\n- コメント機能のテストが順調に進行中\n- 複数のコメントがある投稿での動作確認\n- APIの安定性をテスト中\n\nコメント時刻: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        print("💬 追加コメントを作成中...")
        reply2_response = board.reply(reply2_body, main_post_id)
        
        if reply2_response.success:
            print("✅ 追加コメント作成に成功しました！")
            print(f"   ステータスコード: {reply2_response.status_code}")
            if reply2_response.data:
                reply2_id = reply2_response.data.get('commentId') or reply2_response.data.get('id')
                if reply2_id:
                    print(f"   コメントID: {reply2_id}")
        else:
            print(f"❌ 追加コメント作成に失敗しました")
            print(f"   エラー: {reply2_response.error}")
            print(f"   ステータスコード: {reply2_response.status_code}")
        
        print()
        
        # ステップ4: コメント一覧を取得
        print("📝 ステップ4: コメント一覧を取得中...")
        
        print(f"📥 投稿ID {main_post_id} のコメント一覧を取得中...")
        replies_response = board.get_replies(main_post_id, limit=10)
        
        if replies_response.success:
            print("✅ コメント一覧の取得に成功しました！")
            print(f"   ステータスコード: {replies_response.status_code}")
            
            if replies_response.data and 'comments' in replies_response.data:
                comments = replies_response.data['comments']
                print(f"   コメント数: {len(comments)}件")
                
                for i, comment in enumerate(comments, 1):
                    print(f"\n   コメント #{i}:")
                    print(f"     ID: {comment.get('id', 'N/A')}")
                    print(f"     内容: {(comment.get('content', 'N/A')[:50] + '...') if len(comment.get('content', '')) > 50 else comment.get('content', 'N/A')}")
                    print(f"     作成者: {comment.get('author', {}).get('name', 'N/A')}")
                    print(f"     作成日時: {comment.get('createdAt', 'N/A')}")
            else:
                print("   コメントが見つかりませんでした")
        else:
            print(f"❌ コメント一覧の取得に失敗しました")
            print(f"   エラー: {replies_response.error}")
            print(f"   ステータスコード: {replies_response.status_code}")
        
        print()
        
        # ステップ5: コメント無効の投稿でのコメントテスト
        print("📝 ステップ5: コメント無効投稿でのコメントテスト...")
        
        no_comment_post_body = ComposeBody(
            title='コメント無効投稿テスト',
            body='この投稿はコメントが無効になっています。\n\nコメントが作成できないことを確認します。',
            enableComment=False,  # コメントを無効化
            sendNotifications=False
        )
        
        print("📤 コメント無効投稿を作成中...")
        no_comment_response = board.compose(no_comment_post_body)
        
        if no_comment_response.success:
            no_comment_post_id = no_comment_response.data.get('postId') or no_comment_response.data.get('id') if no_comment_response.data else None
            
            if no_comment_post_id:
                print(f"✅ コメント無効投稿を作成しました: {no_comment_post_id}")
                
                # コメント無効投稿へのコメントを試行
                test_reply_body = ReplyBody(
                    content='このコメントは失敗するはずです（コメント無効のため）'
                )
                
                print("💬 コメント無効投稿へのコメントを試行中...")
                test_reply_response = board.reply(test_reply_body, no_comment_post_id)
                
                if test_reply_response.success:
                    print("⚠️  コメント無効投稿へのコメントが成功してしまいました")
                else:
                    print("✅ コメント無効投稿へのコメントは適切にエラーになりました")
                    print(f"   エラー: {test_reply_response.error}")
                    print(f"   ステータスコード: {test_reply_response.status_code}")
        
        print()
        print("🎉 投稿コメントテストが完了しました！")
        print("\n📊 テスト結果まとめ:")
        print(f"   メイン投稿作成: {'✅ 成功' if create_response.success else '❌ 失敗'}")
        print(f"   通常コメント作成: {'✅ 成功' if reply1_response.success else '❌ 失敗'}")
        print(f"   追加コメント作成: {'✅ 成功' if reply2_response.success else '❌ 失敗'}")
        print(f"   コメント一覧取得: {'✅ 成功' if replies_response.success else '❌ 失敗'}")
        
        if no_comment_response.success:
            error_handling = "✅ 適切" if not test_reply_response.success else "❌ 不適切"
            print(f"   エラーハンドリング: {error_handling}")
        
        print(f"\n📋 作成されたメイン投稿ID: {main_post_id}")
        print("\n📝 次のステップ:")
        print("1. 投稿一覧でコメント付き投稿を確認")
        print("2. 検索機能をテストする")
        print("3. 大量データでのパフォーマンステスト")
        
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
