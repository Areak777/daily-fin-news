# 每日财经新闻盘前纪要

自动抓取每日财经新闻，生成盘前纪要报告并通过邮件推送。

## 功能

- 每天北京时间 **8:50** 自动运行（仅工作日）
- 多源搜索：三大报、财联社、华尔街见闻、韭研公社等
- 输出：HTML 邮件推送到指定邮箱
- 邮件服务：Resend API

## 工作流程

1. **WorkBuddy Agent**（本地）每天 8:50 自动执行：
   - 批量搜索 21 个关键词获取财经新闻
   - 抓取 15+ 篇详细文章
   - 生成 Markdown 报告 + Word 文档
   - 上传 .md 文件到 GitHub 仓库

2. **GitHub Actions** 收到文件后：
   - 将 Markdown 转为精美 HTML 邮件
   - 通过 Resend 发送到指定邮箱

## 手动触发

在 GitHub 仓库页面：
- **Actions** → **每日财经新闻盘前纪要** → **Run workflow**

## Secrets 配置

| Secret | 说明 |
|--------|------|
| RESEND_API_KEY | Resend API 密钥（re_开头） |
| EMAIL_TO | 接收邮箱地址 |
| EMAIL_FROM | 发件邮箱地址 |

## 技术栈

- GitHub Actions
- Resend (邮件 API)
- Python
