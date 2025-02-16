from waitress import serve

from iii.wsgi import application  # Replace "iii" with your actual project name

if __name__ == "__main__":
    serve(application, listen="127.0.0.1:8000")
