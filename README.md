 Для работы необходимо в файле conf.py заменить данные на свои
 
 Запуск из консоли: 
 
Создание python cli.py create Имя Фамилия --birth-date 1990-01-01 --phone +7-916-000-00-00 --document-type паспорт --document-number 0000000000

Вывод на экран первых 10 пользователей: python cli.py show

Вывод на экран произвольного количества пользователей: python cli.py show 8

Вывод на экран количества сохраненных пользователей: python cli.py count

P.S.
 Перед созданием пациента логируется изменение полей, как сделать в декораторе так, чтобы логирование шло именно при реальном изменении, пока не придумал.

P.P.S так же необходимо проделать:
pip3 install psycopg2-binary
В Linux может потребоваться sudo apt install libpq-dev
Ну и сам postgres:

Create the file /etc/apt/sources.list.d/pgdg.list and add a line for the repository
deb http://apt.postgresql.org/pub/repos/apt/ YOUR_UBUNTU_VERSION_HERE-pgdg main
Import the repository signing key, and update the package lists
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
