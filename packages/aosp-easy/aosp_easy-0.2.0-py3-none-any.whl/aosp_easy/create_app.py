import os
import re

# 驼峰命名转换工具函数
def to_camel_case(name):
    return "".join(word.capitalize() for word in name.split('_'))

# 蛇形命名转换工具函数
def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# 生成 Android.bp 文件内容
def create_android_bp(app_dir_name, package_name):
    module_name = app_dir_name if app_dir_name.isidentifier() else package_name.split('.')[-1]
    return f"""android_app {{
    name: "{module_name}",
    srcs: ["src/**/*.java"],
    manifest: "AndroidManifest.xml",
    optimize: {{
        enabled: false,
    }},
    certificate: "platform",
    platform_apis: true,
    dxflags: ["--multi-dex"],
    aaptflags: ["--extra-packages {package_name}"],
    // static_libs: [
    //     "xxxx",
    // ],
    // libs: [
    //     "androidx.annotation_annotation",
    // ],
}}
"""

# 生成 AndroidManifest.xml 文件内容
def create_manifest(package_name, activity_class):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">
    <application>
        <activity
            android:name=".{activity_class}"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

# 生成布局文件内容
def create_layout_xml():
    return """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center"
    android:orientation="vertical">

    <TextView
        android:id="@+id/hello_text"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/hello_world"
        android:textSize="18sp" />

</LinearLayout>
"""

# 生成 strings.xml 文件内容
def create_strings_xml(app_name):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{app_name}</string>
    <string name="hello_world">Hello World!</string>
</resources>
"""

# 生成 Activity Java 文件内容
def create_activity_java(package_name, activity_class, layout_name):
    return f"""package {package_name};

import android.app.Activity;
import android.os.Bundle;

public class {activity_class} extends Activity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.{layout_name});
    }}
}}
"""

# 创建项目结构和文件
def create_project_structure(base_dir, app_dir, pkg_name, act_class, app_name):
    # 处理空 base_dir，默认使用当前目录
    if not base_dir:
        base_dir = os.getcwd()  # 获取当前工作目录
    app_path = os.path.join(base_dir, app_dir)
    
    # 目录已存在检查
    if os.path.exists(app_path):
        print(f"错误：目录 '{app_path}' 已存在！")
        return False
    
    os.makedirs(app_path, exist_ok=True)
    print(f"正在创建项目到：{app_path}")

    act_snake = to_snake_case(act_class)
    # 判断是否为 main activity
    if act_snake in ("main_activity", "mainactivity"):
        layout_file = "activity_main.xml"
        layout_name = "activity_main"
    else:
        # 去掉末尾的 _activity 或 activity
        if act_snake.endswith("_activity"):
            base = act_snake[:-9]
        elif act_snake.endswith("activity"):
            base = act_snake[:-8]
        else:
            base = act_snake
        layout_file = f"activity_{base}.xml"
        layout_name = f"activity_{base}"

    # 创建核心文件
    files = [
        ("Android.bp", create_android_bp(app_dir, pkg_name)),
        ("AndroidManifest.xml", create_manifest(pkg_name, act_class)),
        (f"res/layout/{layout_file}", create_layout_xml()),
        (f"res/values/strings.xml", create_strings_xml(app_name)),
    ]

    # 创建源码目录和Activity文件
    src_dir = os.path.join(app_path, "src", *pkg_name.split('.'))
    os.makedirs(src_dir, exist_ok=True)
    files.append((f"{src_dir}/{act_class}.java", create_activity_java(pkg_name, act_class, layout_name)))

    # 写入所有文件
    for path, content in files:
        full_path = os.path.join(app_path, path)  # 拼接完整路径
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        print(f"  创建文件：{full_path}")

    print("\n项目创建完成！")
    print("构建命令：")
    aosp_root = os.environ.get('ANDROID_BUILD_TOP', base_dir)
    relative_path = os.path.relpath(app_path, aosp_root)
    print(f"mmm {relative_path}")
    return True

# 主函数（输入处理）
def main():
    print("AOSP 测试 APP 创建工具")
    print("-----------------------")
    
    # 应用目录名
    app_dir = input("请输入应用目录名（如 TestApp）：").strip()
    while not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', app_dir):
        print("错误：目录名必须以字母/下划线开头，包含字母/数字/下划线")
        app_dir = input("请重新输入：").strip()
    
    # 应用显示名
    app_name = input(f"请输入应用显示名（默认：{app_dir}）：").strip() or app_dir
    
    # 包名
    pkg_name = input("请输入包名（如 com.example.test）：").strip().lower()
    while not re.match(r'^[a-z][a-z0-9.]*[a-z0-9]$', pkg_name):
        print("错误：包名必须符合 Java 包名规范（如 com.example.test）")
        pkg_name = input("请重新输入：").strip().lower()
    
    # Activity 名
    act_name = input("请输入 Activity 名（如 MainActivity 或 main_activity）：").strip()
    while not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', act_name.replace('_', '')):
        print("错误：Activity 名必须以字母/下划线开头，包含字母/数字/下划线（允许下划线分隔）")
        act_name = input("请重新输入：").strip()
    act_class = to_camel_case(act_name)
    
    # 基础目录
    base_dir = input("请输入创建目录（留空为当前目录）：").strip()
    
    # 执行创建
    create_project_structure(base_dir, app_dir, pkg_name, act_class, app_name)

if __name__ == "__main__":
    main()
