[app]
# (必改) App display name
title = MyKivyApp

# (必改) package name - 只能小写字母/数字/下划线
package.name = mykivyapp

# (必改) reverse domain
package.domain = org.example

# 源
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,ttf,otf,txt,md
source.main = main.py

# 版本
version = 0.1

# 依赖：先保持最小
requirements = python3,kivy

# 权限（需要时再加）
android.permissions = INTERNET

# 图标/方向等
icon.filename =
orientation = portrait

# 排除不必要文件
exclude_patterns = tests, bin, venv, env, .git, __pycache__

# Android 专用配置（放在同一 [app] 节）
android.minapi = 21
android.api = 35
android.ndk = 26b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

# p4a branch
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
target = android
