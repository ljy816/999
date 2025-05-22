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

# 设置全局中文字体
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

class KnowledgeGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self._init_sample_data()

    def _init_sample_data(self):
        sample_data = [
            ("张飞", "属国", "蜀国"),
            ("诸葛亮", "发明", "木牛流马"),
            ("关羽", "称号", "汉寿亭侯"),
            ("吕布", "武器", "方天画戟"),
            ("曹操", "坐骑", "绝影")
        ]
        for head, rel, tail in sample_data:
            self.add_entity(head, rel, tail)

    def add_entity(self, head, rel, tail):
        node_attrs = {"type": "entity", "aliases": [head.lower(), tail.lower()]}
        self.G.add_node(head, **node_attrs)
        self.G.add_node(tail, **node_attrs)
        self.G.add_edge(head, tail, relationship=rel)

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
        self.kg = KnowledgeGraph()
        self.assistant = AIAssistant()
        self.root = root
        self.root.title("上海华强环境科技有限公司智慧环保系统")
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

        label = tk.Label(frame, text="上海华强环境科技有限公司AI助手", font=("微软雅黑", 24), fg="#2E86C1", bg="#f0f0f0")
        label.pack(pady=30)

        buttons = [
            ("智能问答", self.show_qa_screen),
            ("系统设置", self.show_settings_screen),
            ("返回登录", self.show_login_screen),
            ("退出系统", self.root.quit)
        ]

        for text, command in buttons:
            btn = ttk.Button(frame, text=text, command=command, style="TButton")
            btn.pack(pady=15, ipadx=25, ipady=8)

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

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x900")
    app = KnowledgeGraphApp(root)
    root.mainloop()