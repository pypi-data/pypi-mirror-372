"""
LINE WORKS Board API SDK の使用例
"""
from src.line_works_board import Board, BoardBody, ComposeBody, ReplyBody

def main():
    """メイン処理"""
    print("LINE WORKS Board API SDK の使用例")
    print("=" * 50)
    
    # 設定情報（実際の値に置き換えてください）
    board_body = BoardBody(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        service_account="YOUR_SERVICE_ACCOUNT",
        private_key="YOUR_PRIVATE_KEY",
        domain="your-domain.worksmobile.com"  # オプション
    )
    
    # 掲示板ID（実際の値に置き換えてください）
    board_id = "YOUR_BOARD_ID"
    
    try:
        # 掲示板インスタンスを作成
        board = Board(board_body, board_id)
        print("✓ 掲示板インスタンスが作成されました")
        
        # 掲示板の情報を取得
        print("\n掲示板の情報を取得中...")
        board_info = board.get_board_info()
        if board_info.success:
            print("✓ 掲示板の情報を取得しました")
            print(f"  データ: {board_info.data}")
        else:
            print(f"✗ 掲示板の情報取得に失敗: {board_info.error}")
        
        # 投稿一覧を取得
        print("\n投稿一覧を取得中...")
        posts = board.get_posts(limit=5)
        if posts.success:
            print("✓ 投稿一覧を取得しました")
            print(f"  投稿数: {len(posts.data.get('posts', [])) if posts.data else 0}")
        else:
            print(f"✗ 投稿一覧の取得に失敗: {posts.error}")
            
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        print("\n注意: 実際に使用する前に、以下の設定を行ってください:")
        print("1. LINE WORKS Developer Consoleでアプリを作成")
        print("2. クライアントID、クライアントシークレットを取得")
        print("3. サービスアカウントと秘密鍵を設定")
        print("4. 掲示板IDを指定")

if __name__ == "__main__":
    main()
