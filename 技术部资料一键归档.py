# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox

FOLDER_RULES = [
    ("01_预处理车间/01_浸出工艺", ["浸出", "酸溶", "片碱", "纯碱"]),
    ("01_预处理车间/02_除铁及二浸", ["除铁", "二浸", "回调", "铁渣", "除铬"]),
    ("01_预处理车间/03_CCD洗涤及浓密", ["ccd", "浓密", "洗涤", "泥层", "溢流"]),
    ("01_预处理车间/04_MHP原料及投料", ["mhp", "原料投料", "投料测试"]),
    ("01_预处理车间/05_辅料单耗及金属平衡", ["辅料单耗", "杂质平衡", "金属平衡", "硫酸用量", "双氧水用量"]),
    ("01_预处理车间/06_生产数据及计算", ["填槽", "使用量计算", "消耗", "日报", "台账"]),

    ("02_实验研究/01_MHP原料投料试验", ["原料投料", "投料测试"]),
    ("02_实验研究/02_除铁及杂质去除试验", ["除铁实验", "除铬实验", "杂质去除", "硫酸亚铁"]),
    ("02_实验研究/03_双氧水及还原试验", ["双氧水", "还原试验", "过氧化氢"]),
    ("02_实验研究/04_絮凝剂试验", ["絮凝剂", "絮凝", "沉降试验"]),
    ("02_实验研究/05_其他工艺试验", ["试验数据", "实验数据", "试验报告", "实验报告", "试验方案", "实验方案"]),

    ("03_技改及项目建设/01_二浸液铜回收项目", ["铜回收", "置换铜", "海绵铜"]),
    ("03_技改及项目建设/02_除铁工艺优化", ["除铁工艺优化", "除铁工艺变更", "除铁优化"]),
    ("03_技改及项目建设/03_晶体线及电镍线技改", ["晶体线", "电镍线技改", "电镍线技术"]),
    ("03_技改及项目建设/04_备料车间技改", ["备料车间", "备料技改"]),
    ("03_技改及项目建设/05_其他技改项目", ["技改", "改造", "立项报告"]),

    ("04_电镍及结晶/01_电镍工艺", ["电镍", "镍板", "电积"]),
    ("04_电镍及结晶/02_硫酸钴结晶", ["硫酸钴", "结晶", "七水硫酸钴"]),
    ("04_电镍及结晶/03_产品质量及技术标准", ["成品", "产品质量", "质量标准", "fmi-ti"]),

    ("05_设备及工程资料/01_设备计算", ["计算表", "设备容积", "压滤机计算", "用量计算"]),
    ("05_设备及工程资料/02_设备规格及参数", ["规格", "参数", "设备明细"]),
    ("05_设备及工程资料/03_车间布局及流程图", ["布局图", "流程图", "visio", "drawing"]),
    ("05_设备及工程资料/04_设备调试资料", ["调试报告", "调试记录", "设备调试"]),

    ("06_生产管理及月报/01_生产日报及台账", ["日报", "生产台账", "巡检"]),
    ("06_生产管理及月报/02_月报及总结", ["月报", "总结报告", "工作总结"]),
    ("06_生产管理及月报/03_原料及库存盘点", ["盘点", "库存"]),
    ("06_生产管理及月报/04_生产指标统计", ["统计", "指标", "单耗"]),

    ("07_标准规范及参考资料/01_企业技术标准", ["技术标准", "标准", "规范", "测量方法"]),
    ("07_标准规范及参考资料/02_行业标准及规范", ["行业标准", "国家标准", "gb", "ys/t"]),
    ("07_标准规范及参考资料/03_供应商及选型资料", ["供应商", "选型", "有限公司"]),
]

def classify(filename):
    name = filename.lower()
    for folder, keywords in FOLDER_RULES:
        if any(k.lower() in name for k in keywords):
            return folder
    return "99_待确认"

def unique_target(path):
    if not path.exists():
        return path
    i = 1
    while True:
        candidate = path.with_name(f"{path.stem}_副本{i}{path.suffix}")
        if not candidate.exists():
            return candidate
        i += 1

def run():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    source_str = filedialog.askdirectory(parent=root, title="请选择当前存放资料的文件夹")
    if not source_str:
        root.destroy()
        return

    source = Path(source_str)
    destination = source / "技术部工作资料"
    files = [
        p for p in source.iterdir()
        if p.is_file()
        and p.suffix.lower() not in {".pyc"}
        and p.name not in {"技术部资料一键归档.py", "运行整理.bat"}
    ]

    if not files:
        messagebox.showinfo("提示", "所选文件夹第一层没有可整理的文件。", parent=root)
        root.destroy()
        return

    plan = [(p, unique_target(destination / classify(p.name) / p.name),
             classify(p.name)) for p in files]
    counts = {}
    for _, _, folder in plan:
        counts[folder] = counts.get(folder, 0) + 1

    preview = "\n".join(f"{folder}：{count} 个" for folder, count in sorted(counts.items()))
    confirm = (
        f"共发现 {len(plan)} 个文件。\n\n{preview}\n\n"
        f"目标位置：\n{destination}\n\n确认开始移动吗？"
    )
    if not messagebox.askyesno("归档预览", confirm, parent=root):
        root.destroy()
        return

    moved, failed = 0, []
    for src, dst, _ in plan:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            moved += 1
        except Exception as exc:
            failed.append(f"{src.name}：{exc}")

    msg = f"整理完成：成功移动 {moved} 个文件。"
    if failed:
        msg += "\n\n未能移动的文件：\n" + "\n".join(failed[:15])
    msg += f"\n\n归档位置：\n{destination}"
    messagebox.showinfo("整理完成", msg, parent=root)
    root.destroy()

if __name__ == "__main__":
    try:
        run()
    except Exception:
        err = traceback.format_exc()
        try:
            Path(__file__).with_name("运行错误日志.txt").write_text(err, encoding="utf-8")
        except Exception:
            pass
        try:
            r = tk.Tk()
            r.withdraw()
            messagebox.showerror("程序运行出错", "程序发生错误，详细信息已保存到同目录的“运行错误日志.txt”。\n\n" + err[-1800:])
            r.destroy()
        except Exception:
            print(err)
