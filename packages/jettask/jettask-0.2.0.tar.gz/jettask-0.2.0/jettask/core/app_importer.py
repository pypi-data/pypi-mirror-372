"""
App importer module inspired by Uvicorn's import logic.
支持多种方式导入 Jettask 应用实例。
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Optional, Any
import inspect


class AppImporter:
    """应用导入器，支持多种导入方式"""
    
    # 默认查找的应用实例名称
    DEFAULT_APP_NAMES = ['app', 'application', 'jettask_app']
    
    # 默认查找的文件
    DEFAULT_FILES = ['app.py', 'main.py', 'server.py', 'worker.py']
    
    @classmethod
    def import_from_string(cls, import_str: str) -> Any:
        """
        从字符串导入应用，支持多种格式：
        - "module:app" - 从 module 导入 app 实例
        - "module" - 从 module 自动查找应用实例
        - "path/to/file.py:app" - 从文件路径导入
        - "path/to/file.py" - 从文件自动查找
        """
        # 分离模块路径和应用名称
        if ':' in import_str:
            module_str, app_name = import_str.rsplit(':', 1)
        else:
            module_str = import_str
            app_name = None
        
        # 判断是文件路径还是模块名
        if '/' in module_str or module_str.endswith('.py'):
            module = cls._import_from_file(module_str)
        else:
            module = cls._import_from_module(module_str)
        
        # 获取应用实例
        if app_name:
            # 支持嵌套属性访问，如 "module:app.factory()"
            if '.' in app_name or '(' in app_name:
                app = cls._evaluate_app_expression(module, app_name)
            else:
                app = getattr(module, app_name)
        else:
            # 自动查找应用实例
            app = cls._find_app_in_module(module)
            if not app:
                raise ImportError(
                    f"Cannot find Jettask app in {module_str}. "
                    f"Tried names: {', '.join(cls.DEFAULT_APP_NAMES)}"
                )
        
        return app
    
    @classmethod
    def _import_from_file(cls, file_path: str):
        """从文件路径导入模块"""
        path = Path(file_path)
        
        # 处理相对路径
        if not path.is_absolute():
            path = Path.cwd() / path
        
        # 去掉 .py 后缀（如果有）
        if path.suffix == '.py':
            path = path.with_suffix('')
        
        # 检查文件是否存在
        py_file = path.with_suffix('.py')
        if not py_file.exists():
            raise ImportError(f"File not found: {py_file}")
        
        # 添加到 sys.path
        sys.path.insert(0, str(path.parent))
        
        try:
            # 导入模块
            module_name = path.name
            spec = importlib.util.spec_from_file_location(
                module_name, 
                str(py_file)
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                try:
                    spec.loader.exec_module(module)
                    return module
                except Exception as e:
                    # 执行模块时出错，提供详细信息
                    import traceback
                    tb_lines = traceback.format_exc().splitlines()
                    
                    # 找出用户代码中的错误位置
                    user_error_lines = [line for line in tb_lines 
                                       if str(py_file) in line or module_name in line]
                    
                    raise ImportError(
                        f"Failed to load module from {py_file}.\n"
                        f"Error in user code: {str(e)}\n"
                        f"Check the file for syntax errors or missing dependencies."
                    ) from e
            else:
                raise ImportError(f"Cannot create module spec for {py_file}")
        finally:
            # 清理 sys.path
            if str(path.parent) in sys.path:
                sys.path.remove(str(path.parent))
    
    @classmethod
    def _import_from_module(cls, module_str: str):
        """从模块名导入"""
        try:
            return importlib.import_module(module_str)
        except ImportError as e:
            # 保存原始错误信息
            original_error = str(e)
            
            # 如果导入失败，尝试添加当前目录到 sys.path
            if '.' not in sys.path:
                sys.path.insert(0, '.')
                try:
                    return importlib.import_module(module_str)
                except ImportError as retry_error:
                    # 提供更详细的错误信息
                    import traceback
                    tb_str = traceback.format_exc()
                    
                    # 判断是模块不存在还是模块内部有错误
                    if f"No module named '{module_str}'" in str(retry_error):
                        raise ImportError(
                            f"Module '{module_str}' not found. "
                            f"Make sure the module exists and is in the Python path."
                        ) from retry_error
                    else:
                        # 模块存在但内部有错误，保留完整的错误链
                        raise ImportError(
                            f"Failed to import module '{module_str}'. "
                            f"The module was found but contains errors:\n{original_error}"
                        ) from retry_error
            raise
    
    @classmethod
    def _find_app_in_module(cls, module) -> Optional[Any]:
        """在模块中查找 Jettask 应用实例"""
        from ..core.app import Jettask
        
        # 按优先级查找
        for name in cls.DEFAULT_APP_NAMES:
            if hasattr(module, name):
                obj = getattr(module, name)
                if isinstance(obj, Jettask):
                    return obj
        
        # 如果没找到，遍历所有属性查找第一个 Jettask 实例
        for name in dir(module):
            if not name.startswith('_'):
                obj = getattr(module, name, None)
                if isinstance(obj, Jettask):
                    return obj
        
        return None
    
    @classmethod
    def _evaluate_app_expression(cls, module, expression: str):
        """
        评估应用表达式，支持：
        - app.factory() - 调用工厂函数
        - app.create_app() - 调用方法
        - app.instance - 访问属性
        """
        # 安全评估表达式
        # 创建受限的命名空间
        namespace = {'__builtins__': {}}
        namespace.update(vars(module))
        
        try:
            # 使用 eval 但限制在模块的命名空间内
            return eval(expression, namespace)
        except Exception as e:
            raise ImportError(f"Cannot evaluate expression '{expression}': {e}")
    
    @classmethod
    def auto_discover(cls) -> Optional[Any]:
        """
        自动发现应用，按以下顺序查找：
        1. 环境变量 JETTASK_APP
        2. 当前目录的默认文件（app.py, main.py 等）
        3. 当前目录的任何 .py 文件中的 app 实例
        """
        from ..core.app import Jettask
        
        # 1. 检查环境变量
        env_app = os.getenv('JETTASK_APP')
        if env_app:
            try:
                return cls.import_from_string(env_app)
            except Exception:
                pass
        
        # 2. 检查默认文件
        for filename in cls.DEFAULT_FILES:
            file_path = Path.cwd() / filename
            if file_path.exists():
                try:
                    module = cls._import_from_file(str(file_path))
                    app = cls._find_app_in_module(module)
                    if app:
                        return app
                except Exception:
                    continue
        
        # 3. 扫描当前目录的所有 Python 文件
        for py_file in Path.cwd().glob('*.py'):
            if py_file.name.startswith('_'):
                continue
            try:
                module = cls._import_from_file(str(py_file))
                app = cls._find_app_in_module(module)
                if app:
                    return app
            except Exception:
                continue
        
        return None
    
    @classmethod
    def get_app_info(cls, app) -> dict:
        """获取应用信息"""
        from ..core.app import Jettask
        
        if not isinstance(app, Jettask):
            return {'error': 'Not a Jettask instance'}
        
        info = {
            'type': 'Jettask',
            'redis_url': getattr(app, 'redis_url', 'Not configured'),
            'redis_prefix': getattr(app, 'redis_prefix', 'jettask'),
            'tasks': len(getattr(app, '_tasks', {})),
            'queues': [],
        }
        
        # 安全地获取队列信息
        if hasattr(app, 'ep') and hasattr(app.ep, 'queues'):
            queues = app.ep.queues
            if queues is not None:
                info['queues'] = list(queues)
        
        # 获取任务列表
        if hasattr(app, '_tasks'):
            info['task_names'] = list(app._tasks.keys())
        
        return info


def import_app(import_str: Optional[str] = None) -> Any:
    """
    导入 Jettask 应用的便捷函数。
    
    Args:
        import_str: 导入字符串，如 "module:app" 或 "path/to/file.py:app"
                   如果为 None，会尝试自动发现
    
    Returns:
        Jettask 应用实例
    
    Examples:
        >>> app = import_app("myapp:app")
        >>> app = import_app("src/main.py:create_app()")
        >>> app = import_app()  # 自动发现
    """
    if import_str:
        return AppImporter.import_from_string(import_str)
    else:
        app = AppImporter.auto_discover()
        if not app:
            raise ImportError(
                "Cannot auto-discover Jettask app. "
                "Please specify app location (e.g., 'module:app') "
                "or set JETTASK_APP environment variable."
            )
        return app