import os
from flask import Flask, render_template_string, send_from_directory, abort

app = Flask(__name__)

# 演员文件夹路径
ACTORS_DIR = 'static/works'

# 基础模板
BASE_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}演员作品展示{% endblock %}</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <header class="bg-primary text-white text-center py-3">
        <h1>演员作品展示</h1>
        <nav>
            <a class="text-white" href="{{ url_for('index') }}">首页</a>
        </nav>
    </header>
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
    <footer class="text-center mt-4">
        <p>&copy; 2023 作品展示</p>
    </footer>
</body>
</html>
"""

# 首页模板
INDEX_HTML = """
{% extends "base.html" %}

{% block title %}演员歌手清单{% endblock %}

{% block content %}
    <h2>演员清单</h2>
    <div class="list-group">
        {% for actor, details in actors.items() %}
            <a href="{{ url_for('actor', name=actor) }}" class="list-group-item list-group-item-action">
                {{ actor }}
            </a>
        {% endfor %}
    </div>
{% endblock %}
"""

# 演员作品页面模板
ACTOR_HTML = """
{% extends "base.html" %}

{% block title %}{{ name }} 的作品{% endblock %}

{% block content %}
    <h2>{{ name }} 的作品</h2>
    <h3>介绍</h3>
    <p>{{ info }}</p>
    <h3>作品</h3>
    <ul class="list-group">
        {% if works %}
            {% for work in works %}
                <li class="list-group-item">
                    <a href="{{ url_for('work', actor_name=name, work_name=work) }}">{{ work }}</a>
                    <a href="{{ url_for('work', actor_name=name, work_name=work) }}" class="btn btn-secondary btn-sm float-right" download>下载</a>
                </li>
            {% endfor %}
        {% else %}
            <li class="list-group-item">没有作品</li>
        {% endif %}
    </ul>
    <a href="{{ url_for('index') }}" class="btn btn-primary mt-3">返回首页</a>
{% endblock %}
"""

def get_actors():
    actors = {}
    # 遍历演员文件夹
    for actor_name in os.listdir(ACTORS_DIR):
        actor_path = os.path.join(ACTORS_DIR, actor_name)
        if os.path.isdir(actor_path):
            # 读取演员介绍
            info_file = os.path.join(actor_path, 'info.txt')
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = f.read()
            else:
                info = "没有介绍信息"
            
            # 获取作品
            works = []
            for f in os.listdir(actor_path):
                if f != 'info.txt':
                    works.append(f)
            actors[actor_name] = {'info': info, 'works': works}
    return actors

@app.route('/')
def index():
    actors = get_actors()
    return render_template_string(BASE_HTML + INDEX_HTML, actors=actors)

@app.route('/actor/<name>')
def actor(name):
    actors = get_actors()
    actor_info = actors.get(name)
    if actor_info:
        return render_template_string(BASE_HTML + ACTOR_HTML, name=name, info=actor_info['info'], works=actor_info['works'])
    else:
        abort(404)  # 如果演员不存在，返回404错误

@app.route('/actor/<actor_name>/work/<work_name>')
def work(actor_name, work_name):
    actor_path = os.path.join(ACTORS_DIR, actor_name)
    if os.path.exists(actor_path):
        # 获取文件的完整路径
        file_path = os.path.join(actor_path, work_name)
        if os.path.isfile(file_path):
            # 通过 send_from_directory 发送文件
            return send_from_directory(directory=actor_path, path=work_name, as_attachment=True)
        else:
            abort(404)  # 如果文件不存在，返回404错误
    else:
        abort(404)  # 如果演员文件夹不存在，返回404错误

if __name__ == '__main__':
    app.run(debug=True)
