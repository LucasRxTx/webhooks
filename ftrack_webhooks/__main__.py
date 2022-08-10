from ftrack_webhooks import app as __app

app = __app.create_app()

app.run(host="0.0.0.0", port=8000)
