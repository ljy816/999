

4
from datetime import datetime, timedelta
from chinese_calendar import is_workday  # 修改1：移除非必要导入
import calendar

def get_valid_input(prompt, input_type=int, min_val=1, max_val=12):
    """获取并验证用户输入"""
    while True:
        try:
            user_input = input_type(input(prompt))
            if min_val <= user_input <= max_val:
                return user_input
            print(f"输入范围应为{min_val}-{max_val}，请重新输入")
        except ValueError:
            print("输入格式错误，请重新输入")

def calculate_salary():
    """新版工资计算器主函数"""
    # 获取用户输入
    month_number = get_valid_input("请输入工资月份(1-12)：")
    leave_days = get_valid_input("请输入请假天数：", min_val=0, max_val=31)
    
    # 基础参数设置
    daily_wage = 393
    tax_threshold = 5000
    year = 2025
    
    # 生成工资周期（处理跨月问题）
    if month_number == 12:
        start_date = datetime(year, 12, 16)
        end_date = datetime(year+1, 1, 15)
    else:
        start_date = datetime(year, month_number, 16)
        next_month = month_number + 1
        end_date = datetime(year, next_month, 15)
    
    # 计算有效工作日（修改2：简化判断逻辑）
    current_date = start_date
    work_days = 0
    while current_date <= end_date:
        if is_workday(current_date):  # 直接使用官方工作日判断
            work_days += 1
        current_date += timedelta(days=1)
    
    # 工资计算逻辑
    actual_days = max(work_days - leave_days, 0)
    gross_salary = actual_days * daily_wage
    
    # 个税计算（优化计算方式）
    taxable_income = max(gross_salary - tax_threshold, 0)
    tax_brackets = [
        (0, 3000, 0.03, 0),
        (3000, 12000, 0.10, 210),
        (12000, 25000, 0.20, 1410),
        (25000, 35000, 0.25, 2660),
        (35000, 55000, 0.30, 4410),
        (55000, 80000, 0.35, 7160),
        (80000, float('inf'), 0.45, 15160)
    ]
    
    tax = 0
    for bracket in tax_brackets:
        if taxable_income > bracket[0]:
            tax = taxable_income * bracket[2] - bracket[3]
        else:
            break
    
    # 输出结果（优化显示格式）
    print(f"\n{year}年{calendar.month_name[month_number]}工资明细：")
    print(f"工资周期：{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print(f"工作日总数：{work_days}天 | 请假天数：{leave_days}天")
    print(f"实际出勤天数：{actual_days}天")
    print("-"*40)
    print(f"税前工资：{gross_salary:.2f}元")
    print(f"应纳税所得额：{max(taxable_income,0):.2f}元")
    print(f"个人所得税：{max(tax,0):.2f}元")
    print("-"*40)
    print(f"实发工资：{gross_salary - max(tax,0):.2f}元")

if __name__ == "__main__":
    calculate_salary()