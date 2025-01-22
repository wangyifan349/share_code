import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, abort

app = Flask(__name__)
# 配置上传文件夹的路径
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# 首页路由，支持目录浏览
@app.route('/')
@app.route('/browse/<path:subpath>')
def index(subpath=''):
    """
    显示当前目录下的文件和文件夹。
    如果用户点击文件夹，则进入子目录。
    """
    # 计算当前路径
    current_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
    # 如果路径不存在，返回 404 错误
    if not os.path.exists(current_path):
        return "目录不存在", 404
    # 列出当前目录下的文件和文件夹
    items = []
    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        # 判断是文件夹还是文件
        if os.path.isdir(item_path):
            items.append({'name': item, 'type': 'folder'})
        else:
            items.append({'name': item, 'type': 'file'})
    # 渲染模板并传递文件和文件夹列表
    return render_template('index.html', items=items, subpath=subpath)

# 单文件上传路由
@app.route('/upload/file', methods=['POST'])
def upload_file():
    """
    上传单个文件并保存到服务器。
    """
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    # 如果用户没有选择文件
    if file.filename == '':
        return "No selected file", 400
    # 保存文件到上传文件夹
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(save_path)
    return redirect(url_for('index'))

# 文件夹上传路由
@app.route('/upload/folder', methods=['POST'])
def upload_folder():
    """
    上传文件夹并保持文件夹结构。
    """
    # 检查请求中是否包含文件
    if 'files' not in request.files:
        return "No file part", 400
    # 获取所有上传的文件和路径
    files = request.files.getlist('files')
    paths = request.form.getlist('paths')
    for file, path in zip(files, paths):
        # 计算文件的保存路径
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
        # 确保保存路径的文件夹存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # 保存文件
        file.save(save_path)
    return redirect(url_for('index'))

# 文件下载路由
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    提供文件下载功能。
    """
    # 计算文件的完整路径
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # 如果文件不存在，返回 404 错误
    if not os.path.exists(file_path):
        abort(404)
    # 发送文件给用户，作为附件下载
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=False)





<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件管理系统</title>
    <!-- 引入 Bootstrap 样式 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">文件管理系统</h1>

        <!-- 上传文件 -->
        <div class="mb-4">
            <h3>上传文件</h3>
            <form action="/upload/file" method="post" enctype="multipart/form-data" class="mb-3">
                <div class="mb-3">
                    <!-- 文件选择输入框 -->
                    <input type="file" name="file" class="form-control">
                </div>
                <!-- 提交按钮 -->
                <button type="submit" class="btn btn-primary">上传文件</button>
            </form>
        </div>

        <!-- 上传文件夹 -->
        <div class="mb-4">
            <h3>上传文件夹</h3>
            <form id="upload-folder-form" method="post" enctype="multipart/form-data">
                <div class="mb-3">
                    <!-- 文件夹选择输入框 -->
                    <input type="file" id="folder-input" name="files[]" multiple webkitdirectory class="form-control">
                </div>
                <!-- 提交按钮 -->
                <button type="submit" class="btn btn-primary">上传文件夹</button>
            </form>
        </div>

        <!-- 当前路径 -->
        <h3>当前路径：/{{ subpath }}</h3>

        <!-- 文件和文件夹列表 -->
        <ul class="list-group">
            {% for item in items %}
            <li class="list-group-item">
                {% if item.type == 'folder' %}
                <!-- 文件夹链接 -->
                <a href="{{ url_for('index', subpath=subpath + '/' + item.name) }}" class="text-decoration-none">
                    📁 {{ item.name }}
                </a>
                {% else %}
                <!-- 文件下载链接 -->
                <a href="{{ url_for('uploaded_file', filename=subpath + '/' + item.name) }}" class="text-decoration-none">
                    📄 {{ item.name }}
                </a>
                {% endif %}
            </li>
            {% endfor %}
        </ul>
    </div>

    <!-- JavaScript 实现文件夹上传 -->
    <script>
        const folderForm = document.getElementById('upload-folder-form');
        const folderInput = document.getElementById('folder-input');

        folderForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const files = folderInput.files;
            const formData = new FormData();

            for (const file of files) {
                // 获取文件的相对路径
                const relativePath = file.webkitRelativePath || file.name;
                formData.append('files', file);
                formData.append('paths', relativePath);
            }

            // 发送请求到后端
            const response = await fetch('/upload/folder', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                alert('文件夹上传成功！');
                window.location.reload();
            } else {
                alert('文件夹上传失败！');
            }
        });
    </script>
</body>
</html>



