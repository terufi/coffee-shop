# Coffee Shop API

REST API интернет-магазина кофе на Django + DRF.
- JWT-авторизация (SimpleJWT)
- Swagger (`/api/docs/`)
- Пагинация
- 3 связанные таблицы (Category, Product, Order)

## Запуск
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
