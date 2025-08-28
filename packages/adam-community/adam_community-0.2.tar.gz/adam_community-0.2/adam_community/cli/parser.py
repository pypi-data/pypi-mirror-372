import ast
from pathlib import Path
from typing import List, Dict, Any
from docstring_parser import parse as dsp

def parse_python_file(file_path: Path) -> List[Dict[str, Any]]:
    """解析单个 Python 文件，提取类信息
    
    Args:
        file_path: Python 文件路径
        
    Returns:
        List[Dict[str, Any]]: 类信息列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 获取类的文档字符串
                docstring = ast.get_docstring(node) or ""
                
                # 获取类的静态变量
                sif_var = None
                network_var = None
                gpu = 0
                cpu = 1
                mem_per_cpu = 4000
                partition = "gpu"
                conda_env = "base"
                
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if target.id == 'SIF':
                                    if isinstance(item.value, ast.Constant):
                                        sif_var = item.value.value
                                elif target.id == 'NETWORK':
                                    if isinstance(item.value, ast.Constant):
                                        network_var = item.value.value
                                elif target.id == 'GPU':
                                    if isinstance(item.value, ast.Constant):
                                        gpu = item.value.value
                                elif target.id == 'CPU':
                                    if isinstance(item.value, ast.Constant):
                                        cpu = item.value.value
                                elif target.id == 'MEM_PER_CPU':
                                    if isinstance(item.value, ast.Constant):
                                        mem_per_cpu = item.value.value
                                elif target.id == 'PARTITION':
                                    if isinstance(item.value, ast.Constant):
                                        partition = item.value.value
                                elif target.id == 'CONDA_ENV':
                                    if isinstance(item.value, ast.Constant):
                                        conda_env = item.value.value
                                elif target.id == 'DISPLAY_NAME':
                                    if isinstance(item.value, ast.Constant):    
                                        display_name = item.value.value
                
                # 获取类的参数信息
                parameters = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
                
                # 使用 docstring_parser 解析类的文档字符串
                docs = dsp(docstring)
                if docs:
                    for p in docs.params:
                        parameters["properties"][p.arg_name] = {
                            "description": p.description or "",
                            "type": p.type_name or "string"
                        }
                        if not p.is_optional:
                            parameters["required"].append(p.arg_name)
                
                class_info = {
                    "function": {
                        "name": f"{file_path.stem}.{node.name}",
                        "description": docs.short_description if docs else "",
                        "parameters": parameters,
                        "file": str(file_path),
                        "sif": sif_var,
                        "network": network_var,
                        "gpu": gpu,
                        "cpu": cpu,
                        "mem_per_cpu": mem_per_cpu,
                        "partition": partition,
                        "conda_env": conda_env,
                        "display_name": display_name
                    }
                }
                classes.append(class_info)
        
        return classes
    except Exception as e:
        print(f"解析文件 {file_path} 时出错: {str(e)}")
        return []

def parse_directory(directory: Path) -> List[Dict[str, Any]]:
    """解析目录下的所有 Python 文件
    
    Args:
        directory: 目录路径
        
    Returns:
        List[Dict[str, Any]]: 所有类信息列表
    """
    all_classes = []
    # 排除 config 目录
    for py_file in directory.rglob('*.py'):
        if not py_file.name.startswith('_') and 'config' not in py_file.parts:
            classes = parse_python_file(py_file)
            all_classes.extend(classes)
    return all_classes 