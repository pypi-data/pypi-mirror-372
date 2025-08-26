py-eloquent — minimal Eloquent-like ORM for MySQL

Install:
  pip install pymysql
  pip install .

Quick example:
  from py_eloquent import Database, Model, Integer, String
  Database.connect(host='localhost', user='root', password='pwd', db='test')

  class User(Model):
      id = Integer(primary_key=True)
      name = String()
      email = String()

  u = User(name='Alice', email='a@example.com')
  u.save()
  users = User.where(name='Alice').get()

Publishing to PyPI:
  1. Build: python -m build
  2. Upload: python -m twine upload dist/*
