import os
import re

# 命名转换工具函数
def to_camel_case(name):
    return "".join(word.capitalize() for word in name.split('_'))

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# === Android.bp 文件生成 ===
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
    //     "xxx",
    // ],
    // libs: [
    //     "androidx.annotation_annotation",
    // ],
}}
"""

# === Service 应用相关文件生成 ===
def create_manifest(package_name, service_class):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">
    <application>
        <service
            android:name=".{service_class}"
            android:enabled="true"
            android:exported="false" />
    </application>
</manifest>
"""

def create_application_java(package_name, service_class):
    return f"""package {package_name};

import android.app.Application;
import android.content.Intent;

public class MainApplication extends Application {{
    @Override
    public void onCreate() {{
        super.onCreate();
        // 启动服务
        Intent serviceIntent = new Intent(this, {service_class}.class);
        startService(serviceIntent);
    }}
}}
"""

def create_service_java(package_name, service_class, broadcast_action):
    return f"""package {package_name};

import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.IBinder;
import android.util.Log;

public class {service_class} extends Service {{
    private static final String TAG = "{service_class}";
    private static final String CMD_KEY = "command";

    private BroadcastReceiver mReceiver;

    @Override
    public void onCreate() {{
        super.onCreate();
        Log.d(TAG, "Service created");
        
        // 动态注册广播接收器
        mReceiver = new BroadcastReceiver() {{
            @Override
            public void onReceive(Context context, Intent intent) {{
                String command = intent.getStringExtra(CMD_KEY);
                if (command == null) {{
                    Log.e(TAG, "without command in intent" + intent.getAction());
                    return;
                }}
                handleCommand(command, intent);
            }}
        }};
        
        IntentFilter filter = new IntentFilter("{broadcast_action}");
        registerReceiver(mReceiver, filter);
    }}

    @Override
    public void onDestroy() {{
        super.onDestroy();
        Log.d(TAG, "Service destroyed");
        unregisterReceiver(mReceiver);
    }}

    @Override
    public IBinder onBind(Intent intent) {{
        return null;
    }}

    private void handleCommand(String command, Intent intent) {{
        Log.d(TAG, "Received command: " + command);
        
        if ("start".equals(command)) {{
            handleStart(intent);
        }} else if ("stop".equals(command)) {{
            handleStop(intent);
        }} else if ("status".equals(command)) {{
            handleStatus(intent);
        }} else {{
            Log.w(TAG, "Unknown command: " + command);
        }}
    }}

    private void handleStart(Intent intent) {{
        Log.i(TAG, "Starting service operation");
        // TODO: 添加启动逻辑
    }}

    private void handleStop(Intent intent) {{
        Log.i(TAG, "Stopping service operation");
        // TODO: 添加停止逻辑
    }}

    private void handleStatus(Intent intent) {{
        Log.i(TAG, "Reporting service status");
        // TODO: 添加状态报告逻辑
    }}
}}
"""

def create_readme(package_name, service_name, broadcast_action):
    print("生成 README.md 文件内容")
    print(f"包名: {package_name}, 服务名: {service_name}, 广播 Action: {broadcast_action}")
    return f"""# {service_name} Service
This is an Android service that can be controlled via broadcast commands.

## 服务控制命令

### Start Service
```bash
am start-service {package_name}/.{service_name}
```

### Test Commands 测试命令
```bash
am broadcast -a {broadcast_action} --es command "start"
am broadcast -a {broadcast_action} --es command "stop"
am broadcast -a {broadcast_action} --es command "status"
```
"""

# === 项目创建 ===
def create_project_structure(base_dir, app_dir, pkg_name, service_name, broadcast_action):
    if not base_dir:
        base_dir = os.getcwd()
    app_path = os.path.join(base_dir, app_dir)
    
    if os.path.exists(app_path):
        print(f"错误：目录 '{app_path}' 已存在！")
        return False
    
    os.makedirs(app_path, exist_ok=True)
    print(f"正在创建项目到：{app_path}")

    # 生成文件列表
    files = [
        ("README.md", create_readme(pkg_name, service_name, broadcast_action)),
        ("Android.bp", create_android_bp(app_dir, pkg_name)),
        ("AndroidManifest.xml", create_manifest(pkg_name, service_name)),
        (f"src/{'/'.join(pkg_name.split('.'))}/MainApplication.java", 
         create_application_java(pkg_name, service_name)),
        (f"src/{'/'.join(pkg_name.split('.'))}/{service_name}.java", 
         create_service_java(pkg_name, service_name, broadcast_action)),
    ]

    # 写入所有文件
    for path, content in files:
        full_path = os.path.join(app_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        print(f"  创建文件：{full_path}")

    print("\n项目创建完成！")
    print("构建命令：")
    aosp_root = os.environ.get('ANDROID_BUILD_TOP', base_dir)
    relative_path = os.path.relpath(app_path, aosp_root)
    print(f"mmm {relative_path}")
    
    print("\n服务使用说明：")
    print(f"0. 启动服务：")
    print(f"   adb shell am start {pkg_name}/.{service_name}")
    print(f"1. 发送广播命令：")
    print(f"   adb shell am broadcast -a {broadcast_action} -e command [start|stop|status]")
    print(f"2. 查看服务日志：")
    print(f"   adb logcat -s {service_name}")
    
    return True

# === 主函数 ===
def main():
    print("AOSP 简化 Service 应用创建工具")
    print("-------------------------------")
    
    # 应用目录名
    app_dir = input("请输入应用目录名（如 SimpleService）：").strip()
    while not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', app_dir):
        print("错误：目录名必须以字母/下划线开头，包含字母/数字/下划线")
        app_dir = input("请重新输入：").strip()
    
    # 包名
    pkg_name = input("请输入包名（如 com.example.service）：").strip().lower()
    while not re.match(r'^[a-z][a-z0-9.]*[a-z0-9]$', pkg_name):
        print("错误：包名必须符合 Java 包名规范（如 com.example.service）")
        pkg_name = input("请重新输入：").strip().lower()
    
    # Service 名
    service_name = input("请输入 Service 名（默认：MainService）：").strip() or "MainService"
    # service_name = to_camel_case(service_name)
    
    # 广播Action
    default_action = f"{pkg_name}.ACTION_COMMAND"
    broadcast_action = input(f"请输入广播 Action（默认：{default_action}）：").strip() or default_action
    while not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', broadcast_action):
        print("错误：广播 Action 必须符合命名规范")
        broadcast_action = input("请重新输入：").strip() or default_action
    
    # 基础目录
    base_dir = input("请输入创建目录（留空为当前目录）：").strip()
    
    # 执行创建
    create_project_structure(base_dir, app_dir, pkg_name, service_name, broadcast_action)

if __name__ == "__main__":
    main()
