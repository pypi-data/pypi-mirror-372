<p align="center">
  <img src="https://raw.githubusercontent.com/LaFTonTechnology/cardlink/main/assets/cardlinkLogo.png" width="300"/>
  <h1 align="center">cardlink</h1>
  <p align="center">Асинхронный Python клиент для <a href="https://cardlink.link/merchant/api">Cardlink API</a></p>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/LaFTonTechnology/cardlink/main/assets/python-version.json" alt="Python"></a>
  <a href="https://pydantic.dev"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json" alt="Pydantic v2"></a>
  <a href="https://docs.aiohttp.org/en/stable/"><img src="https://img.shields.io/badge/aiohttp-v3-2c5bb4?logo=aiohttp" alt="Aiohttp"></a>
</p>

---

## 📌 О проекте

**cardlink** — асинхронный Python клиент для работы с [Cardlink API](https://cardlink.link/merchant/api).  
Позволяет создавать счета, получать ссылки на оплату и обрабатывать платежи полностью асинхронно.

---

## [Документация](https://laftontechnology.github.io/cardlink/)

---

## 💬 Сообщество

Присоединяйтесь к нашему чату в Telegram: [@pythonCardlink](https://t.me/pythonCardlink)

---

## 🛠 Установка

```bash
pip install cardlink
```

## Quick start

```python
import asyncio
from cardlink import CardLink

async def main():
    cl = CardLink(token="YOUR_TOKEN", shop_id="YOUR_SHOP_ID")

    bill = await cl.create_bill(amount=100)
    return bill.link_page_url  # Ссылка для оплаты счёта

if __name__ == "__main__":
    print(asyncio.run(main()))
```


## 📦 Основные возможности

- ✅ Асинхронный клиент на `aiohttp`  
- ✅ Полная поддержка [Cardlink API](https://cardlink.link/merchant/api)  
- ✅ Быстрое создание счетов и получение ссылок для оплаты  
- ✅ Совместимость с Python 3.10+  

---

## 💖 Поддержка проекта

Вы можете поддержать разработку донатом:

| Сеть     | Адрес                                                                 |
|----------|-----------------------------------------------------------------------|
| **TON**  | `UQCekZTSqysK4OUQFovzI31CILQj0GGjnYxBV77HlK2Zv1BM`                    |
| **TRON** | `TVr8bD8toKF14YY46apFgS1PgiBBtvKsfu`                                  |
| **ETH**  | `0x6406D459D592456dA5E78D789b68029EC7950890`                           |

---

## 📝 Лицензия

Проект распространяется под лицензией MIT.

---

## 📌 Контакты и обратная связь

- Telegram: [@pythonCardlink](https://t.me/pythonCardlink)  
- GitHub Issues: открывайте любые баги или предложения прямо в репозитории.
