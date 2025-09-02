[app]
title = WeChat Ledger
package.name = wechatledger
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,matplotlib,pandas,kivy_garden.matplotlib
orientation = portrait
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.ndk_api = 21  # 指定NDK API版本

[buildozer]
log_level = 2
