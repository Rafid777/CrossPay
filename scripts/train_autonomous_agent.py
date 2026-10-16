"""
Train the CrossPay Autonomous NLP Intent Classifier.
Trains on hundreds of bilingual (EN/ZH) financial queries across 18 banking/fintech intents.
Produces:
  - models/crosspay_intent_classifier.joblib
  - models/training_metrics.json
"""
import sys
import os
import json
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
import joblib

DATASET = [
    # ── 1. get_exchange_rate ──────────────────────────────────────────────────
    ("get_exchange_rate", "What is the exchange rate from BDT to CNY?"),
    ("get_exchange_rate", "Current BDT to CNY exchange rate"),
    ("get_exchange_rate", "What's the PKR to CNY rate today?"),
    ("get_exchange_rate", "Check exchange rate USD to CNY"),
    ("get_exchange_rate", "How much is 1 NGN in CNY?"),
    ("get_exchange_rate", "What is the current foreign exchange rate?"),
    ("get_exchange_rate", "FX rate between Bangladesh Taka and Chinese Yuan"),
    ("get_exchange_rate", "Rate inquiry for PKR to RMB"),
    ("get_exchange_rate", "Exchange rate USD to RMB"),
    ("get_exchange_rate", "EUR to CNY exchange rate today"),
    ("get_exchange_rate", "Show me current currency exchange rate"),
    ("get_exchange_rate", "What is today's FX rate?"),
    ("get_exchange_rate", "查询孟加拉塔卡 BDT 兑人民币汇率"),
    ("get_exchange_rate", "今天的实时汇率是多少"),
    ("get_exchange_rate", "美元兑人民币最新汇率查询"),
    ("get_exchange_rate", "巴基斯坦卢比 PKR 对 CNY 汇率"),
    ("get_exchange_rate", "尼日利亚奈拉 NGN 换算人民币汇率"),
    ("get_exchange_rate", "外汇汇率查询"),
    ("get_exchange_rate", "查一下当前人民币对各币种汇率"),
    ("get_exchange_rate", "请查询最新的 BDT 对人民币 CNY 汇率。"),
    ("get_exchange_rate", "汇率走势如何，现在 1 BDT 等于多少 CNY？"),

    # ── 2. convert_amount ─────────────────────────────────────────────────────
    ("convert_amount", "Convert 1000 BDT to CNY"),
    ("convert_amount", "How much is 50000 BDT in Chinese Yuan?"),
    ("convert_amount", "Convert $500 USD to CNY"),
    ("convert_amount", "How much will I get if I exchange 2000 PKR to CNY?"),
    ("convert_amount", "Convert 100000 NGN to CNY"),
    ("convert_amount", "Calculate currency conversion for 8000 CNY to USD"),
    ("convert_amount", "Convert 250 EUR to CNY"),
    ("convert_amount", "How much is 300 dollars in renminbi?"),
    ("convert_amount", "Convert 1500 USD to Chinese Yuan with fees"),
    ("convert_amount", "换算 1000 美元到人民币是多少钱"),
    ("convert_amount", "把 50000 孟加拉塔卡转成人民币"),
    ("convert_amount", "计算 2000 人民币兑换成美元的净到账金额"),
    ("convert_amount", "500 美元等于多少人民币"),
    ("convert_amount", "将 80000 卢比换算为 CNY"),
    ("convert_amount", "换算 12000 人民币"),

    # ── 3. compare_remittance_options ─────────────────────────────────────────
    ("compare_remittance_options", "Compare remittance options to send $500 USD to China"),
    ("compare_remittance_options", "What is the cheapest way to send money to China?"),
    ("compare_remittance_options", "Compare WeBank Direct vs SWIFT vs Wise"),
    ("compare_remittance_options", "Which remittance provider has the lowest fee?"),
    ("compare_remittance_options", "How should my parents send tuition money from Bangladesh to China?"),
    ("compare_remittance_options", "Compare transfer costs for $1000 tuition transfer"),
    ("compare_remittance_options", "Best money transfer service for international students"),
    ("compare_remittance_options", "WeBank remittance fee comparison"),
    ("compare_remittance_options", "Compare cross-border payment channels to China"),
    ("compare_remittance_options", "Send money home or receive money from abroad cheapest method"),
    ("compare_remittance_options", "我想汇款 $500 美元到中国交学费，请对比各服务商费用和到账速度。"),
    ("compare_remittance_options", "对比跨境汇款渠道费用"),
    ("compare_remittance_options", "微众直通车汇款和传统电汇 SWIFT 哪个更划算？"),
    ("compare_remittance_options", "从海外汇款到中国交学费哪家手续费最低？"),
    ("compare_remittance_options", "对比各家跨境转账到账时间与费率"),
    ("compare_remittance_options", "跨境汇款服务商成本横向评测"),
    ("compare_remittance_options", "哪种方式跨境汇款手续费最便宜？"),

    # ── 4. schedule_tuition_payment ───────────────────────────────────────────
    ("schedule_tuition_payment", "When is the optimal window to pay my tuition?"),
    ("schedule_tuition_payment", "Schedule tuition payment to save on FX"),
    ("schedule_tuition_payment", "Help me find the best date to pay my university tuition"),
    ("schedule_tuition_payment", "Tuition due date is coming, how to optimize FX rate?"),
    ("schedule_tuition_payment", "Help me schedule my tuition payment optimally."),
    ("schedule_tuition_payment", "Recommend tuition payment timing for 8000 CNY"),
    ("schedule_tuition_payment", "When should I convert money for tuition?"),
    ("schedule_tuition_payment", "Optimal tuition schedule"),
    ("schedule_tuition_payment", "根据当前汇率走势，帮我推荐最佳的学费缴纳窗口期。"),
    ("schedule_tuition_payment", "什么时候交学费汇率最划算？"),
    ("schedule_tuition_payment", "智能规划学费缴纳时间窗口"),
    ("schedule_tuition_payment", "下个月学费截止，怎样利用汇率波动省钱缴费？"),
    ("schedule_tuition_payment", "安排学费支付计划"),
    ("schedule_tuition_payment", "学费最优支付时机建议"),

    # ── 5. get_spending_summary ───────────────────────────────────────────────
    ("get_spending_summary", "Show my spending summary for this month"),
    ("get_spending_summary", "How much have I spent so far in October?"),
    ("get_spending_summary", "Show my budget breakdown and expenses"),
    ("get_spending_summary", "Monthly expense report"),
    ("get_spending_summary", "What are my total expenses this month?"),
    ("get_spending_summary", "Check my budget status"),
    ("get_spending_summary", "Spending breakdown by category"),
    ("get_spending_summary", "Did I exceed my monthly budget?"),
    ("get_spending_summary", "查看我本月的各项生活消费支出与预算使用情况。"),
    ("get_spending_summary", "查看本月消费统计和预算使用率"),
    ("get_spending_summary", "我这个月花了多少钱？"),
    ("get_spending_summary", "餐饮、交通、房租各项开销明细汇总"),
    ("get_spending_summary", "查看预算剩余额度"),
    ("get_spending_summary", "本月账单月度汇总"),

    # ── 6. add_expense ────────────────────────────────────────────────────────
    ("add_expense", "Record 50 CNY for lunch"),
    ("add_expense", "Add an expense: 120 CNY for textbooks"),
    ("add_expense", "I spent 35 CNY on metro transport"),
    ("add_expense", "Log expense 80 CNY dinner with friends"),
    ("add_expense", "Record expense 200 CNY groceries"),
    ("add_expense", "Add 500 CNY utilities bill"),
    ("add_expense", "I just paid 15 CNY for coffee"),
    ("add_expense", "Spent 45 CNY on food"),
    ("add_expense", "Record a new expense: 60 CNY transport"),
    ("add_expense", "记一笔支出：食堂吃饭花费 35 元"),
    ("add_expense", "记录消费 80 元 买专业参考书"),
    ("add_expense", "刚才打车花了 42 元人民币，记入交通分类"),
    ("add_expense", "记账 150 元 超市采购日用品"),
    ("add_expense", "添加一笔支出 25 元 奶茶咖啡"),
    ("add_expense", "记一笔 200 元 水电费开销"),

    # ── 7. set_budget_category ────────────────────────────────────────────────
    ("set_budget_category", "Set my food budget to 1500 CNY"),
    ("set_budget_category", "Update transport budget to 300 CNY per month"),
    ("set_budget_category", "Set budget limit for books to 400 CNY"),
    ("set_budget_category", "Change entertainment budget to 200 CNY"),
    ("set_budget_category", "Adjust my monthly dining budget"),
    ("set_budget_category", "设置餐饮每月预算上限为 1200 元"),
    ("set_budget_category", "修改生活费交通预算为 300 元"),
    ("set_budget_category", "把娱乐开销预算设定为 200 CNY"),
    ("set_budget_category", "设定每月预算限额"),

    # ── 8. get_credit_profile ─────────────────────────────────────────────────
    ("get_credit_profile", "What is my credit score?"),
    ("get_credit_profile", "How can an international student build credit history in China?"),
    ("get_credit_profile", "Give me credit building tips for foreigners in China"),
    ("get_credit_profile", "Check my credit tier and milestone"),
    ("get_credit_profile", "How does PBOC credit scoring work for overseas students?"),
    ("get_credit_profile", "How to increase my financial credit score?"),
    ("get_credit_profile", "Tips for improving my credit score"),
    ("get_credit_profile", "作为国际留学生，我在中国有哪些安全合规建立良好征信的方法？"),
    ("get_credit_profile", "查询我的征信积分和信用等级"),
    ("get_credit_profile", "留学生在中国如何积累人行征信记录？"),
    ("get_credit_profile", "提升信用评分的实用建议"),
    ("get_credit_profile", "查看我的信用画像和提分建议"),
    ("get_credit_profile", "中国征信体制对外国留学生的考核机制是什么？"),

    # ── 9. simulate_credit_action ─────────────────────────────────────────────
    ("simulate_credit_action", "Simulate the impact of opening a secured credit card"),
    ("simulate_credit_action", "What happens to my score if I pay tuition early?"),
    ("simulate_credit_action", "Simulate paying on time for 3 months"),
    ("simulate_credit_action", "How many points will I gain by reducing credit utilization?"),
    ("simulate_credit_action", "Simulate reporting rent payments to credit bureau"),
    ("simulate_credit_action", "模拟办理保证金信用卡对征信的提分效果"),
    ("simulate_credit_action", "如果连续3个月按时缴费，我的信用分会涨多少？"),
    ("simulate_credit_action", "模拟提前缴纳学费的提分预测"),
    ("simulate_credit_action", "降低信用卡额度占用率对信用分的影响模拟"),
    ("simulate_credit_action", "将房租支付纳入信用报告会增加多少分？"),

    # ── 10. check_aml_threshold ───────────────────────────────────────────────
    ("check_aml_threshold", "Check if a $12,000 USD transfer will trigger AML reporting requirements."),
    ("check_aml_threshold", "Does a $15,000 transfer trigger anti money laundering checks?"),
    ("check_aml_threshold", "What is the AML threshold for cross-border money transfers?"),
    ("check_aml_threshold", "Will sending $9,500 be flagged for AML?"),
    ("check_aml_threshold", "PBOC AML regulations for large cross-border remittances"),
    ("check_aml_threshold", "Check AML compliance for $20,000"),
    ("check_aml_threshold", "请帮我检查单笔 $12,000 美元的汇款是否会触发外汇反洗钱合规申报？"),
    ("check_aml_threshold", "大额外汇反洗钱申报阈值是多少？"),
    ("check_aml_threshold", "汇款 15000 美元交学费需要向外管局进行大额申报吗？"),
    ("check_aml_threshold", "合规检查：大额资金跨境划转 AML 触发红线"),
    ("check_aml_threshold", "超过1万美元的跨境汇款会有合规审核吗？"),

    # ── 11. check_sanctioned_destination ──────────────────────────────────────
    ("check_sanctioned_destination", "Can I transfer money to Iran?"),
    ("check_sanctioned_destination", "Is North Korea on the sanctions list for financial transfers?"),
    ("check_sanctioned_destination", "Check if remittances to Syria are allowed"),
    ("check_sanctioned_destination", "Check sanctions list for international transfers"),
    ("check_sanctioned_destination", "Are there any sanctioned countries we cannot send money to?"),
    ("check_sanctioned_destination", "Is it safe to transfer money to Bangladesh?"),
    ("check_sanctioned_destination", "制裁国家跨境转账合规核查"),
    ("check_sanctioned_destination", "可以向伊朗或朝鲜汇款吗？"),
    ("check_sanctioned_destination", "查询受国际金融制裁的国家名单"),
    ("check_sanctioned_destination", "汇款目的地合规安全筛查"),

    # ── 12. get_fx_trend ──────────────────────────────────────────────────────
    ("get_fx_trend", "Show me the 30-day FX trend for BDT to CNY"),
    ("get_fx_trend", "Historical exchange rate trend chart"),
    ("get_fx_trend", "How has the exchange rate fluctuated over the last month?"),
    ("get_fx_trend", "FX rate volatility chart"),
    ("get_fx_trend", "查看近30天人民币汇率历史波动趋势"),
    ("get_fx_trend", "显示 BDT 对 CNY 的走势图"),
    ("get_fx_trend", "近期汇率波动历史曲线"),

    # ── 13. get_spending_trend ────────────────────────────────────────────────
    ("get_spending_trend", "Show my 6-month spending trend"),
    ("get_spending_trend", "Historical monthly spending trajectory"),
    ("get_spending_trend", "How much have I spent over the last half year?"),
    ("get_spending_trend", "查看过去 6 个月的月度消费变化趋势"),
    ("get_spending_trend", "半年历史开销变化图"),
    ("get_spending_trend", "我的各月消费趋势分析"),

    # ── 14. get_credit_trend ──────────────────────────────────────────────────
    ("get_credit_trend", "Show my credit score progression over time"),
    ("get_credit_trend", "Credit score history curve"),
    ("get_credit_trend", "How has my credit score grown in China?"),
    ("get_credit_trend", "查看我的信用积分成长历程曲线"),
    ("get_credit_trend", "历史征信评分变化趋势"),
    ("get_credit_trend", "信用分提升轨迹"),

    # ── 15. get_worldbank_remittance ──────────────────────────────────────────
    ("get_worldbank_remittance", "What is Bangladesh's remittance outflow according to World Bank?"),
    ("get_worldbank_remittance", "World Bank remittance statistics for Pakistan"),
    ("get_worldbank_remittance", "How much money flows into Nigeria according to official data?"),
    ("get_worldbank_remittance", "Global remittance macro market size"),
    ("get_worldbank_remittance", "World Bank migration and remittances report data"),
    ("get_worldbank_remittance", "世界银行官方汇款宏观数据查询"),
    ("get_worldbank_remittance", "孟加拉国每年向境外汇出多少留学生学费与汇款？"),
    ("get_worldbank_remittance", "世界银行统计的全球跨境汇款流向与规模"),
    ("get_worldbank_remittance", "巴基斯坦与尼日利亚的外汇流入数据"),

    # ── 16. faq_banking_china ─────────────────────────────────────────────────
    ("faq_banking_china", "How can an international student open a bank account in China?"),
    ("faq_banking_china", "How to link my foreign bank card to WeChat Pay and Alipay?"),
    ("faq_banking_china", "What documents are required to open a WeBank or ICBC account in China?"),
    ("faq_banking_china", "Can foreigners use WeChat Pay and Alipay in China without a Chinese card?"),
    ("faq_banking_china", "SAFE foreign exchange quota for overseas students in China"),
    ("faq_banking_china", "留学生在中国如何办理银行卡开户？"),
    ("faq_banking_china", "境外信用卡如何绑定微信支付和支付宝？"),
    ("faq_banking_china", "外国人在中国使用移动支付的完整指南"),
    ("faq_banking_china", "国家外汇管理局对留学生购汇与结汇的政策规定"),

    # ── 17. greeting ──────────────────────────────────────────────────────────
    ("greeting", "Hello"),
    ("greeting", "Hi"),
    ("greeting", "Good morning"),
    ("greeting", "Hey there CrossPay"),
    ("greeting", "Who are you?"),
    ("greeting", "你好"),
    ("greeting", "您好"),
    ("greeting", "在吗"),
    ("greeting", "早上好"),
    ("greeting", "介绍一下你自己"),

    # ── 18. help ──────────────────────────────────────────────────────────────
    ("help", "What can you do?"),
    ("help", "Show me the available commands"),
    ("help", "Help"),
    ("help", "How do I use this app?"),
    ("help", "你能帮我做什么？"),
    ("help", "功能介绍"),
    ("help", "使用帮助与指令大全"),
    ("help", "请问有哪些可用功能？"),
]

def train_model():
    print("=" * 60)
    print("CrossPay Autonomous NLP Model Training")
    print(f"Total labeled training examples: {len(DATASET)}")
    print("=" * 60)

    texts = [item[1] for item in DATASET]
    labels = [item[0] for item in DATASET]

    unique_intents = sorted(list(set(labels)))
    print(f"Unique intents ({len(unique_intents)}):")
    for i, intent in enumerate(unique_intents, 1):
        count = labels.count(intent)
        print(f"  {i:2d}. {intent:<30} ({count} samples)")

    # Build Pipeline: Char-WB + Word n-grams for dual English + Chinese support
    # analyzer='char_wb' with ngram_range (2, 5) is robust across both Chinese characters and English words
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 5),
            min_df=1,
            sublinear_tf=True
        )),
        ('clf', LogisticRegression(
            C=10.0,
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        ))
    ])

    # Stratified K-Fold Cross Validation
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, texts, labels, cv=cv, scoring='accuracy')
    mean_acc = float(np.mean(scores))
    print(f"\n3-Fold Stratified Cross-Validation Accuracy: {mean_acc * 100:.2f}%")

    # Fit on all data
    pipeline.fit(texts, labels)

    # Ensure models directory exists
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "crosspay_intent_classifier.joblib")
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved successfully to: {model_path}")

    # Save metrics metadata
    metrics = {
        "model_name": "CrossPay-Autonomous-FinIntent-v1",
        "training_samples": len(DATASET),
        "num_classes": len(unique_intents),
        "intents": unique_intents,
        "cv_accuracy_pct": round(mean_acc * 100, 2),
        "vectorizer": "TF-IDF char_wb (2-5 n-grams)",
        "classifier": "LogisticRegression(C=10.0, balanced)",
        "offline_capable": True,
        "cloud_api_required": False,
    }
    metrics_path = os.path.join(model_dir, "training_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"Metrics saved to: {metrics_path}")

    # Sanity checks
    print("\nSanity Check Inference:")
    test_queries = [
        "What's the current BDT to CNY rate?",
        "Compare remittance options to send $500",
        "Record 45 CNY for lunch",
        "Can I transfer money to Iran?",
        "Will $15000 transfer trigger AML checks?",
        "How can an international student open a bank account in China?",
        "根据当前汇率走势，帮我推荐最佳的学费缴纳窗口期。",
        "世界银行官方汇款数据孟加拉国每年汇出多少？",
    ]
    for q in test_queries:
        pred = pipeline.predict([q])[0]
        probs = pipeline.predict_proba([q])[0]
        conf = float(np.max(probs))
        print(f"  Query: '{q}'\n  -> Predicted: [{pred}] (confidence: {conf*100:.1f}%)\n")

if __name__ == "__main__":
    train_model()
