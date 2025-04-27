import os
import json
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Source, ModuleDef, Function, Task


def extract_comments_from_node(node):
    """从AST节点中提取注释"""
    comments = []

    # 获取节点前的注释
    if hasattr(node, 'attr') and hasattr(node.attr, 'leading_comments'):
        for comment in node.attr.leading_comments:
            comment_text = comment.lstrip('//').strip()
            if comment_text and not any(word in comment_text.lower() for word in ['todo', 'fixme']):
                comments.append(comment_text)

    # 获取节点内的注释
    if hasattr(node, 'attr') and hasattr(node.attr, 'inline_comments'):
        for comment in node.attr.inline_comments:
            comment_text = comment.lstrip('//').strip()
            if comment_text and not any(word in comment_text.lower() for word in ['todo', 'fixme']):
                comments.append(comment_text)

    return comments


def extract_functions_with_comments(verilog_file):
    """提取Verilog文件中带有自然语言注释的函数"""
    try:
        file_path = os.path.abspath(verilog_file)
        print(file_path)
        ast, _ = parse([file_path])
    except Exception as e:
        print(f"解析文件 {file_path} 时出错: {str(e)}")
        return []

    functions = []

    for description in ast.description.definitions:
        if isinstance(description, ModuleDef):
            # 在模块定义中查找函数和任务
            for item in description.items:
                if isinstance(item, (Function, Task)):
                    # 获取函数/任务名称
                    func_name = item.name

                    # 获取函数前的注释
                    comments = extract_comments_from_node(item)

                    # 获取函数体中的注释
                    if hasattr(item, 'statement'):
                        for stmt in getattr(item.statement, 'statements', []):
                            comments.extend(extract_comments_from_node(stmt))

                    # 过滤空注释
                    comments = [c for c in comments if c.strip()]

                    if comments:
                        functions.append({
                            'file': verilog_file,
                            'type': 'Function' if isinstance(item, Function) else 'Task',
                            'name': func_name,
                            'comments': comments,
                            'start_line': item.lineno,
                            'end_line': getattr(item, 'end_lineno', item.lineno)
                        })

    return functions


def process_verilog_project(project_path):
    """处理整个Verilog项目"""
    results = []

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.v', '.sv')):
                file_path = os.path.join(root, file)
                print(f"正在处理文件: {file_path}")
                functions = extract_functions_with_comments(file_path)
                results.extend(functions)

    return results


def save_to_jsonl(data, output_file):
    """将结果保存为JSONL文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    # 配置路径
    project_path = "/home/huangjiaming/verilogempirical"
    output_file = "verilog_functions_with_comments.jsonl"

    # 处理项目并保存结果
    results = process_verilog_project(project_path)
    save_to_jsonl(results, output_file)

    print(f"完成! 共提取 {len(results)} 个带注释的函数/任务。结果已保存到 {output_file}")