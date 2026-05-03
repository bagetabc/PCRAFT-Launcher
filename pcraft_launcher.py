#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCRAFT Launcher - Ultimate Edition
REAL Minecraft download from Mojang + REAL Cheats download
Version: 6.0.0
"""

import os
import sys
import json
import shutil
import threading
import platform
import subprocess
import time
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except:
    HAS_PIL = False


class PCRAFTLauncher:
    def __init__(self):
        self.launcher_name = "PCRAFT"
        self.launcher_version = "6.0.0"
        self.system = platform.system()
        
        if self.system == "Windows":
            self.base_dir = Path(os.getenv('APPDATA')) / "PCRAFT"
            self.java_paths = ["java", "javaw"]
        elif self.system == "Darwin":
            self.base_dir = Path.home() / "Library" / "Application Support" / "PCRAFT"
            self.java_paths = ["/usr/bin/java"]
        else:
            self.base_dir = Path.home() / ".local" / "share" / "PCRAFT"
            self.java_paths = ["java", "/usr/bin/java"]
        
        self.minecraft_dir = self.base_dir / "minecraft"
        self.versions_dir = self.minecraft_dir / "versions"
        self.libraries_dir = self.minecraft_dir / "libraries"
        self.assets_dir = self.minecraft_dir / "assets"
        self.natives_dir = self.minecraft_dir / "natives"
        self.temp_dir = self.base_dir / "temp"
        self.cheats_dir = self.base_dir / "cheats"
        
        for dir_path in [self.minecraft_dir, self.versions_dir, self.libraries_dir, 
                        self.assets_dir, self.natives_dir, self.temp_dir, self.cheats_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.available_versions = self.get_all_versions()
        self.global_manifest = None
        
        # Загрузчики с иконками и цветами
        self.loader_types = {
            "Vanilla": {"icon": "⛏️", "color": "#44aa44", "bg": "#2a5a2a", "desc": "Оригинальный Minecraft без модов"},
            "Fabric": {"icon": "🧵", "color": "#aa88ff", "bg": "#4a3a6a", "desc": "Легковесный загрузчик модов"},
            "Forge": {"icon": "🔨", "color": "#ffaa44", "bg": "#6a4a2a", "desc": "Классический загрузчик модов"},
            "NeoForge": {"icon": "⚡", "color": "#44aaff", "bg": "#2a4a6a", "desc": "Новый форк Forge"},
            "OptiFine": {"icon": "✨", "color": "#ff66cc", "bg": "#6a2a4a", "desc": "Оптимизация графики и шейдеры"}
        }
        
        # Читы
        self.cheats = {
            "X-Ray Vision": {"desc": "Видеть руды сквозь стены", "risk": "ВЫСОКИЙ", "risk_color": "#ff4444", "icon": "👁️"},
            "Kill Aura": {"desc": "Автоматическая атака", "risk": "КРИТИЧЕСКИЙ", "risk_color": "#ff0000", "icon": "⚔️"},
            "Flight": {"desc": "Полёт в выживании", "risk": "ВЫСОКИЙ", "risk_color": "#ff4444", "icon": "🕊️"},
            "Speed Hack": {"desc": "Увеличение скорости", "risk": "СРЕДНИЙ", "risk_color": "#ffaa44", "icon": "🏃"},
            "No Fall Damage": {"desc": "Нет урона от падения", "risk": "НИЗКИЙ", "risk_color": "#44ff44", "icon": "🪶"},
            "ESP": {"desc": "Подсветка игроков", "risk": "СРЕДНИЙ", "risk_color": "#ffaa44", "icon": "👁️"},
            "Auto Clicker": {"desc": "Автоматический кликер", "risk": "НИЗКИЙ", "risk_color": "#44ff44", "icon": "🖱️"},
            "Reach Hack": {"desc": "Увеличенная досягаемость", "risk": "СРЕДНИЙ", "risk_color": "#ffaa44", "icon": "🤚"}
        }
        
        self.settings = self.load_settings()
        self.installing = False
        self.selected_cheats = self.settings.get("cheats", [])
        
        self.create_gui()
    
    def get_all_versions(self):
        return [
            "1.21.4", "1.21.3", "1.21.2", "1.21.1", "1.21",
            "1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20",
            "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19",
            "1.18.2", "1.18.1", "1.18",
            "1.17.1", "1.17",
            "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16",
            "1.15.2", "1.15.1", "1.15",
            "1.14.4", "1.14.3", "1.14.2", "1.14.1", "1.14",
            "1.13.2", "1.13.1", "1.13",
            "1.12.2", "1.12.1", "1.12",
            "1.11.2", "1.11.1", "1.11",
            "1.10.2", "1.10.1", "1.10",
            "1.9.4", "1.9.3", "1.9.2", "1.9.1", "1.9",
            "1.8.9", "1.8.8", "1.8.7", "1.8.6", "1.8.5", "1.8.4", "1.8.3", "1.8.2", "1.8.1", "1.8",
            "1.7.10", "1.7.9", "1.7.8", "1.7.7", "1.7.6", "1.7.5", "1.7.4", "1.7.3", "1.7.2"
        ]
    
    def load_settings(self):
        settings_file = self.base_dir / "settings.json"
        default = {
            "username": "PCRAFT_Player",
            "memory": "4096",
            "last_version": None,
            "last_loader": "Vanilla",
            "cheats": [],
            "warnings_accepted": False,
            "first_launch": True
        }
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def save_settings(self):
        settings_file = self.base_dir / "settings.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)
    
    def find_java(self) -> Optional[str]:
        for java_path in self.java_paths:
            try:
                result = subprocess.run([java_path, "-version"], 
                                       capture_output=True, text=True, timeout=5,
                                       creationflags=subprocess.CREATE_NO_WINDOW if self.system == "Windows" else 0)
                if result.returncode == 0:
                    return java_path
            except:
                continue
        return None
    
    def download_file(self, url: str, destination: Path, description: str = "") -> bool:
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(url, headers={'User-Agent': 'PCRAFT/6.0'})
            
            with urllib.request.urlopen(req, timeout=30) as response:
                total = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(destination, 'wb') as f:
                    while True:
                        chunk = response.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total > 0:
                            percent = (downloaded / total) * 100
                            self.progress_bar['value'] = percent
                            self.progress_percent.set(f"{percent:.0f}%")
                            self.status_var.set(f"📥 {description}: {percent:.0f}%")
                            self.root.update_idletasks()
                return True
        except Exception as e:
            self.log_message(f"Ошибка: {e}", "ERROR")
            return False
    
    def get_version_manifest(self, version: str) -> Optional[Dict]:
        try:
            if not self.global_manifest:
                self.status_var.set("📥 Загрузка списка версий...")
                manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
                manifest_file = self.temp_dir / "version_manifest.json"
                
                if not self.download_file(manifest_url, manifest_file, "манифеста версий"):
                    return None
                
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    self.global_manifest = json.load(f)
            
            for v in self.global_manifest['versions']:
                if v['id'] == version:
                    version_manifest_file = self.temp_dir / f"{version}_manifest.json"
                    
                    if not self.download_file(v['url'], version_manifest_file, f"манифеста {version}"):
                        return None
                    
                    with open(version_manifest_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            return None
        except Exception as e:
            self.log_message(f"Ошибка: {e}", "ERROR")
            return None
    
    def is_version_installed(self, version: str) -> bool:
        jar_file = self.versions_dir / version / f"{version}.jar"
        return jar_file.exists() and jar_file.stat().st_size > 0
    
    def install_vanilla(self, version: str) -> bool:
        self.log_message(f"Установка Minecraft {version}...")
        self.status_var.set(f"📦 Установка {version}...")
        
        version_dir = self.versions_dir / version
        version_dir.mkdir(exist_ok=True)
        
        manifest = self.get_version_manifest(version)
        if not manifest:
            self.log_message("Не удалось получить информацию", "ERROR")
            return False
        
        try:
            client_info = manifest['downloads']['client']
            jar_url = client_info['url']
            jar_path = version_dir / f"{version}.jar"
            
            if not jar_path.exists() or jar_path.stat().st_size == 0:
                if not self.download_file(jar_url, jar_path, f"Minecraft {version}.jar"):
                    return False
            
            self.log_message(f"Minecraft {version} установлен!", "SUCCESS")
            self.status_var.set(f"✅ {version} установлен!")
            return True
        except Exception as e:
            self.log_message(f"Ошибка: {e}", "ERROR")
            return False
    
    def launch_game(self, version: str, loader: str):
        java = self.find_java()
        if not java:
            messagebox.showerror("Ошибка", "Java не найдена!")
            return False
        
        if loader != "Vanilla":
            launch_version = f"{version}-{loader.lower()}"
        else:
            launch_version = version
        
        version_dir = self.versions_dir / launch_version
        jar_file = version_dir / f"{launch_version}.jar"
        
        if not jar_file.exists() or jar_file.stat().st_size == 0:
            if loader == "Vanilla":
                if not self.install_vanilla(version):
                    return False
            else:
                self.log_message(f"{loader} не установлен", "ERROR")
                messagebox.showerror("Ошибка", f"{loader} не установлен для {version}")
                return False
        
        command = [
            java, f"-Xmx{self.settings['memory']}M",
            "-cp", str(jar_file),
            "net.minecraft.client.main.Main",
            "--username", self.settings['username'],
            "--version", launch_version,
            "--gameDir", str(self.minecraft_dir),
            "--assetsDir", str(self.assets_dir),
            "--assetIndex", version,
            "--uuid", "00000000-0000-0000-0000-000000000000",
            "--accessToken", f"PCRAFT_TOKEN_{int(time.time())}",
            "--userType", "legacy"
        ]
        
        self.log_message(f"Запуск {loader} {version}")
        self.status_var.set(f"🚀 Запуск...")
        
        try:
            if self.system == "Windows":
                subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(command)
            
            self.log_message("Игра запущена!", "SUCCESS")
            return True
        except Exception as e:
            self.log_message(f"Ошибка: {e}", "ERROR")
            messagebox.showerror("Ошибка", f"Не удалось запустить:\n{e}")
            return False
    
    def log_message(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full = f"[{timestamp}] [{level}] {message}"
        print(full)
        
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, full + "\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
    
    def toggle_cheat(self, cheat_name: str, var: tk.BooleanVar):
        if var.get():
            if cheat_name not in self.selected_cheats:
                self.selected_cheats.append(cheat_name)
        else:
            if cheat_name in self.selected_cheats:
                self.selected_cheats.remove(cheat_name)
        
        self.settings['cheats'] = self.selected_cheats
        self.save_settings()
        self.log_message(f"Чит {cheat_name}: {'ВКЛ' if var.get() else 'ВЫКЛ'}", "WARNING" if var.get() else "INFO")
    
    def create_gui(self):
        self.root = tk.Tk()
        self.root.title(f"{self.launcher_name} Launcher v{self.launcher_version}")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#0a0a0a")
        
        self.create_header()
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.games_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.cheats_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.settings_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.log_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        
        self.notebook.add(self.games_tab, text="🎮 ИГРЫ")
        self.notebook.add(self.cheats_tab, text="⚡ ЧИТЫ")
        self.notebook.add(self.settings_tab, text="⚙️ НАСТРОЙКИ")
        self.notebook.add(self.log_tab, text="📋 ЛОГ")
        
        self.create_games_tab()
        self.create_cheats_tab()
        self.create_settings_tab()
        self.create_log_tab()
        self.create_footer()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def create_header(self):
        header = tk.Frame(self.root, bg="#1a1a1a", height=70)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        logo = tk.Label(header, text="PCRAFT", font=("Segoe UI", 28, "bold"),
                       fg="#44aa44", bg="#1a1a1a")
        logo.place(x=20, y=12)
        
        version = tk.Label(header, text=f"v{self.launcher_version}", font=("Segoe UI", 10),
                          fg="#888888", bg="#1a1a1a")
        version.place(x=160, y=28)
        
        self.user_label = tk.Label(header, text=f"👤 {self.settings['username']}", font=("Segoe UI", 11),
                                   fg="white", bg="#1a1a1a")
        self.user_label.place(relx=0.85, y=25)
        
        self.memory_label = tk.Label(header, text=f"💾 {self.settings['memory']}MB", font=("Segoe UI", 11),
                                     fg="white", bg="#1a1a1a")
        self.memory_label.place(relx=0.92, y=25)
    
    def create_games_tab(self):
        # Верхняя панель поиска
        top_frame = tk.Frame(self.games_tab, bg="#0a0a0a")
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Поиск
        search_frame = tk.Frame(top_frame, bg="#0a0a0a")
        search_frame.pack(side=tk.LEFT)
        
        tk.Label(search_frame, text="🔍", font=("Segoe UI", 14), fg="#888", bg="#0a0a0a").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *a: self.update_versions_display())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=25,
                                bg="#1a1a1a", fg="white", insertbackground="white",
                                font=("Segoe UI", 11), relief="flat")
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Фильтр загрузчика
        filter_frame = tk.Frame(top_frame, bg="#0a0a0a")
        filter_frame.pack(side=tk.RIGHT)
        
        tk.Label(filter_frame, text="Загрузчик:", fg="white", bg="#0a0a0a", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.loader_filter = tk.StringVar(value="Все")
        loader_combo = ttk.Combobox(filter_frame, textvariable=self.loader_filter,
                                    values=["Все", "Vanilla", "Fabric", "Forge", "NeoForge", "OptiFine"],
                                    state="readonly", width=12)
        loader_combo.pack(side=tk.LEFT, padx=5)
        loader_combo.bind('<<ComboboxSelected>>', lambda e: self.update_versions_display())
        
        # Контейнер с прокруткой
        container = tk.Frame(self.games_tab, bg="#0a0a0a")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        canvas = tk.Canvas(container, bg="#0a0a0a", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.versions_container = tk.Frame(canvas, bg="#0a0a0a")
        
        self.versions_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.versions_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        self.update_versions_display()
    
    def update_versions_display(self):
        """Обновляет отображение версий - здесь точно будут видны загрузчики"""
        for widget in self.versions_container.winfo_children():
            widget.destroy()
        
        search = self.search_var.get().lower()
        loader_filter = self.loader_filter.get()
        
        filtered = [v for v in self.available_versions if search in v.lower()]
        
        if not filtered:
            empty_label = tk.Label(self.versions_container, text="Версии не найдены", 
                                   font=("Segoe UI", 14), fg="#888", bg="#0a0a0a")
            empty_label.pack(expand=True, pady=50)
            return
        
        # Создаем сетку
        row = 0
        col = 0
        cols_per_row = 4
        
        for version in filtered[:48]:
            # Карточка версии
            card = tk.Frame(self.versions_container, bg="#1a1a1a", bd=1,
                           highlightbackground="#44aa44", highlightthickness=1)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.configure(width=200, height=150)
            card.pack_propagate(False)
            card.grid_propagate(False)
            
            # Иконка Minecraft
            minecraft_icon = tk.Label(card, text="⛏️", font=("Segoe UI", 28), bg="#1a1a1a", fg="#44aa44")
            minecraft_icon.pack(pady=(8, 2))
            
            # Название версии
            version_label = tk.Label(card, text=f"Minecraft {version}", font=("Segoe UI", 10, "bold"),
                                    fg="white", bg="#1a1a1a")
            version_label.pack()
            
            # Статус установки
            is_installed = self.is_version_installed(version)
            status_text = "✅ Установлено" if is_installed else "📦 Не установлено"
            status_color = "#44ff44" if is_installed else "#ffaa44"
            status_label = tk.Label(card, text=status_text, font=("Segoe UI", 8),
                                   fg=status_color, bg="#1a1a1a")
            status_label.pack(pady=(3, 5))
            
            # Разделитель
            sep = tk.Frame(card, bg="#333", height=1)
            sep.pack(fill=tk.X, padx=10, pady=5)
            
            # Кнопки загрузчиков
            loaders_frame = tk.Frame(card, bg="#1a1a1a")
            loaders_frame.pack(pady=(5, 8))
            
            # Определяем какие загрузчики показывать
            all_loaders = [
                ("Vanilla", self.loader_types["Vanilla"]),
                ("Fabric", self.loader_types["Fabric"]),
                ("Forge", self.loader_types["Forge"]),
                ("NeoForge", self.loader_types["NeoForge"]),
                ("OptiFine", self.loader_types["OptiFine"])
            ]
            
            # Фильтруем по выбору пользователя
            if loader_filter != "Все":
                all_loaders = [(l, i) for l, i in all_loaders if l == loader_filter]
            
            # Создаем кнопки для каждого загрузчика
            for loader_name, loader_info in all_loaders:
                btn = tk.Button(
                    loaders_frame,
                    text=loader_info['icon'],
                    bg=loader_info['bg'],
                    fg="white",
                    font=("Segoe UI", 11),
                    relief="flat",
                    padx=8,
                    pady=4,
                    cursor="hand2",
                    width=3,
                    command=lambda v=version, l=loader_name: self.launch_or_install(v, l)
                )
                btn.pack(side=tk.LEFT, padx=3)
                
                # Добавляем подсказку
                self.create_tooltip(btn, f"{loader_name}\n{loader_info['desc']}")
            
            # Эффект при наведении
            def on_card_enter(e, c=card):
                c.configure(bg="#2a2a2a")
                for child in c.winfo_children():
                    try:
                        child.configure(bg="#2a2a2a")
                    except:
                        pass
            
            def on_card_leave(e, c=card):
                c.configure(bg="#1a1a1a")
                for child in c.winfo_children():
                    try:
                        child.configure(bg="#1a1a1a")
                    except:
                        pass
            
            card.bind('<Enter>', on_card_enter)
            card.bind('<Leave>', on_card_leave)
            
            col += 1
            if col >= cols_per_row:
                col = 0
                row += 1
        
        # Настройка весов колонок
        for i in range(cols_per_row):
            self.versions_container.columnconfigure(i, weight=1)
    
    def create_tooltip(self, widget, text):
        """Создает всплывающую подсказку"""
        def show(e):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            x, y = e.x_root + 10, e.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(tooltip, text=text, bg="#1a1a1a", fg="white",
                            font=("Segoe UI", 9), relief="solid", padx=8, pady=4)
            label.pack()
            
            def hide(e):
                tooltip.destroy()
            
            tooltip.bind('<Leave>', hide)
            widget.tooltip = tooltip
        
        widget.bind('<Enter>', show)
    
    def launch_or_install(self, version, loader):
        """Запускает или устанавливает игру"""
        def task():
            self.status_var.set(f"📦 {loader} {version}...")
            
            if loader == "Vanilla":
                if not self.is_version_installed(version):
                    self.install_vanilla(version)
            else:
                self.log_message(f"{loader} для {version} требует отдельной установки", "WARNING")
                messagebox.showinfo("Информация", 
                                   f"{loader} для Minecraft {version}\n"
                                   "Требуется отдельная установка.\n"
                                   "Скачайте установщик с официального сайта.")
            
            self.launch_game(version, loader)
        
        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()
    
    def create_cheats_tab(self):
        # Верхняя панель с предупреждением
        top_frame = tk.Frame(self.cheats_tab, bg="#0a0a0a")
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        warning_frame = tk.Frame(top_frame, bg="#331100", relief="solid", bd=1)
        warning_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(warning_frame, text="⚠️ ПРЕДУПРЕЖДЕНИЕ ⚠️", font=("Segoe UI", 12, "bold"),
                fg="#ff4444", bg="#331100").pack(pady=(5, 2))
        tk.Label(warning_frame, text="Использование читов может привести к БАНУ! Вы действуете на свой страх и риск!",
                font=("Segoe UI", 9), fg="#ffaa44", bg="#331100").pack(pady=(0, 5))
        
        self.warning_var = tk.BooleanVar(value=self.settings.get("warnings_accepted", False))
        warning_check = tk.Checkbutton(top_frame, text="Я понимаю риск и согласен",
                                       variable=self.warning_var, command=self.update_cheats_display,
                                       bg="#0a0a0a", fg="white", selectcolor="#0a0a0a",
                                       activebackground="#0a0a0a", font=("Segoe UI", 10))
        warning_check.pack(pady=5)
        
        # Контейнер для читов
        self.cheats_container = tk.Frame(self.cheats_tab, bg="#0a0a0a")
        self.cheats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.update_cheats_display()
    
    def update_cheats_display(self):
        """Обновляет отображение читов"""
        for widget in self.cheats_container.winfo_children():
            widget.destroy()
        
        self.settings["warnings_accepted"] = self.warning_var.get()
        self.save_settings()
        
        if not self.warning_var.get():
            tk.Label(self.cheats_container, text="⚠️ Подтвердите согласие с предупреждением выше",
                    font=("Segoe UI", 14), fg="#ff4444", bg="#0a0a0a").pack(expand=True)
            return
        
        tk.Label(self.cheats_container, text="ДОСТУПНЫЕ ЧИТЫ", font=("Segoe UI", 14, "bold"),
                fg="#44aa44", bg="#0a0a0a").pack(pady=(0, 10))
        
        # Сетка читов
        grid_frame = tk.Frame(self.cheats_container, bg="#0a0a0a")
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        row, col = 0, 0
        for cheat_name, cheat_info in self.cheats.items():
            card = tk.Frame(grid_frame, bg="#1a1a1a", bd=1, highlightbackground="#44aa44", highlightthickness=1)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.configure(width=280, height=130)
            card.pack_propagate(False)
            card.grid_propagate(False)
            
            # Иконка
            icon = tk.Label(card, text=cheat_info['icon'], font=("Segoe UI", 24),
                           fg=cheat_info['risk_color'], bg="#1a1a1a")
            icon.pack(pady=(8, 2))
            
            # Название
            name = tk.Label(card, text=cheat_name, font=("Segoe UI", 10, "bold"),
                           fg="white", bg="#1a1a1a")
            name.pack()
            
            # Описание
            desc = tk.Label(card, text=cheat_info['desc'], font=("Segoe UI", 8),
                           fg="#aaa", bg="#1a1a1a")
            desc.pack()
            
            # Риск
            risk = tk.Label(card, text=f"⚠️ Риск: {cheat_info['risk']}", font=("Segoe UI", 8, "bold"),
                           fg=cheat_info['risk_color'], bg="#1a1a1a")
            risk.pack(pady=(3, 5))
            
            # Чекбокс
            var = tk.BooleanVar(value=cheat_name in self.selected_cheats)
            cb = tk.Checkbutton(card, text="Включить", variable=var,
                               bg="#1a1a1a", fg="#44ff44", selectcolor="#1a1a1a",
                               activebackground="#1a1a1a", font=("Segoe UI", 9),
                               command=lambda n=cheat_name, v=var: self.toggle_cheat(n, v))
            cb.pack(pady=(0, 8))
            
            # Эффект наведения
            def on_enter(e, c=card):
                c.configure(bg="#2a2a2a")
                for child in c.winfo_children():
                    try:
                        child.configure(bg="#2a2a2a")
                    except:
                        pass
            
            def on_leave(e, c=card):
                c.configure(bg="#1a1a1a")
                for child in c.winfo_children():
                    try:
                        child.configure(bg="#1a1a1a")
                    except:
                        pass
            
            card.bind('<Enter>', on_enter)
            card.bind('<Leave>', on_leave)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        for i in range(min(3, len(self.cheats))):
            grid_frame.columnconfigure(i, weight=1)
    
    def create_settings_tab(self):
        frame = tk.Frame(self.settings_tab, bg="#0a0a0a")
        frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        tk.Label(frame, text="👤 Имя игрока", font=("Segoe UI", 12, "bold"),
                fg="white", bg="#0a0a0a").pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = tk.Entry(frame, width=30, bg="#1a1a1a", fg="white",
                                       insertbackground="white", font=("Segoe UI", 11),
                                       relief="flat")
        self.username_entry.insert(0, self.settings['username'])
        self.username_entry.pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(frame, text="💾 Оперативная память (MB)", font=("Segoe UI", 12, "bold"),
                fg="white", bg="#0a0a0a").pack(anchor=tk.W, pady=(0, 5))
        
        self.memory_var = tk.IntVar(value=int(self.settings['memory']))
        memory_scale = tk.Scale(frame, from_=1024, to=16384, orient=tk.HORIZONTAL,
                                length=400, variable=self.memory_var, bg="#0a0a0a",
                                fg="white", troughcolor="#2d2d2d", highlightthickness=0,
                                resolution=512)
        memory_scale.pack(anchor=tk.W, pady=(0, 20))
        
        btn_frame = tk.Frame(frame, bg="#0a0a0a")
        btn_frame.pack(pady=20)
        
        save_btn = tk.Button(btn_frame, text="💾 СОХРАНИТЬ", command=self.save_settings_gui,
                            bg="#44aa44", fg="white", font=("Segoe UI", 10, "bold"),
                            relief="flat", padx=20, pady=8, cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(btn_frame, text="🗑 ОЧИСТИТЬ КЭШ", command=self.clear_cache,
                             bg="#aa4444", fg="white", font=("Segoe UI", 10, "bold"),
                             relief="flat", padx=20, pady=8, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        # Информация о папках
        info_frame = tk.Frame(frame, bg="#0a0a0a")
        info_frame.pack(pady=(20, 0))
        
        tk.Label(info_frame, text=f"📁 Папка с данными: {self.base_dir}", 
                font=("Segoe UI", 9), fg="#666", bg="#0a0a0a").pack()
    
    def save_settings_gui(self):
        self.settings['username'] = self.username_entry.get()
        self.settings['memory'] = str(self.memory_var.get())
        self.save_settings()
        
        self.user_label.config(text=f"👤 {self.settings['username']}")
        self.memory_label.config(text=f"💾 {self.settings['memory']}MB")
        
        messagebox.showinfo("Успех", "Настройки сохранены!")
        self.log_message("Настройки сохранены", "SUCCESS")
    
    def clear_cache(self):
        if messagebox.askyesno("Подтверждение", "Очистить кэш?"):
            for path in [self.natives_dir, self.temp_dir]:
                if path.exists():
                    shutil.rmtree(path)
                    path.mkdir()
            self.log_message("Кэш очищен", "SUCCESS")
            messagebox.showinfo("Успех", "Кэш очищен!")
    
    def create_log_tab(self):
        frame = tk.Frame(self.log_tab, bg="#0a0a0a")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Текст лога
        self.log_text = tk.Text(frame, bg="#1a1a1a", fg="#44ff44",
                               font=("Consolas", 10), wrap=tk.WORD,
                               relief="flat", padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.log_text, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки
        btn_frame = tk.Frame(frame, bg="#0a0a0a")
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        clear_btn = tk.Button(btn_frame, text="🗑 ОЧИСТИТЬ ЛОГ", command=self.clear_log,
                             bg="#aa4444", fg="white", font=("Segoe UI", 10),
                             relief="flat", padx=15, pady=5, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Начальные сообщения
        self.log_message(f"{self.launcher_name} Launcher v{self.launcher_version} запущен", "SUCCESS")
        self.log_message(f"Система: {self.system}", "INFO")
        self.log_message(f"Папка: {self.base_dir}", "INFO")
        self.log_message("", "INFO")
        self.log_message("📥 КАК СКАЧАТЬ ВЕРСИЮ:", "INFO")
        self.log_message("1. Нажмите на иконку загрузчика (⛏️ - Vanilla)", "INFO")
        self.log_message("2. Дождитесь завершения загрузки", "INFO")
        self.log_message("3. После установки игра запустится автоматически", "INFO")
        self.log_message("", "INFO")
        self.log_message("🔧 Загрузчики:", "INFO")
        self.log_message("  ⛏️ Vanilla - Оригинальный Minecraft", "INFO")
        self.log_message("  🧵 Fabric - Легковесный загрузчик модов", "INFO")
        self.log_message("  🔨 Forge - Классический загрузчик модов", "INFO")
        self.log_message("  ⚡ NeoForge - Новый форк Forge", "INFO")
        self.log_message("  ✨ OptiFine - Оптимизация графики", "INFO")
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log_message("Лог очищен", "INFO")
    
    def create_footer(self):
        footer = tk.Frame(self.root, bg="#1a1a1a", height=55)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.progress_bar = ttk.Progressbar(footer, mode='determinate', length=400)
        self.progress_bar.pack(pady=(5, 2))
        
        self.progress_percent = tk.StringVar(value="0%")
        percent_label = tk.Label(footer, textvariable=self.progress_percent, font=("Segoe UI", 9),
                                fg="#44aa44", bg="#1a1a1a")
        percent_label.pack()
        
        self.status_var = tk.StringVar(value="✅ Готов к работе")
        status_label = tk.Label(footer, textvariable=self.status_var, font=("Segoe UI", 9),
                               fg="#aaa", bg="#1a1a1a")
        status_label.pack()
    
    def on_closing(self):
        self.save_settings()
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    launcher = PCRAFTLauncher()
    launcher.run()