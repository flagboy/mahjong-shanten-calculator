from flask import Flask, render_template, request, jsonify
from shanten import simulate_shanten

app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST', 'OPTIONS'])
def simulate():
    # CORS対応
    if request.method == 'OPTIONS':
        return '', 204
    data = request.get_json()
    remaining_man = data.get('remaining_man', '111122223333444455556666777888999')
    remaining_honors = data.get('remaining_honors', '')
    iterations = data.get('iterations', 10000)
    melds = data.get('melds', [])
    
    # 副露の数を考慮した必要牌数
    meld_count = len(melds)
    required_tiles = 13 - (meld_count * 3)
    
    # 入力検証
    total_tiles = len(remaining_man) + len(remaining_honors)
    
    # 必要な枚数以上あるか確認
    if total_tiles < required_tiles:
        return jsonify({'error': f'{required_tiles}枚以上の牌が必要です（副露: {meld_count}組）'}), 400
    
    # 萬子の検証
    if remaining_man and not all(c in '123456789' for c in remaining_man):
        return jsonify({'error': '萬子は1-9の数字で入力してください'}), 400
    
    # 字牌の検証（e=東,s=南,w=西,n=北,h=白,f=發,c=中）
    if remaining_honors and not all(c in 'eswnhfc' for c in remaining_honors):
        return jsonify({'error': '字牌はe,s,w,n,h,f,cで入力してください'}), 400
    
    try:
        result, examples = simulate_shanten(remaining_man, remaining_honors, iterations, melds)
        
        # 手牌の例を整形
        formatted_examples = {}
        for shanten, hand_list in examples.items():
            formatted_examples[shanten] = []
            for hand_data in hand_list:
                # 手牌のみを表示用に整形
                hand_tiles = []
                melds_display = []
                
                # 手牌のみの牌を処理
                hand_only = hand_data.get('hand', [])
                man_tiles = []
                honor_tiles = []
                
                for tile in hand_only:
                    if tile in '123456789':
                        man_tiles.append(tile)
                    elif tile in 'eswnhfc':
                        honor_tiles.append(tile)
                
                # 萬子を追加
                for tile in sorted(man_tiles):
                    hand_tiles.append({
                        'type': 'man',
                        'value': tile,
                        'image': f'/static/images/p_ms{tile}_1.gif'
                    })
                
                # 字牌を追加
                honor_mapping = {'e': '1', 's': '2', 'w': '3', 'n': '4', 'h': '5', 'f': '6', 'c': '7'}
                honor_to_img = {'e': 'e', 's': 's', 'w': 'w', 'n': 'n', 'h': 'haku', 'f': 'h', 'c': 'c'}
                
                for tile in sorted(honor_tiles):
                    hand_tiles.append({
                        'type': 'honor',
                        'value': honor_mapping[tile],
                        'image': f'/static/images/p_ji_{honor_to_img[tile]}_1.gif'
                    })
                
                # 副露を処理
                melds = hand_data.get('melds', [])
                for meld in melds:
                    meld_tiles = []
                    for tile in meld:
                        meld_tiles.append(tile)  # 既に整形済みのデータ
                    melds_display.append(meld_tiles)
                
                formatted_examples[shanten].append({
                    'hand': hand_tiles,
                    'melds': melds_display
                })
        
        return jsonify({
            'result': result,
            'examples': formatted_examples,
            'total_tiles': total_tiles,
            'iterations': iterations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, port=port, host='0.0.0.0')