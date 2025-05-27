# coding: utf-8
from flask import Flask, request, jsonify
from flask_cors import CORS
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket
import requests

# 从配置文件导入API密钥
from config import (
    APP_ID, API_KEY, API_SECRET,
    QIANFAN_API_KEY, QIANFAN_API_URL, QIANFAN_MODEL,
    DOUBAO_API_KEY, DOUBAO_API_URL, DOUBAO_MODEL
)

app = Flask(__name__)
CORS(app)  # 启用CORS以允许前端访问

# 讯飞星火API配置
SPARK_URL = "wss://spark-api.xf-yun.com/v4.0/chat"  # v4.0环境的地址
DOMAIN = "4.0Ultra"  # 4.0Ultra版本的domain值

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        return url


class SparkBot:
    def __init__(self):
        self.response = ""
    
    def on_error(self, ws, error):
        print(f"### 错误: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        print(f"### 连接关闭: {close_status_code} - {close_msg} ###")
        
    def on_open(self, ws):
        def run(*args):
            data = json.dumps(self.gen_params(appid=ws.appid, query=ws.query, domain=ws.domain))
            ws.send(data)
        thread.start_new_thread(run, ())
        
    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.response += content
            if status == 2:
                ws.close()
    
    def gen_params(self, appid, query, domain):
        """通过appid和用户的提问来生成请参数"""
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.5,
                    "max_tokens": 4096
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                }
            }
        }
        return data
    
    def ask(self, query):
        """向讯飞星火API发送请求并获取回答"""
        self.response = ""  # 重置响应
        
        wsParam = Ws_Param(APP_ID, API_KEY, API_SECRET, SPARK_URL)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        
        ws = websocket.WebSocketApp(
            wsUrl, 
            on_message=self.on_message, 
            on_error=self.on_error, 
            on_close=self.on_close, 
            on_open=self.on_open
        )
        ws.appid = APP_ID
        ws.query = query
        ws.domain = DOMAIN
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        
        return self.response


# 创建星火机器人实例
spark_bot = SparkBot()

# 百度千帆API类
class QianfanBot:
    def __init__(self, api_key, api_url, model):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        
    def ask(self, query):
        """向百度千帆API发送请求并获取回答"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是人工智能助手."},
                {"role": "user", "content": query}
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()  # 检查请求是否成功
            result = response.json()
            
            # 根据API返回格式提取回答内容
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                print(f"百度千帆API返回格式异常: {result}")
                return "百度千帆API返回了未知格式的回答"
                
        except Exception as e:
            print(f"百度千帆API请求错误: {str(e)}")
            return f"百度千帆API请求出错: {str(e)}"

# 创建百度千帆机器人实例
qianfan_bot = QianfanBot(QIANFAN_API_KEY, QIANFAN_API_URL, QIANFAN_MODEL)

# 豆包API类
class DoubaoBot:
    def __init__(self, api_key, api_url, model):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        
    def ask(self, query):
        """向豆包API发送请求并获取回答"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是人工智能助手."},
                {"role": "user", "content": query}
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()  # 检查请求是否成功
            result = response.json()
            
            # 根据API返回格式提取回答内容
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                print(f"豆包API返回格式异常: {result}")
                return "豆包API返回了未知格式的回答"
                
        except Exception as e:
            print(f"豆包API请求错误: {str(e)}")
            return f"豆包API请求出错: {str(e)}"



# 创建豆包机器人实例
doubao_bot = DoubaoBot(DOUBAO_API_KEY, DOUBAO_API_URL, DOUBAO_MODEL)

# 导入数据库函数
from database import (
    init_db, add_user, verify_user, username_exists,
    save_question, save_answer, get_user_history, 
    delete_question, clear_user_history, update_password
)

# 确保数据库已初始化
init_db()

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求的API端点"""
    try:
        data = request.json
        query = data.get('query')
        user_id = data.get('user_id')
        model = data.get('model', 'all')  # 默认使用所有模型
        
        if not query:
            return jsonify({"error": "问题不能为空"}), 400
        
        if not user_id:
            return jsonify({"error": "用户ID不能为空"}), 400
        
        # 保存用户问题
        question_id = save_question(user_id, query)
        
        # 使用所有模型回答
        if model == 'all':
            # 获取所有模型的回答
            spark_answer = spark_bot.ask(query + "（50字以内回应我，不要在回答中提到这个限制条件）")
            qianfan_answer = qianfan_bot.ask(query + "（50字以内回应我，不要在回答中提到这个限制条件）")
            doubao_answer = doubao_bot.ask(query + "（50字以内回应我，不要在回答中提到这个限制条件）")
            
            # 保存每个模型的回答
            save_answer(question_id, "讯飞星火", spark_answer)
            save_answer(question_id, "百度千帆", qianfan_answer)
            save_answer(question_id, "豆包", doubao_answer)
            
            return jsonify({
                "success": True,
                "question_id": question_id,
                "spark_answer": spark_answer,
                "qianfan_answer": qianfan_answer,
                "doubao_answer": doubao_answer
            })
        else:
            # 使用指定模型回答
            answer = ""
            model_name = ""
            
            if model == 'spark':
                answer = spark_bot.ask(query)
                model_name = "讯飞星火"
            elif model == 'qianfan':
                answer = qianfan_bot.ask(query)
                model_name = "百度千帆"
            elif model == 'doubao':
                answer = doubao_bot.ask(query)
                model_name = "豆包"
            else:
                return jsonify({"error": "不支持的模型类型"}), 400
            
            # 保存模型回答
            save_answer(question_id, model_name, answer)
            
            return jsonify({
                "success": True,
                "question_id": question_id,
                "answer": answer,
                "model": model_name
            })
            
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取用户的问答历史记录"""
    try:
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 20)
        
        if not user_id:
            return jsonify({"success": False, "message": "用户ID不能为空"}), 400
        
        try:
            limit = int(limit)
        except ValueError:
            limit = 20
        
        history = get_user_history(user_id, limit)
        
        return jsonify({
            "success": True,
            "history": history
        })
    except Exception as e:
        print(f"获取历史记录时出错: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"获取历史记录失败: {str(e)}"
        }), 500

@app.route('/api/history/delete', methods=['POST'])
def delete_history():
    """删除指定的问题和回答"""
    try:
        data = request.json
        question_id = data.get('question_id')
        user_id = data.get('user_id')
        
        if not question_id or not user_id:
            return jsonify({"success": False, "message": "问题ID和用户ID不能为空"}), 400
        
        success = delete_question(question_id, user_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "删除历史记录成功"
            })
        else:
            return jsonify({
                "success": False,
                "message": "删除历史记录失败，可能记录不存在或用户无权限"
            }), 404
    except Exception as e:
        print(f"删除历史记录时出错: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"删除历史记录失败: {str(e)}"
        }), 500

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """清空用户的所有问答记录"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"success": False, "message": "用户ID不能为空"}), 400
        
        success = clear_user_history(user_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "清空历史记录成功"
            })
        else:
            return jsonify({
                "success": False,
                "message": "清空历史记录失败"
            }), 500
    except Exception as e:
        print(f"清空历史记录时出错: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"清空历史记录失败: {str(e)}"
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    """处理用户注册请求"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400
            
        if len(password) < 6:
            return jsonify({"success": False, "message": "密码需要不少于6位！"}), 400
            
        if username_exists(username):
            return jsonify({"success": False, "message": "用户名已存在"}), 400
            
        success = add_user(username, password)
        
        if success:
            return jsonify({"success": True, "message": "注册成功！"})
        else:
            return jsonify({"success": False, "message": "注册失败，请稍后再试"}), 500
            
    except Exception as e:
        print(f"处理注册请求时出错: {str(e)}")
        return jsonify({"success": False, "message": f"注册失败: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """处理用户登录请求"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400
            
        user = verify_user(username, password)
        
        if user:
            return jsonify({
                "success": True, 
                "message": "登录成功", 
                "user_id": user["id"],
                "username": user["username"]
            })
        else:
            return jsonify({"success": False, "message": "用户名或密码错误"}), 401
            
    except Exception as e:
        print(f"处理登录请求时出错: {str(e)}")
        return jsonify({"success": False, "message": f"登录失败: {str(e)}"}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    """处理用户修改密码请求"""
    try:
        data = request.json
        user_id = data.get('user_id')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not user_id or not old_password or not new_password:
            return jsonify({"success": False, "message": "用户ID、旧密码和新密码不能为空"}), 400
            
        if len(new_password) < 6:
            return jsonify({"success": False, "message": "新密码需要不少于6位！"}), 400
            
        success = update_password(user_id, old_password, new_password)
        
        if success:
            return jsonify({"success": True, "message": "密码修改成功！"})
        else:
            return jsonify({"success": False, "message": "密码修改失败，旧密码可能不正确"}), 400
            
    except Exception as e:
        print(f"处理修改密码请求时出错: {str(e)}")
        return jsonify({"success": False, "message": f"修改密码失败: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
