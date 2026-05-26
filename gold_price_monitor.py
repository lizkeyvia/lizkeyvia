import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path


def desktop_path() -> Path:
    desktop = Path.home() / "Desktop"
    return desktop if desktop.exists() else Path.cwd()


def fetch_json(url: str, headers=None, timeout=10):
    headers = headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8", errors="ignore"))


def fetch_text(url: str, headers=None, timeout=10):
    headers = headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_gold_price_from_json(data):
    if isinstance(data, dict):
        candidates = [
            "xauPrice",
            "price",
            "current_price",
            "last",
            "bid",
            "ask",
            "gold",
        ]
        for key in candidates:
            value = data.get(key)
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                return float(value)
        for value in data.values():
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                return float(value)
    elif isinstance(data, list) and data:
        return parse_gold_price_from_json(data[0])
    return None


def fetch_gold_price() -> float:
    # 尝试多个公开接口，尽量获取当前国际金价（美元/盎司）
    endpoints = [
        ("https://data-asg.goldprice.org/dbXRates/USD", "json"),
        ("https://api.metals.live/v1/spot/gold", "json"),
        ("https://finance.yahoo.com/quote/XAUUSD=X/", "html"),
    ]

    last_error = None
    for url, kind in endpoints:
        try:
            if kind == "json":
                data = fetch_json(url)
                price = parse_gold_price_from_json(data)
                if price is not None and price > 0:
                    return price
            else:
                text = fetch_text(url)
                match = re.search(r'"currentPrice":\{"raw":([0-9]+\.?[0-9]*)', text)
                if match:
                    return float(match.group(1))
                match = re.search(r'"regularMarketPrice":\{"raw":([0-9]+\.?[0-9]*)', text)
                if match:
                    return float(match.group(1))
        except Exception as exc:
            last_error = exc
    if last_error:
        raise RuntimeError(f"无法获取金价：{last_error}")
    raise RuntimeError("无法获取金价：未找到可用数据")


def save_plot(times, prices, output_path: Path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError(
            "请先安装 matplotlib：pip install matplotlib"
        )

    plt.figure(figsize=(10, 5), dpi=120)
    plt.plot(times, prices, marker="o", linestyle="-", color="#b8860b")
    plt.title("实时国际金价曲线（美元/盎司）")
    plt.xlabel("时间")
    plt.ylabel("价格 USD/oz")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.xticks(rotation=45, ha="right")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="每5秒获取实时国际金价并输出曲线到桌面")
    parser.add_argument("--interval", type=float, default=5.0, help="刷新间隔，秒")
    parser.add_argument("--points", type=int, default=60, help="图表最多保留的数据点数")
    parser.add_argument("--output", type=str, default=str(desktop_path() / "gold_price_curve.png"), help="输出图像路径")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    times = []
    prices = []

    print(f"输出图像：{output_path}")
    print("按 Ctrl+C 退出程序。")

    while True:
        try:
            price = fetch_gold_price()
            now = datetime.now()
            times.append(now.strftime("%H:%M:%S"))
            prices.append(price)

            if len(times) > args.points:
                times = times[-args.points :]
                prices = prices[-args.points :]

            save_plot(times, prices, output_path)
            print(f"[{now.strftime('%H:%M:%S')}] 当前金价：{price:.2f} USD/oz，已保存曲线")
        except ImportError as err:
            print(err)
            print("安装后重新运行: pip install matplotlib")
            sys.exit(1)
        except Exception as err:
            print(f"获取失败：{err}")

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
