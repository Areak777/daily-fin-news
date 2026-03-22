# -*- coding: utf-8 -*-
"""
生成报告 - 从 WorkBuddy 自动化生成的 Markdown 创建邮件报告
GitHub Actions 环境下运行时，从预置的 report 模板生成
"""
import os
import sys
import re
from datetime import datetime, timedelta
import requests


def get_trade_date(target_str=""):
    """获取最近的交易日日期"""
    if target_str:
        try:
            dt = datetime.strptime(target_str, "%Y%m%d")
            return target_str
        except ValueError:
            pass
    
    today = datetime.now()
    # If weekend, go back to Friday
    if today.weekday() >= 5:
        days_back = today.weekday() - 4  # Sat=5->1, Sun=6->2
        today = today - timedelta(days=days_back)
    return today.strftime("%Y%m%d")


def generate_placeholder_report(trade_date):
    """生成占位报告（当无法从外部获取时使用）"""
    dt = datetime.strptime(trade_date, "%Y%m%d")
    date_str = dt.strftime("%Y年%m月%d日")
    weekday = ["周一","周二","周三","周四","周五","周六","周日"][dt.weekday()]
    
    content = f"""# 每日财经新闻盘前纪要

> **报告日期**：{date_str}（{weekday}）
> **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> **数据来源**：三大报、财联社、华尔街见闻、韭研公社等公开搜索

---

## 一、三大报精华

> 今日三大报内容请关注以下渠道：
> - 中国证券报：https://www.cs.com.cn
> - 上海证券报：https://www.cnstock.com
> - 证券时报：https://www.stse.com.cn

---

## 二、盘前个股重要公告

> 公告数据请关注以下渠道：
> - 巨潮资讯网：http://www.cninfo.com.cn
> - 上交所公告：http://www.sse.com.cn
> - 深交所公告：http://www.szse.cn

---

## 三、热门题材

> 题材分析请关注：
> - 韭研公社：https://jiuyangongshe.com/square_hot

---

## 四、隔夜外盘

> 外盘数据请关注：
> - 新浪财经美股：https://finance.sina.com.cn/stock/usstock

---

## 五、重要事件

---

## 六、昨日热点回顾

---

## 七、次日盘前关注清单

---

> ⚠️ **注意**：此为自动化占位报告。完整版报告由 WorkBuddy Agent 在本地生成后上传。
> 请查看邮件附件或访问本地 output 目录获取完整报告。

> 免责声明：本报告信息来源于公开搜索结果，仅供学习参考，不构成投资建议。
"""
    return content


def download_report_from_source(trade_date):
    """尝试从预配置的源下载已生成的报告"""
    # Report will be uploaded by WorkBuddy automation
    # This is a placeholder for the download logic
    return None


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else ""
    trade_date = get_trade_date(target)
    
    os.makedirs("output", exist_ok=True)
    output_path = f"output/report_{trade_date}.md"
    
    # Try to download pre-generated report first
    content = download_report_from_source(trade_date)
    
    if not content:
        content = generate_placeholder_report(trade_date)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    main()
