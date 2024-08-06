import os

def generate_tree(dir_path, max_depth, current_depth=0, prefix="", exclude=None):
    if exclude is None:
        exclude = {"__pycache__", ".git", ".idea", ".venv", ".gitignore", ".gitattributes", "migrations"}

    if current_depth > max_depth:
        return ""

    tree_str = ""
    try:
        items = os.listdir(dir_path)
    except PermissionError:
        return ""

    for i, item in enumerate(items):
        if item in exclude:
            continue

        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            tree_str += f"{prefix}├── {item}/\n"
            tree_str += generate_tree(item_path, max_depth, current_depth + 1, prefix + "│   ", exclude)
        else:
            tree_str += f"{prefix}├── {item}\n"

    return tree_str

def save_tree_to_file(dir_path, file_path, max_depth):
    tree = generate_tree(dir_path, max_depth)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"# {zagolovok}\n\n")
        file.write("# Directory Tree\n")
        file.write(f"## {dir_path}\n\n")
        file.write("```\n")
        file.write(tree)
        file.write("```\n")

# Переменные
zagolovok = 'Структура файлов и папок проекта "flowers_shop" в формате дерева с разметкой в Markdown'
papka_project = "../../flowers_shop"  # Замените на путь к вашей папке
file_out = "for_chat_derevo_project.md"  # Замените на путь к выходному файлу
urovni = 3  # Максимальный уровень вложенности

# Генерация дерева и сохранение в файл
save_tree_to_file(papka_project, file_out, urovni)
