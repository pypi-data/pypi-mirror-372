#!/usr/bin/env python3
import json
import os
import re
from .client import HttpClient


class ScriptExecutionError(Exception):
    """脚本执行错误异常"""
    def __init__(self, message, traceback_info=None, script_path=None):
        super().__init__(message)
        self.traceback_info = traceback_info
        self.script_path = script_path


class SocExecutor:
    """SOC工具执行器"""
    
    def __init__(self):
        self.client = HttpClient()
    
    def parse_html_content(self, html_content):
        """解析HTML格式的响应内容，提取运行日志和结果"""
        if not html_content:
            return None, None
        
        # 先将<br>标签替换为换行符
        content_with_newlines = html_content.replace('<br>', '\n')
        
        # 移除其他HTML标签
        clean_content = re.sub(r'<[^>]+>', '', content_with_newlines)
        
        # 按"运行结果："分割内容
        parts = clean_content.split('运行结果：')
        
        if len(parts) >= 2:
            # 提取运行日志部分（去掉"运行日志："前缀）
            log_part = parts[0].replace('运行日志：', '').strip()
            # 提取运行结果部分
            result_part = parts[1].strip()
            
            return log_part, result_part
        else:
            # 如果没有找到分隔符，返回整个内容作为日志
            return clean_content.strip(), None
    
    def clean_traceback(self, traceback_text, script_path=None):
        """清理和格式化Python错误信息"""
        if not traceback_text:
            return traceback_text
        
        lines = traceback_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 跳过包含服务器路径的行
            if '/data/soc/soar/jar/main.py' in line:
                continue
            # 跳过exec相关的行
            if 'exec_func(logger)' in line or 'exec(str_func_copy, a)' in line:
                continue
            # 将<string>替换为实际的脚本路径
            if 'File "<string>"' in line:
                display_path = script_path if script_path else "用户脚本"
                line = line.replace('File "<string>"', f'File "{display_path}"')
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

    def format_output(self, result, script_path=None, raise_on_error=False):
        """格式化输出结果"""
        if "error" in result:
            if raise_on_error:
                raise ScriptExecutionError(result['error'], script_path=script_path)
            else:
                print(f"\033[91m错误: {result['error']}\033[0m")
                if "content" in result:
                    print(f"详细信息: {result['content']}")
                return
        
        code = result.get('code', -1)
        message = result.get('message', '')
        data = result.get('data', '')
        
        if code == 0:
            # 解析HTML内容
            log_content, result_content = self.parse_html_content(data)
            
            if log_content:
                print("=" * 50)
                print("运行日志:")
                print("-" * 30)
                print(log_content)
                print()
            
            if result_content:
                print("运行结果:")
                print("-" * 30)
                print(result_content)
                print()
            
            # 绿色显示成功信息
            print(f"\033[92m✓ {message}\033[0m")
        else:
            # 处理失败情况
            log_content, result_content = self.parse_html_content(data)
            
            # 提取错误信息，优先从message字段中查找
            error_info = None
            
            # 1. 首先检查message字段是否包含__error__
            if message and '__error__' in message:
                try:
                    # 尝试解析message中的JSON
                    start_idx = message.find('{')
                    end_idx = message.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        error_json = message[start_idx:end_idx]
                        error_data = json.loads(error_json)
                        if '__error__' in error_data:
                            error_info = error_data['__error__']
                except:
                    # 如果JSON解析失败，尝试直接提取
                    if "Traceback" in message:
                        error_info = message
            
            # 2. 如果message中没有找到，检查data字段
            if not error_info and log_content and '__error__' in log_content:
                try:
                    start_idx = log_content.find('{')
                    end_idx = log_content.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        error_json = log_content[start_idx:end_idx]
                        error_data = json.loads(error_json)
                        if '__error__' in error_data:
                            error_info = error_data['__error__']
                except:
                    pass
            
            # 3. 如果都没有找到，使用result_content
            if not error_info and result_content:
                error_info = result_content
            
            if error_info:
                cleaned_error = self.clean_traceback(error_info, script_path)
                if raise_on_error:
                    raise ScriptExecutionError(cleaned_error, traceback_info=cleaned_error, script_path=script_path)
                else:
                    print(f"\033[91m{cleaned_error}\033[0m")
            else:
                error_msg = f"执行失败 (code: {code})"
                if raise_on_error:
                    raise ScriptExecutionError(error_msg, script_path=script_path)
                else:
                    print(f"\033[91m✗ {error_msg}\033[0m")
                    if message:
                        clean_message = self.parse_html_content(message)[0] if message else message
                        print(f"消息: {clean_message}")
                    if data:
                        print(f"详细信息: {data}")
    
    def read_python_file(self, file_path):
        """读取Python文件内容"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not file_path.endswith('.py'):
            raise ValueError("仅支持Python文件(.py)")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def execute_python_file(self, file_path, params=None, raise_on_error=False):
        """执行Python文件"""
        if params is None:
            params = {}
        
        try:
            # 读取Python代码
            code_content = self.read_python_file(file_path)
            
            # 构造请求数据
            data = {
                "code": code_content,
                "type": "python",
                "params": params
            }
            
            # 发送请求
            response = self.client.post('/soar-service/tool/run', data)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.format_output(result, file_path, raise_on_error)
                    return result
                except json.JSONDecodeError:
                    error_result = {"error": "响应格式错误", "content": response.text}
                    self.format_output(error_result, file_path, raise_on_error)
                    return error_result
            else:
                error_result = {"error": f"请求失败，状态码: {response.status_code}", "content": response.text}
                self.format_output(error_result, file_path, raise_on_error)
                return error_result
                
        except FileNotFoundError as e:
            error_result = {"error": f"文件错误: {str(e)}"}
            self.format_output(error_result, file_path, raise_on_error)
            return error_result
        except Exception as e:
            error_result = {"error": f"请求异常: {str(e)}"}
            self.format_output(error_result, file_path, raise_on_error)
            return error_result