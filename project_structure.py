import os

def get_project_structure(start_path='.', output_file='project_structure.txt'):
    """
    Рекурсивно сканирует структуру папок и файлов, начиная с start_path,
    и сохраняет её в output_file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(start_path):
            level = root.replace(start_path, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                f.write(f"{subindent}{file}\n")

if __name__ == "__main__":
    print("Сканирую структуру проекта...")
    get_project_structure()
    print("Готово! Результат сохранён в project_structure.txt")
