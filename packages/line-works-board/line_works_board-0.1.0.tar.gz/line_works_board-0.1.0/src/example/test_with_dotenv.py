"""
python-dotenvを使用したLINE WORKS Board API SDKの設定例

使用方法:
1. env_example.txtを.envにコピー
2. .envファイルに実際の値を設定
3. このスクリプトを実行
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from line_works_board import Board, BoardBody, ComposeBody, ReplyBody


def load_config_from_dotenv():
    """dotenvを使用して.envファイルから設定を読み込み"""
    # 現在のディレクトリから.envファイルを探す
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"❌ .envファイルが見つかりません: {env_path}")
        print("env_example.txtを.envにコピーして、実際の値を設定してください。")
        return None
    
    # .envファイルを読み込み
    load_dotenv(env_path)
    
    # 必須環境変数をチェック
    required_vars = [
        'LINE_WORKS_CLIENT_ID',
        'LINE_WORKS_CLIENT_SECRET', 
        'LINE_WORKS_SERVICE_ACCOUNT',
        'LINE_WORKS_PRIVATE_KEY',
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        print(".envファイルに値を設定してから再実行してください。")
        return None
    
    # 設定値を取得
    board_body = BoardBody(
        client_id=os.getenv('LINE_WORKS_CLIENT_ID'),
        client_secret=os.getenv('LINE_WORKS_CLIENT_SECRET'),
        service_account=os.getenv('LINE_WORKS_SERVICE_ACCOUNT'),
        private_key=os.getenv('LINE_WORKS_PRIVATE_KEY'),
        domain=os.getenv('LINE_WORKS_DOMAIN', 'worksmobile.com'),
        
    )
    
    board_id = "YOUR_BOARD_ID"
    
    print("✅ 設定の読み込みが完了しました")
    print(f"   クライアントID: {board_body.client_id}")
    print(f"   サービスアカウント: {board_body.service_account}")
    print(f"   掲示板ID: {board_id}")
    print(f"   ドメイン: {board_body.domain}")
    
    return board_body, board_id


def test_board_operations(board):
    """掲示板の基本操作をテスト"""
    print("\n🔍 掲示板の基本操作をテスト中...")
    
    # 1. 掲示板の情報を取得
    print("\n1. 掲示板の情報を取得中...")
    board_info = board.get_board_info()
    if board_info.success:
        print("   ✅ 掲示板の情報を取得しました")
        if board_info.data:
            print(f"     掲示板名: {board_info.data.get('name', 'N/A')}")
            print(f"     説明: {board_info.data.get('description', 'N/A')}")
    else:
        print(f"   ❌ 掲示板の情報取得に失敗: {board_info.error}")
    
    # 2. 投稿一覧を取得
    print("\n2. 投稿一覧を取得中...")
    posts = board.get_posts(limit=5)
    if posts.success:
        print("   ✅ 投稿一覧を取得しました")
        if posts.data and 'posts' in posts.data:
            post_count = len(posts.data['posts'])
            print(f"     投稿数: {post_count}")
            if post_count > 0:
                latest_post = posts.data['posts'][0]
                print(f"     最新投稿: {latest_post.get('title', 'N/A')}")
        else:
            print("     投稿はありません")
    else:
        print(f"   ❌ 投稿一覧の取得に失敗: {posts.error}")
    
    # 3. 投稿の作成テスト（コメントアウト）
    print("\n3. 投稿の作成テスト（コメントアウト）")
    print("   実際に投稿を作成するには、以下のコードのコメントアウトを解除してください:")
    print("   " + "="*50)
    print("   compose_body = ComposeBody(")
    print("       title='テスト投稿',")
    print("       content='これはテスト投稿です。',")
    print("       is_notice=False,")
    print("       is_secret=False")
    print("   )")
    print("   response = board.compose(compose_body)")
    print("   " + "="*50)
    
    #実際に投稿を作成したい場合は、以下のコメントアウトを解除
    compose_body = ComposeBody(
        title='テスト投稿',
        content='これはテスト投稿です。',
        is_notice=False,
        is_secret=False
    )
    response = board.compose(compose_body)
    if response.success:
        print("   ✅ テスト投稿が作成されました")
        print(f"     投稿ID: {response.data.get('postId')}")
    else:
        print(f"   ❌ テスト投稿の作成に失敗: {response.error}")


def main():
    """メイン処理"""
    print("🚀 python-dotenvを使用したLINE WORKS Board API SDKの設定例")
    print("=" * 70)
    
    # .envファイルから設定を読み込み
    config = load_config_from_dotenv()
    if not config:
        return
    
    board_body, board_id = config
    
    try:
        # 掲示板インスタンスを作成
        print("\n🔧 掲示板インスタンスを作成中...")
        board = Board(board_body, board_id)
        print("✅ 掲示板インスタンスが作成されました")
        
        # 認証テストを実行
        print("\n🔐 認証テストを実行中...")
        auth_result = board.test_auth()
        if auth_result.success:
            print("✅ 認証テストが成功しました！")
        else:
            print(f"❌ 認証テストが失敗しました: {auth_result.error}")
            return
        
        # 掲示板の基本操作をテスト
        test_board_operations(board)
        
        print("\n🎉 テストが完了しました！")
        print("\n📝 次のステップ:")
        print("1. 実際の投稿を作成する")
        print("2. 投稿の更新・削除を試す")
        print("3. 返信機能をテストする")
        print("4. 検索機能を試す")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("\n🔧 トラブルシューティング:")
        print("1. .envファイルの設定値を確認")
        print("2. 秘密鍵の形式が正しいか確認")
        print("3. LINE WORKS Developer Consoleの設定を確認")
        print("4. ネットワーク接続を確認")


if __name__ == "__main__":
    main()
