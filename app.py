from web import create_app
from web.config.config import DevConfig
app = create_app(DevConfig())
if __name__ == '__main__':
    app.run()
