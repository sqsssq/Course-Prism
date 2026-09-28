# 港科大（广州）课程评价（本机预览）

基于 [Course-Prism](https://github.com/siruizou2005/Course-Prism) 的独立课程评价项目。课程、教师及教学班信息通过 [港科大（广州）SISN 公开课程查询页](https://sisn.hkust-gz.edu.cn/cq) 使用的公开 JSON 接口按学期同步；评价由本站用户提交。本站不是学校官方平台。

## 已完成的第一版

- 浏览和搜索课程，并查看任课教师、教学班、时间地点。
- 登录后提交课程点评；一个账户对同一课程与教师组合保留一条可修改的点评。
- 按学期导入公开课程信息，重复运行会更新课程和教学班，不重复创建。
- 本机 SQLite 预览；另提供 MySQL 容器配置作为后续部署基础。

## 本机快速预览

需要 Node.js 22、npm、[uv](https://docs.astral.sh/uv/) 和 Python 3.13。首次运行：

```sh
./scripts/setup-preview.sh
```

这个脚本会安装依赖、建立本地 SQLite 数据库、同步最新公开学期的课程，并创建一个仅供本机使用的 `preview` 普通账户。密码保存在被 Git 忽略的 `.preview-login` 文件中。

启动：

```sh
./scripts/start-preview.sh
```

打开 <http://localhost:3000>。后端位于 <http://127.0.0.1:18000>。在“账号登录”页用 `.preview-login` 中的账户登录，即可试写评价。预览服务只监听本机地址。

## 课程同步

```sh
cd backend/jcourse_api-master
USE_SQLITE=1 SECRET_KEY=local-only .venv/bin/python manage.py sync_hkustgz_courses --dry-run
USE_SQLITE=1 SECRET_KEY=local-only .venv/bin/python manage.py sync_hkustgz_courses --term-id 2610
```

不传 `--term-id` 时同步公开学期列表中的第一项。数据接口返回的课程信息可能更改；同步有短暂的请求间隔。只同步公开课程、主讲教师和教学班字段，不导入学生或选课记录。

## 容器部署准备

`compose.yaml` 使用 MySQL 8.4、Django 和 Next.js。复制 `.env.example` 为 `.env` 后设置不同的随机密钥，再运行 `docker compose up --build`。目前容器配置用于本机开发；公开上线仍需域名、HTTPS、邮件服务和管理规则。

学生自助注册需要配置 `EMAIL_ACCOUNT_DOMAIN` 与 SMTP；未配置时注册页会明确提示尚未开放。请确认学校实际使用的邮箱域名后再启用。

上游项目原始说明保留在 [README.upstream.md](README.upstream.md) 和 [README.upstream_zh.md](README.upstream_zh.md)。
