import random

# 定义子宇宙和因果信息
sub_universes = {
    "子宇宙A": [  # 子宇宙A的事件和结果
        ("事件1: 播种", "结果1: 收获果实"),
        ("事件2: 下雨", "结果2: 土壤湿润"),
        ("事件3: 施肥", "结果3: 植物生长更快"),
    ],
    "子宇宙B": [  # 子宇宙B的事件和结果
        ("事件1: 读书", "结果1: 知识增加"),
        ("事件2: 锻炼", "结果2: 身体健康"),
        ("事件3: 睡觉", "结果3: 精力恢复"),
    ],
    "子宇宙C": [  # 子宇宙C的事件和结果
        ("事件1: 旅行", "结果1: 见识广阔"),
        ("事件2: 交友", "结果2: 友情加深"),
        ("事件3: 学习新技能", "结果3: 职业发展"),
    ],
}

def display_sub_universes():
    """显示可选择的子宇宙列表"""
    print("可选择的子宇宙:")
    for index, universe in enumerate(sub_universes.keys(), start=1):
        print(f"{index}. {universe}")  # 打印每个子宇宙的名称和对应的索引

def explore_sub_universe(universe_name):
    """探索指定的子宇宙，显示事件及其结果"""
    print(f"\n探索 {universe_name}:")
    for event, result in sub_universes[universe_name]:
        print(f"{event} -> {result}")  # 打印事件和对应的结果

def main():
    """主函数，控制游戏的流程"""
    print("欢迎来到因果探索游戏！")  # 欢迎信息
    while True:  # 无限循环，直到用户选择退出
        display_sub_universes()  # 显示子宇宙列表
        choice = input("请选择一个子宇宙（输入数字，或输入'退出'结束游戏）: ")
        
        if choice.lower() == '退出':  # 检查用户是否输入退出
            print("感谢游玩！")  # 退出时的感谢信息
            break  # 退出循环，结束游戏
        
        try:
            choice_index = int(choice) - 1  # 将用户输入的数字转换为索引
            universe_name = list(sub_universes.keys())[choice_index]  # 获取对应的子宇宙名称
            explore_sub_universe(universe_name)  # 探索选定的子宇宙
        except (ValueError, IndexError):  # 捕获无效输入的异常
            print("无效的选择，请重新输入。")  # 提示用户重新输入

if __name__ == "__main__":
    main()  # 运行主函数
