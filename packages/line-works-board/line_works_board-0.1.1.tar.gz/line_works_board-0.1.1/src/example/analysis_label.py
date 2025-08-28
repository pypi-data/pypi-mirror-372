#!/usr/bin/env python3
"""
LINE WORKS Board API SDKの投稿ラベル分析
指定された投稿のデータ構造を調査してラベル情報の格納場所を特定する
"""
import os
import sys
import json
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from line_works_board.types import BoardBody
from line_works_board.board import Board

def analyze_post_structure(post_data, indent=0):
    """投稿データ構造を詳細に分析"""
    prefix = "  " * indent
    
    if isinstance(post_data, dict):
        for key, value in post_data.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}: {type(value).__name__}")
                analyze_post_structure(value, indent + 1)
            else:
                # 文字列の場合は長さ制限して表示
                if isinstance(value, str) and len(value) > 100:
                    display_value = value[:100] + "..."
                else:
                    display_value = value
                print(f"{prefix}{key}: {display_value}")
    elif isinstance(post_data, list):
        for i, item in enumerate(post_data):
            print(f"{prefix}[{i}]: {type(item).__name__}")
            analyze_post_structure(item, indent + 1)

def search_for_labels(data, path=""):
    """データ構造内でラベルに関連する可能性のある項目を検索"""
    label_keywords = ['label', 'tag', 'category', 'type', 'classification', 'badges', 'flags']
    findings = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            # キー名にラベル関連のキーワードが含まれているかチェック
            for keyword in label_keywords:
                if keyword.lower() in key.lower():
                    findings.append({
                        'path': current_path,
                        'key': key,
                        'value': value,
                        'type': type(value).__name__,
                        'reason': f"キー名に '{keyword}' を含む"
                    })
                    break
            
            # 再帰的に検索
            findings.extend(search_for_labels(value, current_path))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            findings.extend(search_for_labels(item, current_path))
    
    return findings

def main():
    """メイン関数"""
    print("🔍 LINE WORKS Board API SDKの投稿ラベル分析")
    print("=" * 60)
    
    # 環境変数の読み込み
    load_dotenv()
    
    board_id = "YOUR_BOARD_ID"
    target_post_id = "YOUR_POST_ID"  # 分析対象の投稿ID
    
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
    print(f"   分析対象投稿ID: {target_post_id}")
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
        
        # 指定された投稿を取得
        print(f"📥 投稿ID {target_post_id} を取得中...")
        get_response = board.get_post(target_post_id)
        
        if not get_response.success:
            print(f"❌ 投稿の取得に失敗しました: {get_response.error}")
            print(f"   ステータスコード: {get_response.status_code}")
            return
        
        if not get_response.data:
            print("❌ 投稿データが空です")
            return
        
        print("✅ 投稿の取得に成功しました！")
        print()
        
        post_data = get_response.data
        
        # 基本情報の表示
        print("📋 基本投稿情報:")
        print(f"   タイトル: {post_data.get('title', 'N/A')}")
        print(f"   内容: {(post_data.get('body', 'N/A')[:100] + '...') if len(post_data.get('body', '')) > 100 else post_data.get('body', 'N/A')}")
        print(f"   作成者: {post_data.get('author', {}).get('name', 'N/A')}")
        print(f"   作成日時: {post_data.get('createdAt', 'N/A')}")
        print()
        
        # JSON形式で完全なデータを保存
        print("💾 完全なレスポンスデータをJSONファイルに保存中...")
        json_filename = f"post_{target_post_id}_analysis.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, ensure_ascii=False, indent=2)
        print(f"   保存先: {json_filename}")
        print()
        
        # データ構造の詳細分析
        print("🔍 データ構造の詳細分析:")
        print("-" * 40)
        analyze_post_structure(post_data)
        print()
        
        # ラベル関連項目の検索
        print("🏷️  ラベル関連項目の検索:")
        print("-" * 40)
        label_findings = search_for_labels(post_data)
        
        if label_findings:
            print(f"   見つかった候補: {len(label_findings)}件")
            for finding in label_findings:
                print(f"   📍 {finding['path']}")
                print(f"      キー: {finding['key']}")
                print(f"      値: {finding['value']}")
                print(f"      型: {finding['type']}")
                print(f"      理由: {finding['reason']}")
                print()
        else:
            print("   ❌ ラベル関連の項目は見つかりませんでした")
        
        # 特定のフィールドの詳細確認
        print("🔎 特定フィールドの詳細確認:")
        print("-" * 40)
        
        # タイトルの詳細分析
        title = post_data.get('title', '')
        print(f"   タイトル詳細:")
        print(f"     内容: '{title}'")
        print(f"     文字数: {len(title)}")
        print(f"     ブラケット含有: {'[' in title or ']' in title}")
        print()
        
        # メタデータの確認
        if 'metadata' in post_data:
            print("   メタデータ:")
            analyze_post_structure(post_data['metadata'], 2)
        
        # 属性情報の確認
        if 'attributes' in post_data:
            print("   属性情報:")
            analyze_post_structure(post_data['attributes'], 2)
        
        # カスタムフィールドの確認
        if 'customFields' in post_data:
            print("   カスタムフィールド:")
            analyze_post_structure(post_data['customFields'], 2)
        
        print()
        print("🎉 投稿ラベル分析が完了しました！")
        print()
        print("📊 分析結果サマリー:")
        print(f"   投稿ID: {target_post_id}")
        print(f"   データフィールド数: {len(post_data) if isinstance(post_data, dict) else 'N/A'}")
        print(f"   ラベル候補数: {len(label_findings)}")
        print(f"   詳細データ: {json_filename}")
        print()
        print("📝 次のステップ:")
        print("1. JSONファイルを手動で確認")
        print("2. ラベル関連フィールドの特定")
        print("3. ラベル付き投稿作成のテスト")
        
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
