import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import networkx as nx
import matplotlib.pyplot as plt
from openai import OpenAI
import threading
import sqlite3
import random
import string

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

    def get_response(self, query, callback):
        def ai_task():
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "我是华强智能ai,有什么能为你服务的"},
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
        
        # 初始化数据库
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (username TEXT PRIMARY KEY,
                             password TEXT,
                             security_question TEXT,
                             security_answer TEXT)''')
        self.conn.commit()
        
        self.show_welcome_screen()

    def show_welcome_screen(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        try:
            img = Image.open("C:/Users/31240/Desktop/python/1.png")
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=photo)
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
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)
        self.generate_captcha()

        # 登录界面组件
        ttk.Label(frame, text="用户登录", font=("楷体", 20)).pack(pady=20)

        # 账号输入
        ttk.Label(frame, text="账号:").pack()
        self.username_entry = ttk.Entry(frame)
        self.username_entry.pack(pady=5)

        # 密码输入
        ttk.Label(frame, text="密码:").pack()
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(pady=5)

        # 验证码
        captcha_frame = tk.Frame(frame)
        captcha_frame.pack(pady=5)
        ttk.Label(captcha_frame, text="验证码:").pack(side="left")
        self.captcha_entry = ttk.Entry(captcha_frame, width=8)
        self.captcha_entry.pack(side="left", padx=5)
        self.captcha_label = ttk.Label(captcha_frame, text=self.captcha_code, 
                                     font=("Courier", 14), foreground="blue")
        self.captcha_label.pack(side="left")
        ttk.Button(captcha_frame, text="刷新", command=self.refresh_captcha).pack(side="left", padx=5)

        # 功能按钮
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
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
        window = tk.Toplevel(self.root)
        window.title("用户注册")

        # 注册表单组件
        ttk.Label(window, text="新用户注册", font=("楷体", 16)).grid(row=0, columnspan=2, pady=10)

        ttk.Label(window, text="账号:").grid(row=1, column=0, padx=5, pady=5)
        username_entry = ttk.Entry(window)
        username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(window, text="密码:").grid(row=2, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(window, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(window, text="确认密码:").grid(row=3, column=0, padx=5, pady=5)
        confirm_entry = ttk.Entry(window, show="*")
        confirm_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(window, text="安全问题:").grid(row=4, column=0, padx=5, pady=5)
        question_entry = ttk.Entry(window)
        question_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(window, text="答案:").grid(row=5, column=0, padx=5, pady=5)
        answer_entry = ttk.Entry(window)
        answer_entry.grid(row=5, column=1, padx=5, pady=5)

        def submit():
            # 表单验证逻辑
            if password_entry.get() != confirm_entry.get():
                messagebox.showerror("错误", "两次密码输入不一致")
                return
            
            try:
                self.cursor.execute("INSERT INTO users VALUES (?,?,?,?)",
                                  (username_entry.get(), password_entry.get(),
                                   question_entry.get(), answer_entry.get()))
                self.conn.commit()
                messagebox.showinfo("成功", "注册成功")
                window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "用户名已存在")

        ttk.Button(window, text="提交注册", command=submit).grid(row=6, columnspan=2, pady=10)

    def show_forgot_password(self):
        window = tk.Toplevel(self.root)
        window.title("密码重置")

        ttk.Label(window, text="密码重置", font=("楷体", 16)).grid(row=0, columnspan=2, pady=10)

        ttk.Label(window, text="账号:").grid(row=1, column=0, padx=5, pady=5)
        username_entry = ttk.Entry(window)
        username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(window, text="安全问题:").grid(row=2, column=0, padx=5, pady=5)
        question_label = ttk.Label(window, text="")
        question_label.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(window, text="答案:").grid(row=3, column=0, padx=5, pady=5)
        answer_entry = ttk.Entry(window)
        answer_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(window, text="新密码:").grid(row=4, column=0, padx=5, pady=5)
        new_password_entry = ttk.Entry(window, show="*")
        new_password_entry.grid(row=4, column=1, padx=5, pady=5)

        def get_question():
            self.cursor.execute("SELECT security_question FROM users WHERE username=?", 
                              (username_entry.get(),))
            result = self.cursor.fetchone()
            question_label.config(text=result[0] if result else "用户不存在")

        def reset_password():
            self.cursor.execute("SELECT security_answer FROM users WHERE username=?", 
                              (username_entry.get(),))
            result = self.cursor.fetchone()
            
            if result and answer_entry.get() == result[0]:
                self.cursor.execute("UPDATE users SET password=? WHERE username=?",
                                  (new_password_entry.get(), username_entry.get()))
                self.conn.commit()
                messagebox.showinfo("成功", "密码已重置")
                window.destroy()
            else:
                messagebox.showerror("错误", "答案不正确")

        ttk.Button(window, text="获取安全问题", command=get_question).grid(row=1, column=2, padx=5)
        ttk.Button(window, text="重置密码", command=reset_password).grid(row=5, columnspan=2, pady=10)

    def switch_frame(self, new_frame):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = new_frame

    # 以下为原有代码保持不变
    def show_main_menu(self, previous_frame=None):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        label = tk.Label(frame, text="上海华强环境科技有限公司智慧环保系统", font=("楷体", 24), fg="#2E86C1")
        label.pack(pady=30)

        buttons = [
            ("智能问答", self.show_qa_screen),
            ("退出系统", self.root.quit)
        ]

        for text, command in buttons:
            btn = ttk.Button(frame, text=text, command=command, style="TButton")
            btn.pack(pady=15, ipadx=25, ipady=8)

        self.switch_frame(frame)


    def show_qa_screen(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

     # 输入区域
        input_frame = tk.Frame(frame)
        input_frame.pack(pady=20, fill="x")

        self.entry = ttk.Entry(input_frame, width=60, font=("宋体", 16))  # 创建输入框
        self.entry.pack(side="left", padx=10)  # 左对齐布局

        btn_ask = ttk.Button(input_frame, text="提问", command=self.start_qa_thread)  # 提问按钮
        btn_ask.pack(side="left", padx=10)  

        # 显示区域
        self.answer_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, 
                                                    font=("宋体", 12), 
                                                    padx=15, pady=15,
                                                    height=15)
        self.answer_area.pack(fill="both", expand=True, padx=20)
        self.answer_area.config(state=tk.DISABLED)

        # 底部按钮
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="清空记录", command=self.clear_history).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="返回主菜单", command=self.show_main_menu).pack(side="left", padx=10)

        self.switch_frame(frame)

    def start_qa_thread(self):
        if self.assistant.is_responding:
            return
        query = self.entry.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入问题内容")
            return
        
        self.assistant.is_responding = True
        self.update_answer("【系统】正在思考，请稍候...\n\n", tag="system")
        self.entry.config(state=tk.DISABLED)
        self.assistant.get_response(query, self.handle_ai_response)

    def handle_ai_response(self, answer, error):
        self.assistant.is_responding = False
        self.entry.config(state=tk.NORMAL)
        
        if error:
            self.update_answer(f"【错误】{error}\n", tag="error")
            return
        
        self.update_answer("【AI助手】\n", tag="assistant")
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

    def show_full_graph(self):
        plt.figure(figsize(12, 8))
        pos = nx.spring_layout(self.kg.G, seed=42)
        nx.draw(self.kg.G, pos, with_labels=True, node_color="#F9E79F", 
               node_size=1500, edge_color="#7D3C98", 
               arrows=True, arrowsize=20)
        plt.title("上海华强环境工程有限公司智慧环保")
        plt.show()

    def switch_frame(self, new_frame):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = new_frame


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    style = ttk.Style()
    style.configure("TButton", font=("宋体", 12), padding=6)
    app = KnowledgeGraphApp(root)
    root.mainloop()