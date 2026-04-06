from publish_raw_web import build_outputs


def main() -> None:
    build_outputs(include_site=False)


if __name__ == "__main__":
    main()

"""
在本機看 preview：
1. 先產生預覽版
   python scripts/build_preview_web.py

2. 在專案根目錄開本機靜態伺服器
   python -m http.server 8080
   
3. 瀏覽器打開：
   http://127.0.0.1:8080/web/
"""
