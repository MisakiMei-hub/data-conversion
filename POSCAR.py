import os
import glob

def convert_all_to_poscar(all_file_path, poscar_file_path):
    # 读取输入文件
    with open(all_file_path, 'r') as f:
        lines = f.readlines()
    
    # 初始化存储变量
    lattice_vectors = []
    species = []
    positions = []
    selective_dynamics = []
    
    # 解析文件内容
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line == "%BLOCK LATTICE_CART":
            i += 1
            # 读取晶格矢量
            for _ in range(3):
                lattice_vectors.append([float(x) for x in lines[i].strip().split()])
                i += 1
                
        elif line == "%BLOCK POSITIONS_FRAC":
            i += 1
            while i < len(lines) and lines[i].strip() != "%ENDBLOCK POSITIONS_FRAC":
                parts = lines[i].strip().split()
                if len(parts) >= 4:
                    species.append(parts[0])
                    positions.append([float(x) for x in parts[1:4]])
                    # 默认所有原子可移动
                    selective_dynamics.append(["T", "T", "T"])
                i += 1
        i += 1
    
    # 统计各元素数量
    unique_species = sorted(list(set(species)))
    species_counts = {s: species.count(s) for s in unique_species}
    
    # 合并数据用于排序
    combined = list(zip(species, positions, selective_dynamics))
    # 按z坐标排序
    combined.sort(key=lambda x: x[1][2])
    
    # 写入POSCAR文件（修正缩进格式）
    with open(poscar_file_path, 'w') as f:
        # 系统名称行
        f.write(" ".join(unique_species) + "\n")
        
        # 缩放因子行
        f.write("   1.00000000\n")  # 缩进4个空格
        
        # 晶格矢量（每行缩进8个空格）
        for vec in lattice_vectors:
            f.write("   " + " ".join(["%19.15f" % x for x in vec]) + "\n")
        
        # 元素行和数量行（缩进4个空格）
        f.write("   " + " ".join(unique_species) + "\n")
        f.write("   " + " ".join(map(str, [species_counts[s] for s in unique_species])) + "\n")
        
        # 选择动力学和坐标类型行
        f.write("Selective Dynamics\n")
        f.write("Direct\n")
        
        # 原子位置（每行缩进4个空格）
        for item in combined:
            species, pos, sd = item
            pos_str = " ".join(["%19.15f" % x for x in pos])
            f.write("   " + pos_str + "   " + " ".join(sd) + "\n")  # 位置和标记间加3个空格

def find_and_convert_files():
    # 获取当前目录所有cell文件
    cell_files = glob.glob('*.cell')
    
    # 排除已生成的POSCAR文件
    input_files = [f for f in cell_files if not f.lower().startswith('poscar')]
    
    if not input_files:
        print("当前目录未找到可转换的输入文件")
        return
    
    for input_file in input_files:
        # 生成输出文件名
        base_name = os.path.splitext(input_file)[0]
        output_file = f"POSCAR"
        
        try:
            convert_all_to_poscar(input_file, output_file)
            print(f"成功转换: {input_file} -> {output_file}")
        except Exception as e:
            print(f"转换失败 {input_file}: {str(e)}")

if __name__ == "__main__":
    print("正在扫描当前目录...")
    find_and_convert_files()
    print("转换完成")
