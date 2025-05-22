import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
import networkx as nx
import matplotlib.pyplot as plt
from openai import OpenAI
import threading
import sqlite3
import random
import string
import json 
import math
import pandas as pd

# 设置全局中文字体
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


class AIAssistant:
    def __init__(self):
        self.key = 'sk-434b86347128483585c50e8905047166'
        self.api_url = "https://api.deepseek.com"
        self.client = OpenAI(api_key=self.key, base_url=self.api_url)
        self.is_responding = False
        self.model ='deepseek-chat'
        self.model_mapping = {  # 模型名称与指令的映射
            'deepseekV3': 'deepseek-chat',
            'deepseekR1': 'deepseek-reasoner'
             }
    def set_model(self, model_name):
        if model_name not in self.model_mapping:
            raise ValueError(f"无效的模型名称: {model_name}")
        self.model = self.model_mapping[model_name]  # 更新为对应的模型指令

    def get_response(self, query, callback):
        def ai_task():
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "我是智能AI,能够解答各种问题，有什么可以帮助你的？"},
                        {"role": "user", "content": query},
                    ],
                    stream=False
                )
                callback(response.choices[0].message.content, error=None)
            except Exception as e:
                callback(None, error=str(e))
        
        thread = threading.Thread(target=ai_task)
        thread.start()

class KnowledgeGraphApp:
    def __init__(self, root):
        self.assistant = AIAssistant()
        self.root = root
        self.root.title("上海华强AI助手")
        self.current_frame = None
        self.login_attempts = 0
        self.config_file = "config.json"
        self.background_image_path = self.load_config().get("background_image_path", "C:/Users/31240/Desktop/python/1.png")
    

        # 初始化数据库
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (username TEXT PRIMARY KEY,
                             password TEXT,
                             security_question TEXT,
                             security_answer TEXT)''')
        self.conn.commit()

        # 设置全局样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 12), padding=6)
        self.style.configure("TLabel", font=("微软雅黑", 12), background="#f0f0f0")
        self.style.configure("Title.TLabel", font=("微软雅黑", 20, "bold"), background="#f0f0f0", foreground="#2E86C1")

        self.show_welcome_screen()

    def show_welcome_screen(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        try:
            img = Image.open(self.background_image_path)
            img = img.resize((1200, 900), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=photo, bg="#f0f0f0")
            label.image = photo
            label.pack()
        except Exception as e:
            print(f"图片加载失败: {str(e)}")

        self.root.after(3000, self.show_login_screen)
        self.switch_frame(frame)

    def generate_captcha(self):
        characters = string.digits + string.ascii_uppercase
        self.captcha_code = ''.join(random.choices(characters, k=4))

    def show_login_screen(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

    # 添加背景图片
        try:
            img = Image.open("C:/Users/31240/Desktop/python/2.png")
            img = img.resize((1200, 900), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=photo, bg="#f0f0f0")
            label.image = photo  # 防止图片被垃圾回收
            label.place(x=0, y=0, relwidth=1, relheight=1)  # 设置背景图片填充整个窗口
        except Exception as e:
            print(f"图片加载失败: {str(e)}")

        self.generate_captcha()
    
    # 登录框容器
        login_frame = tk.Frame(frame, bg="#FFFFFF")
        login_frame.pack(expand=True, anchor="center")  # 自动居中



    # 登录界面标题
        tk.Label(login_frame, text="用户登录", font=("微软雅黑", 20, "bold"), bg="#FFFFFF", fg="#2E86C1").pack(pady=20)

    # 账号输入
        ttk.Label(login_frame, text="账号:", background="#FFFFFF").pack(pady=5)
        self.username_entry = ttk.Entry(login_frame, font=("微软雅黑", 12))
        self.username_entry.pack(pady=5)

    # 密码输入
        ttk.Label(login_frame, text="密码:", background="#FFFFFF").pack(pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*", font=("微软雅黑", 12))
        self.password_entry.pack(pady=5)

    # 验证码
        captcha_frame = tk.Frame(login_frame, bg="#FFFFFF")
        captcha_frame.pack(pady=10)
        ttk.Label(captcha_frame, text="验证码:", background="#FFFFFF").pack( pady=5)
        self.captcha_entry = ttk.Entry(captcha_frame, font=("微软雅黑", 12))
        self.captcha_entry.pack( padx=5)
        self.captcha_label = ttk.Label(captcha_frame, text=self.captcha_code, font=("Courier", 14), foreground="blue", background="#FFFFFF")
        self.captcha_label.pack(side="left",padx=10)
        ttk.Button(captcha_frame, text="刷新", command=self.refresh_captcha).pack(side="left", padx=5,pady=1)

    # 功能按钮
        btn_frame = tk.Frame(login_frame, bg="#FFFFFF")
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="登录", command=self.handle_login).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="注册", command=self.show_register_screen).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="忘记密码", command=self.show_forgot_password).pack(side="left", padx=10)
        

        self.switch_frame(frame)

    def refresh_captcha(self):
        self.generate_captcha()
        self.captcha_label.config(text=self.captcha_code)

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        captcha = self.captcha_entry.get().upper()

        if not all([username, password, captcha]):
            messagebox.showerror("错误", "请填写所有字段")
            return

        if captcha != self.captcha_code:
            messagebox.showerror("错误", "验证码错误")
            self.refresh_captcha()
            return

        self.cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("错误", "用户不存在")
            self.login_attempts += 1
        elif result[0] != password:
            messagebox.showerror("错误", "密码错误")
            self.login_attempts += 1
        else:
            self.login_attempts = 0
            self.show_main_menu()
            return

        if self.login_attempts >= 3:
            messagebox.showinfo("提示", "您已连续输错3次，请通过忘记密码重置")
            self.show_forgot_password()

    def show_register_screen(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="新用户注册", style="Title.TLabel").pack(pady=20)

        ttk.Label(frame, text="账号:").pack(pady=5)
        self.register_username_entry = ttk.Entry(frame, font=("微软雅黑", 12))
        self.register_username_entry.pack(pady=5)

        ttk.Label(frame, text="密码:").pack(pady=5)
        self.register_password_entry = ttk.Entry(frame, show="*", font=("微软雅黑", 12))
        self.register_password_entry.pack(pady=5)

        ttk.Label(frame, text="确认密码:").pack(pady=5)
        self.register_confirm_entry = ttk.Entry(frame, show="*", font=("微软雅黑", 12))
        self.register_confirm_entry.pack(pady=5)

        ttk.Label(frame, text="安全问题:").pack(pady=5)
        self.register_question_entry = ttk.Entry(frame, font=("微软雅黑", 12))
        self.register_question_entry.pack(pady=5)

        ttk.Label(frame, text="答案:").pack(pady=5)
        self.register_answer_entry = ttk.Entry(frame, font=("微软雅黑", 12))
        self.register_answer_entry.pack(pady=5)

        ttk.Button(frame, text="提交注册", command=self.submit_register).pack(pady=10)
        ttk.Button(frame, text="返回登录", command=self.show_login_screen).pack(pady=10)

        self.switch_frame(frame)

    def submit_register(self):
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()
        confirm_password = self.register_confirm_entry.get()
        question = self.register_question_entry.get()
        answer = self.register_answer_entry.get()

        if password != confirm_password:
            messagebox.showerror("错误", "两次密码输入不一致")
            return

        try:
            self.cursor.execute("INSERT INTO users VALUES (?,?,?,?)",
                                (username, password, question, answer))
            self.conn.commit()
            messagebox.showinfo("成功", "注册成功")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "用户名已存在")

    def show_forgot_password(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="密码重置", style="Title.TLabel").pack(pady=20)

        ttk.Label(frame, text="账号:").pack(pady=5)
        self.forgot_username_entry = ttk.Entry(frame, font=("微软雅黑", 12))
        self.forgot_username_entry.pack(pady=5)

        ttk.Label(frame, text="安全问题:").pack(pady=5)
        self.forgot_question_label = ttk.Label(frame, text="", font=("微软雅黑", 12))
        self.forgot_question_label.pack(pady=5)

        ttk.Label(frame, text="答案:").pack(pady=5)
        self.forgot_answer_entry = ttk.Entry(frame, font=("微软雅黑", 12))
        self.forgot_answer_entry.pack(pady=5)

        ttk.Label(frame, text="新密码:").pack(pady=5)
        self.forgot_new_password_entry = ttk.Entry(frame, show="*", font=("微软雅黑", 12))
        self.forgot_new_password_entry.pack(pady=5)

        ttk.Button(frame, text="获取安全问题", command=self.get_security_question).pack(pady=10)
        ttk.Button(frame, text="重置密码", command=self.reset_password).pack(pady=10)
        ttk.Button(frame, text="返回登录", command=self.show_login_screen).pack(pady=10)

        self.switch_frame(frame)

    def get_security_question(self):
        username = self.forgot_username_entry.get()
        self.cursor.execute("SELECT security_question FROM users WHERE username=?", (username,))
        result = self.cursor.fetchone()
        self.forgot_question_label.config(text=result[0] if result else "用户不存在")

    def reset_password(self):
        username = self.forgot_username_entry.get()
        answer = self.forgot_answer_entry.get()
        new_password = self.forgot_new_password_entry.get()

        self.cursor.execute("SELECT security_answer FROM users WHERE username=?", (username,))
        result = self.cursor.fetchone()

        if result and answer == result[0]:
            self.cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
            self.conn.commit()
            messagebox.showinfo("成功", "密码已重置")
            self.show_login_screen()
        else:
            messagebox.showerror("错误", "答案不正确")

    def switch_frame(self, new_frame):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = new_frame

    def show_main_menu(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        label = tk.Label(frame, text="华强AI专家助手", font=("微软雅黑", 24), fg="#2E86C1", bg="#f0f0f0")
        label.pack(pady=30)

        buttons = [
            ("华强AI", self.show_qa_screen),
            ("化工工具箱", self.show_suo_menu),  # 新增按钮
            ("工艺计算", self.show_gongyi_screen),
            ("系统设置", self.show_settings_screen),
            ("返回登录", self.show_login_screen),
            ("退出系统", self.root.quit)
        ]

        for text, command in buttons:
            btn = ttk.Button(frame, text=text, command=command, style="TButton")
            btn.pack(pady=15, ipadx=25, ipady=8)

        self.switch_frame(frame)

    def show_suo_menu(self):
       frame = tk.Frame(self.root, bg="#f0f0f0")
       frame.pack(fill="both", expand=True)

    # 标题（相对定位居中）
       label = tk.Label(frame, text="化工工具箱", font=("微软雅黑", 24), fg="#2E86C1", bg="#f0f0f0")
       label.place(relx=0.5, rely=0.05, anchor="center")  # 水平居中，垂直20%位置

    # 加载图标
       gas_icon = tk.PhotoImage(file="C:/Users/31240/Desktop/python/4.png")  # 替换为你的图标路径
       dust_icon = tk.PhotoImage(file="C:/Users/31240/Desktop/python/5.png")  # 替换为你的图标路径
       unit_icon = tk.PhotoImage(file="C:/Users/31240/Desktop/python/3.png")  # 替换为你的图标路径

    # 气体按钮（左下四分之一区域）
       btn1 = ttk.Button(frame, text="气体爆炸极限", image=gas_icon, compound="top", command=self.show_search1_screen, style="TButton")
       btn1.image = gas_icon  # 防止图标被垃圾回收
       btn1.place(relx=0.1, rely=0.2, anchor="nw")  # 水平30%，垂直中点，左下锚点

    # 粉尘按钮（右下四分之一区域）
       btn2 = ttk.Button(frame, text="粉尘爆炸极限", image=dust_icon, compound="top", command=self.show_search2_screen, style="TButton")
       btn2.image = dust_icon  # 防止图标被垃圾回收
       btn2.place(relx=0.3, rely=0.2, anchor="nw")  # 水平70%，垂直中点，右下锚点

    # 单位换算工具按钮
       btn3 = ttk.Button(frame, text="单位换算工具", image=unit_icon, compound="top", command=self.show_danweihuansuan_menu, style="TButton")
       btn3.image = unit_icon  # 防止图标被垃圾回收
       btn3.place(relx=0.5, rely=0.2, anchor="nw")

    # 返回按钮（底部居中）
       return_btn = ttk.Button(frame, text="返回主菜单", command=self.show_main_menu)
       return_btn.pack(side="bottom", pady=10)  # 水平居中，垂直90%位置

       self.switch_frame(frame)
    
    def show_gongyi_screen(self):
       frame = tk.Frame(self.root, bg="#f0f0f0")
       frame.pack(fill="both", expand=True)

    # 标题（相对定位居中）
       label = tk.Label(frame, text="工艺计算软件", font=("微软雅黑", 24), fg="#2E86C1", bg="#f0f0f0")
       label.place(relx=0.5, rely=0.05, anchor="center")  # 水平居中，垂直20%位置

    # 加载图标
       gas_icon = tk.PhotoImage(file="C:/Users/31240/Desktop/python/6.png")  # 替换为你的图标路径

    # 格栅计算软件按钮（左下四分之一区域）
       btn1 = ttk.Button(frame, text="格栅计算软件", image=gas_icon, compound="top", command=self.show_格栅_screen, style="TButton")
       btn1.image = gas_icon  # 防止图标被垃圾回收
       btn1.place(relx=0.1, rely=0.2, anchor="nw")  # 水平30%，垂直中点，左下锚点


    # 返回按钮（底部居中）
       return_btn = ttk.Button(frame, text="返回主菜单", command=self.show_main_menu)
       return_btn.pack(side="bottom", pady=10)  # 水平居中，垂直90%位置

       self.switch_frame(frame)   

    def show_settings_screen(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="系统设置", style="Title.TLabel").pack(pady=20)

        ttk.Label(frame, text="背景图片路径:").pack(pady=5)
        self.bg_path_entry = ttk.Entry(frame, font=("微软雅黑", 12), width=50)
        self.bg_path_entry.insert(0, self.background_image_path)
        self.bg_path_entry.pack(pady=5)

        ttk.Button(frame, text="选择文件", command=self.select_background_image).pack(pady=5)
        ttk.Button(frame, text="保存设置", command=self.save_settings).pack(pady=10)
        ttk.Button(frame, text="返回主菜单", command=self.show_main_menu).pack(pady=10)

        self.switch_frame(frame)

    def select_background_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.bg_path_entry.delete(0, tk.END)
            self.bg_path_entry.insert(0, file_path)

    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def save_config(self):
        config = {"background_image_path": self.background_image_path}
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def save_settings(self):
        new_path = self.bg_path_entry.get()
        if new_path:
            self.background_image_path = new_path
            self.save_config()  # 保存到配置文件
            messagebox.showinfo("成功", "背景图片路径已更新")
        else:
            messagebox.showerror("错误", "路径不能为空")

    def show_qa_screen(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        input_frame = tk.Frame(frame, bg="#f0f0f0")
        input_frame.pack(pady=20, fill="x")

        # 添加模型选择下拉菜单
        model_label = ttk.Label(input_frame, text="选择模型:", font=("微软雅黑", 12))
        model_label.pack(side="left", padx=5)

        self.model_var = tk.StringVar(value='deepseekV3')
        model_selector = ttk.Combobox(input_frame, textvariable=self.model_var, state="readonly", font=("微软雅黑", 12))
        model_selector['values'] = ['deepseekV3', 'deepseekR1']  # 模型选项
        model_selector.pack(side="left", padx=5)
        model_selector.bind("<<ComboboxSelected>>", self.update_model)

        self.entry = ttk.Entry(input_frame, width=50, font=("微软雅黑", 12))
        self.entry.pack(side="left", padx=10)
        self.entry.bind("<Return>", lambda event: self.start_qa_thread())

        btn_ask = ttk.Button(input_frame, text="提问", command=self.start_qa_thread)
        btn_ask.pack(side="left", padx=10)

        self.answer_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("微软雅黑", 12), padx=15, pady=15, height=15)
        self.answer_area.pack(fill="both", expand=True, padx=20)
        self.answer_area.config(state=tk.DISABLED)

        self.answer_area.tag_configure("user", justify="right", foreground="blue")
        self.answer_area.tag_configure("assistant", justify="left", foreground="green")
        self.answer_area.tag_configure("system", justify="center", foreground="gray")
        self.answer_area.tag_configure("error", justify="center", foreground="red")

        btn_frame = tk.Frame(frame, bg="#f0f0f0")
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="清空记录", command=self.clear_history).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="返回主菜单", command=self.show_main_menu).pack(side="left", padx=10)

        self.switch_frame(frame)

    def update_model(self, event):
        selected_model = self.model_var.get()
        
        self.assistant.set_model(selected_model)
        

    def start_qa_thread(self):
        if self.assistant.is_responding:
            return
        query = self.entry.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入问题内容")
            return
        
        self.entry.delete(0, tk.END)
        self.assistant.is_responding = True
        self.update_answer(f"【用户】{query}\n", tag="user")
        self.update_answer("【系统】正在思考，请稍候...\n\n", tag="system")
        self.entry.config(state=tk.DISABLED)
        self.assistant.get_response(query, self.handle_ai_response)

    def handle_ai_response(self, answer, error):
        self.assistant.is_responding = False
        self.entry.config(state=tk.NORMAL)
        
        if error:
            self.update_answer(f"【错误】{error}\n", tag="error")
            return
        
        self.update_answer("【DandD】\n", tag="assistant")
        self.typewriter_effect(answer + "\n\n")

    def update_answer(self, text, tag="normal"):
        self.answer_area.config(state=tk.NORMAL)
        self.answer_area.insert(tk.END, text, tag)
        self.answer_area.see(tk.END)
        self.answer_area.config(state=tk.DISABLED)

    def typewriter_effect(self, text):
        def add_char(i=0):
            if i < len(text):
                char = text[i]
                self.answer_area.config(state=tk.NORMAL)
                self.answer_area.insert(tk.END, char)
                self.answer_area.see(tk.END)
                self.answer_area.config(state=tk.DISABLED)
                self.root.after(50, add_char, i+1)
        add_char()

    def clear_history(self):
        self.answer_area.config(state=tk.NORMAL)
        self.answer_area.delete(1.0, tk.END)
        self.answer_area.config(state=tk.DISABLED)
    
#-------------------------------------------气体爆炸极限-----------------------------------------------------

    def show_search1_screen(self):
        """显示化学品搜索界面"""
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="气体爆炸极限", style="Title.TLabel").pack(pady=20)

        # 搜索框
        ttk.Label(frame, text="搜索关键词:").pack(pady=5)
        self.search_entry = ttk.Entry(frame, font=("微软雅黑", 12), width=50)
        self.search_entry.pack(pady=5)
 
        # 绑定双回车键（兼容主键盘和小键盘）
        self.search_entry.bind("<Return>", lambda event: self.perform_search1())  # 
        self.search_entry.bind("<KP_Enter>", lambda event: self.perform_search1())  # 

        # 搜索按钮
        ttk.Button(frame, text="搜索", command=self.perform_search1).pack(pady=10)

        # 搜索结果显示区域
        self.result_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("微软雅黑", 12), padx=15, pady=15, height=15)
        self.result_area.pack(fill="both", expand=True, padx=20)
        self.result_area.config(state=tk.DISABLED)

        # 返回主菜单按钮
        ttk.Button(frame, text="返回", command=self.show_suo_menu).pack(pady=10)

        self.switch_frame(frame)

    def perform_search1(self):
        """执行搜索功能"""
        # 硬编码的 Excel 文件路径
        file_path = "C:/Users/31240/Desktop/python/气体爆炸极限.xlsx"
        keyword = self.search_entry.get().strip()

        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return

        try:
            # 加载Excel数据
            df = self.load_excel_data1(file_path)
            # 搜索化学品
            results = self.search_chemical1(df, keyword)
            # 显示结果
            self.display_results1(results)
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败: {str(e)}")

    def load_excel_data1(self, file_path):
        """读取Excel数据并预处理"""
        df = pd.read_excel(file_path, sheet_name='Sheet1', header=2)
        df.columns = ['序号', '名称', '化学式', 'LEL', 'UEL', '毒性']
        df['毒性'] = df['毒性'].fillna('无')
        return df

    def search_chemical1(self, df, keyword):
        """执行搜索功能"""
        mask = df['名称'].str.contains(keyword, case=False) | df['化学式'].str.contains(keyword, case=False)
        results = df[mask]
        output = []
        for _, row in results.iterrows():
            item = {
                "名称": row['名称'],
                "化学式": row['化学式'],
                "爆炸极限": f"下限：{row['LEL']}%，上限：{row['UEL']}%",
                "毒性": row['毒性']
            }
            output.append(item)
        return output

    def display_results1(self, results):
        """显示搜索结果"""
        self.result_area.config(state=tk.NORMAL)
        self.result_area.delete(1.0, tk.END)
        if not results:
            self.result_area.insert(tk.END, "未找到相关化学品。\n")
        else:
            for item in results:
                self.result_area.insert(tk.END, f"""
                名称：{item['名称']}
                化学式：{item['化学式']}
                爆炸极限：{item['爆炸极限']}
                毒性：{item['毒性']}
                """)
        self.result_area.config(state=tk.DISABLED)

#-------------------------------------------气体爆炸极限-----------------------------------------------------

#-------------------------------------------粉尘爆炸极限-----------------------------------------------------

    def show_search2_screen(self):
        """显示化学品搜索界面"""
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="粉尘爆炸极限", style="Title.TLabel").pack(pady=20)

        # 搜索框
        ttk.Label(frame, text="搜索关键词:").pack(pady=5)
        self.search_entry = ttk.Entry(frame, font=("微软雅黑", 12), width=50)
        self.search_entry.pack(pady=5)
        
        # 绑定双回车键（兼容主键盘和小键盘）
        self.search_entry.bind("<Return>", lambda event: self.perform_search2())  # 
        self.search_entry.bind("<KP_Enter>", lambda event: self.perform_search2())  # 

        # 搜索按钮
        ttk.Button(frame, text="搜索", command=self.perform_search2).pack(pady=10)

        # 搜索结果显示区域
        self.result_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("微软雅黑", 12), padx=15, pady=15, height=15)
        self.result_area.pack(fill="both", expand=True, padx=20)
        self.result_area.config(state=tk.DISABLED)

        # 返回主菜单按钮
        ttk.Button(frame, text="返回", command=self.show_suo_menu).pack(pady=10)

        self.switch_frame(frame)

    def perform_search2(self):
        """执行搜索功能"""
        # 硬编码的 Excel 文件路径
        file_path = "C:/Users/31240/Desktop/python/粉尘爆炸极限.xlsx"
        keyword = self.search_entry.get().strip()

        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return

        try:
            # 加载Excel数据
            df = self.load_excel_data2(file_path)
            # 搜索化学品
            results = self.search_chemical2(df, keyword)
            # 显示结果
            self.display_results2(results)
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败: {str(e)}")

    def load_excel_data2(self, file_path):
        """读取Excel数据并预处理"""
        df = pd.read_excel(file_path, sheet_name='Sheet1', header=4)
        df.columns = ['粉尘种类', '名称', '爆炸下限', '自燃点']
        return df

    def search_chemical2(self, df, keyword):
        """执行搜索功能"""
        mask = df['名称'].str.contains(keyword, case=False)
        results = df[mask]
        output = []
        for _, row in results.iterrows():
            item = {
                "粉尘种类": row['粉尘种类'],
                "名称": row['名称'],
                "爆炸下限": row['爆炸下限'],
                "自燃点": row['自燃点']
            }
            output.append(item)
        return output

    def display_results2(self, results):
        """显示搜索结果"""
        self.result_area.config(state=tk.NORMAL)
        self.result_area.delete(1.0, tk.END)
        if not results:
            self.result_area.insert(tk.END, "未找到相关化学品。\n")
        else:
            for item in results:
                self.result_area.insert(tk.END, f"""
                名称: {item['名称']}
                爆炸下限: {item['爆炸下限']}
                自燃点: {item['自燃点']}
                """)
        self.result_area.config(state=tk.DISABLED)

#-------------------------------------------粉尘爆炸极限-----------------------------------------------------

#-------------------------------------------------------------------------------------------------------单位换算工具-----------------------------------------------------------------------------------------------------------------

    def show_danweihuansuan_menu(self):
      frame = tk.Frame(self.root, bg="#f0f0f0")
      frame.pack(fill="both", expand=True)

    # 标题（相对定位居中）
      label = tk.Label(frame, text="单位换算工具", font=("微软雅黑",24), fg="#2E86C1", bg="#f0f0f0")
      label.place(relx=0.5, rely=0.05, anchor="center")  # 水平居中，垂直20%位置

    # 长度单位转换器按钮
      btn1 = ttk.Button(frame, text="长度单位", command=self.show_length_converter,
                     style="TButton", width=18,padding=(0, 15))
      btn1.place(relx=0.1, rely=0.2, anchor="nw")  # 水平30%，垂直中点，左下锚点
   
    # 面积单位转换器按钮
      btn1 = ttk.Button(frame, text="面积单位", command=self.show_mianji_converter,
                     style="TButton", width=18,padding=(0, 15))
      btn1.place(relx=0.3, rely=0.2, anchor="nw")  # 水平30%，垂直中点，左下锚点

    # 返回按钮（底部居中）
      return_btn = ttk.Button(frame, text="返回", command=self.show_suo_menu)
      return_btn.pack(side="bottom", pady=10)  # 水平居中，垂直90%位置

      self.switch_frame(frame)

#-------------------------------------------------------------------------------------------------------单位换算工具-----------------------------------------------------------------------------------------------------------------

#-------------------------------------------长度单位换算-----------------------------------------------------
    def show_length_converter(self):     
         
    # 主框架
       frame = tk.Frame(self.root, bg="#f0f0f0")
       frame.pack(fill="both", expand=True)

    # 标题
       label = tk.Label(frame, text="长度单位换算", font=("微软雅黑", 24, "bold"), fg="#2E86C1", bg="#f0f0f0")
       label.pack(pady=20)

    # 输入部分
       input_frame = tk.Frame(frame, bg="#f0f0f0")
       input_frame.pack(pady=100)

       tk.Label(input_frame, text="输入值：", font=("微软雅黑", 18), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")
       entry_input = ttk.Entry(input_frame, width=15)  # 设置宽度为20，高度为5行
       entry_input.grid(row=0, column=1, padx=5, pady=5)

       units = ["千米", "米", "分米", "厘米","毫米","微米","纳米", "英尺", "英寸"]
       combo_from = ttk.Combobox(input_frame, values=units, width=10, state="readonly")
       combo_from.grid(row=0, column=2, padx=5, pady=5)
       combo_from.current(0)

    # 转换箭头
       arrow_label = tk.Label(frame, text="→", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#2E86C1")
       arrow_label.pack(pady=10)

    # 输出部分
       output_frame = tk.Frame(frame, bg="#f0f0f0")
       output_frame.pack(pady=100)

       tk.Label(output_frame, text="输出值：", font=("微软雅黑", 18), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")

       combo_to = ttk.Combobox(output_frame, values=units, width=10, state="readonly")
       combo_to.grid(row=0, column=2, padx=5, pady=5)
       combo_to.current(1)

       output_var = tk.StringVar()
       output_label = tk.Label(output_frame, textvariable=output_var, width=10, relief="sunken", padx=5, bg="#ffffff", font=("微软雅黑", 12))
       output_label.grid(row=0, column=1, padx=5, pady=5)


# 转换逻辑
       def auto_convert(*args):
         try:
            value = float(entry_input.get())
            from_unit = combo_from.get()
            to_unit = combo_to.get()

        # 简单的单位转换逻辑（示例）
            conversion_factors = {
            "千米": 1000,
            "米": 1,
            "分米": 0.1,
            "厘米": 0.01,
            "毫米": 0.001,
            "微米": 0.000001,
            "纳米": 0.000000001,
            "英尺": 0.3048,
            "英寸": 0.0254
        }

            result = value * conversion_factors[from_unit] / conversion_factors[to_unit]
            output_var.set(f"{result:.3e}")
         except ValueError:
            output_var.set("输入无效")
     # 绑定事件
       entry_input.bind("<KeyRelease>", lambda event: auto_convert())
       combo_from.bind("<<ComboboxSelected>>", auto_convert)
       combo_to.bind("<<ComboboxSelected>>", auto_convert)


    # 返回按钮
       return_button = ttk.Button(frame, text="返回", command=self.show_danweihuansuan_menu)
       return_button.pack(side="bottom",pady=10)

    # 切换到新框架
       self.switch_frame(frame)
#-------------------------------------------长度单位换算-----------------------------------------------------

#-------------------------------------------面积单位换算-----------------------------------------------------
    def show_mianji_converter(self):     
         
    # 主框架
       frame = tk.Frame(self.root, bg="#f0f0f0")
       frame.pack(fill="both", expand=True)

    # 标题
       label = tk.Label(frame, text="面积单位换算", font=("微软雅黑", 24, "bold"), fg="#2E86C1", bg="#f0f0f0")
       label.pack(pady=20)

    # 输入部分
       input_frame = tk.Frame(frame, bg="#f0f0f0")
       input_frame.pack(pady=100)

       tk.Label(input_frame, text="输入值：", font=("微软雅黑", 18), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")
       entry_input = ttk.Entry(input_frame, width=15)  # 设置宽度为20，高度为5行
       entry_input.grid(row=0, column=1, padx=5, pady=5)

       units = ["平方米",  "平方分米", "平方厘米","平方毫米","顷","亩"]
       combo_from = ttk.Combobox(input_frame, values=units, width=10, state="readonly")
       combo_from.grid(row=0, column=2, padx=5, pady=5)
       combo_from.current(0)

    # 转换箭头
       arrow_label = tk.Label(frame, text="→", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#2E86C1")
       arrow_label.pack(pady=10)

    # 输出部分
       output_frame = tk.Frame(frame, bg="#f0f0f0")
       output_frame.pack(pady=100)

       tk.Label(output_frame, text="输出值：", font=("微软雅黑", 18), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="e")

       combo_to = ttk.Combobox(output_frame, values=units, width=10, state="readonly")
       combo_to.grid(row=0, column=2, padx=5, pady=5)
       combo_to.current(1)

       output_var = tk.StringVar()
       output_label = tk.Label(output_frame, textvariable=output_var, width=10, relief="sunken", padx=5, bg="#ffffff", font=("微软雅黑", 12))
       output_label.grid(row=0, column=1, padx=5, pady=5)


# 转换逻辑
       def auto_convert(*args):
         try:
            value = float(entry_input.get())
            from_unit = combo_from.get()
            to_unit = combo_to.get()

        # 简单的单位转换逻辑（示例）
            conversion_factors = {
            "平方米": 1,
            "平方分米": 0.01,
            "平方厘米": 0.0001,
            "平方毫米": 0.000001,
            "顷": 66666.7,
            "亩":  666.667,
        }

            result = value * conversion_factors[from_unit] / conversion_factors[to_unit]
            output_var.set(f"{result:.3e}")
         except ValueError:
            output_var.set("输入无效")
     # 绑定事件
       entry_input.bind("<KeyRelease>", lambda event: auto_convert())
       combo_from.bind("<<ComboboxSelected>>", auto_convert)
       combo_to.bind("<<ComboboxSelected>>", auto_convert)


    # 返回按钮
       return_button = ttk.Button(frame, text="返回", command=self.show_danweihuansuan_menu)
       return_button.pack(side="bottom",pady=10)

    # 切换到新框架
       self.switch_frame(frame)
#-------------------------------------------面积单位换算-----------------------------------------------------

    def show_格栅_screen(self):
        """显示格栅计算界面"""
        # 创建一个新的框架用于格栅计算
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)

        # 嵌入 GrilleDesignApp 的功能
        class GrilleDesignApp:
            def __init__(self, parent, back_to_gongyi_screen):
                self.parent = parent
                self.back_to_gongyi_screen = back_to_gongyi_screen  # 保存返回方法
                self.entries = {}  # 统一初始化参数存储字典
                
                # 创建主容器
                self.main_frame = ttk.Frame(parent)
                self.main_frame.pack(fill="both", expand=True)
                
                # 创建两个界面：输入界面和结果界面
                self.input_frame = ttk.Frame(self.main_frame)
                self.result_frame = ttk.Frame(self.main_frame)
                
                # 默认显示输入界面
                self.input_frame.pack(fill="both", expand=True)
                self.result_frame = ttk.Frame(self.main_frame)
                
                # ========== 输入界面 ==========
                # 输入参数区域
                input_container = ttk.LabelFrame(self.input_frame, text="设计参数输入")
                input_container.pack(fill="x", padx=10, pady=10)
                
                # 使用网格布局填充整个 x 轴
                input_container.columnconfigure(0, weight=1)
                input_container.columnconfigure(1, weight=1)
                input_container.columnconfigure(2, weight=1)
                
                # 左列参数
                left_col = ttk.Frame(input_container)
                left_col.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
                self.create_entries(left_col, [
                    ("最大设计流量Qmax(m³/s)", "Q_max"),
                    ("格栅倾角alpha(度)", "alpha"),
                    ("栅条间隙宽度b(m)", "b"),
                    ("栅前水深h(m)", "h"),
                    ("过栅流速v(m/s)", "v"),
                    ("栅条宽度S(m)", "S"),
                    ("进水渠宽B1(m)", "B1")
                ])
                
                # 中列参数
                middle_col = ttk.Frame(input_container)
                middle_col.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
                self.create_entries(middle_col, [
                    ("渐宽部分展开角alpha1(度)", "alpha1"),
                    ("水头损失倍加系数k", "k"),
                    ("渠道超高h2(m)", "h2"),
                    ("日设计流量Q(m³/d)", "Q"),
                    ("栅渣量W1(m³/10³m³)", "W1"),
                    ("重力加速度g(m/s²)", "g")
                ])
                
                # 右列参数
                shape_frame = ttk.LabelFrame(input_container, text="栅条断面形状")
                shape_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
                self.shape_var = tk.StringVar()
                shapes = [
                    ("锐边矩形", "2.42"),
                    ("圆形", "1.79"),
                    ("半圆形", "1.83"),
                    ("梯形", "2.00"),
                    ("正方形", "special")
                ]
                for text, value in shapes:
                    ttk.Radiobutton(shape_frame, text=text, variable=self.shape_var,
                                value=value).pack(anchor="w", pady=2)
                self.shape_var.set("2.42")
                
                # 操作按钮
                btn_frame = ttk.Frame(self.input_frame)
                btn_frame.pack(pady=10)
                ttk.Button(btn_frame, text="计算", command=self.show_results).pack(side="left", padx=5)
                ttk.Button(btn_frame, text="返回", command=self.back_to_gongyi_screen).pack(side="left", padx=5)
                
                # 设计示意图区域
                diagram_container = ttk.LabelFrame(self.input_frame, text="设计示意图")
                diagram_container.pack(fill="both", expand=True, padx=10, pady=10)
                try:
                    img = Image.open("C:/Users/31240/Desktop/python/123.jpg")
                    img = img.resize((900, 480), Image.LANCZOS)
                    self.diagram_img = ImageTk.PhotoImage(img)
                    ttk.Label(diagram_container, image=self.diagram_img).pack(pady=10)
                except Exception as e:
                    ttk.Label(diagram_container, text=f"示意图加载失败: {str(e)}").pack()
                
                # ========== 结果界面 ==========
                # 结果表格区域
                result_container = ttk.LabelFrame(self.result_frame, text="计算结果")
                result_container.pack(fill="x", padx=10, pady=10)
                
                self.result_tree = ttk.Treeview(result_container, columns=("参数", "值"), show="headings", height=10)
                self.result_tree.heading("参数", text="参数")
                self.result_tree.heading("值", text="值")
                self.result_tree.column("参数", width=300, anchor="center")
                self.result_tree.column("值", width=300, anchor="center")
                self.result_tree.pack(fill="both", expand=True, padx=10, pady=10)
                
                # 设计示意图区域
                result_diagram_container = ttk.LabelFrame(self.result_frame, text="设计示意图")
                result_diagram_container.pack(fill="both", expand=True, padx=10, pady=10)
                ttk.Label(result_diagram_container, image=self.diagram_img).pack(pady=10)
                
                # 返回按钮
                back_btn_frame = ttk.Frame(self.result_frame)
                back_btn_frame.pack(pady=10)
                ttk.Button(back_btn_frame, text="返回", command=self.show_input).pack()

            def create_entries(self, parent, fields):
                """统一创建参数输入组件"""
                for row, (label_text, key) in enumerate(fields):
                    ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="e", padx=5, pady=2)
                    entry = ttk.Entry(parent, width=12)
                    entry.grid(row=row, column=1, padx=5, pady=2)
                    self.entries[key] = entry
                    # 设置默认参数
                    defaults = {
                        "Q_max": "1.03", "alpha": "60", "b": "0.019",
                        "h": "0.75", "v": "0.9", "S": "0.01", "B1": "1.3",
                        "alpha1": "20", "k": "3", "h2": "0.3",
                        "Q": "70000", "W1": "0.09", "g": "9.8"
                    }
                    entry.insert(0, defaults.get(key, ""))

            def validate_number(self, key):
                entry = self.entries.get(key)
                if not entry:
                  raise ValueError(f"参数 {key} 未找到")
            
                value = entry.get()
                if not value.strip():
                  raise ValueError(f"参数 {key} 不能为空")
            
                try:
                  return float(value)
                except ValueError:
                  raise ValueError(f"参数 {key} 输入值 '{value}' 无效")


            def calculate(self):
      
                try:
                # 获取并验证所有参数
                    params = {key: self.validate_number(key) for key in [
                             "Q_max", "alpha", "b", "h", "v", "S", "B1",
                             "alpha1", "k", "h2", "Q", "W1", "g"
                              ]}
            
                # 转换角度单位
                    params["alpha"] = math.radians(params["alpha"])
                    params["alpha1"] = math.radians(params["alpha1"])
            
            # 计算阻力系数
                    shape_value = self.shape_var.get()
                    if shape_value == "special":  # 正方形断面
                       epsilon = 0.64
                       xi = ((params["b"] + params["S"])/(epsilon*params["b"]) - 1)**2
                    else:
                       beta = float(shape_value)
                       xi = beta * (params["S"]/params["b"])**(4/3)
            
             # 计算公式
                    results = {}
                    n = params["Q_max"] * math.sqrt(math.sin(params["alpha"])) / (params["b"] * params["h"] * params["v"])
                    results["栅条间隙数 n"] = round(n)
                    B = params["S"] * (results["栅条间隙数 n"] - 1) + params["b"] * results["栅条间隙数 n"]
                    results["渠道宽度 B"] = round(B, 3)
                    l1 = (B - params["B1"]) / (2 * math.tan(params["alpha1"]))
                    results["渐宽段长度 l₁"] = round(l1, 4)
                    l2 = l1 / 2
                    results["渐宽段中间长度 l₂"] = round(l2, 5)
                    dh0 = xi * (params["v"]**2)/(2*params["g"]) * math.sin(params["alpha"])
                    results["水头损失 Δh₀"] = round(dh0, 6)
                    h1 = params["k"] * dh0
                    results["水头损失倍加 h₁"] = round(h1, 5)
                    H = params["h"] + h1 + params["h2"]
                    results["总水深 H"] = round(H, 4)
                    L = l1 + l2 + 0.5 + 1.0 + (params["h"] + params["h2"])/math.tan(params["alpha"])
                    results["总长度 L"] = round(L, 4)
                    W = params["Q"] * params["W1"] / 1000
                    results["栅渣量 W"] = round(W, 1)
            
            # 显示结果
                    for item in self.result_tree.get_children():
                        self.result_tree.delete(item)
                    for key, value in results.items():
                        self.result_tree.insert("", "end", values=(key, value))
        
                except ValueError as e:
                       messagebox.showerror("输入错误", str(e))
                except Exception as e:
                       messagebox.showerror("系统错误", f"计算过程异常: {str(e)}")        

            def show_results(self):
                """切换到结果界面并执行计算"""
                self.calculate()
                self.input_frame.pack_forget()
                self.result_frame.pack(fill="both", expand=True)

            def show_input(self):
                """切换回输入界面"""
                self.result_frame.pack_forget()
                self.input_frame.pack(fill="both", expand=True)

        # 创建 GrilleDesignApp 实例
        grille_app = GrilleDesignApp(frame, self.show_gongyi_screen) 
        # 切换到格栅计算界面
        self.switch_frame(frame)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x900")
    app = KnowledgeGraphApp(root)
    root.mainloop()