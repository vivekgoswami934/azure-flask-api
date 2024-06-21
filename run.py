from app import create_app
from waitress import serve

import azure.functions as func


app = create_app()

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the WSGI handler.
    """
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)

        
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8000)


