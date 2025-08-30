#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import signal
import sys
import time
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()

def make_clock() -> Panel:
    """生成完美显示的时钟面板"""
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d %A")
    
    # 计算所需最小宽度
    min_width = max(
        len(time_str) + 8,  # 时间文字+两边留空
        len(date_str) + 8,  # 日期文字+两边留空
        28  # 保证"按 Ctrl+C 退出"能完整显示
    )
    
    content = Align.center(
        Text.from_markup(
            f"[bold yellow]{time_str}[/]\n[green]{date_str}[/]",
            justify="center"
        ),
        vertical="middle"
    )
    
    return Panel(
        content,
        title="[bold cyan]⌚ 终端时钟[/]",
        subtitle="[dim]按 Ctrl+C 退出",
        border_style="bright_blue",
        padding=(1, 4),  # (垂直, 水平) 内边距
        width=min_width + 4,  # 保证所有内容完整显示
        expand=False
    )

def build_layout() -> Layout:
    """只保留时钟区域"""
    layout = Layout()
    layout.split_column(
        Layout(name="clock", size=10),
    )
    layout["clock"].update(make_clock())
    return layout

def graceful_exit(signum, frame):
    console.show_cursor(True)
    console.print("\n[dim]时钟已停止")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, graceful_exit)
    console.show_cursor(False)
    
    try:
        with Live(build_layout(), refresh_per_second=10, screen=True) as live:
            while True:
                live.update(build_layout())
                time.sleep(0.1)
    finally:
        console.show_cursor(True)

if __name__ == "__main__":
    main()# 终端时钟程序