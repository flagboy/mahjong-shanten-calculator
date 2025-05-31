from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter
from collections import defaultdict
import random
import sys

def simulate_shanten(remaining_man='111122223333444455556666777888999', remaining_honors='', iterations=100000, melds=None, collect_examples=True):
    shanten = Shanten()
    s = defaultdict(int)
    examples = defaultdict(list)
    
    # 残り牌をリストに変換（各文字を個別の要素として）
    all_remaining = list(remaining_man + remaining_honors)
    
    # 副露の数を考慮
    if melds is None:
        melds = []
    meld_count = len(melds)
    tiles_to_select = 13 - (meld_count * 3)  # 副露分を引いた枚数を選択
    
    # ポンされている字牌を収集
    ponned_honors = set()
    for meld in melds:
        if len(meld) == 3 and meld[0]['type'] == 'honor':
            # 同じ字牌3枚の場合（ポン）
            if meld[0]['value'] == meld[1]['value'] == meld[2]['value']:
                ponned_honors.add(meld[0]['value'])
    
    completed = 0
    while completed < iterations:
        # 必要な枚数をランダムに選択
        selected = random.sample(all_remaining, tiles_to_select)
        
        # 副露の牌を追加
        meld_tiles = []
        for meld in melds:
            for tile in meld:
                if tile['type'] == 'man':
                    meld_tiles.append(tile['value'])
                else:  # honor
                    meld_tiles.append(tile['value'])
        
        # 全ての牌を結合
        all_tiles = selected + meld_tiles
        
        # 字牌の枚数をチェック
        honor_count = {}
        for tile in all_tiles:
            if tile in 'eswnhfc':
                honor_count[tile] = honor_count.get(tile, 0) + 1
        
        # 同じ字牌を4つ持つ場合は再抽選
        if any(count >= 4 for count in honor_count.values()):
            continue
        
        # ポンされている字牌の残り1枚を持つ場合は再抽選
        # ポンされた字牌が手牌内に存在し、かつその枚数が1枚の場合
        skip_hand = False
        for honor in ponned_honors:
            hand_count = sum(1 for t in selected if t == honor)
            if hand_count == 1:  # 手牌内にポンされた字牌が1枚だけある
                skip_hand = True
                break
        if skip_hand:
            continue
        
        # 萬子と字牌に分離
        man = ''
        honors = ''
        honor_mapping = {'e': '1', 's': '2', 'w': '3', 'n': '4', 'h': '5', 'f': '6', 'c': '7'}
        
        for tile in all_tiles:
            if tile in '123456789':
                man += tile
            elif tile in honor_mapping:
                honors += honor_mapping[tile]
        
        # ソート
        man = ''.join(sorted(man))
        honors = ''.join(sorted(honors))
        
        # 副露がある場合も含めて13枚として扱う
        # ただし、副露は完成面子として扱われるべきなので、
        # 計算上は手牌のみでシャンテン数を算出する
        tiles = TilesConverter.string_to_34_array(man=man, honors=honors)
        
        # 副露の数に応じてシャンテン計算を調整
        if meld_count > 0:
            # 副露がある場合の特別な処理
            # 13枚のうち副露分を除いた手牌でシャンテン計算
            hand_man = ''
            hand_honors = ''
            
            for tile in selected:  # selectedは副露を除いた手牌のみ
                if tile in '123456789':
                    hand_man += tile
                elif tile in honor_mapping:
                    hand_honors += honor_mapping[tile]
            
            hand_man = ''.join(sorted(hand_man))
            hand_honors = ''.join(sorted(hand_honors))
            
            hand_tiles = TilesConverter.string_to_34_array(man=hand_man, honors=hand_honors)
            
            # 手牌のみでシャンテン計算（七対子と国士無双は副露不可なので無効化）
            result = shanten.calculate_shanten(hand_tiles, use_chiitoitsu=False, use_kokushi=False)
            
            # 副露を考慮したシャンテン数の調整
            # 副露1つにつき1面子完成とみなす
            # 基本形: (4 - 完成面子数) * 2 - 対子・塔子の有効数 - 1
            # ただし、mahjongライブラリが内部で調整しているため、ここでは調整しない
        else:
            # 副露なしの通常計算
            result = shanten.calculate_shanten(tiles)
        
        # アガリ（-1）の場合は再抽選
        if result == -1:
            continue
            
        s[result] += 1
        
        # 手牌の例を収集（各シャンテン数につき最大3つ）
        if collect_examples and len(examples[result]) < 3:
            examples[result].append({
                'man': man,
                'honors': honors,
                'tiles': all_tiles,  # 副露を含む全ての牌
                'hand': selected,   # 手牌のみ
                'melds': melds      # 副露
            })
        
        completed += 1
    
    return dict(s), dict(examples)

# 旧APIとの互換性
def simulate_shanten_compat(remaining_tiles='111122223333444455556666777888999', iterations=100000):
    # 萬子のみの場合
    return simulate_shanten(remaining_man=remaining_tiles, remaining_honors='', iterations=iterations)

if __name__ == "__main__":
    # コマンドライン引数から残り牌を取得
    if len(sys.argv) > 1:
        remaining = sys.argv[1]
    else:
        remaining = '111122223333444455556666777888999'
    
    # 反復回数の指定（オプション）
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
    
    result = simulate_shanten(remaining_man=remaining, iterations=iterations)
    print(result)