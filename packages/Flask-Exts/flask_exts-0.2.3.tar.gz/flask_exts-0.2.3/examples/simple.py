# simple.py

from flask import Flask
from flask_exts import Manager
from flask_exts.admin import expose
from flask_exts.admin import BaseView
from flask_exts.views.index_view import IndexView


class MockView(BaseView):
    @expose("/")
    def index(self):
        return "Success!"


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
manager = Manager()
manager.init_app(app)
# Register the index view
manager.admin.add_view(IndexView(), is_menu=False)
# Register a mock view
manager.admin.add_view(MockView())


if __name__ == "__main__":
    app.run(debug=True)
