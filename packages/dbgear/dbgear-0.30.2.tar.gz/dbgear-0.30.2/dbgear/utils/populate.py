import re
import copy
from typing import Dict, Any, List


def auto_populate_from_keys(data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    階層データのキーから値を抽出して、指定されたパスに自動補完する関数

    Args:
        data: 元のYAMLデータ
        mapping: 補完ルールの辞書
                キー: 補完先のパステンプレート（値を設定する場所）
                値: 補完する値のテンプレート
                例: {'schemas.$1.name': '$1', 'schemas.$1.tables.$2.table_name': '$2'}

    Returns:
        補完されたデータ
    """
    result = copy.deepcopy(data)

    # 実際のデータパスを全て取得
    all_existing_paths = _get_all_paths(result)

    for target_template, value_template in mapping.items():
        # 既存パスから変数を抽出できるパターンを探す
        variables_found = _extract_variables_from_existing_paths(
            all_existing_paths, target_template
        )

        # 各変数組み合わせに対して補完を実行
        for variables in variables_found:
            # 補完先パスを生成
            target_path = _substitute_variables(target_template, variables)

            # 補完値を生成
            final_value = _substitute_variables(value_template, variables)

            # 値を設定
            _set_nested_value(result, target_path, final_value)

    return result


def _extract_variables_from_existing_paths(existing_paths: List[str], target_template: str) -> List[Dict[str, str]]:
    """
    既存パスから、補完先テンプレートで使用される変数を抽出
    """
    variables_list = []

    # テンプレートから必要な変数を特定
    required_vars = re.findall(r'\$(\d+)', target_template)
    if not required_vars:
        return []

    # 変数を抽出するためのパターンを作成
    extraction_pattern = target_template
    for var_num in sorted(set(required_vars), reverse=True):
        extraction_pattern = extraction_pattern.replace(f'${var_num}', '([^.]+)')

    # 補完先の最後の項目を削除して、既存パス用のパターンにする
    pattern_parts = extraction_pattern.split('.')
    if len(pattern_parts) > 1:
        base_pattern = '.'.join(pattern_parts[:-1])

        # 既存パスでマッチするものを全て試す
        for path in existing_paths:
            match = re.match(f'^{base_pattern}', path)
            if match:
                variables = {}
                for i, var_num in enumerate(sorted(set(required_vars)), 0):
                    if i < len(match.groups()):
                        variables[f'${var_num}'] = match.groups()[i]

                if variables and variables not in variables_list:
                    variables_list.append(variables)

    return variables_list


def _get_all_paths(data: Dict[str, Any], current_path: str = "") -> List[str]:
    """データ構造から全てのパスを取得"""
    paths = []

    def _traverse(obj, path):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                paths.append(new_path)
                _traverse(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                paths.append(new_path)
                _traverse(item, new_path)

    _traverse(data, current_path)
    return paths


def _substitute_variables(template: str, variables: Dict[str, str]) -> str:
    """テンプレート文字列に変数を代入"""
    result = template
    for var_name, var_value in variables.items():
        result = result.replace(var_name, var_value)
    return result


def _set_nested_value(data: Dict[str, Any], path: str, value: Any):
    """ネストした辞書の指定パスに値を設定"""
    keys = path.split('.')
    current = data

    # 最後のキー以外を辿る
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            return
        current = current[key]

    # 最後のキーに値を設定
    final_key = keys[-1]
    current[final_key] = value


# 使用例
if __name__ == "__main__":
    import yaml

    # サンプルデータ
    yaml_data = {
        'schemas': {
            'user_db': {
                'host': 'localhost',
                'tables': {
                    'users': {
                        'columns': ['id', 'name', 'email']
                    },
                    'posts': {
                        'columns': ['id', 'title', 'content']
                    }
                }
            },
            'product_db': {
                'host': 'remote',
                'tables': {
                    'products': {
                        'columns': ['id', 'name', 'price']
                    }
                }
            }
        }
    }

    # 補完ルール
    population_rules = {
        'schemas.$1.name': '$1',
        'schemas.$1.tables.$2.instance': '$1',
        'schemas.$1.tables.$2.table_name': '$2'
    }

    # 補完実行
    populated_data = auto_populate_from_keys(yaml_data, population_rules)

    print(yaml.dump(populated_data, default_flow_style=False, allow_unicode=True))
