[app]
# 必改：应用展示名
title = MyKivyApp

# 必改：包名，只能小写字母+数字+下划线
package.name = mykivyapp

# 必改：反向域名，不能留默认例子；不含大写和特殊字符
package.domain = org.example

source.dir = .
source.include_exts = py,kv,png,jpg,atlas,ttf,otf,txt,md

# 入口脚本
main.py = main.py

# 要打包进 APK 的图标（先用 Kivy 默认）
icon.filename =

# 运行时权限（先留空，有需要再加）
android.permissions =

# Kivy + Python 标准依赖
requirements = python3,kivy

# 如果你未来用到 requests、pillow 等，在这里逗号追加：
# requirements = python3,kivy,requests,pillow

# 忽略测试/无关文件，减少体积
exclude_patterns = tests, bin, venv, env, .git, __pycache__

# 安卓端配置
[buildozer]
# 用 debug 先打通流程
log_level = 2
warn_on_root = 1

# 构建目标平台
target = android

# ---------------- Android 专区 ----------------
[app]
# 最低、目标 SDK。建议用 p4a 支持的稳定组合（2025年可用）
android.minapi = 21
android.api = 35

# 指定 NDK（与 p4a/Buildozer 当前兼容性最好的一版）
android.ndk = 26b

# 使用 Gradle 构建（默认）
android.accept_sdk_license = True

# （如需 Java 最大堆，解决 dex 内存问题）
# android.gradle_arguments = -Xmx4g

# 如果你需要 armeabi-v7a + arm64-v8a，都打开（默认 p4a 会处理）
# android.archs = arm64-v8a, armeabi-v7a

# 使用最新稳定的 p4a 分支（遇到食谱问题再考虑 pin 具体 commit）
p4a.branch = master

# 关闭一些会导致签名问题的默认行为（可选）
# android.disable_android_x = False

# （如需硬件加速窗口）
# android.window = softinput

# （如需添加 AAR/JAR/本地库，可用以下字段）
# android.add_libs_armeabi_v7a =
# android.add_libs_arm64_v8a   =
