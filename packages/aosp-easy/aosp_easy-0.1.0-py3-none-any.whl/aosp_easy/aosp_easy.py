import sys

def main():
    if len(sys.argv) < 2:
        print("usage: aosp_easy [app|service]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "app":
        from .create_app import main as create_app_main
        create_app_main()
    elif mode == "service":
        from .create_service import main as create_service_main
        create_service_main()
    else:
        print("错误：参数错误")
        print("usage: aosp_easy [app|service]")
        sys.exit(1)

if __name__ == "__main__":
    main()