import os
from app import create_app
from app.views import analysis
from app.views import patients

app = create_app()

if __name__ == "__main__":
    # 开发模式下仍可以直接运行
    app.run(debug=True, host="0.0.0.0", port=8080)