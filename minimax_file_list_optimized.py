import os
import json
import asyncio
import argparse
from typing import List, Dict, Optional, Tuple

import httpx
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# --- 配置常量 ---
API_BASE_URL = "https://api.minimax.chat/v1"
ALL_PURPOSES = [
    't2a_async_input', 'retrieval', 'fine-tune', 'fine-tune-result',
    'voice_clone', 'prompt_audio', 'assistants', 'role-recognition'
]

# --- 控制台和颜色 ---
console = Console()

def get_env_variable(var_name: str) -> str:
    """安全地获取环境变量"""
    value = os.getenv(var_name)
    if not value:
        console.print(f"[bold red]错误: 环境变量 {var_name} 未设置。[/bold red]")
        raise ValueError(f"环境变量 {var_name} 未设置")
    return value

def save_to_json(data: dict, purpose: str) -> str:
    """将数据保存为JSON文件"""
    filename = f'files_{purpose}.json'
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename
    except IOError as e:
        console.print(f"[yellow]警告: 无法写入文件 {filename}: {e}[/yellow]")
        return ""

class MinimaxFileClient:
    """用于与Minimax文件API异步交互的客户端"""
    def __init__(self, group_id: str, api_key: str):
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.group_id = group_id
        self.client = httpx.AsyncClient(base_url=API_BASE_URL, headers=self.headers, timeout=30.0)

    async def close(self):
        """关闭httpx客户端"""
        await self.client.aclose()

    async def get_files_for_purpose(self, purpose: str) -> Tuple[str, Optional[Dict]]:
        """异步获取单个purpose的文件列表"""
        url = f"/files/list"
        params = {'GroupId': self.group_id, 'purpose': purpose}
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return purpose, response.json()
        except httpx.HTTPStatusError as e:
            console.print(f"[red]请求错误 (purpose: {purpose}): {e.response.status_code} - {e.response.text}[/red]")
        except httpx.RequestError as e:
            console.print(f"[red]网络请求失败 (purpose: {purpose}): {e}[/red]")
        except json.JSONDecodeError as e:
            console.print(f"[red]JSON解析失败 (purpose: {purpose}): {e}[/red]")
        return purpose, None

    async def get_all_files(self, purposes: List[str]) -> List[Tuple[str, Optional[Dict]]]:
        """并发获取所有指定purpose的文件列表"""
        tasks = [self.get_files_for_purpose(p) for p in purposes]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task_id = progress.add_task("[cyan]查询中...", total=len(tasks))
            results = []
            for future in asyncio.as_completed(tasks):
                result = await future
                results.append(result)
                progress.update(task_id, advance=1)
        
        return results

async def main():
    """主执行函数"""
    parser = argparse.ArgumentParser(description="从Minimax API获取文件列表。")
    parser.add_argument(
        'purposes',
        nargs='*',
        default=ALL_PURPOSES,
        help=f"要查询的一个或多个文件用途。如果未提供，则查询所有类型: {', '.join(ALL_PURPOSES)}"
    )
    parser.add_argument(
        '--save-json',
        action='store_true',
        help="将获取到的列表保存为JSON文件。"
    )
    args = parser.parse_args()

    try:
        group_id = get_env_variable('MINIMAX_GROUP_ID')
        api_key = get_env_variable('MINIMAX_API_KEY')
    except ValueError:
        return

    client = MinimaxFileClient(group_id, api_key)
    results = await client.get_all_files(args.purposes)
    await client.close()

    # --- 准备表格 ---
    table = Table(title="[bold magenta]Minimax 文件列表统计[/bold magenta]", show_header=True, header_style="bold cyan")
    table.add_column("文件用途 (Purpose)", style="green", min_width=20)
    table.add_column("文件数量", justify="right", style="magenta")
    table.add_column("状态", justify="center", style="yellow")
    if args.save_json:
        table.add_column("保存路径", style="dim")

    # --- 填充数据 ---
    sorted_results = sorted(results, key=lambda x: x[0]) # 按purpose名称排序
    for purpose, result in sorted_results:
        row_data = [purpose]
        if result and result.get('base_resp', {}).get('status_code') == 0:
            file_count = len(result.get('files', []))
            row_data.extend([str(file_count), "[green]成功[/green]"])
            if args.save_json:
                filename = save_to_json(result, purpose)
                row_data.append(filename if filename else "[red]保存失败[/red]")
        else:
            error_msg = result.get('base_resp', {}).get('status_msg', '请求失败') if result else '请求失败'
            row_data.extend(["0", f"[red]失败 ({error_msg})[/red]"])
            if args.save_json:
                row_data.append("-")
        
        table.add_row(*row_data)

    console.print(table)

if __name__ == '__main__':
    # Note: This script requires 'httpx' and 'rich'. Install with: pip install httpx rich
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作被用户中断。[/yellow]")
    except Exception as e:
        console.print(f"[bold red]发生了一个意外错误: {e}[/bold red]")