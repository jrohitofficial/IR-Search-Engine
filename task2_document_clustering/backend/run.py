"""Entry point for the Task 2 document clustering backend."""
import os
from app import create_app
from config.settings import settings

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", settings.TASK2_PORT))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
