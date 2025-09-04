швидкий старт

1) створити бот-токен у @BotFather і скопіювати його.
2) завантажити ці файли та встановити залежності:
   pip install -r requirements.txt
3) встановити змінну середовища TELEGRAM_BOT_TOKEN та запустити:
   export TELEGRAM_BOT_TOKEN=123456:ABC...   # mac/linux
   python bot.py
   (у windows powershell)
   setx TELEGRAM_BOT_TOKEN "123456:ABC..."
   python bot.py
4) відредагувати flow.yaml під ваш sendpulse-флоу:
   - замініть тексти в "text"
   - у "options" використовуйте:
       label: текст кнопки
       target: id іншої ноди  (для переходу)
       url:    посилання      (для відкриття лінка)
   - start_node: нода, що показується на /start

додатково
- щоб додати кнопку "назад", просто додайте опцію з target на попередню ноду або використайте спеціальний target "__back" (див. код, за замовчуванням теж працює).
- для постійного збереження стану замість USER_STATE використайте БД/redis/ptb persistence.