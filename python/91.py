import requests
import os
from urllib.parse import unquote

def download_file():
    # 文件URL
    url = "https://raw.githubusercontent.com/ljy816/999/902087ac3ce801644f2939b1ddb3b8cc59bfad60/%E6%B0%94%E4%BD%93%E7%88%86%E7%82%B8%E6%9E%81%E9%99%90.xlsx"
    
    try:
        # 获取并解码文件名
        filename = unquote(url.split('/')[-1])
        
        # 固定保存路径（可修改下列路径）
        save_dir = "C:/Users/31240/Desktop"  # 保存到用户下载目录下的"自动下载"文件夹
        
        # 创建目录（如果不存在）
        os.makedirs(save_dir, exist_ok=True)
        
        # 构建完整保存路径
        file_path = os.path.join(save_dir, filename)
        
        # 下载文件
        print("正在下载文件...")
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP状态码

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"文件已自动保存到：{file_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"下载失败，网络错误: {e}")
    except PermissionError as e:
        print(f"权限不足，无法保存到指定目录: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    return False

if __name__ == "__main__":
    download_file()