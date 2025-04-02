
1)Реализовал все основные функции:
![image](https://github.com/user-attachments/assets/7791a35e-2cec-41a9-8ee8-54ea9695556e)
+ Реализовал доп.функцию в частности удаление неиспользуемых ссылок путем добавление в crud.delete_expired_links(db) ещё и условие на то, что ссылка не использовалась более 90 дней. 
+ Реализовал кэширование топ 100 самых популярных ссылок через Redis

Использовал Postgres как основную БД:
Подключался к ней также через dBeaver:
![image](https://github.com/user-attachments/assets/700fb4c7-c36a-4dad-9b90-60883751845c)

Postgres и redis поднимал через docker, сам сервис - тоже. Dockerfile и dockercompose.yaml приложены в репозитории.

![image](https://github.com/user-attachments/assets/f1fdf464-2d61-4cbb-941e-431190314b1d)
