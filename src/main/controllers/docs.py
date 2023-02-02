from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/docs'

bp = get_swaggerui_blueprint(
        "/docs",  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        "/docs/openapi.yaml"
    )
