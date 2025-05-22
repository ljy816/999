import tkinter as tk
from tkinter import ttk, messagebox
import math
from PIL import Image, ImageTk

class GrilleDesignApp:
    def __init__(self, root):
        self.root = root
        self.root.title("污水处理厂设计辅助计算 v2.2")
        self.root.geometry("1200x900")
        self.entries = {}  # 统一初始化参数存储字典
        
        # 创建主容器
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        # 创建两个界面：输入界面和结果界面
        self.input_frame = ttk.Frame(self.main_frame)
        self.result_frame = ttk.Frame(self.main_frame)
        
        # 默认显示输入界面
        self.input_frame.pack(fill="both", expand=True)
        
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
        ttk.Button(btn_frame, text="退出", command=self.root.destroy).pack(side="left", padx=5)
        
        # 设计示意图区域
        diagram_container = ttk.LabelFrame(self.input_frame, text="设计示意图")
        diagram_container.pack(fill="both", expand=True, padx=10, pady=10)
        try:
            img = Image.open("C:/Users/31240/Desktop/sewagetreatment/dist/geshan3.gif")
            img = img.resize((1100, 500), Image.LANCZOS)
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
        """强化参数验证"""
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
        """执行计算逻辑"""
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

if __name__ == "__main__":
    root = tk.Tk()
    app = GrilleDesignApp(root)
    root.mainloop()