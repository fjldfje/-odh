import os
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL 설정 - 여기만 바꾸세요!
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'      # <-- 여기에 MySQL 사용자명
app.config['MYSQL_PASSWORD'] = '0000'  # <-- 여기에 비밀번호
app.config['MYSQL_DB'] = 'flask_board'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# templates 폴더 및 HTML 파일 자동 생성 함수
def create_templates():
    if not os.path.exists('templates'):
        os.mkdir('templates')

    templates = {
        'base.html': """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title> 게시판</title>
</head>
<body>
    <h1><a href="{{ url_for('index') }}"> 게시판</a></h1>
    <hr>
    {% block content %}{% endblock %}
</body>
</html>""",

        'index.html': """{% extends 'base.html' %}
{% block content %}
<form method="get">
    <input type="text" name="q" placeholder="검색어" value="{{ keyword }}">
    <input type="submit" value="검색">
</form>
<a href="{{ url_for('create') }}"> 새 글 작성</a>
<ul>
    {% for post in posts %}
    <li>
        <a href="{{ url_for('detail', post_id=post.id) }}">{{ post.title }}</a>
        <small>({{ post.created_at }})</small>
    </li>
    {% else %}
    <li>게시글이 없습니다.</li>
    {% endfor %}
</ul>
{% endblock %}""",

        'create.html': """{% extends 'base.html' %}
{% block content %}
<h2> 글 작성</h2>
<form method="post">
    <p>제목: <input type="text" name="title" required></p>
    <p>내용:<br><textarea name="content" rows="10" cols="50" required></textarea></p>
    <input type="submit" value="작성">
</form>
{% endblock %}""",

        'detail.html': """{% extends 'base.html' %}
{% block content %}
<h2>{{ post.title }}</h2>
<p>{{ post.content }}</p>
<p><small>작성일: {{ post.created_at }}</small></p>
<a href="{{ url_for('update', post_id=post.id) }}">✏️ 수정</a>
<form method="post" action="{{ url_for('delete', post_id=post.id) }}" style="display:inline;">
    <button type="submit"> 삭제</button>
</form>
<a href="{{ url_for('index') }}"> 목록으로</a>
{% endblock %}""",

        'update.html': """{% extends 'base.html' %}
{% block content %}
<h2> 글 수정</h2>
<form method="post">
    <p>제목: <input type="text" name="title" value="{{ post.title }}" required></p>
    <p>내용:<br><textarea name="content" rows="10" cols="50" required>{{ post.content }}</textarea></p>
    <input type="submit" value="수정">
</form>
{% endblock %}"""
    }

    for filename, content in templates.items():
        with open(os.path.join('templates', filename), 'w', encoding='utf-8') as f:
            f.write(content)

# 실행시 템플릿 생성
create_templates()

@app.route('/')
def index():
    keyword = request.args.get('q', '')
    cur = mysql.connection.cursor()
    if keyword:
        cur.execute("SELECT * FROM posts WHERE title LIKE %s ORDER BY created_at DESC", (f"%{keyword}%",))
    else:
        cur.execute("SELECT * FROM posts ORDER BY created_at DESC")
    posts = cur.fetchall()
    return render_template('index.html', posts=posts, keyword=keyword)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s)", (title, content))
        mysql.connection.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/post/<int:post_id>')
def detail(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()
    if not post:
        return "게시글이 없습니다.", 404
    return render_template('detail.html', post=post)

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def update(post_id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cur.execute("UPDATE posts SET title=%s, content=%s WHERE id=%s", (title, content, post_id))
        mysql.connection.commit()
        return redirect(url_for('detail', post_id=post_id))
    else:
        cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        post = cur.fetchone()
        if not post:
            return "게시글이 없습니다.", 404
        return render_template('update.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete(post_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    mysql.connection.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)