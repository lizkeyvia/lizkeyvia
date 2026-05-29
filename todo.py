# 简易待办清单程序
# 功能：添加、查看、标记完成、删除待办任务
#
# 使用方法：
#   1. 运行程序后，会显示主菜单。
#   2. 输入对应数字（1-5）选择操作：
#      1 - 添加任务
#      2 - 查看所有任务
#      3 - 标记任务为已完成
#      4 - 删除任务
#      5 - 退出程序
#   3. 添加任务时，输入任务内容即可。
#   4. 标记或删除任务时，输入任务编号（从1开始）。
#   5. 程序会持续运行，直到用户选择退出或按下 Ctrl+C 中断。
#
# 注意事项：
#   - 任务数据仅保存在内存中，程序退出后丢失。
#   - 输入非数字或超出范围时，程序会提示错误并重新要求输入。
#   - 支持 Ctrl+C 或 Ctrl+D 中断程序。

import sys

def get_int_input(prompt: str, min_val: int, max_val: int) -> int:
    """循环获取整数输入，直到输入有效范围内的整数。"""
    while True:
        try:
            user_input = input(prompt)
            num = int(user_input)
            if min_val <= num <= max_val:
                return num
            else:
                print(f"❌ 编号超出范围，请输入 {min_val}-{max_val} 之间的数字！")
        except ValueError:
            print("❌ 请输入有效的数字！")
        except (KeyboardInterrupt, EOFError):
            # 重新抛出，由外层处理
            raise

def main():
    # 用列表存储任务，每个任务是字典，包含内容和状态
    todo_list = []

    try:
        while True:
            # 打印主菜单
            print("\n===== 简易待办清单 =====")
            print("1. 添加任务")
            print("2. 查看所有任务")
            print("3. 标记任务为已完成")
            print("4. 删除任务")
            print("5. 退出程序")
            print("========================")

            # 获取用户选择
            choice = input("请输入选项数字（1-5）：")

            # 选项1：添加任务
            if choice == "1":
                task = input("请输入要添加的任务内容：")
                todo_list.append({"内容": task, "已完成": False})
                print(f"✅ 已添加任务：{task}")

            # 选项2：查看所有任务
            elif choice == "2":
                if not todo_list:
                    print("📭 待办清单是空的，快去添加任务吧！")
                    continue
                print("\n你的待办任务：")
                for i, task in enumerate(todo_list, start=1):
                    status = "✅ 已完成" if task["已完成"] else "🔲 未完成"
                    print(f"{i}. {task['内容']} —— {status}")

            # 选项3：标记任务为已完成
            elif choice == "3":
                if not todo_list:
                    print("📭 还没有任务可以标记哦！")
                    continue
                num = get_int_input("请输入要标记的任务编号：", 1, len(todo_list))
                todo_list[num-1]["已完成"] = True
                print(f"✅ 已将任务 {num} 标记为已完成！")

            # 选项4：删除任务
            elif choice == "4":
                if not todo_list:
                    print("📭 还没有任务可以删除哦！")
                    continue
                num = get_int_input("请输入要删除的任务编号：", 1, len(todo_list))
                deleted_task = todo_list.pop(num-1)
                print(f"🗑️ 已删除任务：{deleted_task['内容']}")

            # 选项5：退出程序
            elif choice == "5":
                print("👋 感谢使用待办清单，再见！")
                break

            # 无效选项
            else:
                print("❌ 无效选项，请输入 1-5 之间的数字！")
    except (KeyboardInterrupt, EOFError):
        print("\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"❌ 程序发生意外错误：{e}")

# 程序入口
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 程序发生意外错误：{e}")
        sys.exit(1)
