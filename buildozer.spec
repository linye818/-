[app]
# (必改) 应用展示名
title = MyKivyApp

# (必改) 包名，只能是小写字母/数字/下划线
package.name = mykivyapp

# (必改) 反向域名
package.domain = org.example

# 源代码目录和入口
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,ttf,otf,txt,md
source.main = main.py

# 版本号
version = 0.1

# 最小依赖：先只放 python3,kivy
requirements = python3,kivy

# 权限（如需要再加）
android.permissions = INTERNET

# 其他
icon.filename =
exclude_patterns = tests, bin, venv, env, .git, __pycache__
orientation = portrait

# ---------------- Android 专用（记得不要重复 [app]） ----------------
android.minapi = 21
android.api = 35
android.ndk = 26b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.branch = master

# 如需增加 gradle 参数，可在这里放开注释
# android.gradle_arguments = -Xmx4g
