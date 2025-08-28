import os
import time
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP, Context
from agentsphere import AsyncSandbox, Sandbox
import logging
import pathlib
from platformdirs import user_desktop_dir, user_documents_dir, user_downloads_dir
import asyncio


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
    # handlers=[
    #     logging.FileHandler('mcp_server.log'),
    #     # 对于 STDIO 传输，可以注释掉控制台输出避免干扰
    #     # logging.StreamHandler()
    # ]
)

logger = logging.getLogger(__name__)

# 创建 FastMCP 实例，声明依赖项
mcp = FastMCP(
    name="Agent Sphere STDIO MCP Server",
    dependencies=["agentsphere"]  # 声明依赖项
)


# 单沙箱管理器
class SingleSandboxManager:
    def __init__(self):
        # 存储沙箱实例和相关信息
        self._sandbox: Optional[AsyncSandbox] = None
        self._sandbox_info: Optional[Dict[str, Any]] = None
        self._api_key: Optional[str] = None
        logger.info("单沙箱管理器初始化完成")

    def _get_api_key(self) -> str:
        """从环境变量获取 API key"""
        if self._api_key:
            return self._api_key
            
        # 尝试从环境变量获取 API key
        api_key = os.getenv("AGENTSPHERE_API_KEY")
        
        if not api_key:
            raise Exception("AGENTSPHERE_API_KEY not found, please set environment variable")
        
        self._api_key = api_key
        logger.info(f"成功获取 API key: ***{api_key[-4:]}")
        return api_key

    async def get_sandbox(self) -> AsyncSandbox:
        """获取或创建沙箱实例"""
        current_time = time.time()
        logger.debug("获取沙箱实例")

        # 检查是否已有沙箱实例
        if self._sandbox is not None:
            logger.debug("找到现有沙箱实例")
            
            # 检查沙箱是否仍然运行中
            try:
                if await self._sandbox.is_running(request_timeout=5.0):
                    # 更新最后使用时间
                    if self._sandbox_info:
                        self._sandbox_info["last_used"] = current_time
                    logger.info(f"复用现有沙箱: {self._sandbox.sandbox_id}")
                    return self._sandbox
                else:
                    # 沙箱已经停止，清除缓存
                    logger.info("现有沙箱已停止，将创建新沙箱")
                    self._sandbox = None
                    self._sandbox_info = None
            except Exception as e:
                # 沙箱连接异常，清除缓存
                logger.error(f"沙箱连接异常: {str(e)}")
                self._sandbox = None
                self._sandbox_info = None

        # 获取或创建沙箱实例
        api_key = self._get_api_key()
        target_template = "agentsphere-code-interpreter-v1"
        
        # 尝试获取并连接到现有沙箱
        existing_sandbox = await self._try_connect_existing_sandbox(api_key, target_template, current_time)
        if existing_sandbox:
            return existing_sandbox
        
        # 没有找到合适的现有沙箱，创建新的
        return await self._create_new_sandbox(api_key, target_template, current_time)

    async def _try_connect_existing_sandbox(self, api_key: str, target_template: str, current_time: float) -> Optional[AsyncSandbox]:
        """
        尝试连接到现有的相同template沙箱
        
        :param api_key: API密钥
        :param target_template: 目标模板ID
        :param current_time: 当前时间戳
        :return: 成功连接的沙箱实例，如果没有找到或连接失败则返回None
        """
        try:
            logger.info("检查云端现有沙箱...")
            existing_sandboxes = await AsyncSandbox.list(
                api_key=api_key,
                domain="agentsphere.run"
            )
            
            # 筛选出相同template且运行中的沙箱
            target_sandboxes = [
                sbx for sbx in existing_sandboxes 
                if sbx.name == target_template and sbx.state.lower() == "running"
            ]
            
            if not target_sandboxes:
                logger.info("未找到运行中的相同template沙箱")
                return None
            
            # 按启动时间降序排序，选择最新的
            latest_sandbox = max(target_sandboxes, key=lambda x: x.started_at)
            logger.info(f"找到现有沙箱: {latest_sandbox.sandbox_id} (启动于 {latest_sandbox.started_at})")
            
            # 尝试连接到现有沙箱
            connected_sandbox = await AsyncSandbox.connect(
                sandbox_id=latest_sandbox.sandbox_id,
                api_key=api_key,
                domain="agentsphere.run"
            )
            
            # 设置沙箱信息
            self._sandbox = connected_sandbox
            self._sandbox_info = {
                "sandbox_id": connected_sandbox.sandbox_id,
                "created_at": latest_sandbox.started_at.timestamp(),
                "last_used": current_time
            }
            
            logger.info(f"成功连接到现有沙箱: {connected_sandbox.sandbox_id}")
            return connected_sandbox
            
        except Exception as e:
            logger.warning(f"尝试连接现有沙箱失败: {str(e)}")
            return None

    async def _create_new_sandbox(self, api_key: str, target_template: str, current_time: float) -> AsyncSandbox:
        """
        创建新的沙箱实例
        
        :param api_key: API密钥
        :param target_template: 模板ID
        :param current_time: 当前时间戳
        :return: 新创建的沙箱实例
        """
        try:
            logger.info("创建新沙箱...")
            new_sandbox = await AsyncSandbox.create(
                api_key=api_key,
                template=target_template,
                domain="agentsphere.run",
                timeout=43200  # 12小时超时
            )
            
            self._sandbox = new_sandbox
            self._sandbox_info = {
                "sandbox_id": new_sandbox.sandbox_id,
                "created_at": current_time,
                "last_used": current_time
            }
            
            logger.info(f"成功创建新沙箱: {new_sandbox.sandbox_id}")
            return new_sandbox
            
        except Exception as e:
            logger.error(f"创建沙箱失败: {str(e)}")
            raise Exception(f"Failed to create sandbox: {str(e)}")

    def get_sandbox_info(self) -> Optional[Dict[str, Any]]:
        """获取沙箱信息"""
        if self._sandbox_info:
            logger.debug(f"获取沙箱信息: {self._sandbox_info}")
            return self._sandbox_info.copy()
        logger.debug("没有沙箱信息")
        return None

    async def cleanup(self):
        """清理沙箱资源"""
        if self._sandbox:
            try:
                logger.info(f"正在清理沙箱: {self._sandbox.sandbox_id}")
                await self._sandbox.kill()
                logger.info("沙箱清理完成")
            except Exception as e:
                logger.error(f"沙箱清理失败: {str(e)}")
            finally:
                self._sandbox = None
                self._sandbox_info = None


# 全局沙箱管理器实例
sandbox_manager = SingleSandboxManager()


def _read_local_file(file_path: str) -> bytes:
    """
    读取本地文件内容
    
    Args:
        file_path: 绝对文件路径
        
    Returns:
        文件内容（字节格式）
        
    Raises:
        Exception: 文件不存在或无法读取
    """
    try:
        # 使用pathlib确保跨平台兼容性
        path = pathlib.Path(file_path).resolve()
        
        # 检查文件是否存在
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 检查是否为文件（不是目录）
        if not path.is_file():
            raise IsADirectoryError(f"Path is not a file: {file_path}")
        
        # 读取文件内容
        with open(path, 'rb') as f:
            content = f.read()
        
        logger.debug(f"成功读取文件: {file_path}, 大小: {len(content)} 字节")
        return content
        
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {str(e)}")
        raise Exception(f"Failed to read file: {str(e)}")


def _normalize_path(path: Optional[str]) -> str:
    """规范化路径格式
    
    Args:
        path: 原始路径
        
    Returns:
        规范化后的路径
    """
    # 处理空值情况
    if path is None or path == "":
        return "/user_uploaded_files/"
    
    # 特殊情况：根目录保持为 "/"
    if path == "/":
        return "/"
    
    # 确保路径以/开头和结尾
    if not path.startswith('/'):
        path = '/' + path
    if not path.endswith('/'):
        path = path + '/'
    
    return path


def _scan_directory(dir_path: str, target_base_path: str = "/user_uploaded_files/") -> List[Dict[str, str]]:
    """
    递归扫描目录，获取所有文件信息
    
    Args:
        dir_path: 绝对目录路径
        target_base_path: 沙箱中的目标基础路径，默认为 /user_uploaded_files/ 
        
    Returns:
        文件信息列表，包含local_path和sandbox_path
        
    Raises:
        Exception: 目录不存在或无法访问
    """
    try:
        # 使用pathlib确保跨平台兼容性
        root_path = pathlib.Path(dir_path).resolve()
        
        # 检查目录是否存在
        if not root_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        # 检查是否为目录
        if not root_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {dir_path}")
        
        files_info = []
        
        # 路径预处理
        target_base_path = _normalize_path(target_base_path)
        
        # 递归遍历目录中的所有文件
        for file_path in root_path.rglob('*'):
            if file_path.is_file():
                # 计算相对路径（保持目录结构）
                relative_path = file_path.relative_to(root_path)
                
                # 构建沙箱中的路径（使用Unix风格的路径分隔符）
                if target_base_path == '/':
                    sandbox_path = f"/{root_path.name}/{relative_path.as_posix()}"
                else:
                    # target_base_path 已经以/结尾，直接拼接目录名和文件路径
                    sandbox_path = f"{target_base_path}{root_path.name}/{relative_path.as_posix()}"
                
                files_info.append({
                    "local_path": str(file_path),
                    "sandbox_path": sandbox_path
                })
        
        logger.info(f"扫描目录完成: {dir_path}, 找到 {len(files_info)} 个文件，目标路径: {target_base_path}")
        return files_info
        
    except Exception as e:
        logger.error(f"扫描目录失败 {dir_path}: {str(e)}")
        raise Exception(f"Failed to scan directory: {str(e)}")


def _prepare_file_upload_list(local_path: str, target_path: str) -> List[Dict[str, str]]:
    """准备文件上传列表
    
    Args:
        local_path: 本地文件或目录路径
        target_path: 沙箱目标路径
        
    Returns:
        包含local_path和sandbox_path的文件信息列表
        
    Raises:
        FileNotFoundError: 路径不存在
        Exception: 不支持的路径类型
    """
    path = pathlib.Path(local_path).resolve()
    
    # 检查路径是否存在
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {local_path}")
    
    files_to_upload = []
    
    if path.is_file():
        # 单个文件上传
        file_name = path.name
        if target_path == '/':
            sandbox_path = f"/{file_name}"
        else:
            sandbox_path = f"{target_path}{file_name}"
        
        files_to_upload.append({
            "local_path": str(path),
            "sandbox_path": sandbox_path
        })
        
        logger.info(f"准备上传单个文件: {file_name} 到 {sandbox_path}")
        
    elif path.is_dir():
        # 目录上传
        files_to_upload = _scan_directory(str(path), target_path)
        logger.info(f"准备上传目录: {path.name} 到 {target_path}, 包含 {len(files_to_upload)} 个文件")
        
    else:
        raise Exception(f"Unsupported path type: {local_path}")
    
    return files_to_upload


async def _create_sandbox_directories(sandbox, target_path: str, files_to_upload: List[Dict[str, str]]):
    """在沙箱中创建必要的目录结构
    
    Args:
        sandbox: 沙箱实例
        target_path: 目标基础路径
        files_to_upload: 文件上传列表
    """
    # 创建目标基础目录
    target_dir_for_creation = target_path.rstrip('/') if target_path != '/' else '/'
    logger.info(f"创建目标目录: {target_dir_for_creation}")
    
    if target_dir_for_creation != '/':
        await sandbox.files.make_dir(target_dir_for_creation)
    
    # 创建文件所需的子目录
    created_dirs = {target_dir_for_creation}
    
    for file_info in files_to_upload:
        sandbox_dir = str(pathlib.Path(file_info["sandbox_path"]).parent)
        if sandbox_dir not in created_dirs and sandbox_dir != "/":
            try:
                await sandbox.files.make_dir(sandbox_dir)
                created_dirs.add(sandbox_dir)
            except Exception as e:
                logger.warning(f"创建目录失败 {sandbox_dir}: {str(e)}")


def _prepare_upload_entries(files_to_upload: List[Dict[str, str]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """准备上传条目和文件信息
    
    Args:
        files_to_upload: 文件上传列表
        
    Returns:
        (write_entries, uploaded_files) 元组
    """
    write_entries = []
    uploaded_files = []
    
    for file_info in files_to_upload:
        try:
            # 读取本地文件内容
            file_content = _read_local_file(file_info["local_path"])
            
            # 添加到上传列表
            write_entries.append({
                "path": file_info["sandbox_path"],
                "data": file_content
            })
            
            uploaded_files.append({
                "local_path": file_info["local_path"],
                "sandbox_path": file_info["sandbox_path"],
                "size": len(file_content)
            })
            
        except Exception as e:
            logger.warning(f"跳过文件 {file_info['local_path']}: {str(e)}")
            continue
    
    return write_entries, uploaded_files


@mcp.tool
async def exec_command(
    cmd: str,
    ctx: Context  # FastMCP 会自动注入，Context 参数对客户端不可见
) -> Dict[str, Any]:
    """Execute Linux system commands in the sandbox

    Note:
        - If the executed command occupies the command line window (like starting a web service), the function will wait indefinitely
        - For services that need to run continuously, it's recommended to use nohup background startup:
          * Next.js example: "nohup npm run dev > nextjs.log 2>&1 &"
        - Command execution timeout is 60 seconds

    Args:
        cmd: Command to execute

    Returns:
        Command execution result containing stdout, stderr and success fields
    """
    try:
        # loguru 日志 - 服务器端可见
        logger.info(f"[MCP工具调用 exec_command] 请求执行命令: {cmd}")

        # 获取沙箱实例
        sandbox = await sandbox_manager.get_sandbox()

        # 执行命令
        logger.debug(f"开始执行命令: {cmd}")
        result = await sandbox.commands.run(cmd=cmd, timeout=60, request_timeout=60)

        # 记录执行结果
        logger.info(
            f"命令执行完成 - 退出码: {result.exit_code}, "
            f"stdout长度: {len(result.stdout)}, stderr长度: {len(result.stderr)}"
        )
        if result.stdout:
            logger.debug(f"命令输出 (stdout): {result.stdout}")
        if result.stderr:
            logger.warning(f"命令错误输出 (stderr): {result.stderr}")

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": "true" if result.exit_code == 0 else "false"
        }

    except Exception as e:
        # loguru 错误日志 - 服务器端可见，包含完整堆栈信息
        logger.error(f"[MCP工具错误] 命令执行失败: {str(e)}", exc_info=True)

        return {
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


@mcp.tool
async def get_preview_link(
    port: int,
    ctx: Context  # FastMCP 会自动注入，Context 参数对客户端不可见
) -> Dict[str, Any]:
    """Get the URL for web services running in the sandbox.
    
    Note: You need to first create and start web services (like Next.js, Streamlit, etc.) using exec_command.
    Make sure the web service port is not occupied.
    Due to sandbox network security policies, all web services cannot be accessed directly via IP + port number. 
    You need to call this method to get the externally accessible URL.

    Args:
        port: Port number

    Returns:
        URL link
    """
    try:
        # 服务器端日志
        logger.info(f"[MCP工具调用 get_preview_link] 请求获取端口 {port} 的预览链接")

        # 获取沙箱实例
        sandbox = await sandbox_manager.get_sandbox()

        # 获取主机地址
        host = sandbox.get_host(port)
        
        # 构建完整的 URL
        preview_url = f"https://{host}"

        logger.info(f"成功生成预览链接: {preview_url}")

        return {
            "url": preview_url
        }

    except Exception as e:
        logger.error(f"[MCP工具错误] 获取预览链接失败: {str(e)}", exc_info=True)
        return {
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


@mcp.tool
async def upload_files_to_sandbox(
        local_path: str,
        ctx: Context,  # FastMCP 会自动注入，Context 参数对客户端不可见
        target_path: Optional[str] = "/user_uploaded_files/"
) -> Dict[str, Any]:
    """Upload local files or folders to a specified directory in the sandbox.

    Can upload single files or entire folders, maintaining the original directory structure during upload.

    Tip: If you know the file name but are unsure of the complete path, you can first use the find_file_path tool to determine the absolute path of the file.

    Args:
        local_path: Absolute path of local file or folder
        target_path: Target directory path in sandbox, defaults to /user_uploaded_files/ (ending with / indicates directory)

    Returns:
        Upload result containing list of successfully uploaded files or error information
    """
    try:
        # 路径预处理
        target_path = _normalize_path(target_path)
        logger.info(f"[MCP工具调用 upload_files_to_sandbox] 请求上传: {local_path} 到 {target_path}")

        # 获取沙箱实例
        sandbox = await sandbox_manager.get_sandbox()

        # 准备文件上传列表
        files_to_upload = _prepare_file_upload_list(local_path, target_path)
        
        if not files_to_upload:
            return {
                "success": "true",
                "message": "No files found for upload",
                "uploaded_files": []
            }

        # 创建沙箱目录结构
        await _create_sandbox_directories(sandbox, target_path, files_to_upload)

        # 准备上传条目
        write_entries, uploaded_files = _prepare_upload_entries(files_to_upload)

        if not write_entries:
            return {
                "success": "false",
                "message": "No files successfully prepared for upload",
                "uploaded_files": []
            }

        # 批量上传文件到沙箱
        logger.info(f"开始批量上传 {len(write_entries)} 个文件到沙箱...")
        upload_results = await sandbox.files.write(write_entries)

        # 记录上传结果
        total_size = sum(f["size"] for f in uploaded_files)
        logger.info(f"文件上传完成 - 成功上传 {len(uploaded_files)} 个文件到 {target_path}，总大小: {total_size} 字节")

        return {
            "success": "true",
            "message": f"Successfully uploaded {len(uploaded_files)} files to {target_path}",
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files),
            "total_size": total_size,
            "target_path": target_path
        }

    except Exception as e:
        logger.error(f"[MCP工具错误] 文件上传失败: {str(e)}", exc_info=True)
        return {
            "success": "false",
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            }
        }


def _resolve_file_path(
    filename: str,
    search_path: Optional[str] = None,
    max_results: int = 30,
    max_depth: int = 10,
    include_directories: bool = False
) -> List[Dict[str, Any]]:
    """
    搜索文件路径
    
    Args:
        filename: 要搜索的文件名（支持通配符，如 *.py, test*.txt）
        search_path: 搜索起始路径，默认为用户主目录
        max_results: 最大返回结果数，避免返回过多文件
        max_depth: 最大搜索深度，避免搜索太深影响性能
        include_directories: 是否包含目录，默认为False只返回文件
        
    Returns:
        找到的文件/目录信息列表，每个元素包含path、size、modified、type等信息
    """
    try:
        # 确定搜索起始路径
        if search_path is None:
            # 默认从用户主目录开始搜索
            start_path = pathlib.Path.home()
        else:
            start_path = pathlib.Path(search_path).resolve()
        
        # 检查起始路径是否存在
        if not start_path.exists():
            raise FileNotFoundError(f"Search path not found: {search_path}")
        
        if not start_path.is_dir():
            raise NotADirectoryError(f"Search path is not a directory: {search_path}")
        
        found_files = []
        searched_count = 0
        
        logger.info(f"开始搜索{'文件和目录' if include_directories else '文件'}: {filename} 在路径: {start_path}")
        
        # 使用 rglob 进行递归搜索（支持通配符）
        try:
            for file_path in start_path.rglob(filename):
                # 控制搜索深度
                try:
                    relative_path = file_path.relative_to(start_path)
                    depth = len(relative_path.parents)
                    if depth > max_depth:
                        continue
                except ValueError:
                    # 如果无法计算相对路径，跳过
                    continue
                
                # 根据参数决定是否包含目录
                is_file = file_path.is_file()
                is_dir = file_path.is_dir()
                
                if not is_file and not is_dir:
                    continue  # 跳过既不是文件也不是目录的项目
                
                if not include_directories and not is_file:
                    continue  # 如果不包含目录且不是文件，跳过
                
                # 获取文件/目录信息
                try:
                    stat = file_path.stat()
                    file_info = {
                        "path": str(file_path.resolve()),
                        "name": file_path.name,
                        "type": "file" if is_file else "directory",  # 明确标识类型
                        "size": stat.st_size if is_file else "Unknown",   # 目录大小设为 Unknown
                        "modified": time.ctime(stat.st_mtime)
                    }
                    found_files.append(file_info)
                    
                    # 限制返回结果数量
                    if len(found_files) >= max_results:
                        logger.info(f"已找到 {max_results} 个结果，停止搜索")
                        break
                        
                except (PermissionError, OSError) as e:
                    # 跳过无权限访问的项目
                    logger.debug(f"跳过无法访问/无权限访问的{'文件' if is_file else '目录'}: {file_path} - {str(e)}")
                    continue
                
                searched_count += 1
                
                # 每搜索100个项目记录一次进度
                if searched_count % 100 == 0:
                    logger.debug(f"已搜索 {searched_count} 个项目，找到 {len(found_files)} 个匹配结果")
                    
        except Exception as e:
            logger.error(f"搜索过程中发生错误: {str(e)}")
            raise Exception(f"Error occurred during search: {str(e)}")
        
        # 按类型和名称排序（文件在前，目录在后）
        found_files.sort(key=lambda x: (x["type"], x["name"]))
        
        # 统计结果
        files_count = sum(1 for item in found_files if item["type"] == "file")
        dirs_count = sum(1 for item in found_files if item["type"] == "directory")
        
        logger.info(f"搜索完成 - 找到 {files_count} 个文件，{dirs_count} 个目录")
        return found_files
        
    except Exception as e:
        logger.error(f"文件搜索失败: {str(e)}")
        raise Exception(f"File search failed: {str(e)}")


async def _resolve_file_path_async(
    filename: str,
    search_path: Optional[str] = None,
    max_results: int = 30,
    max_depth: int = 10,
    include_directories: bool = False
) -> List[Dict[str, Any]]:
    """异步版本的文件搜索"""
    
    # 在线程池中执行同步的文件搜索
    return await asyncio.to_thread(
        _resolve_file_path,
        filename, search_path, max_results, max_depth, include_directories
    )


@mcp.tool
async def find_file_path(
    filename: str,
    ctx: Context,  # FastMCP 会自动注入，Context 参数对客户端不可见
    search_path: Optional[str] = None
) -> Dict[str, Any]:
    """Search for absolute paths of files or directories by name
    
    This tool can search for and return complete absolute paths based on names. The returned paths can be directly used for the upload_files_to_sandbox tool.
    
    Use cases:
    - When you know the file name but are unsure of the complete path
    - When you need to upload files to sandbox but don't remember the file location
    - When batch searching for certain types of files
    
    Args:
        filename: File name to search for (supports wildcards)
                 Examples: "test.py", "*.txt", "project*", "*.json"
        search_path: Search starting path or shortcut options (optional)
                    Specific paths, such as:
                    - macOS: "/Users/username/Desktop/Projects"
                    - Windows: "C:\\Users\\username\\Documents\\Work"
                    - Linux: "/home/username/workspace"

                    Shortcut options:
                    - "desktop": Search desktop directory (default option)
                    - "documents": Search documents directory
                    - "downloads": Search downloads directory
                    - "home": Search user home directory (high success rate but very slow search, recommend trying desktop/documents etc. smaller scope options first, use this option if not found)

                    Tip: If unsure about file location or user's operating system, recommend using shortcut options or leave this parameter empty to use default value. The system will default to searching the user's desktop
    
    Returns:
        Search results containing list of found files/directories, each result includes complete path, type, size, modification time, etc.
        
    Examples:        
        # Search for specific file name
        find_file_path("config.json")

        # Search for files of specified format
        find_file_path("*.py")

        # Search for all files starting with "project" (like project.json, project_config.py, project1.txt etc.)
        find_file_path("project*")
        
        # Search in specific directory
        find_file_path("*.txt", "/Users/username/Documents")
    """
    try:
        include_directories = True
        logger.info(f"[MCP工具调用 find_file_path] 请求搜索{'文件和目录' if include_directories else '文件'}: {filename}")
        
        # 参数验证
        if not filename or filename.strip() == "":
            return {
                "success": "false",
                "message": "Filename cannot be empty",
                "found_items": []
            }
        
        # 确定实际使用的搜索路径
        if search_path is None:
            actual_search_path = user_desktop_dir()
        elif search_path.lower() == "desktop":
            actual_search_path = user_desktop_dir()
        elif search_path.lower() == "downloads":
            actual_search_path = user_downloads_dir()
        elif search_path.lower() == "documents":
            actual_search_path = user_documents_dir()
        elif search_path.lower() == "home":
            actual_search_path = str(pathlib.Path.home())
        else:
            actual_search_path = search_path

        # 异步执行搜索（避免阻塞事件循环）
        found_items = await _resolve_file_path_async(
            filename=filename.strip(),
            search_path=actual_search_path,
            include_directories=include_directories
        )
        
        if not found_items:
            item_type = "files and directories" if include_directories else "files"
            logger.info(f"未找到匹配的{item_type}: {filename}")
            return {
                "success": "true",
                "message": f"No matching {item_type} found: {filename}",
                "found_items": [],
                "start_path": actual_search_path,
                "total_found": 0,
                "files_count": 0,
                "directories_count": 0
            }
        
        # 统计结果
        files_count = sum(1 for item in found_items if item["type"] == "file")
        dirs_count = sum(1 for item in found_items if item["type"] == "directory")
        
        # 为用户提供使用提示
        usage_tip = (
            "Tip: You can copy the above paths directly for use with the upload_files_to_sandbox tool. "
            "Both files and directories support upload, directories will maintain their original structure."
            if found_items else ""
        )
        
        return {
            "success": "true",
            "message": f"Found {len(found_items)} results ({files_count} files, {dirs_count} directories)",
            "found_items": found_items,
            "start_path": actual_search_path,
            "total_found": len(found_items),
            "files_count": files_count,
            "directories_count": dirs_count,
            "usage_tip": usage_tip
        }
        
    except Exception as e:
        logger.error(f"[MCP工具错误] 搜索失败: {str(e)}", exc_info=True)
        return {
            "success": "false",
            "error": {
                "name": type(e).__name__,
                "value": str(e)
            },
            "message": f"Search failed: {str(e)}",
            "found_items": []
        }



def main():
    """主入口函数 - 供 uvx 和命令行调用"""

    # 设置全局环境变量，确保整个程序和依赖库都能读取到
    os.environ["AGENTSPHERE_DOMAIN"] = "agentsphere.run"
    
    logger.info("启动 Agent Sphere STDIO MCP 服务器...")
    
    try:
        # STDIO 是 FastMCP 的默认传输方式，适用于本地客户端（如 Claude Desktop）
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行失败: {str(e)}", exc_info=True)
    finally:
        logger.info("正在清理资源...")
        try:
            # 异步清理需要在事件循环中执行
            import asyncio
            asyncio.run(sandbox_manager.cleanup())
        except Exception as e:
            logger.error(f"资源清理失败: {str(e)}")
        logger.info("MCP STDIO 服务器已停止")


if __name__ == "__main__":
    main()
