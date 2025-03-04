# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, scrolledtext
import ctypes
import sys
import subprocess
import locale

# 获取系统编码
system_encoding = locale.getpreferredencoding()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if sys.platform == 'win32':
        params = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    else:
        messagebox.showerror("错误", "此功能仅在 Windows 系统上可用。")

def create_button(frame, text, cmd, info, set_text_func):
    """创建按钮并设置其命令。"""
    button = tk.Button(frame, text=text, command=lambda: set_text_func(cmd, info))
    button.pack(side=tk.LEFT, padx=5)
    return button

def set_command_and_info(input_cmd, input_info, cmd, info):
    """在输入框中设置命令和信息。"""
    input_cmd.delete(0, tk.END)
    input_cmd.insert(0, cmd)
    input_info.delete(0, tk.END)
    input_info.insert(0, info)

def execute_command(input_cmd, text_output):
    """执行命令并在新窗口显示输出，按任意键退出"""
    command = input_cmd.get()
    try:
        # 添加 pause 命令实现任意键退出
        subprocess.Popen(
            f'cmd /k chcp 65001 & {command} & pause>nul & exit',  # 关键修改处
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        output = f"命令已在新窗口执行: {command}"
    except Exception as e:
        output = f"执行命令时出错: {str(e)}"
  
  
    # 清空并更新输出文本框
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, output)

def create_base_config_frame(root, set_text_func):
    """创建基本配置框架，包含按钮。"""
    frame = tk.Frame(root)
    tk.Label(frame, text="基本配置:").pack(side=tk.LEFT)
    buttons = [
        ("查看配置", "uwfmgr Get-Config", "查看配置详情，里面有下一次启动的配置，注意检查哦"),
        ("启用UWF", "uwfmgr filter enable", "启用命令可能需要执行多次，并重启电脑才有效"),
        ("禁用UWF", "uwfmgr filter disable", "禁用命令可能需要执行多次，并重启电脑才有效")
    ]
    for text, cmd, info in buttons:
        create_button(frame, text, cmd, info, set_text_func)
    return frame

def create_save_patch_frame(root, set_text_func):
    """创建保存补丁框架，包含按钮。"""
    frame = tk.Frame(root)
    tk.Label(frame, text="写入过滤:").pack(side=tk.LEFT)
    buttons = [
        ("内存", "uwfmgr overlay Set-Type RAM", "可能在禁用UWF并重启后才可以修改这个参数，保存到内存有助于保护硬盘"),
        ("硬盘", "uwfmgr overlay Set-Type DISK", "可能在禁用UWF并重启后才可以修改这个参数，保存到硬盘可以配置更大的overlay容量")
    ]
    for text, cmd, info in buttons:
        create_button(frame, text, cmd, info, set_text_func)
    tk.Label(frame, text="写入位置").pack(side=tk.RIGHT)
    return frame

def create_cache_size_frame(root, set_text_func):
    """创建缓存大小框架，包含按钮。"""
    frame = tk.Frame(root)
    tk.Label(frame, text="缓存设置:").pack(side=tk.LEFT)
    buttons = [
        ("最大缓存", "uwfmgr overlay set-size 10240", "单位是MB，如果是内存模式建议5120以上，硬盘模式建议20480以上"),
        ("警告阈值", "uwfmgr overlay set-warningthreshold 5024", "建议为最大缓存的50-70%左右，超过这个容量后电脑会弹出一条提醒消息"),
        ("严重阈值", "uwfmgr overlay set-criticalthreshold 8192", "建议为最大缓存的80-95%左右，超过这个容量后电脑随时都可能要求重启")
    ]
    for text, cmd, info in buttons:
        create_button(frame, text, cmd, info, set_text_func)
    tk.Label(frame, text="单位MB").pack(side=tk.RIGHT)
    return frame

def create_disk_part_set_frame(root, set_text_func):
    """创建磁盘分区设置框架，包含按钮。"""
    frame = tk.Frame(root)
    tk.Label(frame, text="分区保护:").pack(side=tk.LEFT)
    buttons = [
        ("启用C盘", "uwfmgr volume protect C:", "建议开启UWF后并保护Windows所在分区，如果你要保护的盘符不是C自行修改即可"),
        ("移除C盘", "uwfmgr volume unprotect C:", "盘符可以自行修改"),  # 修正命令拼写
        ("启用所有分区", "uwfmgr volume protect all", "建议开启UWF后并保护Windows所在分区，如果你要保护的盘符不是C自行修改即可"),
        ("禁用所有分区", "uwfmgr volume unprotect all", "这样会导致UWF虽然开启了服务但是其实是失效状态")  # 修正命令拼写
    ]
    for text, cmd, info in buttons:
        create_button(frame, text, cmd, info, set_text_func)
    return frame

def create_windows_update_frame(root, set_text_func):
    """创建Windows更新框架，包含按钮。"""
    frame = tk.Frame(root)
    tk.Label(frame, text="Windows更新:").pack(side=tk.LEFT)
    buttons = [
        ("允许绕过UWF", "uwfmgr servicing Update-Windows", "允许Windows更新来更新受保护的系统"),
        ("禁止绕过UWF", "uwfmgr servicing disable", "禁止Windows更新来更新受保护的系统（这条命令并不能禁用Windows更新的运行，只是更新后重启无效而已）")
    ]
    for text, cmd, info in buttons:
        create_button(frame, text, cmd, info, set_text_func)
    return frame

def create_file_exclusion_frame(root, set_text_func):
    """创建文件排除框架，包含按钮。"""
    frame = tk.Frame(root)
    tk.Label(frame, text="排除目录:").pack(side=tk.LEFT)
    buttons = [
        ("排除目录", "uwfmgr file add-exclusion Path C:\\Users\\yh\\Downloads", "重启后才有效"),
        ("不再排除目录", "uwfmgr file remove-exclusion Path C:\\Users\\yh\\Downloads", "重启后才有效"),
        ("排除文件", "uwfmgr file add-exclusion Filename C:\\Users\\yh\\Downloads\\demo.txt", "重启后才有效"),
        ("不再排除文件", "uwfmgr file remove-exclusion Filename C:\\Users\\yh\\Downloads\\demo.txt", "重启后才有效"),
        ("保存文件", "uwfmgr file commit Filename C:\\Users\\yh\\Downloads\\demo.txt", "保存一个文件的内容修改和更新"),
        ("确定删除", "uwfmgr file commit-delete Filename C:\\Users\\yh\\Downloads\\demo.txt", "这个文件你已经删除，不希望重启后恢复"),
        ("查看配置", "uwfmgr file get-exclusions", "显示针对当前会话和下次会话的具体文件排除配置信息")
    ]
    for text, cmd, info in buttons:
        create_button(frame, text, cmd, info, set_text_func)
    return frame

def create_registry_set_frame(root, set_text_func):
    """创建注册表设置框架，包含按钮。"""
    frame = tk.Frame(root)
    tk.Label(frame, text="注册表排除:").pack(side=tk.LEFT)
    buttons = [
        ("排除路径", "uwfmgr registry add-exclusion HKLM\\Software\\Microsoft\\Windows\\run", "重启后才有效"),
        ("不再排除", "uwfmgr registry remove-exclusion HKLM\\Software\\Microsoft\\Windows\\run", "重启后才有效"),
        ("保存注册表值", "uwfmgr registry commit HKLM\\Software\\Test TestValue", "保存一个注册表键值的修改"),  # 修正命令格式
        ("确定删除", "uwfmgr registry commit-delete HKLM\\Software\\Test TestValue", "这个键值你已经删除，不希望重启后恢复"),
        ("查看配置", "uwfmgr registry get-exclusions", "显示针对当前会话和下次会话的具体注册表排除配置信息")
    ]
    for text, cmd, info in buttons:
        create_button(frame, text, cmd, info, set_text_func)
    return frame

def main():
    if not is_admin():
        run_as_admin()
        sys.exit()

    root = tk.Tk()
    root.title("UWF管理器")
    root.geometry("700x500")

    # 命令输入框
    input_cmd = tk.Entry(root, width=70)
    input_cmd.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5)

    # 信息输入框
    input_info = tk.Entry(root, width=70)
    input_info.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5)

    # 创建并放置所有框架
    frames = [
        create_base_config_frame(root, lambda c, i: set_command_and_info(input_cmd, input_info, c, i)),
        create_save_patch_frame(root, lambda c, i: set_command_and_info(input_cmd, input_info, c, i)),
        create_cache_size_frame(root, lambda c, i: set_command_and_info(input_cmd, input_info, c, i)),
        create_disk_part_set_frame(root, lambda c, i: set_command_and_info(input_cmd, input_info, c, i)),
        create_windows_update_frame(root, lambda c, i: set_command_and_info(input_cmd, input_info, c, i)),
        create_file_exclusion_frame(root, lambda c, i: set_command_and_info(input_cmd, input_info, c, i)),
        create_registry_set_frame(root, lambda c, i: set_command_and_info(input_cmd, input_info, c, i))
    ]

    for idx, frame in enumerate(frames):
        frame.grid(row=2 + idx, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5)

    # 执行按钮
    execute_button = tk.Button(root, text="执行", command=lambda: execute_command(input_cmd, text_output))
    execute_button.grid(row=len(frames) + 2, column=0, columnspan=2, pady=10)

    # 命令输出文本框
    text_output = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        width=80,
        height=10,
        font=('Microsoft YaHei', 10)  # 使用更通用的中文字体
    )
    text_output.grid(row=len(frames) + 3, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5)

    # 配置 grid 权重
    root.columnconfigure(0, weight=1)
    for i in range(len(frames) + 4):
        root.rowconfigure(i, weight=1)

    root.mainloop()

if __name__ == "__main__":
    main()