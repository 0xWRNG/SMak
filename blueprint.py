import json
import uuid
import os
from pathlib import Path
import PIL
import shutil


matrix = [
    ['1', '1', '1', '1', '1', '1', '1', '1', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['0', '0', '0', '0', '0', '0', '0', '0', ],
    ['2', '2', '2', '2', '2', '2', '2', '2', ],

]




def print_matrix(matrix):
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            if matrix[row][col] == '0':
                print('⬛', end='')
            elif matrix[row][col] == '1':
                print('⬜', end='')
            elif matrix[row][col] == '2':
                print('🏽', end='')

        print()


def change_symbol(corner, symbol):
    transform_rules = {
        'ul': {
            'h': 'hd', 'v': 'vr', 'dr': 'dr', 'dl': 'hd', 'ur': 'vr',
            'ul': 'hv', 'vr': 'vr', 'vl': 'hv', 'hd': 'hd', 'hu': 'hv',
            'hv': 'hv', ' ': 'dr'
        },
        'ur': {
            'h': 'hd', 'v': 'vl', 'dr': 'hd', 'dl': 'dl', 'ur': 'hv',
            'ul': 'vl', 'vr': 'hv', 'vl': 'vl', 'hd': 'hd', 'hu': 'hv',
            'hv': 'hv', ' ': 'dl'
        },
        'dl': {
            'h': 'hu', 'v': 'vr', 'dr': 'vr', 'dl': 'hv', 'ur': 'ur',
            'ul': 'hu', 'vr': 'vr', 'vl': 'hv', 'hd': 'hv', 'hu': 'hu',
            'hv': 'hv', ' ': 'ur'
        },
        'dr': {
            'h': 'hu', 'v': 'vl', 'dr': 'hv', 'dl': 'vl', 'ur': 'hu',
            'ul': 'ul', 'vr': 'hv', 'vl': 'vl', 'hd': 'hv', 'hu': 'hu',
            'hv': 'hv', ' ': 'ul'
        },
        'eu': {
            'h': 'h', 'ur': 'hu', 'ul': 'hu', 'hu': 'hu', ' ': 'h'
        },
        'ed': {
            'h': 'h', 'dr': 'hd', 'dl': 'hd', 'hd': 'hd', ' ': 'h'
        },
        'el': {
            'v': 'v', 'dl': 'vl', 'ul': 'vl', 'vl': 'vl', ' ': 'v'
        },
        'er': {
            'v': 'v', 'dr': 'vr', 'ur': 'vr', 'vr': 'vr', ' ': 'v'
        }
    }
    return transform_rules.get(corner, {}).get(symbol, '')


def print_rects(old_matrix, rectangles):
    symbols = {
        'h': '─', 'v': '│', 'dr': '┌', 'dl': '┐', 'ur': '└',
        'ul': '┘', 'vr': '├', 'vl': '┤', 'hd': '┬', 'hu': '┴',
        'hv': '┼', ' ': ' '
    }

    rows = len(old_matrix) + 1
    cols = len(old_matrix[0]) + 1
    grid = [[' '] * cols for _ in range(rows)]

    grid[0][0] = 'dr'
    grid[0][cols - 1] = 'dl'
    grid[rows - 1][0] = 'ur'
    grid[rows - 1][cols - 1] = 'ul'

    for j in range(1, cols - 1):
        grid[0][j] = 'h'
    for j in range(1, cols - 1):
        grid[rows - 1][j] = 'h'
    for i in range(1, rows - 1):
        grid[i][0] = 'v'
    for i in range(1, rows - 1):
        grid[i][cols - 1] = 'v'

    for top, left, bottom, right, _ in rectangles:
        corners = [
            ('ul', top, left),
            ('ur', top, right + 1),
            ('dl', bottom + 1, left),
            ('dr', bottom + 1, right + 1)
        ]

        for corner_type, r, c in corners:
            grid[r][c] = change_symbol(corner_type, grid[r][c])

        edges = [
            ('eu', top, left + 1, right),
            ('ed', bottom + 1, left + 1, right),
            ('el', left, top + 1, bottom),
            ('er', right + 1, top + 1, bottom)
        ]

        for edge_type, pos, start, end in edges:
            if edge_type in ('eu', 'ed'):
                for col in range(start, end + 1):
                    grid[pos][col] = change_symbol(edge_type, grid[pos][col])
            else:
                for row in range(start, end + 1):
                    grid[row][pos] = change_symbol(edge_type, grid[row][pos])

    for row in grid:
        print(' '.join(symbols.get(sym, '') for sym in row))


def get_segments(row):
    segments = []
    start = 0
    current_color = row[0]
    for j in range(1, len(row)):
        if row[j] != current_color:
            segments.append((start, j - 1, current_color))
            start = j
            current_color = row[j]
    segments.append((start, len(row) - 1, current_color))
    return segments


def matrix_to_rectangles(matrix):
    if not matrix or not matrix[0]:
        return 0, []

    rows = len(matrix)

    active_rects = []
    final_rects = []

    for i in range(rows):
        segments = get_segments(matrix[i])
        remaining_active = active_rects.copy()
        new_active_rects = []

        for seg in segments:
            start_col, end_col, color = seg
            found = False

            for idx, rect in enumerate(remaining_active):
                r_start, r_end, r_sc, r_ec, r_color = rect
                if r_sc == start_col and r_ec == end_col and r_color == color:
                    new_rect = (r_start, i, r_sc, r_ec, r_color)
                    new_active_rects.append(new_rect)
                    del remaining_active[idx]
                    found = True
                    break

            if not found:
                new_rect = (i, i, start_col, end_col, color)
                new_active_rects.append(new_rect)

        final_rects.extend(remaining_active)
        active_rects = new_active_rects

    final_rects.extend(active_rects)

    formatted_rects = []
    for rect in final_rects:
        start_row, end_row, start_col, end_col, color = rect
        formatted_rects.append((start_row, start_col, end_row, end_col, color))

    return len(formatted_rects), formatted_rects

def rectangles_to_json(rects=None):
    if rects is None:
        rects = []
    color_map = {
        "0": "222222",
        "1": "EEEEEE",
        "2": "D02525",
    }

    childs = []
    shapeId = str('628b2d61-5ceb-43e9-8334-a4135566df7a')

    for r1, c1, r2, c2, color_index in rects:
        width = r2 - r1+1
        height = c2 - c1+1

        child = {
            "bounds": {
                "x": width,
                "y": height,
                "z": 1
            },
            "color": color_map.get(color_index, "222222"),
            "pos": {
                "x": r1,
                "y": c1,
                "z": 2
            },
            "shapeId": shapeId,
            "xaxis": 1,
            "zaxis": 3
        }
        childs.append(child)

    result = {
        "bodies": [
            {
                "childs": childs
            }
        ],
        "version": 4
    }

    return result

def generate_description(description = "#{STEAM_WORKSHOP_NO_DESCRIPTION}",  blueprint_name = "Unnamed", uid = str(uuid.uuid4())):
    return {
        "description": description,
        "localId": uid,
        "name": blueprint_name,
        "type": "Blueprint",
        "version": 0,
    }


def update_ugccache(path, blueprint_id, name):
    ugc_path = os.path.join(path, 'ugccache.json')

    if os.path.exists(ugc_path):
        with open(ugc_path, "r", encoding="utf-8") as f:
            ugc_data = json.load(f)
    else:
        ugc_data = {}

    ugc_data[blueprint_id] = {"name": name}

    sorted_data = dict(sorted(ugc_data.items()))

    with open(ugc_path, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=3, ensure_ascii=False)

    print(f"ugccache.json updated: {blueprint_id} → {name}")

def update_program_registry(uid, name='Placeholder', type_='Placeholder'):
    filepath = 'program_registry.json'
    uid = str(uid)

    data = {}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    print("[!] Corrupted file, rewriting")
            else:
                print("[!] Empty file, rewriting")

    data[uid] = {
        "name": name,
        "type": type_
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_placeholder_uid(filepath='program_registry.json', new_name = 'Placeholder'):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("[!] File corrupted")
        return None

    for uid, info in data.items():
        if info.get("type") == "Placeholder":
            info["type"] = "Blueprint"
            info["name"] = new_name
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return uid

    print("[!] Placeholders not found")
    return None

def generate_placeholders(path, count):
    for _ in range(count):
        uid = str(uuid.uuid4())
        uid = 'f' * 2 + uid[2:]
        blueprint = rectangles_to_json()
        description = generate_description(blueprint_name='Placeholder', uid=uid)

        Path(path + '/Blueprints/' + uid).mkdir(parents=True, exist_ok=True)
        shutil.copy('assets/placeholder.png', path + '/Blueprints/' + uid + '/icon.png')

        with open(path + '/Blueprints/' + uid + '/blueprint.json', 'w') as f:
            json.dump(blueprint, f)
        print('Saved placeholder blueprint.json to:' + 'Blueprints/' + uid)

        with open(path + '/Blueprints/' + uid + '/description.json', 'w') as f:
            json.dump(description, f)
        print('Saved placeholder description.json to:' + 'Blueprints/' + uid)

        update_program_registry(uid, 'Placeholder')
        update_ugccache(path, uid, 'Placeholder')

def matrix_to_blueprint(matrix, path, description, blueprint_name):
    uid = get_placeholder_uid(new_name=blueprint_name)
    if uid is None:
        generate_placeholders(path,1)
        uid = get_placeholder_uid(new_name=blueprint_name)
    count,rectangles = matrix_to_rectangles(matrix[::-1])
    blueprint_data = rectangles_to_json(rectangles)
    blueprint_description = generate_description(description, blueprint_name, uid)
    shutil.copy('assets/cover.png', path+'/Blueprints/'+ uid+'/icon.png')
    print('Moved cover: icon.png')

    with open(path+'/Blueprints/'+ uid+'/blueprint.json', 'w') as f:
        json.dump(blueprint_data, f)
    print('Saved blueprint.json to:' + 'Blueprints/'+ uid)

    with open(path+'/Blueprints/'+ uid+'/description.json', 'w') as f:
        json.dump(blueprint_description, f)
    print('Saved description.json to:' + 'Blueprints/' + uid)
    update_ugccache(path, uid, blueprint_name)


matrix_to_blueprint(matrix, "C:/Users/abras/AppData/Roaming/Axolot Games/Scrap Mechanic/User/User_76561198121774007", "Test code fragment 2", "Coder")
# generate_placeholders("C:/Users/abras/AppData/Roaming/Axolot Games/Scrap Mechanic/User/User_76561198121774007", 5)