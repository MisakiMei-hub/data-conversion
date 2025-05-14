import os
from datetime import datetime

# 元素周期表顺序（按原子序数）
PERIODIC_TABLE_ORDER = [
    'H', 'He',
    'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
    'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
    'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
    'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
    'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
    'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
    'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
    'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
    'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No',
    'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn',
    'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'
]

def get_element_order(element):
    """获取元素在周期表中的顺序"""
    element = element.capitalize()
    if element in PERIODIC_TABLE_ORDER:
        return PERIODIC_TABLE_ORDER.index(element)
    return len(PERIODIC_TABLE_ORDER)  # 未知元素放在最后

def convert_type1_to_type2(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = [
        '!BIOSYM archive 2',
        'PBC=ON',
        '                      Energy         0          0.0301         -6.768682        C1',
        '!DATE'
    ]

    # 处理PBC行但不作为原子行
    pbc_line_added = False
    for line in lines:
        if line.strip().startswith('PBC') and 'P1' in line and not pbc_line_added:
            output_lines.append(line.strip())
            pbc_line_added = True
            break

    # 收集所有原子信息
    atoms = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 4:
            try:
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                if not parts[0].startswith('PBC'):
                    # 提取纯元素符号
                    element = ''.join([c for c in parts[0] if not c.isdigit()])
                    element = element.capitalize()
                    atoms.append({
                        'element': element,
                        'x': x,
                        'y': y,
                        'z': z,
                        'original_line': line
                    })
            except ValueError:
                continue

    # 先按元素周期表排序，再按z坐标排序
    atoms.sort(key=lambda atom: (get_element_order(atom['element']), atom['z']))

    # 添加排序后的原子
    atom_index = 1
    for atom in atoms:
        element = atom['element']
        x, y, z = atom['x'], atom['y'], atom['z']
        
        formatted_line = (
            f"{element:4}"
            f"{x:15.9f}{y:15.9f}{z:15.9f}"
            f"{' CORE':>6}"
            f"{atom_index:>6}"
            f"{element:>4}{element:>4}"
            f"{0.0000:>10.4f}"
            f"{atom_index:>8}"
        )
        output_lines.append(formatted_line)
        atom_index += 1

    output_lines.append('end')
    output_lines.append('end')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

def process_directory():
    current_dir = os.getcwd()
    
    for filename in os.listdir(current_dir):
        if filename.endswith(('.car')) and not filename.startswith('converted_'):
            input_path = os.path.join(current_dir, filename)
            output_filename = f'input.arc'
            output_path = os.path.join(current_dir, output_filename)
            
            print(f'Processing: {filename}')
            try:
                convert_type1_to_type2(input_path, output_path)
                print(f'Saved as: {output_filename}')
            except Exception as e:
                print(f'Error processing {filename}: {str(e)}')

if __name__ == "__main__":
    process_directory()
定义元素周期表顺序 PERIODIC_TABLE_ORDER（按原子序排列）

函数 GetElementOrder(元素):
    将元素名标准化（首字母大写）
    若元素存在于周期表中:
        返回其索引
    否则返回一个较大值（表示未知元素）

函数 ConvertType1ToType2(输入路径, 输出路径):
    读取输入文件中所有行
    初始化输出文件的开头内容（包括 Energy 行和 PBC）
    在输入文件中查找包含 "PBC" 和 "P1" 的行，写入输出内容中（仅添加一次）
    初始化原子列表
    对于每一行:
        分割字符串，若至少包含四个部分:
            尝试解析第2~4列为坐标
            若成功且非PBC行:
                提取元素符号（去除尾部数字）
                存储元素、坐标、原始行等信息
    对原子列表排序：
        首先根据元素在周期表中的顺序排序
        然后根据 z 坐标升序排序
    遍历排序后的原子列表，按 `.arc` 格式逐行写入：
        每行包含元素、坐标、标签、编号等信息
    写入 "end" 和 "end" 表示文件结束

函数 ProcessDirectory():
    获取当前目录
    遍历当前目录下所有文件:
        若文件以 ".car" 结尾，且不以 "converted_" 开头:
            设置输入路径和输出路径（命名为 input.arc）
            调用 ConvertType1ToType2 处理该文件

主程序入口:
    调用 ProcessDirectory()
