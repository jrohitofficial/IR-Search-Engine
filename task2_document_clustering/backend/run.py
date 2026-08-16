"""Entry point for the Task 2 document clustering backend."""
from app import create_app
from config.settings import settings

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=settings.TASK2_PORT, debug=False, use_reloader=False)
