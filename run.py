from app import create_app
import os
import dotenv
dotenv.load_dotenv()

PORT = 3000
if os.environ.get('MODE') == 'PRODUCTION':
    debug = False
    print("PRODUCTION MODE")
else:
    print("DEVELOPMENT MODE")
    debug = True
app = create_app()
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, debug=debug)
