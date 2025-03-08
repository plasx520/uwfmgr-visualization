import sys
import subprocess
import ctypes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QTextEdit, QTabWidget, QLineEdit, QMessageBox,
                            QGroupBox, QFormLayout, QCheckBox, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

def is_admin():
    """检查程序是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class CommandThread(QThread):
    """执行命令的线程，避免UI卡顿"""
    output_signal = pyqtSignal(str)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
        
    def run(self):
        try:
            # 创建一个临时批处理文件来执行命令并等待用户按键
            temp_bat = "temp_command.bat"
            with open(temp_bat, "w", encoding="gbk") as f:
                f.write(f"@echo off\n")
                f.write(f"echo 正在执行: {self.command}\n")
                f.write(f"{self.command}\n")
                f.write("echo.\n")
                f.write("echo ======================================================================================================\n")
                f.write("echo =====                                  命令执行完成                                              =====\n")
                f.write("echo ======================================================================================================\n")
                f.write("pause > nul\n")
            
            # 直接启动批处理文件，显示窗口
            subprocess.run(temp_bat, shell=True)
            
            # 执行完成后删除临时文件
            import os
            try:
                os.remove(temp_bat)
            except:
                pass
                
            self.output_signal.emit("命令已在命令行窗口中执行完成。")
        except Exception as e:
            self.output_signal.emit(f"执行出错: {str(e)}")

class UWFManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("UWF 管理工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建选项卡
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # 状态选项卡
        status_tab = QWidget()
        status_layout = QVBoxLayout(status_tab)
        
        # 状态控制组
        status_group = QGroupBox("UWF 状态控制")
        status_control_layout = QHBoxLayout()
        
        self.get_status_btn = QPushButton("获取状态")
        self.get_status_btn.clicked.connect(lambda: self.execute_command("uwfmgr get-config"))
        
        self.enable_btn = QPushButton("启用 UWF")
        self.enable_btn.clicked.connect(lambda: self.execute_command("uwfmgr filter enable"))
        
        self.disable_btn = QPushButton("禁用 UWF")
        self.disable_btn.clicked.connect(lambda: self.execute_command("uwfmgr filter disable"))
        
        status_control_layout.addWidget(self.get_status_btn)
        status_control_layout.addWidget(self.enable_btn)
        status_control_layout.addWidget(self.disable_btn)
        status_group.setLayout(status_control_layout)
        status_layout.addWidget(status_group)
        
        # 保护设置组
        protection_group = QGroupBox("保护设置")
        protection_layout = QVBoxLayout()
        
        # 卷保护
        volume_layout = QHBoxLayout()
        self.volume_combo = QComboBox()
        self.refresh_volumes()
        self.refresh_volumes_btn = QPushButton("刷新卷列表")
        self.refresh_volumes_btn.clicked.connect(self.refresh_volumes)
        self.protect_volume_btn = QPushButton("保护卷")
        self.protect_volume_btn.clicked.connect(self.protect_volume)
        self.unprotect_volume_btn = QPushButton("取消保护")
        self.unprotect_volume_btn.clicked.connect(self.unprotect_volume)
        
        volume_layout.addWidget(QLabel("选择卷:"))
        volume_layout.addWidget(self.volume_combo)
        volume_layout.addWidget(self.refresh_volumes_btn)
        volume_layout.addWidget(self.protect_volume_btn)
        volume_layout.addWidget(self.unprotect_volume_btn)
        protection_layout.addLayout(volume_layout)
        # 文件排除
        file_exclusion_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.add_file_exclusion_btn = QPushButton("添加文件夹排除")
        self.add_file_exclusion_btn.clicked.connect(self.add_file_exclusion)
        self.remove_file_exclusion_btn = QPushButton("移除文件夹排除")
        self.remove_file_exclusion_btn.clicked.connect(self.remove_file_exclusion)
        
        file_exclusion_layout.addWidget(QLabel("文件夹路径:"))
        file_exclusion_layout.addWidget(self.file_path_edit)
        file_exclusion_layout.addWidget(self.add_file_exclusion_btn)
        file_exclusion_layout.addWidget(self.remove_file_exclusion_btn)
        protection_layout.addLayout(file_exclusion_layout)
        
        # 注册表排除
        registry_exclusion_layout = QHBoxLayout()
        self.registry_path_edit = QLineEdit()
        self.add_registry_exclusion_btn = QPushButton("添加注册表排除")
        self.add_registry_exclusion_btn.clicked.connect(self.add_registry_exclusion)
        self.remove_registry_exclusion_btn = QPushButton("移除注册表排除")
        self.remove_registry_exclusion_btn.clicked.connect(self.remove_registry_exclusion)
        
        registry_exclusion_layout.addWidget(QLabel("注册表路径:"))
        registry_exclusion_layout.addWidget(self.registry_path_edit)
        registry_exclusion_layout.addWidget(self.add_registry_exclusion_btn)
        registry_exclusion_layout.addWidget(self.remove_registry_exclusion_btn)
        protection_layout.addLayout(registry_exclusion_layout)
        
        protection_group.setLayout(protection_layout)
        status_layout.addWidget(protection_group)
        
        # 添加覆盖层类型控制组
        overlay_type_group = QGroupBox("覆盖层类型")
        overlay_type_layout = QHBoxLayout()
        
        self.ram_btn = QPushButton("内存")
        self.ram_btn.clicked.connect(lambda: self.execute_command("uwfmgr overlay Set-Type RAM"))
        
        self.disk_btn = QPushButton("硬盘")
        self.disk_btn.clicked.connect(lambda: self.execute_command("uwfmgr overlay Set-Type DISK"))
        
        overlay_type_layout.addWidget(self.ram_btn)
        overlay_type_layout.addWidget(self.disk_btn)
        overlay_type_group.setLayout(overlay_type_layout)
        status_layout.addWidget(overlay_type_group)
        
        # 高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QFormLayout()
        
        self.overlay_btn = QPushButton("设置覆盖")
        self.overlay_btn.clicked.connect(self.set_overlay)
        self.overlay_edit = QLineEdit()
        self.overlay_edit.setPlaceholderText("输入覆盖大小 (MB)")
        
        self.critical_threshold_btn = QPushButton("设置临界阈值")
        self.critical_threshold_btn.clicked.connect(self.set_critical_threshold)
        self.critical_threshold_edit = QLineEdit()
        self.critical_threshold_edit.setPlaceholderText("输入临界阈值 (MB)")
        
        self.warning_threshold_btn = QPushButton("设置警告阈值")
        self.warning_threshold_btn.clicked.connect(self.set_warning_threshold)
        self.warning_threshold_edit = QLineEdit()
        self.warning_threshold_edit.setPlaceholderText("输入警告阈值 (MB)")
        
        advanced_layout.addRow(self.overlay_edit, self.overlay_btn)
        advanced_layout.addRow(self.critical_threshold_edit, self.critical_threshold_btn)
        advanced_layout.addRow(self.warning_threshold_edit, self.warning_threshold_btn)
        
        advanced_group.setLayout(advanced_layout)
        status_layout.addWidget(advanced_group)
        
        # 会话控制组
        session_group = QGroupBox("会话控制")
        session_layout = QHBoxLayout()
        
        self.restart_btn = QPushButton("重启系统")
        self.restart_btn.clicked.connect(self.restart_system)
        self.shutdown_btn = QPushButton("关闭系统")
        self.shutdown_btn.clicked.connect(self.shutdown_system)
        self.commit_btn = QPushButton("查询剩余")
        self.commit_btn.clicked.connect(lambda: self.execute_command("uwfmgr overlay get-availablespace"))
        
        session_layout.addWidget(self.restart_btn)
        session_layout.addWidget(self.shutdown_btn)
        session_layout.addWidget(self.commit_btn)
        session_group.setLayout(session_layout)
        status_layout.addWidget(session_group)
        
        # 输出区域 - 改为简单的状态显示
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(100)  # 减小高度，只用于显示状态信息
        status_layout.addWidget(QLabel("状态信息:"))
        status_layout.addWidget(self.output_text)
        
        # 添加选项卡
        tabs.addTab(status_tab, "UWF 管理")
        
        # 添加关于选项卡
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <h2>UWF 管理工具</h2>
        <p>这是一个用于管理 Windows 统一写入过滤器 (UWF) 的图形界面工具。</p>
        <p>UWF 是一种基于扇区的写入过滤器，可以将对系统卷的写入重定向到RAM中的覆盖层，从而保护系统卷不被更改。</p>
        <h3>功能:</h3>
        <ul>
            <li>启用/禁用 UWF 过滤器</li>
            <li>管理受保护的卷</li>
            <li>添加/删除文件和注册表排除项</li>
            <li>配置覆盖设置</li>
            <li>系统重启和关机</li>
        </ul>
        <p>注意: 某些操作需要管理员权限才能执行。</p>
        """)
        about_layout.addWidget(about_text)
        tabs.addTab(about_tab, "关于")
        
    def execute_command(self, command):
        self.output_text.append(f"执行命令: {command}")
        self.thread = CommandThread(command)
        self.thread.output_signal.connect(self.update_output)
        self.thread.start()
    
    def update_output(self, text):
        self.output_text.append(text)
    
    def refresh_volumes(self):
        self.volume_combo.clear()
        try:
            result = subprocess.run("wmic logicaldisk get caption", shell=True, capture_output=True, text=True)
            volumes = result.stdout.strip().split('\n')[1:]
            for volume in volumes:
                vol = volume.strip()
                if vol:
                    self.volume_combo.addItem(vol)
        except Exception as e:
            self.update_output(f"获取卷列表出错: {str(e)}")
    
    def protect_volume(self):
        volume = self.volume_combo.currentText()
        if volume:
            self.execute_command(f'uwfmgr volume protect {volume}')
        else:
            QMessageBox.warning(self, "警告", "请选择一个卷")
    
    def unprotect_volume(self):
        volume = self.volume_combo.currentText()
        if volume:
            self.execute_command(f'uwfmgr volume unprotect {volume}')
        else:
            QMessageBox.warning(self, "警告", "请选择一个卷")
    # 删除 browse_file 方法
    def add_file_exclusion(self):
        file_path = self.file_path_edit.text()
        if file_path:
            # 确保路径使用反斜杠
            file_path = file_path.replace('/', '\\')
            self.execute_command(f'uwfmgr file add-exclusion {file_path}')
        else:
            QMessageBox.warning(self, "警告", "请输入文件路径")
    
    def remove_file_exclusion(self):
        file_path = self.file_path_edit.text()
        if file_path:
            # 确保路径使用反斜杠
            file_path = file_path.replace('/', '\\')
            self.execute_command(f'uwfmgr file remove-exclusion {file_path}')
        else:
            QMessageBox.warning(self, "警告", "请输入文件路径")
    def add_registry_exclusion(self):
        registry_path = self.registry_path_edit.text()
        if registry_path:
            self.execute_command(f'uwfmgr registry commit {registry_path}')
        else:
            QMessageBox.warning(self, "警告", "请输入注册表路径")
    
    def remove_registry_exclusion(self):
        registry_path = self.registry_path_edit.text()
        if registry_path:
            self.execute_command(f'uwfmgr registry commit-delete {registry_path}')
        else:
            QMessageBox.warning(self, "警告", "请输入注册表路径")
    
    def set_overlay(self):
        overlay_size = self.overlay_edit.text()
        if overlay_size and overlay_size.isdigit():
            self.execute_command(f'uwfmgr overlay set-size {overlay_size}')
        else:
            QMessageBox.warning(self, "警告", "请输入有效的覆盖大小")
    
    def set_critical_threshold(self):
        threshold = self.critical_threshold_edit.text()
        if threshold and threshold.isdigit():
            self.execute_command(f'uwfmgr overlay set-warningthreshold {threshold}')
        else:
            QMessageBox.warning(self, "警告", "请输入有效的临界阈值")
    
    def set_warning_threshold(self):
        threshold = self.warning_threshold_edit.text()
        if threshold and threshold.isdigit():
            self.execute_command(f'uwfmgr overlay set-criticalthreshold {threshold}')
        else:
            QMessageBox.warning(self, "警告", "请输入有效的警告阈值")
    
    def restart_system(self):
        reply = QMessageBox.question(self, '确认', '确定要重启系统吗？',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_command('shutdown /r /t 0')
    
    def shutdown_system(self):
        reply = QMessageBox.question(self, '确认', '确定要关闭系统吗？',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.execute_command('shutdown /s /t 0')

def main():
    # 检查是否以管理员权限运行，如果不是则请求提升
    if not is_admin():
        # 重新以管理员权限启动程序
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格，在所有平台上看起来都很一致
    
    # 设置应用程序样式表，美化界面
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #00a2ed;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QLineEdit, QComboBox {
            border: 1px solid #cccccc;
            border-radius: 3px;
            padding: 3px;
            background-color: white;
        }
        QTextEdit {
            border: 1px solid #cccccc;
            border-radius: 3px;
            background-color: white;
        }
    """)
    
    window = UWFManager()
    window.show()
    
    # 由于已经在程序开始时请求了管理员权限，这里可以移除原来的检查代码
    # 或者保留它作为二次确认
    try:
        result = subprocess.run("uwfmgr get-config", shell=True, capture_output=True, 
                               text=True, encoding='utf-8', errors='replace')
        if "拒绝访问" in result.stderr or "Access is denied" in result.stderr:
            QMessageBox.warning(window, "警告", "尽管程序以管理员身份运行，但仍无法访问UWF功能。请确认您的系统支持UWF。")
    except Exception:
        pass
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
