import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QGroupBox,
    QCheckBox, QSpinBox, QFrame, QSizePolicy, QDialog
)
from PyQt5.QtCore import Qt, QProcess, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class HelpDialog(QDialog):
    """自定义对话框，用于显示播放控制键说明"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("播放控制键说明")
        self.resize(420, 380) # 调整窗口大小
        if parent:
             self.move(
                 parent.x() + (parent.width() - self.width()) // 2,
                 parent.y() + (parent.height() - self.height()) // 2
             )
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel("播放时的控制键：")
        title_label.setStyleSheet("font-weight: bold; font-size: 14pt; margin-bottom: 10px; color: #333;")
        title_label.setAlignment(Qt.AlignCenter) # 居中标题
        layout.addWidget(title_label)

        # 帮助文本内容 - 使用 HTML 和 CSS 样式
        help_text = """
        <style>
            .key { font-family: 'Consolas', 'Courier New', monospace; font-weight: bold; color: #0078d4; } /* 蓝色加粗等宽字体 */
            .desc { font-family: 'Microsoft YaHei', sans-serif;font-weight: bold; } /* 描述使用默认字体 */
            p { margin: 5px 0; } /* 段落间距 */
        </style>
        
        <p><span class="key">q</span>, <span class="key">ESC    </span> <span class="desc">退出</span></p>
        <p><span class="key">f    </span> <span class="desc">全屏</span></p>
        <p><span class="key">p</span>, <span class="key">space    </span> <span class="desc">暂停</span></p>
        <p><span class="key">s    </span> <span class="desc">播放下一帧</span></p>
        <p><span class="key">F1    </span> <span class="desc">左边的画面播放到下一帧</span></p>
        <p><span class="key">F2    </span> <span class="desc">右边的画面播放到下一帧</span></p>
        <p><span class="key">左键    </span> <span class="desc">回退10秒</span></p>
        <p><span class="key">右键    </span> <span class="desc">快进10秒</span></p>
        <p><span class="key">上键    </span> <span class="desc">快进60秒</span></p>
        <p><span class="key">下键    </span> <span class="desc">回退60秒</span></p>
        <p><span class="key">鼠标左键单击    </span> <span class="desc">移动分割线到鼠标位置</span></p>
        <p><span class="key">按住鼠标左键    </span> <span class="desc">移动分割线</span></p>
        <p><span class="key">鼠标滚轮    </span> <span class="desc">调整画面大小</span></p>
        """

        # 使用 QLabel 显示 HTML 内容
        help_label = QLabel(help_text)
        help_label.setTextFormat(Qt.RichText) # 指定文本格式为富文本 (HTML)
        help_label.setWordWrap(True) # 允许文本换行
        help_label.setAlignment(Qt.AlignLeft | Qt.AlignTop) # 内容靠左上对齐
        # 可选：添加一个边框或背景来突出显示内容区域
        # help_label.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; padding: 10px;")
        
        # 将 QLabel 放入一个 QWidget 或直接添加滚动条（如果内容可能很长）
        # 这里内容不多，暂时不需要滚动条
        layout.addWidget(help_label)

        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)


class VCmpLauncher(QMainWindow):
    process_finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VCmpTool 快速启动器")
        self.resize(550, 420)
        self.setMinimumSize(480, 370)

        self.vcmp_executable = self.locate_vcmp_executable()
        if not self.vcmp_executable:
            QMessageBox.critical(self, "致命错误", "找不到 VCmpTool 可执行文件！程序将退出。")
            sys.exit(1)

        self.current_process = None
        self.help_dialog = None

        self.init_ui()
        self.apply_winui_style()
        self.process_finished.connect(self.on_process_finished)

    def locate_vcmp_executable(self):
        try:
            base_path = sys._MEIPASS
        except Exception:
            if getattr(sys, 'frozen', False):
                 base_path = os.path.dirname(sys.executable)
            else:
                 base_path = os.path.dirname(os.path.abspath(__file__))
        possible_names = ["VCmpTool.exe", "vcmptool.exe", "VCmpTool"]
        for name in possible_names:
            full_path = os.path.join(base_path, name)
            if os.path.isfile(full_path):
                return full_path
        return None

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        file_frame = QFrame()
        file_frame.setObjectName("fileFrame")
        file_layout = QGridLayout(file_frame)
        file_layout.setContentsMargins(15, 15, 15, 15)
        file_layout.setSpacing(10)

        self.label_file1 = QLabel("视频文件 1:")
        self.entry_file1 = QLineEdit()
        self.entry_file1.setObjectName("fileEntry")
        self.btn_browse1 = QPushButton("浏览")
        self.btn_browse1.setObjectName("browseButton")
        self.btn_browse1.clicked.connect(lambda: self.browse_file(self.entry_file1))

        self.label_file2 = QLabel("视频文件 2:")
        self.entry_file2 = QLineEdit()
        self.entry_file2.setObjectName("fileEntry")
        self.btn_browse2 = QPushButton("浏览")
        self.btn_browse2.setObjectName("browseButton")
        self.btn_browse2.clicked.connect(lambda: self.browse_file(self.entry_file2))

        file_layout.addWidget(self.label_file1, 0, 0)
        file_layout.addWidget(self.entry_file1, 0, 1)
        file_layout.addWidget(self.btn_browse1, 0, 2)
        file_layout.addWidget(self.label_file2, 1, 0)
        file_layout.addWidget(self.entry_file2, 1, 1)
        file_layout.addWidget(self.btn_browse2, 1, 2)

        param_group = QGroupBox(" 播放参数 ")
        param_group.setObjectName("paramGroup")
        param_layout = QGridLayout(param_group)
        param_layout.setContentsMargins(15, 20, 15, 15)
        param_layout.setSpacing(15)

        self.label_loop = QLabel("循环次数 (-loop):")
        self.spin_loop = QSpinBox()
        self.spin_loop.setRange(1, 9999)
        self.spin_loop.setValue(1)
        self.spin_loop.setObjectName("spinBox")

        self.check_auto_move = QCheckBox("自动移动分割线 (-m)")
        self.check_auto_move.setObjectName("checkBox")

        param_layout.addWidget(self.label_loop, 0, 0, alignment=Qt.AlignRight)
        param_layout.addWidget(self.spin_loop, 0, 1, alignment=Qt.AlignLeft)
        param_layout.addWidget(self.check_auto_move, 1, 0, 1, 2, alignment=Qt.AlignLeft)

        status_layout = QHBoxLayout()
        self.label_status = QLabel("状态: 空闲")
        self.label_status.setObjectName("statusLabel")
        status_layout.addWidget(self.label_status)
        status_layout.addStretch()

        help_button = QPushButton("ℹ️ 控制键说明")
        help_button.clicked.connect(self.show_help)
        status_layout.addWidget(help_button)

        button_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶️ 启动视频对比")
        self.btn_start.setObjectName("startButton")
        self.btn_start.clicked.connect(self.launch_vcmp)
        self.btn_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.btn_terminate = QPushButton("⏹️ 结束进程")
        self.btn_terminate.setObjectName("terminateButton")
        self.btn_terminate.clicked.connect(self.terminate_vcmp)
        self.btn_terminate.setEnabled(False)
        self.btn_terminate.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_terminate)

        main_layout.addWidget(file_frame)
        main_layout.addWidget(param_group)
        main_layout.addLayout(status_layout)
        main_layout.addLayout(button_layout)

    def show_help(self):
        if self.help_dialog is not None and self.help_dialog.isVisible():
            self.help_dialog.raise_()
            self.help_dialog.activateWindow()
        else:
            self.help_dialog = HelpDialog(self)
            self.help_dialog.finished.connect(self.on_help_dialog_closed)
            self.help_dialog.show()

    def on_help_dialog_closed(self):
        self.help_dialog = None

    def apply_winui_style(self):
        style = """
        QMainWindow {
            background-color: #f3f3f3;
        }
        QWidget {
        }
        QFrame#fileFrame {
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e1e1e1;
        }
        QLabel {
            color: #333;
        }
        QLineEdit#fileEntry {
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: #fafafa;
        }
        QLineEdit#fileEntry:focus {
            border: 1px solid #0078d4;
        }
        QPushButton#browseButton {
            padding: 5px 15px;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 4px;
            color: #333;
        }
        QPushButton#browseButton:hover {
            background-color: #e6e6e6;
            border-color: #999;
        }
        QPushButton#browseButton:pressed {
            background-color: #d6d6d6;
        }
        QGroupBox#paramGroup {
            font-weight: bold;
            color: #555;
            border: 1px solid #e1e1e1;
            border-radius: 8px;
            margin-top: 1ex;
            background-color: rgba(255, 255, 255, 180);
        }
        QGroupBox#paramGroup::title {
            subline-offset: -14px;
            padding: 0 5px;
            background-color: transparent;
        }
        QSpinBox#spinBox {
            padding: 3px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: white;
        }
        QSpinBox#spinBox::up-button, QSpinBox#spinBox::down-button {
            width: 16px;
            border: none;
            background: transparent;
        }
        QCheckBox#checkBox {
            spacing: 5px;
        }
        QCheckBox#checkBox::indicator {
            width: 18px;
            height: 18px;
        }
        QCheckBox#checkBox::indicator:unchecked {
            border: 1px solid #999;
            border-radius: 3px;
            background-color: white;
        }
        QCheckBox#checkBox::indicator:checked {
            border: 1px solid #0078d4;
            border-radius: 3px;
            background-color: #0078d4;
            image: url();
        }
        QLabel#statusLabel {
            color: blue;
            font-style: italic;
        }
        QPushButton#startButton, QPushButton#terminateButton {
            padding: 10px;
            border-radius: 4px;
            border: none;
            font-weight: bold;
        }
        QPushButton#startButton {
            background-color: #107c10;
            color: white;
        }
        QPushButton#startButton:hover {
            background-color: #0d6b0d;
        }
        QPushButton#startButton:pressed {
            background-color: #0a5a0a;
        }
        QPushButton#terminateButton {
            background-color: #d13438;
            color: white;
        }
        QPushButton#terminateButton:hover {
            background-color: #c02d33;
        }
        QPushButton#terminateButton:pressed {
            background-color: #b0282e;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }

        /* 帮助按钮样式 */
        QPushButton {
            padding: 5px 10px;
        }
        """
        self.setStyleSheet(style)

    def browse_file(self, entry_widget):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4s);;所有文件 (*)"
        )
        if file_path:
            entry_widget.setText(file_path)

    def update_status(self, message, color="blue"):
        colors = {"blue": "blue", "green": "green", "red": "red", "orange": "orange", "black": "black"}
        self.label_status.setText(f"状态: {message}")
        self.label_status.setStyleSheet(f"QLabel#statusLabel {{ color: {colors.get(color, 'black')}; font-style: italic; }}")

    def launch_vcmp(self):
        if self.current_process and self.current_process.state() != QProcess.NotRunning:
            QMessageBox.information(self, "提示", "VCmpTool 已在运行！")
            return

        file1 = self.entry_file1.text().strip()
        file2 = self.entry_file2.text().strip()
        loop_count = self.spin_loop.value()

        if not file1 or not file2:
            QMessageBox.warning(self, "警告", "请先选择两个视频文件！")
            return

        for i, path in enumerate([file1, file2], 1):
            if not os.path.isfile(path):
                QMessageBox.critical(self, "错误", f"文件 {i} 不存在或不是文件：\n{path}")
                return

        cmd = [self.vcmp_executable, file1, file2]
        if loop_count > 1:
            cmd.extend(["-loop", str(loop_count)])
        if self.check_auto_move.isChecked():
            cmd.append("-m")

        print("准备执行命令:")
        print(" ".join(f'"{arg}"' if " " in arg else arg for arg in cmd))

        try:
            self.current_process = QProcess(self)
            self.current_process.finished.connect(lambda code, status: self.process_finished.emit(code))
            
            self.current_process.setWorkingDirectory(os.path.dirname(self.vcmp_executable))
            self.current_process.start(cmd[0], cmd[1:])
            
            if self.current_process.waitForStarted(msecs=2000):
                 self.update_status("运行中...", "green")
                 self.btn_terminate.setEnabled(True)
                 self.btn_start.setEnabled(False)
            else:
                 error_msg = self.current_process.errorString()
                 raise Exception(f"无法启动进程: {error_msg}")

        except Exception as e:
            error_msg = f"启动失败:\n{type(e).__name__}: {e}"
            print(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            self.reset_buttons()
            self.update_status("启动失败", "red")

    def on_process_finished(self, exit_code):
        self.update_status(f"已停止 (返回码: {exit_code})", "blue" if exit_code == 0 else "red")
        self.reset_buttons()
        self.current_process = None

    def terminate_vcmp(self):
        if not self.current_process or self.current_process.state() == QProcess.NotRunning:
            QMessageBox.information(self, "提示", "没有正在运行的 VCmpTool 进程。")
            return

        self.update_status("正在终止...", "orange")
        self.current_process.terminate()
        if not self.current_process.waitForFinished(msecs=3000):
            self.current_process.kill()
            self.current_process.waitForFinished(msecs=1000)
            QMessageBox.warning(self, "已强制结束", "VCmpTool 进程未响应，已强制结束。")
        
    def reset_buttons(self):
        self.btn_start.setEnabled(True)
        self.btn_terminate.setEnabled(False)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    
    font = QFont("Microsoft YaHei", 11)
    app.setFont(font)
    
    try:
        base_path = sys._MEIPASS
    except Exception:
         base_path = os.path.dirname(os.path.abspath(__file__))
         
    icon_path = os.path.join(base_path, "favicon.ico")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    launcher = VCmpLauncher()
    launcher.show()
    sys.exit(app.exec_())




