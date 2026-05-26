import argparse
import json
import os
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
    headers = headers or {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8", errors="ignore"))


def fetch_temperature(latitude: float, longitude: float) -> float:
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&current_weather=true"
    )
    data = fetch_json(url)
    current = data.get("current_weather")
    if not isinstance(current, dict):
        raise RuntimeError("接口响应中未包含当前天气数据")
    temperature = current.get("temperature")
    if temperature is None:
        raise RuntimeError("接口响应中未包含温度字段")
    return float(temperature)


def save_plot(times, values, output_path: Path, title: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("请先安装 matplotlib：pip install matplotlib")

    plt.figure(figsize=(10, 5), dpi=120)
    plt.plot(times, values, marker="o", linestyle="-", color="#1f77b4")
    plt.title(title)
    plt.xlabel("时间")
    plt.ylabel("温度 (°C)")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.xticks(rotation=45, ha="right")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()


def parse_location(location: str):
    if "," in location:
        parts = [part.strip() for part in location.split(",") if part.strip()]
        if len(parts) == 2:
            return float(parts[0]), float(parts[1])
    raise ValueError(
        "位置格式错误，正确格式示例：39.9042,116.4074（纬度,经度）"
    )


def main():
    parser = argparse.ArgumentParser(description="每5秒获取实时气温并输出曲线到桌面")
    parser.add_argument("--interval", type=float, default=5.0, help="刷新间隔（秒）")
    parser.add_argument("--points", type=int, default=60, help="图表最多保留的数据点数")
    parser.add_argument(
        "--location",
        type=str,
        default="39.9042,116.4074",
        help="经纬度坐标，格式：纬度,经度。例如北京 39.9042,116.4074",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(desktop_path() / "temperature_curve.png"),
        help="输出图像文件路径",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        latitude, longitude = parse_location(args.location)
    except ValueError as exc:
        print(f"位置参数错误：{exc}")
        sys.exit(1)

    times = []
    values = []
    title = f"实时气温曲线 ({latitude:.4f},{longitude:.4f})"

    print(f"输出图像：{output_path}")
    print("按 Ctrl+C 退出程序。")

    while True:
        try:
            temp = fetch_temperature(latitude, longitude)
            now = datetime.now().strftime("%H:%M:%S")
            times.append(now)
            values.append(temp)

            if len(times) > args.points:
                times = times[-args.points :]
                values = values[-args.points :]

            save_plot(times, values, output_path, title)
            print(f"[{now}] 当前温度：{temp:.1f}°C，已保存曲线")
        except ImportError as err:
            print(err)
            print("请安装 matplotlib 后重新运行: pip install matplotlib")
            sys.exit(1)
        except Exception as err:
            print(f"获取失败：{err}")

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
