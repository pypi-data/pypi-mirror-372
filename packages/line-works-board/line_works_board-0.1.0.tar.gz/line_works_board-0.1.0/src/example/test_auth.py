#!/usr/bin/env python3
"""
LINE WORKS Board API SDKの認証テスト
"""
import os
import sys
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from line_works_board.types import BoardBody
from line_works_board.board import Board

def main():
    """メイン関数"""
    print("🚀 LINE WORKS Board API SDKの認証テスト")
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
        print("  - LINE_WORKS_BOARD_ID")
        print("  - LINE_WORKS_DOMAIN (オプション)")
        return
    
    print("✅ 設定の読み込みが完了しました")
    print(f"   クライアントID: {client_id}")
    print(f"   サービスアカウント: {service_account}")
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
        
        print()
        print("📊 認証テスト結果:")
        print(f"   成功: {auth_result.success}")
        if auth_result.success:
            print(f"   ステータスコード: {auth_result.status_code}")
            if auth_result.data:
                print(f"   メッセージ: {auth_result.data.get('message', 'N/A')}")
        else:
            print(f"   エラー: {auth_result.error}")
            print(f"   ステータスコード: {auth_result.status_code}")
        
        print()
        if auth_result.success:
            print("🎉 認証テストが成功しました！")
        else:
            print("❌ 認証テストが失敗しました")
            print("設定値や秘密鍵の形式を確認してください")
            
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
