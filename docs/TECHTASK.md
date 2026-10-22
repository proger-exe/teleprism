# Техническое задание

# TelePrism

Telegram-бот для продажи Telegram Stars с оплатой криптовалютой и ручным выполнением заказов менеджерами.

---

# 1. Концепция проекта

TelePrism представляет собой полностью нативного Telegram-бота без Mini App и без внешнего пользовательского сайта.

Пользователь взаимодействует с сервисом через:

* сообщения;
* inline-кнопки;
* постоянную reply-клавиатуру;
* редактируемые карточки;
* изображения с QR-кодами;
* стандартные Telegram-команды.

Основной сценарий:

```text
Пользователь выбирает количество Stars
→ указывает получателя
→ получает реквизиты USDT TRC20
→ оплачивает заказ
→ TelePrism обнаруживает оплату через polling CryptAPI
→ заказ попадает менеджеру
→ менеджер вручную отправляет Stars
→ пользователь получает уведомление
```

В первой версии Stars не отправляются автоматически.

Причина: Bot API не предоставляет обычному боту прямой метод пополнения баланса Telegram Stars произвольного пользователя. Покупка или подарок Stars выполняются через клиентский платёжный flow Telegram либо Fragment, поэтому заказ исполняется менеджером через пользовательский Telegram-аккаунт.

---

# 2. Основные технические решения

## 2.1. Telegram updates

Используется только long polling:

```python
await dispatcher.start_polling(bot)
```

Webhook Telegram Bot API не используется.

Для одного токена допускается только один polling-процесс. Поэтому TelePrism разворачивается в одном экземпляре без горизонтального масштабирования.

## 2.2. Платёжные обновления

Используется только polling CryptAPI Logs API.

TelePrism:

* не принимает платёжные webhook-запросы;
* не поднимает HTTP API;
* не содержит webhook handlers;
* не меняет статус оплаты по входящим HTTP-запросам;
* самостоятельно опрашивает CryptAPI;
* считает SQLite единственным источником состояния заказа.

## 2.3. База данных

Используется SQLite.

Режим:

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
PRAGMA synchronous = NORMAL;
```

SQLite подходит для проекта, поскольку:

* работает один экземпляр приложения;
* ожидается умеренное количество заказов;
* нет нескольких одновременно работающих worker-нод;
* большинство операций короткие;
* запись централизована внутри одного процесса.

## 2.4. Redis

Redis не используется.

Не используются:

* Redis FSM;
* Redis cache;
* Redis locks;
* Redis queues;
* Redis pub/sub;
* Redis rate limiting.

Все важные данные хранятся в SQLite.

## 2.5. WebApp

WebApp и Mini App не используются.

Запрещены:

* `web_app` кнопки;
* отдельный frontend;
* Telegram Mini App;
* авторизация через `initData`;
* внешняя пользовательская панель.

---

# 3. Базовые зависимости

## 3.1. Основа проекта

Использовать:

```text
github.com/Forden/aiogram-bot-template
```

Поверх базового шаблона подключить:

```text
github.com/Aidenable/Raito
```

Raito используется для:

* загрузки routers;
* регистрации команд;
* ролей;
* генерации клавиатур;
* пагинации;
* rate limiting;
* lifecycle hooks;
* внутренних инструментов разработки.

Бизнес-логика, платежи и работа с заказами не должны зависеть от внутреннего состояния Raito.

## 3.2. Технологический стек

```text
Python 3.11+
aiogram 3.25+
Raito 1.4+
aiosqlite
aiohttp
Pydantic 2
pydantic-settings
structlog
orjson
tenacity
qrcode
Pillow
pytest
pytest-asyncio
Ruff
mypy
```

## 3.3. Хранение зависимостей

Использовать `pyproject.toml`.

Допускается:

* Poetry;
* uv.

Предпочтительно использовать `uv` с lock-файлом.

---

# 4. UX-ориентиры

В качестве продуктовых ориентиров используются крупные Telegram-сервисы:

* `@CryptoBot`, около 1,5–1,6 млн активных пользователей в месяц;
* `@Tribute`, около 1,7 млн активных пользователей в месяц;
* `@Wallet`, крупный встроенный криптовалютный сервис Telegram.

Интерфейс не копирует их буквально, но использует те же базовые принципы:

1. Пользователь сразу видит основное действие.
2. Один экран отвечает за одну задачу.
3. Навигация выполняется кнопками, а не командами.
4. Текущая карточка редактируется вместо отправки десятков новых сообщений.
5. На каждом шаге доступны «Назад» и «Отмена».
6. Перед финансовым действием показывается итоговое подтверждение.
7. Статус заказа отображается одной понятной карточкой.
8. Пользователь не должен помнить номер команды или синтаксис.
9. Свободный текст используется только там, где кнопками задачу решить нельзя.

Telegram официально разделяет reply-клавиатуры для глобальных действий и inline-клавиатуры для локальной навигации внутри конкретного сообщения.

---

# 5. Визуальный дизайн

## 5.1. Общий стиль

Название:

```text
TelePrism
```

Характер интерфейса:

* чистый;
* технологичный;
* спокойный;
* без визуального мусора;
* без чрезмерного количества эмодзи;
* без текста в стиле криптоказино;
* без кислотной рекламы;
* без бессмысленных «LIVE», «FAST» и прочей маркетинговой шелухи.

## 5.2. Визуальная тема

Основные ассоциации:

* призма;
* свет;
* спектр;
* прозрачность;
* цифровой платёж;
* Telegram Stars.

Основные символы:

```text
✦ Stars
◈ TelePrism
◆ заказ
✓ выполнено
⏳ ожидание
⚠ проблема
```

Не использовать в каждом сообщении по семь разных эмодзи. Один экран должен содержать максимум два-три смысловых символа.

## 5.3. Формат заголовков

Пример:

```text
◈ TelePrism

Покупка Telegram Stars
```

Или:

```text
◆ Заказ #1042

Статус: ожидается оплата
```

## 5.4. Карточки

Каждый экран состоит из:

1. заголовка;
2. одного короткого пояснения;
3. данных;
4. основной кнопки;
5. вторичных действий.

Пример:

```text
◆ Заказ #1042

Получатель: @username
Количество: 500 Stars
К оплате: 8.75 USDT
Сеть: TRC20

Проверьте получателя перед оплатой.
После отправки изменить username будет нельзя.
```

## 5.5. Цветные кнопки

Использовать актуальные стили Telegram:

* `primary` — синяя;
* `success` — зелёная;
* `danger` — красная;
* без стиля — нейтральная.

Telegram рекомендует `primary` для основных действий, `success` для положительных и `danger` для разрушительных.

### Primary

```text
Купить Stars
Продолжить
Проверить оплату
Взять заказ
Открыть заказ
```

### Success

```text
Подтвердить заказ
Начать выполнение
Stars отправлены
Подтвердить получение
```

### Danger

```text
Отменить заказ
Сообщить о проблеме
Заблокировать
Отклонить
```

### Neutral

```text
Назад
Мои заказы
Поддержка
Обновить
```

Цвет не является единственным признаком назначения кнопки. Текст должен быть понятным и на старых клиентах Telegram.

---

# 6. Навигационная модель

## 6.1. Главное меню

Постоянная reply-клавиатура:

```text
[ ✦ Купить Stars ]
[ ◆ Мои заказы ] [ ◈ Прайс ]
[ Поддержка ]     [ Информация ]
```

Кнопка покупки занимает отдельную широкую строку.

## 6.2. Inline-навигация

Inline-кнопки используются внутри:

* оформления заказа;
* карточки оплаты;
* истории заказов;
* карточки менеджера;
* административных экранов;
* настроек.

## 6.3. Один активный экран

Для каждого пользователя хранится:

```text
current_screen_chat_id
current_screen_message_id
```

При переходах бот по возможности вызывает:

```python
edit_message_text()
edit_message_caption()
edit_message_reply_markup()
```

Новое сообщение отправляется только если:

* старое невозможно отредактировать;
* нужно отправить QR-код;
* пользователь должен получить отдельное уведомление;
* изменился тип контента;
* прошлое сообщение удалено.

## 6.4. Возврат в меню

На каждом вложенном экране должна быть кнопка:

```text
← Назад
```

На финансовых этапах дополнительно:

```text
Отменить заказ
```

---

# 7. Пользовательский flow

# 7.1. Первый запуск

Команда:

```text
/start
```

Бот:

1. создаёт пользователя;
2. сохраняет Telegram ID;
3. сохраняет username;
4. сохраняет имя и язык;
5. показывает приветствие;
6. показывает главное меню.

Текст:

```text
◈ TelePrism

Покупка Telegram Stars с оплатой в криптовалюте.

Выберите количество Stars, оплатите заказ и дождитесь выполнения менеджером.
```

Кнопки:

```text
[ ✦ Купить Stars ]
[ ◆ Мои заказы ] [ ◈ Прайс ]
[ Поддержка ]     [ Как это работает ]
```

---

# 7.2. Начало покупки

Пользователь нажимает:

```text
✦ Купить Stars
```

Экран:

```text
✦ Покупка Stars

Кому нужно отправить Stars?
```

Кнопки:

```text
[ Мне ]
[ Другому пользователю ]
[ ← Главное меню ]
```

Кнопка «Мне» доступна только если у пользователя есть username.

Если username отсутствует:

```text
У вашего аккаунта нет публичного username.

Укажите username получателя вручную.
```

---

# 7.3. Выбор получателя

## Покупка себе

Бот использует:

```text
message.from_user.username
```

Затем показывает подтверждение:

```text
Получатель: @shelby

Это правильный аккаунт?
```

Кнопки:

```text
[ Да, продолжить ]
[ Указать другой ]
[ ← Назад ]
```

## Покупка другому

Бот просит отправить:

```text
@username
```

Допускаются форматы:

```text
username
@username
https://t.me/username
t.me/username
```

Все значения нормализуются до:

```text
username
```

Проверки:

```text
длина 5–32 символа;
латинские буквы;
цифры;
нижнее подчёркивание;
без пробелов;
без специальных символов;
без двойной ссылки;
не bot invite link;
не private invite link.
```

Бот не должен утверждать, что пользователь существует, если существование невозможно проверить через Bot API.

После ввода:

```text
Получатель: @username

Проверьте написание.
После оплаты получателя изменить нельзя.
```

Кнопки:

```text
[ Всё верно ]
[ Изменить ]
[ ← Назад ]
```

---

# 7.4. Выбор количества Stars

Экран:

```text
✦ Выберите количество

Чем больше пакет, тем ниже цена за одну Star.
```

Кнопки в две колонки:

```text
[ 50 Stars ]   [ 100 Stars ]
[ 250 Stars ]  [ 500 Stars ]
[ 1 000 Stars ][ 2 500 Stars ]
[ Другое количество ]
[ ← Назад ]
```

Пакеты хранятся в SQLite и редактируются администратором.

Для каждого пакета можно задать собственную цену.

Пример:

```text
50 Stars    — 1.20 USDT
100 Stars   — 2.20 USDT
250 Stars   — 5.10 USDT
500 Stars   — 9.80 USDT
1000 Stars  — 18.90 USDT
```

## Произвольное количество

Пользователь нажимает:

```text
Другое количество
```

Бот просит:

```text
Введите количество Stars числом.

Минимум: 50
Максимум: 10 000
```

Проверяется:

* целое число;
* минимум;
* максимум;
* допустимый шаг;
* существование активного тарифа.

---

# 7.5. Подтверждение заказа

Экран:

```text
◆ Новый заказ

Получатель: @username
Количество: 500 Stars
Стоимость: 9.80 USDT
Сеть оплаты: TRC20
Срок оплаты: 30 минут
Обычное выполнение: до 15 минут после оплаты

Проверьте данные перед созданием счёта.
```

Кнопки:

```text
[ Подтвердить заказ ]
[ Изменить количество ]
[ Изменить получателя ]
[ Отменить ]
```

Стили:

```text
Подтвердить заказ → success
Отменить → danger
```

После подтверждения:

1. создаётся заказ;
2. фиксируется стоимость;
3. создаётся платёж;
4. запрашивается CryptAPI address;
5. формируется QR-код;
6. открывается платёжный экран.

---

# 7.6. Экран оплаты

Бот отправляет QR-код отдельным изображением.

Caption:

```text
◆ Заказ #1042

Отправьте ровно:

9.80 USDT

Сеть: TRC20
Адрес:
TXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Осталось: 29:42

Не отправляйте токены другой сети.
Комиссия вашей биржи не должна уменьшать сумму перевода.
```

Кнопки:

```text
[ Скопировать адрес ]
[ Скопировать сумму ]
[ Проверить оплату ]
[ Отменить заказ ]
```

Использовать `CopyTextButton`, если его поддерживает установленная версия aiogram и Telegram-клиент.

QR должен содержать адрес.

Сумму всё равно необходимо отображать текстом, поскольку некоторые кошельки игнорируют сумму, встроенную в QR-код.

## Поведение кнопки проверки

При нажатии:

```text
Проверить оплату
```

бот:

1. проверяет cooldown;
2. выполняет немедленный запрос CryptAPI Logs;
3. сохраняет найденные транзакции;
4. обновляет карточку;
5. отвечает callback notification.

Cooldown:

```text
5 секунд
```

---

# 7.7. Оплата обнаружена

Если найдена неподтверждённая транзакция:

```text
◆ Заказ #1042

Оплата обнаружена.
Ожидаются подтверждения сети.

Получено: 9.80 USDT
Подтверждений: 0
```

Статус:

```text
PAYMENT_DETECTED
```

Кнопки:

```text
[ Обновить ]
[ Мои заказы ]
```

---

# 7.8. Частичная оплата

Если получено меньше необходимой суммы:

```text
◆ Заказ #1042

Получена неполная оплата.

Получено: 8.00 USDT
Не хватает: 1.80 USDT

Отправьте недостающую сумму на тот же адрес.
```

Статус:

```text
PARTIALLY_PAID
```

Пользователь может доплатить несколькими транзакциями.

Система суммирует подтверждённые транзакции по уникальным `txid_in`.

---

# 7.9. Полная оплата

После достаточной подтверждённой оплаты:

```text
✓ Оплата подтверждена

Заказ #1042 передан менеджеру.

Получатель: @username
Количество: 500 Stars
Ориентировочное выполнение: до 15 минут
```

Статус заказа:

```text
QUEUED
```

Кнопки:

```text
[ Открыть заказ ]
[ Мои заказы ]
[ Поддержка ]
```

---

# 7.10. Заказ выполняется

Когда менеджер берёт заказ:

```text
◆ Заказ #1042

Статус: выполняется менеджером

Получатель: @username
Количество: 500 Stars
```

Имя и Telegram ID менеджера пользователю не показываются.

---

# 7.11. Заказ выполнен

После завершения:

```text
✓ Заказ выполнен

Заказ: #1042
Получатель: @username
Отправлено: 500 Stars

Проверьте баланс Telegram Stars.
```

Кнопки:

```text
[ Stars получены ]
[ Есть проблема ]
[ Купить ещё ]
```

## Подтверждение пользователем

При нажатии:

```text
Stars получены
```

сохраняется:

```text
customer_confirmed_at
```

Статус заказа остаётся:

```text
COMPLETED
```

## Проблема

Пользователь выбирает:

```text
Stars не пришли
Отправлено не тому пользователю
Получено неверное количество
Другая проблема
```

Создаётся обращение в поддержку.

---

# 8. История заказов

Раздел:

```text
◆ Мои заказы
```

Показывать последние заказы пагинацией.

Карточка:

```text
#1042 · 500 Stars
@username

✓ Выполнен
9.80 USDT
21 июля, 02:15
```

Статусы:

```text
⏳ Ожидает оплаты
◌ Оплата обнаружена
◒ Оплачен частично
✓ Оплачен
◆ В очереди
◆ Выполняется
✓ Выполнен
× Отменён
⌛ Истёк
⚠ Проблема
```

Кнопки:

```text
[ Открыть ]
[ ‹ ] [ 2 / 5 ] [ › ]
[ ← Главное меню ]
```

Пагинацию реализовать через Raito.

---

# 9. Flow менеджера

# 9.1. Менеджерская очередь

После подтверждения оплаты бот отправляет карточку в выделенную Telegram-группу менеджеров.

Пример:

```text
◆ Новый оплаченный заказ #1042

Stars: 500
Получатель: @username
Покупатель: @buyer
Оплачено: 9.80 USDT
Время оплаты: 02:15
В очереди: 00:01
```

Кнопки:

```text
[ Взять заказ ]
[ Открыть детали ]
```

`Взять заказ` имеет стиль `primary`.

---

# 9.2. Атомарное назначение

Назначение выполняется одним SQL-запросом:

```sql
UPDATE orders
SET
    status = 'ASSIGNED',
    assigned_manager_id = ?,
    assigned_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?
  AND status = 'QUEUED'
  AND assigned_manager_id IS NULL
RETURNING *;
```

Запрос выполнять внутри:

```sql
BEGIN IMMEDIATE;
```

Только один менеджер может получить заказ.

Остальные получают:

```text
Заказ уже взят другим менеджером.
```

---

# 9.3. Карточка назначенного заказа

После назначения карточка в группе редактируется:

```text
◆ Заказ #1042

Статус: взят в работу
Менеджер: @manager
Stars: 500
Получатель: @username
```

Кнопки:

```text
[ Начать выполнение ]
[ Вернуть в очередь ]
[ Проблема ]
```

---

# 9.4. Начало выполнения

Менеджер нажимает:

```text
Начать выполнение
```

Статус:

```text
PROCESSING
```

Карточка:

```text
◆ Заказ #1042

Получатель: @username
Количество: 500 Stars

Откройте профиль получателя и выполните отправку через официальный Telegram-клиент или Fragment.
```

Кнопки:

```text
[ Открыть @username ]
[ Stars отправлены ]
[ Возникла проблема ]
```

Кнопка `Открыть @username` содержит URL:

```text
https://t.me/username
```

---

# 9.5. Завершение

Менеджер нажимает:

```text
Stars отправлены
```

Бот требует повторное подтверждение:

```text
Подтвердите выполнение.

Получатель: @username
Количество: 500 Stars

Отменить это действие сможет только администратор.
```

Кнопки:

```text
[ Подтвердить выполнение ]
[ Назад ]
```

После подтверждения:

```text
status = COMPLETED
completed_at = current time
completed_by = manager ID
```

Пользователю отправляется уведомление.

---

# 9.6. Доказательство выполнения

Настройка:

```text
REQUIRE_MANAGER_PROOF=false
```

Если включена, перед завершением менеджер должен отправить:

* скриншот;
* фотографию;
* документ.

Сохраняется Telegram `file_id`.

Файл не скачивается на сервер без необходимости.

---

# 9.7. Проблема при выполнении

Причины:

```text
Пользователь не найден
Telegram не позволяет отправить Stars
Неверный username
Недоступна нужная сумма
Проблема с аккаунтом менеджера
Требуется администратор
Другое
```

Статус:

```text
ISSUE
```

Администратор получает уведомление.

---

# 10. Административный flow

Команда:

```text
/admin
```

Главный экран:

```text
◈ TelePrism Admin

Заказов сегодня: 42
Оплачено: 38
В очереди: 3
В работе: 1
Проблемных: 0
Выручка: 412.80 USDT
```

Кнопки:

```text
[ Заказы ]      [ Платежи ]
[ Тарифы ]      [ Менеджеры ]
[ Пользователи ][ Статистика ]
[ Настройки ]   [ Журнал ]
```

## 10.1. Заказы

Фильтры:

```text
Новые
В очереди
В работе
Выполненные
Проблемные
Отменённые
Все
```

Администратор может:

* открыть заказ;
* назначить менеджера;
* снять менеджера;
* вернуть в очередь;
* завершить вручную;
* отменить;
* пометить проблемным;
* добавить внутренний комментарий.

Каждое действие записывается в audit log.

## 10.2. Тарифы

Администратор может:

* создать пакет;
* изменить пакет;
* выключить пакет;
* изменить минимальное количество;
* изменить максимальное количество;
* изменить цену произвольного количества;
* изменить fixed fee;
* изменить срок оплаты.

Изменение тарифа не влияет на уже созданные заказы.

## 10.3. Менеджеры

Владелец может:

* добавить менеджера по Telegram ID;
* выключить менеджера;
* назначить администратора;
* снять роль;
* посмотреть статистику;
* посмотреть активные заказы.

## 10.4. Режим обслуживания

При включении:

* новые заказы не создаются;
* оплаченные заказы продолжают выполняться;
* менеджеры сохраняют доступ;
* пользователи видят сообщение об обслуживании.

---

# 11. Роли

```text
USER
MANAGER
ADMIN
OWNER
```

## USER

* покупка;
* история;
* поддержка.

## MANAGER

* очередь;
* назначенные заказы;
* выполнение;
* история собственных заказов.

## ADMIN

* все заказы;
* платежи;
* тарифы;
* пользователи;
* ручные изменения статусов.

## OWNER

* роли;
* глобальные настройки;
* служебные функции Raito;
* экспорт;
* полный audit log.

Raito используется для фильтрации handler-ов по ролям.

Роль пользователя хранится в SQLite, а не внутри памяти Raito.

---

# 12. Статусы заказа

```text
DRAFT
AWAITING_PAYMENT
PAYMENT_DETECTED
PARTIALLY_PAID
PAID
QUEUED
ASSIGNED
PROCESSING
COMPLETED
CANCELED
EXPIRED
ISSUE
REFUND_REQUIRED
```

## Переходы

```text
DRAFT
├── AWAITING_PAYMENT
└── CANCELED

AWAITING_PAYMENT
├── PAYMENT_DETECTED
├── PARTIALLY_PAID
├── PAID
├── CANCELED
└── EXPIRED

PAYMENT_DETECTED
├── PARTIALLY_PAID
├── PAID
├── ISSUE
└── EXPIRED

PARTIALLY_PAID
├── PAID
├── ISSUE
└── EXPIRED

PAID
└── QUEUED

QUEUED
├── ASSIGNED
└── ISSUE

ASSIGNED
├── PROCESSING
├── QUEUED
└── ISSUE

PROCESSING
├── COMPLETED
└── ISSUE

ISSUE
├── QUEUED
├── PROCESSING
├── REFUND_REQUIRED
└── CANCELED
```

Любой переход выполняется только через:

```python
OrderService.transition()
```

Прямое изменение `orders.status` из handler запрещено.

---

# 13. Статусы платежа

```text
CREATING
WAITING
DETECTED
PARTIALLY_PAID
CONFIRMED
OVERPAID
LATE_PAID
EXPIRED
FAILED
```

---

# 14. CryptAPI: polling-only интеграция

# 14.1. Ограничение CryptAPI

CryptAPI требует параметр:

```text
callback
```

при создании адреса.

Также Logs API требует передать тот же callback URL, который использовался при создании адреса.

Поэтому TelePrism использует callback URL исключительно как идентификатор платёжного адреса.

TelePrism:

* не принимает callback;
* не анализирует callback;
* не меняет статус по callback;
* не имеет webhook endpoint.

## 14.2. Passive callback sink

В конфигурации задаётся:

```env
CRYPTAPI_CALLBACK_SINK=https://ack.example.com/cryptapi
```

Для каждого платежа формируется уникальный URL:

```text
https://ack.example.com/cryptapi?payment_id=<uuid>&nonce=<random>
```

Passive sink должен всегда возвращать:

```text
HTTP 200
*ok*
```

Он:

* не обращается к SQLite;
* не содержит бизнес-логики;
* не отправляет события TelePrism;
* не идентифицирует оплату;
* только прекращает повторные запросы CryptAPI.

Это не webhook-интеграция приложения. Состояние платежа определяется исключительно polling worker.

Если даже такой пассивный ACK URL запрещён, необходимо заменить CryptAPI на провайдера, который создаёт адрес без callback.

## 14.3. Создание адреса

Запрос:

```text
GET https://api.cryptapi.io/trc20/usdt/create/
```

Параметры:

```text
address=<wallet>
callback=<unique callback sink URL>
confirmations=1
pending=1
```

Ответ:

```json
{
  "address_in": "...",
  "address_out": "...",
  "callback_url": "...",
  "minimum_transaction_coin": 1,
  "status": "success"
}
```

CryptAPI возвращает уникальный входящий адрес и минимальную допустимую сумму транзакции.

Сохранить:

```text
address_in
address_out
callback_url
minimum_transaction_coin
ticker
expected_amount
expires_at
```

## 14.4. Polling Logs API

Запрос:

```text
GET https://api.cryptapi.io/trc20/usdt/logs/
```

Параметр:

```text
callback=<exact stored callback URL>
```

Ответ содержит:

* `address_in`;
* `address_out`;
* список callbacks;
* `txid_in`;
* `value_coin`;
* `confirmations`;
* `pending`;
* `confirmed`;
* `result`;
* сведения о forwarding transaction.

## 14.5. Интервалы polling

Для активного счёта:

```text
первые 5 минут: каждые 10 секунд
5–30 минут: каждые 20 секунд
после истечения: каждые 2 минуты
grace period: 24 часа
после grace period: не опрашивать автоматически
```

Настройки:

```env
PAYMENT_POLL_INITIAL_INTERVAL=10
PAYMENT_POLL_NORMAL_INTERVAL=20
PAYMENT_POLL_EXPIRED_INTERVAL=120
PAYMENT_GRACE_PERIOD_HOURS=24
```

## 14.6. Ограничение параллелизма

Одновременно выполнять не более:

```text
5 запросов
```

Использовать:

```python
asyncio.Semaphore(5)
```

## 14.7. Обработка транзакций

Для каждого callback item:

1. извлечь `txid_in`;
2. проверить наличие в `payment_transactions`;
3. сохранить новую транзакцию;
4. обновить confirmations;
5. пересчитать суммы;
6. определить новый статус.

Уникальность:

```sql
UNIQUE(ticker, txid_in)
```

## 14.8. Расчёт оплаты

```text
confirmed_total =
    сумма value_coin всех подтверждённых txid

pending_total =
    сумма value_coin всех неподтверждённых txid
```

Сравнение выполнять через `Decimal`.

```text
confirmed_total >= expected_amount
```

## 14.9. Полная оплата

```text
confirmed_total >= expected_amount
```

Результат:

```text
payment = CONFIRMED
order = PAID
order = QUEUED
```

## 14.10. Частичная оплата

```text
0 < confirmed_total < expected_amount
```

Результат:

```text
payment = PARTIALLY_PAID
order = PARTIALLY_PAID
```

Пользователь может доплатить на тот же адрес.

## 14.11. Переплата

```text
confirmed_total > expected_amount + tolerance
```

Результат:

```text
payment = OVERPAID
order = PAID
order = QUEUED
```

Переплата фиксируется:

```text
overpaid_amount = confirmed_total - expected_amount
```

## 14.12. Поздняя оплата

Если деньги поступили после `expires_at`:

```text
payment = LATE_PAID
order = ISSUE
```

Администратор принимает решение вручную.

## 14.13. Ошибки CryptAPI

Использовать retry:

```text
3 попытки
экспоненциальная задержка
1 → 2 → 4 секунды
```

При недоступности CryptAPI:

* заказ не отменяется;
* платёж не считается неоплаченным;
* увеличивается `poll_failures`;
* назначается следующий poll;
* пользователь видит сохранённый статус.

---

# 15. Фоновые worker-ы

Все worker-ы запускаются внутри одного процесса через lifespan Raito.

```text
telegram polling
payment polling
order expiration
manager reminders
notification outbox
database backup
```

## 15.1. PaymentPoller

Ищет платежи:

```sql
WHERE status IN (
    'WAITING',
    'DETECTED',
    'PARTIALLY_PAID',
    'EXPIRED'
)
AND next_poll_at <= CURRENT_TIMESTAMP
```

## 15.2. OrderExpirationWorker

Раз в минуту:

* ищет истёкшие неоплаченные заказы;
* переводит их в `EXPIRED`;
* не прекращает grace-period polling.

## 15.3. ManagerReminderWorker

Если заказ находится в очереди дольше SLA:

```text
5 минут  → повтор менеджерам
15 минут → уведомление администратору
30 минут → критическое уведомление владельцу
```

## 15.4. NotificationOutboxWorker

Уведомления сначала сохраняются в SQLite:

```text
outbox_messages
```

Worker отправляет их в Telegram.

Это исключает потерю уведомления, если приложение завершилось между изменением статуса и `bot.send_message()`.

## 15.5. BackupWorker

Раз в сутки:

1. выполняет SQLite online backup;
2. создаёт файл с датой;
3. хранит последние N копий;
4. удаляет старые копии.

---

# 16. SQLite schema

# 16.1. users

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT,
    role TEXT NOT NULL DEFAULT 'USER',
    is_blocked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);
```

# 16.2. orders

```sql
CREATE TABLE orders (
    id TEXT PRIMARY KEY,
    number INTEGER NOT NULL UNIQUE,

    buyer_id INTEGER NOT NULL,
    recipient_username TEXT,

    stars_count INTEGER,
    package_id INTEGER,

    unit_price TEXT,
    base_amount TEXT,
    fixed_fee TEXT,
    total_amount TEXT,
    currency TEXT NOT NULL DEFAULT 'USDT',

    status TEXT NOT NULL,

    assigned_manager_id INTEGER,
    manager_comment TEXT,
    proof_file_id TEXT,
    issue_reason TEXT,

    screen_chat_id INTEGER,
    screen_message_id INTEGER,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT,
    paid_at TEXT,
    queued_at TEXT,
    assigned_at TEXT,
    processing_at TEXT,
    completed_at TEXT,
    customer_confirmed_at TEXT,

    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (assigned_manager_id) REFERENCES users(id)
);
```

Индексы:

```sql
CREATE INDEX idx_orders_buyer
ON orders(buyer_id);

CREATE INDEX idx_orders_status
ON orders(status);

CREATE INDEX idx_orders_queue
ON orders(status, queued_at);

CREATE INDEX idx_orders_manager
ON orders(assigned_manager_id, status);
```

# 16.3. star_packages

```sql
CREATE TABLE star_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stars_count INTEGER NOT NULL,
    price_usdt TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

# 16.4. payments

```sql
CREATE TABLE payments (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,

    provider TEXT NOT NULL DEFAULT 'CRYPTAPI',
    ticker TEXT NOT NULL,
    network TEXT NOT NULL,

    expected_amount TEXT NOT NULL,
    confirmed_amount TEXT NOT NULL DEFAULT '0',
    pending_amount TEXT NOT NULL DEFAULT '0',
    overpaid_amount TEXT NOT NULL DEFAULT '0',

    address_in TEXT,
    address_out TEXT,
    callback_url TEXT,
    callback_nonce TEXT,

    minimum_transaction TEXT,
    status TEXT NOT NULL,

    poll_failures INTEGER NOT NULL DEFAULT 0,
    last_polled_at TEXT,
    next_poll_at TEXT,

    created_at TEXT NOT NULL,
    detected_at TEXT,
    confirmed_at TEXT,
    expires_at TEXT NOT NULL,
    grace_expires_at TEXT NOT NULL,

    raw_create_response TEXT,

    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

# 16.5. payment_transactions

```sql
CREATE TABLE payment_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id TEXT NOT NULL,

    ticker TEXT NOT NULL,
    txid_in TEXT NOT NULL,
    txid_out TEXT,

    value_coin TEXT NOT NULL,
    value_forwarded_coin TEXT,
    fee_coin TEXT,

    confirmations INTEGER NOT NULL DEFAULT 0,
    is_pending INTEGER NOT NULL,
    is_confirmed INTEGER NOT NULL,

    first_seen_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    raw_data TEXT,

    UNIQUE(ticker, txid_in),

    FOREIGN KEY (payment_id) REFERENCES payments(id)
);
```

# 16.6. order_events

```sql
CREATE TABLE order_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    actor_user_id INTEGER,

    event_type TEXT NOT NULL,
    old_status TEXT,
    new_status TEXT,
    payload TEXT,

    created_at TEXT NOT NULL,

    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (actor_user_id) REFERENCES users(id)
);
```

# 16.7. support_tickets

```sql
CREATE TABLE support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_id TEXT,

    category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN',
    message TEXT,
    assigned_admin_id INTEGER,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    closed_at TEXT,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

# 16.8. outbox_messages

```sql
CREATE TABLE outbox_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    chat_id INTEGER NOT NULL,
    message_type TEXT NOT NULL,
    payload TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'PENDING',
    attempts INTEGER NOT NULL DEFAULT 0,
    next_attempt_at TEXT NOT NULL,

    created_at TEXT NOT NULL,
    sent_at TEXT,
    last_error TEXT
);
```

# 16.9. settings

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_by INTEGER,
    updated_at TEXT NOT NULL
);
```

---

# 17. Состояние диалога

Redis FSM отсутствует.

Использовать таблицу:

```sql
CREATE TABLE user_sessions (
    user_id INTEGER PRIMARY KEY,
    state TEXT,
    data TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    expires_at TEXT,

    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Примеры состояний:

```text
WAITING_RECIPIENT
WAITING_CUSTOM_STARS
WAITING_SUPPORT_MESSAGE
WAITING_MANAGER_COMMENT
WAITING_PROOF
WAITING_ADMIN_VALUE
```

После перезапуска приложения пользователь не теряет незавершённый checkout.

---

# 18. Архитектура кода

```text
teleprism/
├── app/
│   ├── __init__.py
│   ├── bot.py
│   ├── bootstrap.py
│   ├── config.py
│   ├── container.py
│   │
│   ├── core/
│   │   ├── enums.py
│   │   ├── errors.py
│   │   ├── models.py
│   │   ├── money.py
│   │   ├── time.py
│   │   └── ids.py
│   │
│   ├── db/
│   │   ├── connection.py
│   │   ├── migrations.py
│   │   ├── transaction.py
│   │   └── backup.py
│   │
│   ├── repositories/
│   │   ├── users.py
│   │   ├── sessions.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   ├── packages.py
│   │   ├── tickets.py
│   │   ├── outbox.py
│   │   └── settings.py
│   │
│   ├── services/
│   │   ├── user_service.py
│   │   ├── session_service.py
│   │   ├── pricing_service.py
│   │   ├── checkout_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   ├── manager_service.py
│   │   ├── support_service.py
│   │   ├── notification_service.py
│   │   └── audit_service.py
│   │
│   ├── integrations/
│   │   └── cryptapi/
│   │       ├── client.py
│   │       ├── schemas.py
│   │       ├── provider.py
│   │       └── parser.py
│   │
│   ├── handlers/
│   │   ├── user/
│   │   │   ├── start.py
│   │   │   ├── menu.py
│   │   │   ├── checkout.py
│   │   │   ├── payment.py
│   │   │   ├── orders.py
│   │   │   └── support.py
│   │   │
│   │   ├── manager/
│   │   │   ├── queue.py
│   │   │   ├── assignment.py
│   │   │   ├── execution.py
│   │   │   └── history.py
│   │   │
│   │   └── admin/
│   │       ├── dashboard.py
│   │       ├── orders.py
│   │       ├── payments.py
│   │       ├── pricing.py
│   │       ├── managers.py
│   │       ├── users.py
│   │       └── settings.py
│   │
│   ├── keyboards/
│   │   ├── common.py
│   │   ├── user.py
│   │   ├── checkout.py
│   │   ├── payment.py
│   │   ├── manager.py
│   │   └── admin.py
│   │
│   ├── presenters/
│   │   ├── home.py
│   │   ├── checkout.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── manager.py
│   │
│   ├── workers/
│   │   ├── runner.py
│   │   ├── payment_poller.py
│   │   ├── order_expiration.py
│   │   ├── manager_reminders.py
│   │   ├── notification_outbox.py
│   │   └── backups.py
│   │
│   ├── middlewares/
│   │   ├── database.py
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── throttling.py
│   │   └── maintenance.py
│   │
│   └── utils/
│       ├── usernames.py
│       ├── qr.py
│       ├── callbacks.py
│       └── telegram.py
│
├── migrations/
├── tests/
├── data/
│   ├── teleprism.sqlite3
│   └── backups/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── example.env
└── README.md
```

---

# 19. Разделение ответственности

## Handler

Отвечает только за:

* принятие update;
* первичную валидацию;
* вызов service;
* отображение результата.

## Service

Отвечает за:

* бизнес-правила;
* переход статусов;
* создание заказа;
* расчёт цены;
* обработку оплаты;
* назначение менеджера.

## Repository

Отвечает только за SQLite.

## Presenter

Формирует:

* текст;
* caption;
* отображаемый статус;
* клавиатуру экрана.

## Worker

Запускает периодические операции.

## Integration

Работает с внешним API и ничего не знает о Telegram handler-ах.

---

# 20. Конфигурация

```env
ENVIRONMENT=development

BOT_TOKEN=
BOT_USERNAME=

OWNER_IDS=123456789
MANAGER_CHAT_ID=-1001234567890

DATABASE_PATH=./data/teleprism.sqlite3
BACKUP_DIRECTORY=./data/backups
BACKUP_RETENTION_DAYS=14

CRYPTAPI_TICKER=trc20/usdt
CRYPTAPI_WALLET_ADDRESS=
CRYPTAPI_CALLBACK_SINK=
CRYPTAPI_CONFIRMATIONS=1

PAYMENT_TTL_MINUTES=30
PAYMENT_GRACE_PERIOD_HOURS=24
PAYMENT_POLL_INITIAL_INTERVAL=10
PAYMENT_POLL_NORMAL_INTERVAL=20
PAYMENT_POLL_EXPIRED_INTERVAL=120
PAYMENT_POLL_CONCURRENCY=5

MIN_STARS=50
MAX_STARS=10000
CUSTOM_STARS_STEP=50

MANAGER_SLA_WARNING_MINUTES=5
MANAGER_SLA_ADMIN_MINUTES=15
MANAGER_PROCESSING_TIMEOUT_MINUTES=30

REQUIRE_MANAGER_PROOF=false

RAITO_HOT_RELOAD=true
RAITO_REPL_ENABLED=true

LOG_LEVEL=INFO
```

Для production:

```env
RAITO_HOT_RELOAD=false
RAITO_REPL_ENABLED=false
```

REPL может быть включён только для OWNER.

---

# 21. Безопасность

Обязательно:

* токен бота только в environment;
* crypto wallet только в environment;
* SQLite не хранить в публичном репозитории;
* права файла базы `600`;
* резервные копии;
* parameterized SQL;
* `Decimal` вместо `float`;
* уникальные `txid`;
* атомарное назначение менеджера;
* журнал административных действий;
* rate limiting;
* ограничение callback_data;
* проверка роли на каждом manager/admin handler;
* экранирование пользовательского текста;
* запрет прямых SQL-запросов из handlers.

Не хранить:

* приватный ключ криптокошелька;
* seed phrase;
* Telegram session менеджера;
* пароль аккаунта менеджера;
* данные банковской карты.

TelePrism требует только публичный адрес получения USDT.

---

# 22. Rate limiting без Redis

Использовать in-memory limiter Raito.

Пример:

```text
/start              5 в минуту
создание заказа     5 за 10 минут
проверка оплаты     1 за 5 секунд
support             5 за 10 минут
manager action      30 в минуту
admin action        60 в минуту
```

После перезапуска лимиты сбрасываются. Это допустимо, поскольку лимиты не являются финансовым источником истины.

Финансовая идемпотентность обеспечивается SQLite.

---

# 23. Логирование

Использовать structured logging.

Поля:

```text
event
telegram_user_id
order_id
payment_id
txid
manager_id
old_status
new_status
duration_ms
error
```

События:

```text
user_created
order_created
payment_address_created
payment_poll_started
payment_detected
payment_partially_paid
payment_confirmed
payment_overpaid
payment_late
order_queued
order_assigned
order_processing
order_completed
order_issue
admin_action
cryptapi_error
telegram_error
database_error
```

Не выводить полный callback nonce и секреты.

---

# 24. Обработка ошибок

## CryptAPI недоступен при создании

* заказ остаётся `DRAFT`;
* payment переводится в `FAILED`;
* пользователь видит ошибку;
* разрешается повторить;
* новый адрес создаётся только после явного retry.

## CryptAPI недоступен при polling

* статус не меняется;
* заказ не отменяется;
* увеличивается счётчик ошибок;
* polling повторяется позже.

## Telegram API недоступен

* изменение состояния сохраняется;
* уведомление помещается в outbox;
* worker повторяет отправку.

## SQLite locked

* повторить транзакцию;
* использовать busy timeout;
* не выполнять долгие сетевые запросы внутри SQL-транзакции.

## Перезапуск приложения

После запуска:

1. выполняются миграции;
2. проверяется SQLite;
3. восстанавливаются worker-ы;
4. продолжается polling активных платежей;
5. отправляются pending outbox notifications;
6. long polling Telegram запускается последним.

---

# 25. Тестирование

## Unit

Покрыть:

* нормализацию username;
* расчёт цены;
* `Decimal`;
* ограничения количества;
* переходы статусов;
* частичную оплату;
* несколько транзакций;
* переплату;
* позднюю оплату;
* дедупликацию txid;
* формирование polling schedule;
* права ролей;
* форматирование карточек.

## Integration

Проверить:

* создание пользователя;
* создание заказа;
* создание CryptAPI payment;
* сохранение address;
* polling без транзакций;
* pending transaction;
* confirmed transaction;
* частичную оплату;
* доплату вторым txid;
* атомарное назначение менеджера;
* завершение;
* outbox retry;
* восстановление после перезапуска.

## Конкурентный тест

Два менеджера одновременно нажимают:

```text
Взять заказ
```

Ожидается:

```text
один получает заказ;
второй получает отказ;
назначение одно;
событие назначения одно;
статус консистентен.
```

---

# 26. Docker

Docker Compose содержит только приложение:

```yaml
services:
  teleprism:
    build: .
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
```

Не добавлять:

* PostgreSQL;
* Redis;
* Nginx;
* frontend;
* backend API;
* Celery;
* RabbitMQ.

При наличии passive callback sink он не является частью TelePrism и не обрабатывает данные приложения.

---

# 27. Команды

## Пользователь

```text
/start
/buy
/orders
/price
/support
/help
/cancel
```

## Менеджер

```text
/manager
/queue
/my_orders
```

## Администратор

```text
/admin
/orders
/payments
/packages
/managers
/users
/settings
/stats
```

Команды являются запасным способом навигации. Основной интерфейс строится на кнопках.

---

# 28. Что не входит в MVP

Не реализовывать:

* WebApp;
* сайт;
* PostgreSQL;
* Redis;
* Telegram webhook;
* платёжный webhook handler;
* автоматическую отправку Stars;
* Fragment automation;
* userbot;
* хранение Telegram user sessions;
* реферальную систему;
* промокоды;
* внутренний баланс;
* автоматические возвраты;
* несколько валют;
* несколько сетей;
* локализацию;
* публичное API;
* веб-панель администратора;
* горизонтальное масштабирование.

---

# 29. Критерии приёмки

Проект готов, если:

1. Бот работает через Telegram long polling.
2. В проекте нет Telegram webhook.
3. В проекте нет платёжного webhook handler.
4. В проекте нет HTTP-сервера.
5. В проекте нет Redis.
6. Все данные хранятся в SQLite.
7. SQLite работает в WAL mode.
8. Пользователь может выбрать получателя.
9. Пользователь может выбрать пакет Stars.
10. Пользователь может ввести своё количество.
11. Стоимость фиксируется при создании заказа.
12. CryptAPI создаёт платёжный адрес.
13. Пользователь получает адрес, сумму и QR-код.
14. Статус оплаты проверяется через CryptAPI Logs polling.
15. Одна транзакция не учитывается дважды.
16. Поддерживается частичная оплата.
17. Поддерживается доплата несколькими транзакциями.
18. Поддерживается переплата.
19. Поддерживается поздняя оплата.
20. После полной оплаты заказ передаётся менеджерам.
21. Только один менеджер может взять заказ.
22. Менеджер может начать выполнение.
23. Менеджер может завершить заказ.
24. Пользователь получает уведомление.
25. Пользователь может подтвердить получение.
26. Пользователь может открыть спор.
27. Администратор может управлять тарифами.
28. Администратор может управлять менеджерами.
29. Все изменения статуса записываются в журнал.
30. После перезапуска активные платежи продолжают опрашиваться.
31. Неотправленные уведомления восстанавливаются из outbox.
32. Используются цветные кнопки.
33. Пользовательский интерфейс не требует WebApp.
34. Основной flow проходится кнопками без команд.
35. В чате не создаётся помойка из нового сообщения на каждый callback.

---

# 30. Итоговый flow системы

```text
/start
  ↓
Главное меню
  ↓
Купить Stars
  ↓
Себе / другому
  ↓
Подтверждение username
  ↓
Выбор количества
  ↓
Итог заказа
  ↓
Создание CryptAPI address
  ↓
QR + адрес + сумма
  ↓
PaymentPoller → CryptAPI Logs
  ↓
Оплата обнаружена
  ↓
Подтверждения сети
  ↓
Полная оплата
  ↓
Очередь менеджеров
  ↓
Менеджер атомарно берёт заказ
  ↓
Менеджер отправляет Stars
  ↓
Менеджер подтверждает выполнение
  ↓
Пользователь получает уведомление
  ↓
Получено / проблема
```

---

# 31. Риск платформенной совместимости

Telegram указывает, что цифровые товары и услуги внутри ботов должны продаваться за Telegram Stars. TelePrism, напротив, принимает криптовалюту за сами Stars, поэтому перед публичным запуском необходимо отдельно проверить соответствие актуальным Bot Terms и Stars Terms. Это не архитектурная проблема, а потенциальная проблема блокировки проекта, что обычно несколько неприятнее отсутствующего индекса в SQLite.

