from app.main import app

# Export the app for Vercel
# This is the ASGI application that Vercel will use
def handler(scope, receive, send):
    return app(scope, receive, send)
