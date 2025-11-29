import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import sys


class SaveManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("游戏存档SL工具")
        self.root.geometry("600x350")
        self.root.resizable(False, False)

        # 样式设置
        self.font_label = ("Microsoft YaHei", 12)
        self.font_entry = ("Microsoft YaHei", 10)
        self.font_note = ("Microsoft YaHei", 12)
        self.font_btn = ("Microsoft YaHei", 12)

        # 布局容器
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 第一行：游戏存档目录 ---
        row1 = tk.Frame(main_frame)
        row1.pack(fill=tk.X, pady=10)

        tk.Label(row1, text="游戏存档目录", width=12, bg="#d9d9d9", relief="solid",
                 borderwidth=1, font=self.font_label).pack(side=tk.LEFT)
        self.entry_game_path = tk.Entry(
            row1, font=self.font_entry, relief="solid", borderwidth=1)
        self.entry_game_path.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        # 添加一个选择文件夹的按钮，方便操作
        tk.Button(row1, text="...", command=self.select_game_path,
                  width=3).pack(side=tk.LEFT, padx=(5, 0))

        # --- 第二行：存档备份目录 ---
        row2 = tk.Frame(main_frame)
        row2.pack(fill=tk.X, pady=10)

        tk.Label(row2, text="存档备份目录", width=12, bg="#d9d9d9", relief="solid",
                 borderwidth=1, font=self.font_label).pack(side=tk.LEFT)
        self.entry_backup_path = tk.Entry(
            row2, font=self.font_entry, relief="solid", borderwidth=1)
        self.entry_backup_path.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        tk.Button(row2, text="...", command=self.select_backup_path,
                  width=3).pack(side=tk.LEFT, padx=(5, 0))

        # --- 第三行：红色提示语 ---
        tk.Label(main_frame, text="注：使用前最好手动备份一份至非工作目录，防止存档丢失",
                 fg="red", font=self.font_note, pady=20).pack()

        # --- 第四行：功能按钮 ---
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)

        # 按钮样式配置
        btn_style = {"font": self.font_btn, "bg": "#d9d9d9",
                     "relief": "solid", "borderwidth": 1, "height": 2}

        # 备份按钮
        self.btn_backup = tk.Button(
            btn_frame, text="备份当前存档", command=self.backup_save, **btn_style)
        self.btn_backup.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        # 恢复按钮
        self.btn_restore = tk.Button(
            btn_frame, text="恢复备份存档", command=self.restore_save, **btn_style)
        self.btn_restore.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        # 退出按钮
        self.btn_exit = tk.Button(
            btn_frame, text="退出", command=root.quit, **btn_style)
        self.btn_exit.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

    def select_game_path(self):
        path = filedialog.askdirectory(title="选择游戏存档目录")
        if path:
            self.entry_game_path.delete(0, tk.END)
            self.entry_game_path.insert(0, path)

    def select_backup_path(self):
        path = filedialog.askdirectory(title="选择备份存放目录")
        if path:
            self.entry_backup_path.delete(0, tk.END)
            self.entry_backup_path.insert(0, path)

    def get_paths(self):
        """获取并检查路径，同时计算实际的完整路径"""
        game_dir = self.entry_game_path.get().strip()
        backup_root = self.entry_backup_path.get().strip()

        if not game_dir or not backup_root:
            messagebox.showwarning("提示", "请先设置游戏目录和备份目录！")
            return None, None, None

        # 获取游戏存档文件夹的名字 (例如 C:/abc/gameA -> gameA)
        folder_name = os.path.basename(os.path.normpath(game_dir))

        # 构造实际的备份目标路径 (例如 C:/def/gameA)
        target_backup_dir = os.path.join(backup_root, folder_name)

        return game_dir, backup_root, target_backup_dir

    def backup_save(self):
        """备份逻辑：将 game_dir 复制到 target_backup_dir"""
        game_dir, _, target_backup_dir = self.get_paths()
        if not game_dir:
            return

        if not os.path.exists(game_dir):
            messagebox.showerror("错误", f"找不到游戏存档目录：\n{game_dir}")
            return

        try:
            # 如果备份目录里已经有这个游戏的存档，先删除旧备份，确保完全覆盖
            if os.path.exists(target_backup_dir):
                shutil.rmtree(target_backup_dir)

            # 复制整个目录
            shutil.copytree(game_dir, target_backup_dir)
            messagebox.showinfo("成功", f"存档已备份至：\n{target_backup_dir}")
        except Exception as e:
            messagebox.showerror("错误", f"备份失败：\n{str(e)}")

    def restore_save(self):
        """恢复逻辑：将 target_backup_dir 复制回 game_dir"""
        game_dir, _, target_backup_dir = self.get_paths()
        if not game_dir:
            return

        if not os.path.exists(target_backup_dir):
            messagebox.showerror(
                "错误", f"找不到备份文件！\n请检查该路径是否存在：\n{target_backup_dir}")
            return

        # 二次确认，防止误操作
        confirm = messagebox.askyesno("确认恢复", "确定要恢复存档吗？\n当前的游戏进度将被备份文件覆盖！")
        if not confirm:
            return

        try:
            # 如果游戏目录存在，先清空，确保恢复后和备份一模一样（防止有多余文件）
            if os.path.exists(game_dir):
                shutil.rmtree(game_dir)

            # 从备份复制回游戏目录
            shutil.copytree(target_backup_dir, game_dir)
            messagebox.showinfo("成功", "存档已恢复！")
        except Exception as e:
            messagebox.showerror("错误", f"恢复失败：\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SaveManagerApp(root)
    root.mainloop()
